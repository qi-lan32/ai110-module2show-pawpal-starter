from pawpal_system import Owner, Pet, Task, Scheduler


# ── Setup ──────────────────────────────────────────────────────────────────────

owner = Owner(name="Sarah", location="Austin, TX")

buddy = Pet(
    name="Buddy",
    species="dog",
    breed="Golden Retriever",
    age=4,
    gender="male",
    health_condition="healthy"
)

whiskers = Pet(
    name="Whiskers",
    species="cat",
    breed="Siamese",
    age=7,
    gender="female",
    health_condition="arthritis"   # triggers a medication task
)

owner.add_pet(buddy)
owner.add_pet(whiskers)

# ── Owner preferences and constraints ─────────────────────────────────────────

owner.edit_preference("walk_time",  "07:30")
owner.edit_preference("feed_times", ["07:00", "17:30"])
owner.edit_constraint("medication_time", "09:00")

# ── Scheduler: auto-generate baseline plan ─────────────────────────────────────

scheduler = Scheduler(owner=owner)
scheduler.create_plan()   # generates feeding, walk, and medication tasks

# ── Manually add extra tasks ───────────────────────────────────────────────────

scheduler.add_task(Task(
    task_type="appointment",
    scheduled_time="14:00",
    status="pending",
    priority=1,
    pet=whiskers
))

scheduler.add_task(Task(
    task_type="walk",
    scheduled_time="17:00",
    status="pending",
    priority=2,
    pet=buddy
))

# ── Print Today's Schedule ─────────────────────────────────────────────────────

def print_schedule(scheduler: Scheduler) -> None:
    WIDTH = 52
    print()
    print("╔" + "═" * WIDTH + "╗")
    print("║" + " 🐾  TODAY'S PAWPAL+ SCHEDULE".center(WIDTH) + "║")
    print("║" + f"  Owner: {scheduler.owner.name} — {scheduler.owner.location}".ljust(WIDTH) + "║")
    print("╠" + "═" * WIDTH + "╣")

    sorted_tasks = sorted(scheduler.tasks, key=lambda t: t.scheduled_time)

    for task in sorted_tasks:
        status_icon = "✓" if task.status == "completed" else "○"
        line = f"  {task.scheduled_time}  [{status_icon}]  {task.task_type.upper():<14}  {task.pet.name}"
        print("║" + line.ljust(WIDTH) + "║")

    print("╠" + "═" * WIDTH + "╣")
    next_task = scheduler.get_next_task()
    if next_task:
        next_line = f"  Next up: {next_task.task_type} for {next_task.pet.name} at {next_task.scheduled_time}"
        print("║" + next_line.ljust(WIDTH) + "║")
    else:
        print("║" + "  All tasks complete for today!".ljust(WIDTH) + "║")
    print("╚" + "═" * WIDTH + "╝")
    print()


print_schedule(scheduler)

# ── Verify ownership guard ─────────────────────────────────────────────────────

stranger_pet = Pet("Rex", "dog", "Labrador", 2, "male", "healthy")
print("Testing ownership guard...")
try:
    scheduler.add_task(Task("walk", "10:00", "pending", 2, stranger_pet))
except ValueError as e:
    print(f"  Caught expected error: {e}")

# ── Verify task completion ─────────────────────────────────────────────────────

print("\nCompleting Buddy's morning feeding...")
morning_feed = next(t for t in scheduler.tasks
                    if t.pet == buddy and t.task_type == "feeding" and t.scheduled_time == "07:00")
morning_feed.mark_complete()
print(f"  Status: {morning_feed.status}")
print_schedule(scheduler)
