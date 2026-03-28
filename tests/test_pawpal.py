from datetime import date, timedelta
from pawpal_system import Owner, Pet, Task, Scheduler


# ── Shared helper ──────────────────────────────────────────────────────────────

def _make_scheduler():
    """Return a fresh (owner, buddy, whiskers, scheduler) tuple for each test."""
    owner = Owner(name="Sarah", location="Austin, TX")
    buddy = Pet("Buddy", "dog", "Golden Retriever", 4, "male", "healthy")
    whiskers = Pet("Whiskers", "cat", "Siamese", 7, "female", "arthritis")
    owner.add_pet(buddy)
    owner.add_pet(whiskers)
    owner.edit_preference("walk_time", "07:30")
    owner.edit_preference("feed_times", ["07:00", "17:30"])
    owner.edit_constraint("medication_time", "09:00")
    scheduler = Scheduler(owner=owner)
    return owner, buddy, whiskers, scheduler


# ── Existing tests (fixed) ─────────────────────────────────────────────────────

def test_mark_complete_updates_status():
    """Calling mark_complete() on a task should set its status to 'completed'."""
    pet = Pet("Buddy", "dog", "Golden Retriever", 4, "male", "healthy")
    task = Task(task_type="feeding", scheduled_time="08:00", status="pending", priority=3, pet=pet)

    task.mark_complete()

    assert task.status == "completed"


def test_add_task_increases_scheduler_task_count():
    """Adding a task via the scheduler should increase scheduler.tasks by 1."""
    owner = Owner(name="Sarah", location="Austin, TX")
    pet = Pet("Buddy", "dog", "Golden Retriever", 4, "male", "healthy")
    owner.add_pet(pet)
    scheduler = Scheduler(owner=owner)

    assert len(scheduler.tasks) == 0

    scheduler.add_task(Task(task_type="walk", scheduled_time="08:00", status="pending", priority=2, pet=pet))

    assert len(scheduler.tasks) == 1


# ── Ownership guard ────────────────────────────────────────────────────────────

def test_ownership_guard_raises_for_unowned_pet():
    """add_task() must raise ValueError when the task's pet does not belong to the owner."""
    _, _, _, scheduler = _make_scheduler()
    stranger = Pet("Rex", "dog", "Labrador", 2, "male", "healthy")

    try:
        scheduler.add_task(Task("walk", "10:00", "pending", 2, stranger))
        assert False, "FAIL: expected ValueError was not raised"
    except ValueError:
        pass


# ── Filter by pet ──────────────────────────────────────────────────────────────

def test_filter_by_pet_returns_only_that_pets_tasks():
    """get_tasks_for_pet() must return tasks belonging exclusively to the given pet."""
    _, buddy, whiskers, scheduler = _make_scheduler()
    scheduler.create_plan()

    buddy_tasks    = scheduler.get_tasks_for_pet(buddy)
    whiskers_tasks = scheduler.get_tasks_for_pet(whiskers)

    assert all(t.pet is buddy    for t in buddy_tasks)
    assert all(t.pet is whiskers for t in whiskers_tasks)
    assert len(buddy_tasks) + len(whiskers_tasks) == len(scheduler.tasks)


# ── Filter by status ───────────────────────────────────────────────────────────

def test_filter_by_status_returns_matching_tasks():
    """get_tasks_by_status() must return only tasks with the requested status."""
    _, _, _, scheduler = _make_scheduler()
    scheduler.create_plan()

    # Complete one task so both statuses exist
    task_to_complete = scheduler.tasks[0]
    task_to_complete.mark_complete()

    pending_tasks   = scheduler.get_tasks_by_status("pending")
    completed_tasks = scheduler.get_tasks_by_status("completed")

    assert all(t.status == "pending"   for t in pending_tasks)
    assert all(t.status == "completed" for t in completed_tasks)
    assert len(pending_tasks) + len(completed_tasks) == len(scheduler.tasks)


# ── Recurring task: daily ──────────────────────────────────────────────────────

def test_complete_task_daily_spawns_next_occurrence():
    """Completing a daily task must add a new pending task dated today + 1 day."""
    _, _, _, scheduler = _make_scheduler()
    scheduler.create_plan()

    daily_task = next(t for t in scheduler.tasks if t.recurrence == "daily")
    count_before = len(scheduler.tasks)

    scheduler.complete_task(daily_task)

    assert daily_task.status == "completed"
    assert len(scheduler.tasks) == count_before + 1

    expected_date = (date.today() + timedelta(days=1)).isoformat()
    next_occ = next(
        (t for t in scheduler.tasks
         if t.pet is daily_task.pet
         and t.task_type == daily_task.task_type
         and t.scheduled_time == daily_task.scheduled_time
         and t.status == "pending"
         and t.scheduled_date == expected_date),
        None
    )
    assert next_occ is not None, f"No next occurrence found with scheduled_date={expected_date}"


# ── Recurring task: weekly ─────────────────────────────────────────────────────

def test_complete_task_weekly_spawns_next_occurrence():
    """Completing a weekly task must add a new pending task dated today + 7 days."""
    _, _, whiskers, scheduler = _make_scheduler()

    weekly_task = Task(
        task_type="medication",
        scheduled_time="10:00",
        status="pending",
        priority=4,
        pet=whiskers,
        recurrence="weekly",
    )
    scheduler.add_task(weekly_task)
    count_before = len(scheduler.tasks)

    scheduler.complete_task(weekly_task)

    assert weekly_task.status == "completed"
    assert len(scheduler.tasks) == count_before + 1

    expected_date = (date.today() + timedelta(weeks=1)).isoformat()
    next_occ = next(
        (t for t in scheduler.tasks
         if t.pet is whiskers
         and t.task_type == "medication"
         and t.scheduled_time == "10:00"
         and t.scheduled_date == expected_date),
        None
    )
    assert next_occ is not None, f"No weekly next occurrence found with scheduled_date={expected_date}"


# ── One-time task: no spawn ────────────────────────────────────────────────────

def test_complete_task_one_time_does_not_spawn():
    """Completing a one-time task (recurrence=None) must not add any new task."""
    _, _, whiskers, scheduler = _make_scheduler()

    one_time = Task(
        task_type="appointment",
        scheduled_time="11:00",
        status="pending",
        priority=1,
        pet=whiskers,
        recurrence=None,
    )
    scheduler.add_task(one_time)
    count_before = len(scheduler.tasks)

    scheduler.complete_task(one_time)

    assert one_time.status == "completed"
    assert len(scheduler.tasks) == count_before
