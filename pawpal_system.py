from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Optional


@dataclass
class Pet:
    name: str
    species: str
    breed: str
    age: int
    gender: str
    health_condition: str
    tasks: list = field(default_factory=list)  # tasks assigned to this pet

    def edit_info(self, **kwargs) -> None:
        """Update one or more pet attributes by keyword. e.g. edit_info(age=3, health_condition='recovered')"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)


@dataclass
class Task:
    task_type: str       # e.g. "feeding", "walk", "medication", "appointment"
    scheduled_time: str  # 24h format string, e.g. "08:00"
    status: str          # "pending", "completed", or "skipped"
    priority: int        # higher number = more urgent (1=low, 4=critical)
    pet: Pet
    recurrence: Optional[str] = None   # "daily", "weekly", or None (one-time)
    scheduled_date: Optional[str] = None  # ISO date "YYYY-MM-DD"; None = no specific date

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.status = "completed"

    def reschedule(self, new_time: str) -> None:
        """Move this task to a new time and reset its status to pending."""
        self.scheduled_time = new_time
        self.status = "pending"


class Owner:
    def __init__(self, name: str, location: str):
        self.name = name
        self.location = location
        self.pets: list[Pet] = []
        self.preferences: dict = {}  # e.g. {"walk_time": "07:00", "feed_times": ["08:00", "18:00"]}
        self.constraints: dict = {}  # e.g. {"medication_time": "09:00", "max_walks_per_day": 1}

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner, ignoring duplicates."""
        if pet not in self.pets:
            self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Unregister a pet from this owner if it exists."""
        if pet in self.pets:
            self.pets.remove(pet)

    def edit_preference(self, key: str, value) -> None:
        """Set or update a scheduling preference by key."""
        self.preferences[key] = value

    def edit_constraint(self, key: str, value) -> None:
        """Set or update a scheduling constraint by key."""
        self.constraints[key] = value


class Scheduler:
    def __init__(self, owner: Owner):
        self.owner = owner          # pets are accessed via self.owner.pets
        self.tasks: list[Task] = []

    def add_task(self, task: Task) -> None:
        """Add a task only if its pet belongs to this scheduler's owner."""
        if task.pet not in self.owner.pets:
            raise ValueError(f"'{task.pet.name}' does not belong to {self.owner.name}.")
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a task from the schedule by identity."""
        self.tasks = [t for t in self.tasks if t is not task]

    def prioritize_tasks(self) -> None:
        """Sort tasks by priority (desc) then scheduled_time (asc)."""
        self.tasks.sort(key=lambda t: (-t.priority, t.scheduled_time))

    def get_next_task(self) -> Optional[Task]:
        """Return the highest-priority pending task, or None if all are done."""
        pending = [t for t in self.tasks if t.status == "pending"]
        if not pending:
            return None
        return max(pending, key=lambda t: t.priority)

    def get_tasks_by_time(self) -> list[Task]:
        """Return all tasks sorted by scheduled_time ascending."""
        return sorted(self.tasks, key=lambda t: t.scheduled_time)

    def get_tasks_for_pet(self, pet: Pet) -> list[Task]:
        """Return all tasks assigned to a specific pet."""
        return [t for t in self.tasks if t.pet is pet]

    def get_tasks_by_status(self, status: str) -> list[Task]:
        """Return all tasks with the given status ('pending', 'completed', 'skipped')."""
        return [t for t in self.tasks if t.status == status]

    def detect_conflicts(self) -> list[str]:
        """
        Scan pending tasks for scheduling overlaps and return warning strings.
        Never raises — always returns a (possibly empty) list of messages.

        Two severity levels:
          [CONFLICT] Same pet scheduled for two tasks at the same time.
                     The pet physically cannot do both; one must be moved.
          [WARNING]  Different pets overlap at the same time.
                     The owner may not be able to attend to both simultaneously.
        """
        warnings: list[str] = []
        pending = [t for t in self.tasks if t.status == "pending"]
        for i in range(len(pending)):
            for j in range(i + 1, len(pending)):
                a, b = pending[i], pending[j]
                if a.scheduled_time != b.scheduled_time:
                    continue
                if a.pet is b.pet:
                    warnings.append(
                        f"[CONFLICT] {a.pet.name} has '{a.task_type}' and "
                        f"'{b.task_type}' both scheduled at {a.scheduled_time}."
                    )
                else:
                    warnings.append(
                        f"[WARNING] '{a.task_type}' for {a.pet.name} and "
                        f"'{b.task_type}' for {b.pet.name} overlap at {a.scheduled_time}."
                    )
        return warnings

    def complete_task(self, task: Task) -> None:
        """
        Mark a task complete and, if it recurs, schedule the next occurrence.

        timedelta arithmetic:
          date.today() + timedelta(days=1)  → tomorrow        (daily)
          date.today() + timedelta(weeks=1) → same day next week (weekly)
        The result is converted to an ISO string ("YYYY-MM-DD") via .isoformat()
        so it can be stored in scheduled_date without importing datetime everywhere.
        """
        task.mark_complete()
        if task.recurrence == "daily":
            next_date = date.today() + timedelta(days=1)
        elif task.recurrence == "weekly":
            next_date = date.today() + timedelta(weeks=1)
        else:
            return  # one-time task — nothing more to do
        self.add_task(Task(
            task_type=task.task_type,
            scheduled_time=task.scheduled_time,
            status="pending",
            priority=task.priority,
            pet=task.pet,
            recurrence=task.recurrence,
            scheduled_date=next_date.isoformat(),
        ))

    def clear_plan(self) -> None:
        """Remove only auto-generated (recurrence='daily') tasks, preserving manually added tasks."""
        for task in [t for t in self.tasks if t.recurrence == "daily"]:
            self.remove_task(task)

    def _daily_task(self, task_type: str, scheduled_time: str, priority: int, pet: Pet) -> Task:
        """Build a pending daily Task — shared boilerplate for create_plan."""
        return Task(
            task_type=task_type,
            scheduled_time=scheduled_time,
            status="pending",
            priority=priority,
            pet=pet,
            recurrence="daily",
        )

    def create_plan(self) -> None:
        """
        Auto-generate a baseline set of tasks for every pet under this owner,
        using preferences and constraints to customise times.

        Priority scale used here:
          4 — medication   (must not be missed)
          3 — feeding      (twice daily by default)
          2 — walk         (dogs only)
          1 — appointment  (manually added; lowest default urgency)
        """
        self.clear_plan()   # drop previous daily tasks; keep manually-added ones

        walk_time  = self.owner.preferences.get("walk_time", "08:00")
        feed_times = self.owner.preferences.get("feed_times", ["08:00", "18:00"])
        med_time   = self.owner.constraints.get("medication_time", None)

        for pet in self.owner.pets:
            for time in feed_times:
                self.add_task(self._daily_task("feeding", time, 3, pet))

            if pet.species.lower() == "dog":
                self.add_task(self._daily_task("walk", walk_time, 2, pet))

            if pet.health_condition.lower() != "healthy" and med_time:
                self.add_task(self._daily_task("medication", med_time, 4, pet))

        self.prioritize_tasks()
