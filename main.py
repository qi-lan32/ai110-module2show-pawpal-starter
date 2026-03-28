import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "tests"))

from pawpal_system import Owner, Pet, Task, Scheduler
from test_pawpal import (
    test_mark_complete_updates_status,
    test_add_task_increases_scheduler_task_count,
    test_ownership_guard_raises_for_unowned_pet,
    test_filter_by_pet_returns_only_that_pets_tasks,
    test_filter_by_status_returns_matching_tasks,
    test_complete_task_daily_spawns_next_occurrence,
    test_complete_task_weekly_spawns_next_occurrence,
    test_complete_task_one_time_does_not_spawn,
)


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

# ── Conflict detection demo ────────────────────────────────────────────────────
# Same-pet conflict: Buddy gets a second walk at 07:30 (same time as his generated walk)
# Different-pet conflict: Whiskers gets a walk at 17:00 (same time as Buddy's afternoon walk)

scheduler.add_task(Task(
    task_type="grooming",
    scheduled_time="07:30",   # Buddy already has a walk at 07:30 from create_plan
    status="pending",
    priority=2,
    pet=buddy
))

scheduler.add_task(Task(
    task_type="grooming",
    scheduled_time="17:00",   # Buddy already has a walk at 17:00
    status="pending",
    priority=2,
    pet=whiskers
))

print("Checking for scheduling conflicts...")
warnings = scheduler.detect_conflicts()
if warnings:
    for msg in warnings:
        print(f"  {msg}")
else:
    print("  No conflicts found.")
print()

# ── Run tests ──────────────────────────────────────────────────────────────────

tests = [
    test_mark_complete_updates_status,
    test_add_task_increases_scheduler_task_count,
    test_ownership_guard_raises_for_unowned_pet,
    test_filter_by_pet_returns_only_that_pets_tasks,
    test_filter_by_status_returns_matching_tasks,
    test_complete_task_daily_spawns_next_occurrence,
    test_complete_task_weekly_spawns_next_occurrence,
    test_complete_task_one_time_does_not_spawn,
]

print("Running tests...")
for test_fn in tests:
    test_fn()
    print(f"  {test_fn.__name__}  PASSED")
print()
