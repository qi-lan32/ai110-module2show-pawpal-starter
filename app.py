import streamlit as st
from collections import defaultdict
from pawpal_system import Pet, Task, Owner, Scheduler

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")

# ── Session state init ────────────────────────────────────────────────────────
# st.session_state is Streamlit's in-memory "vault": a dictionary that survives
# across reruns (button clicks, widget changes) for the lifetime of the browser tab.
# Keys are strings; values can be any Python object — including class instances.
#
# Structure used here:
#   st.session_state.owners          dict[str, Owner]     — all profiles ever created
#   st.session_state.schedulers      dict[str, Scheduler] — one Scheduler per Owner
#   st.session_state.active_owner    str | None           — name of the logged-in owner
#
# Pattern to safely initialise a key without overwriting it on reruns:
#   if "key" not in st.session_state:
#       st.session_state["key"] = default_value

if "owners" not in st.session_state:
    st.session_state.owners = {}                # vault: name → Owner instance
if "schedulers" not in st.session_state:
    st.session_state.schedulers = {}            # name → Scheduler instance
if "active_owner" not in st.session_state:
    st.session_state.active_owner = None        # name of currently logged-in owner

# ── Constants ─────────────────────────────────────────────────────────────────
PRIORITY_LABELS = {1: "Low", 2: "Medium", 3: "High", 4: "Critical"}
PRIORITY_COLORS = {1: "🟢", 2: "🔵", 3: "🟠", 4: "🔴"}
STATUS_ICONS = {"pending": "⏳", "completed": "✅", "skipped": "⏭️"}
TASK_TYPES = ["feeding", "walk", "medication", "appointment"]


# ── Sidebar – Owner setup ─────────────────────────────────────────────────────
with st.sidebar:
    st.title("🐾 PawPal+")
    st.subheader("Owner Setup")

    if st.session_state.active_owner is None:
        # ── LOGIN / CREATE FLOW ──────────────────────────────────────────────
        vault = st.session_state.owners  # the dict of all saved Owner instances

        # If the vault already has profiles, offer a login picker first
        if vault:
            st.markdown("**Select an existing profile:**")
            selected = st.selectbox(
                "Profiles in this session",
                options=list(vault.keys()),
                label_visibility="collapsed",
            )
            if st.button("Log in", type="primary"):
                # Just update the active pointer — the Owner object is already
                # stored in the vault, so all pets/tasks are intact
                st.session_state.active_owner = selected
                st.rerun()
            st.divider()

        # Always show the "create new" form below the picker
        with st.expander("Create a new profile", expanded=not bool(vault)):
            with st.form("owner_form"):
                new_name = st.text_input("Your Name")
                new_location = st.text_input("Location")
                if st.form_submit_button("Create Profile") and new_name:
                    if new_name in vault:
                        st.error(f"A profile named '{new_name}' already exists. Log in instead.")
                    else:
                        # Store the new Owner + Scheduler in the vault
                        new_owner = Owner(new_name, new_location)
                        st.session_state.owners[new_name] = new_owner
                        st.session_state.schedulers[new_name] = Scheduler(new_owner)
                        st.session_state.active_owner = new_name
                        st.success(f"Welcome, {new_name}!")
                        st.rerun()

    else:
        # ── LOGGED-IN STATE ──────────────────────────────────────────────────
        active_name = st.session_state.active_owner
        owner = st.session_state.owners[active_name]
        st.success(f"Logged in as **{owner.name}**")
        st.caption(f"Location: {owner.location}")

        col_sw, col_del = st.columns(2)
        if col_sw.button("Switch Account"):
            # Log out — Owner stays in the vault for next login
            st.session_state.active_owner = None
            st.rerun()
        if col_del.button("Delete Profile"):
            # Remove from vault entirely
            del st.session_state.owners[active_name]
            del st.session_state.schedulers[active_name]
            st.session_state.active_owner = None
            st.rerun()

    if st.session_state.active_owner:
        active_name = st.session_state.active_owner
        st.divider()
        st.subheader("Preferences")
        walk_time = st.text_input("Walk time (HH:MM)", value="08:00", key="pref_walk")
        feed_morning = st.text_input("Morning feed (HH:MM)", value="08:00", key="pref_feed_am")
        feed_evening = st.text_input("Evening feed (HH:MM)", value="18:00", key="pref_feed_pm")
        med_time = st.text_input("Medication time (HH:MM, blank = none)", value="", key="pref_med")
        if st.button("Save Preferences"):
            o = st.session_state.owners[active_name]
            o.edit_preference("walk_time", walk_time)
            o.edit_preference("feed_times", [feed_morning, feed_evening])
            if med_time:
                o.edit_constraint("medication_time", med_time)
            st.success("Preferences saved.")


# ── Guard: require owner ──────────────────────────────────────────────────────
if st.session_state.active_owner is None:
    st.title("Welcome to PawPal+")
    st.info("Create or log in to an owner profile in the sidebar to get started.")
    st.stop()

_active = st.session_state.active_owner
owner = st.session_state.owners[_active]
scheduler = st.session_state.schedulers[_active]

st.title(f"PawPal+ — {owner.name}'s Dashboard")

tab_pets, tab_tasks, tab_schedule, tab_next = st.tabs(
    ["🐶 Pets", "📋 Tasks", "📅 Schedule", "⚡ Next Task"]
)

# ─── TAB 1: Pets ──────────────────────────────────────────────────────────────
with tab_pets:
    st.header("My Pets")
    col_list, col_add = st.columns([1, 1], gap="large")

    with col_add:
        st.subheader("Add a Pet")
        with st.form("add_pet_form"):
            pet_name = st.text_input("Name")
            species = st.selectbox("Species", ["Dog", "Cat", "Bird", "Rabbit", "Other"])
            breed = st.text_input("Breed")
            age = st.number_input("Age (years)", min_value=0, max_value=50, value=1)
            gender = st.selectbox("Gender", ["Male", "Female"])
            health = st.text_input("Health Condition", value="healthy")
            if st.form_submit_button("Add Pet") and pet_name:
                owner.add_pet(Pet(
                    name=pet_name,
                    species=species.lower(),
                    breed=breed,
                    age=int(age),
                    gender=gender,
                    health_condition=health,
                ))
                st.success(f"{pet_name} added!")
                st.rerun()

    with col_list:
        if not owner.pets:
            st.info("No pets yet. Add one on the right.")
        else:
            for pet in list(owner.pets):
                with st.expander(f"**{pet.name}** — {pet.species.capitalize()}"):
                    st.write(f"**Breed:** {pet.breed}")
                    st.write(f"**Age:** {pet.age} yr(s) | **Gender:** {pet.gender}")
                    st.write(f"**Health:** {pet.health_condition}")
                    st.write(f"**Tasks assigned:** {len(scheduler.get_tasks_for_pet(pet))}")
                    if st.button(f"Remove {pet.name}", key=f"remove_{pet.name}"):
                        scheduler.tasks = [t for t in scheduler.tasks if t.pet is not pet]
                        owner.remove_pet(pet)
                        st.rerun()

# ─── TAB 2: Tasks ─────────────────────────────────────────────────────────────
with tab_tasks:
    st.header("Task Management")

    if not owner.pets:
        st.warning("Add a pet first before creating tasks.")
    else:
        col_task_add, col_task_list = st.columns([1, 1], gap="large")

        with col_task_add:
            st.subheader("Add a Task")
            with st.form("add_task_form"):
                task_pet_name = st.selectbox("Pet", [p.name for p in owner.pets])
                task_type = st.selectbox("Task Type", TASK_TYPES)
                task_time = st.text_input("Scheduled Time (HH:MM)", value="09:00")
                task_priority = st.select_slider(
                    "Priority", options=[1, 2, 3, 4],
                    format_func=lambda x: f"{PRIORITY_COLORS[x]} {PRIORITY_LABELS[x]}"
                )
                task_recurrence = st.selectbox(
                    "Recurrence", ["none", "daily", "weekly"],
                    format_func=lambda x: x.capitalize()
                )
                if st.form_submit_button("Add Task"):
                    selected_pet = next(p for p in owner.pets if p.name == task_pet_name)
                    try:
                        scheduler.add_task(Task(
                            task_type=task_type,
                            scheduled_time=task_time,
                            status="pending",
                            priority=task_priority,
                            pet=selected_pet,
                            recurrence=None if task_recurrence == "none" else task_recurrence,
                        ))
                        st.success(f"'{task_type}' added for {task_pet_name}.")
                        st.rerun()
                    except ValueError as e:
                        st.error(str(e))

        with col_task_list:
            st.subheader("All Tasks")
            if not scheduler.tasks:
                st.info("No tasks yet.")
            else:
                filter_pet = st.selectbox(
                    "Filter by pet", ["All"] + [p.name for p in owner.pets], key="filter_pet"
                )
                filter_status = st.selectbox(
                    "Filter by status", ["All", "pending", "completed", "skipped"], key="filter_status"
                )
                if filter_pet != "All":
                    sel_pet = next(p for p in owner.pets if p.name == filter_pet)
                    display_tasks = scheduler.get_tasks_for_pet(sel_pet)
                else:
                    display_tasks = list(scheduler.tasks)
                if filter_status != "All":
                    display_tasks = scheduler.get_tasks_by_status(filter_status)
                    if filter_pet != "All":
                        display_tasks = [t for t in display_tasks if t.pet is sel_pet]
                for i, task in enumerate(display_tasks):
                    icon = STATUS_ICONS.get(task.status, "")
                    badge = f"{PRIORITY_COLORS[task.priority]} {PRIORITY_LABELS[task.priority]}"
                    recur_label = f" 🔁 {task.recurrence}" if task.recurrence else ""
                    with st.expander(
                        f"{icon} [{task.scheduled_time}] {task.task_type.capitalize()} — {task.pet.name} | {badge}{recur_label}"
                    ):
                        st.write(f"**Status:** {task.status}")
                        c1, c2, c3 = st.columns(3)
                        if c1.button("Complete", key=f"done_{i}"):
                            scheduler.complete_task(task)
                            st.rerun()
                        new_time = c2.text_input("New time", key=f"rtime_{i}", placeholder="HH:MM")
                        if c2.button("Reschedule", key=f"resched_{i}") and new_time:
                            task.reschedule(new_time)
                            st.rerun()
                        if c3.button("Remove", key=f"del_{i}"):
                            scheduler.remove_task(task)
                            st.rerun()

# ─── TAB 3: Schedule ──────────────────────────────────────────────────────────
with tab_schedule:
    st.header("Daily Schedule")
    col_gen, col_view = st.columns([1, 2], gap="large")

    with col_gen:
        st.subheader("Auto-Generate Plan")
        st.write(
            "Creates feeding, walk, and medication tasks for all pets "
            "based on the preferences set in the sidebar."
        )
        if st.button("Generate Plan", type="primary"):
            if not owner.pets:
                st.warning("Add at least one pet first.")
            else:
                scheduler.create_plan()
                st.success("Plan generated and prioritized!")
                st.rerun()
        st.divider()
        if st.button("Prioritize Tasks"):
            scheduler.prioritize_tasks()
            st.success("Tasks sorted by priority then time.")
            st.rerun()
        st.divider()
        if st.button("Clear Plan", type="secondary"):
            scheduler.clear_plan()
            st.success("All tasks cleared.")
            st.rerun()

    with col_view:
        st.subheader("Prioritized Task List")
        if not scheduler.tasks:
            st.info("No tasks scheduled yet.")
        else:
            conflicts = scheduler.detect_conflicts()
            if conflicts:
                st.warning(f"⚠️ {len(conflicts)} scheduling conflict(s) detected!")
                for msg in conflicts:
                    st.caption(f"  • {msg}")
            time_groups: dict = defaultdict(list)
            for t in scheduler.get_tasks_by_time():
                time_groups[t.scheduled_time].append(t)
            for time_slot in time_groups.keys():
                st.markdown(f"**🕐 {time_slot}**")
                for t in time_groups[time_slot]:
                    icon = STATUS_ICONS.get(t.status, "")
                    badge = PRIORITY_COLORS[t.priority]
                    st.markdown(
                        f"&nbsp;&nbsp;&nbsp;{icon} {badge} "
                        f"`{t.task_type.capitalize()}` — **{t.pet.name}** ({t.status})"
                    )
                st.write("")

# ─── TAB 4: Next Task ─────────────────────────────────────────────────────────
with tab_next:
    st.header("Next Task")
    st.write("Shows the highest-priority pending task.")

    next_task = scheduler.get_next_task()
    if next_task is None:
        st.success("All tasks are completed — nothing left to do!")
    else:
        st.metric(
            label=f"{PRIORITY_COLORS[next_task.priority]} Priority",
            value=PRIORITY_LABELS[next_task.priority],
        )
        st.markdown(f"**Task:** {next_task.task_type.capitalize()}")
        st.markdown(f"**Pet:** {next_task.pet.name}")
        st.markdown(f"**Scheduled Time:** {next_task.scheduled_time}")
        st.markdown(
            f"**Status:** {STATUS_ICONS.get(next_task.status, '')} {next_task.status}"
        )
        if st.button("Mark as Complete", type="primary"):
            scheduler.complete_task(next_task)
            st.success("Task marked complete!")
            st.rerun()
