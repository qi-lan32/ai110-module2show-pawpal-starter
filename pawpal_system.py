from __future__ import annotations
from dataclasses import dataclass, field
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
        task.pet.tasks.append(task)  # keep pet's own task list in sync

    def remove_task(self, task: Task) -> None:
        """Remove a task from the schedule if it exists."""
        if task in self.tasks:
            self.tasks.remove(task)

    def prioritize_tasks(self) -> None:
        """Sort tasks by priority (desc) then scheduled_time (asc)."""
        self.tasks.sort(key=lambda t: (-t.priority, t.scheduled_time))

    def get_next_task(self) -> Optional[Task]:
        """Return the highest-priority pending task, or None if all are done."""
        pending = [t for t in self.tasks if t.status == "pending"]
        if not pending:
            return None
        return max(pending, key=lambda t: t.priority)

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
        walk_time  = self.owner.preferences.get("walk_time", "08:00")
        feed_times = self.owner.preferences.get("feed_times", ["08:00", "18:00"])
        med_time   = self.owner.constraints.get("medication_time", None)

        for pet in self.owner.pets:
            # Every pet gets fed on the owner's preferred schedule
            for time in feed_times:
                self.add_task(Task(
                    task_type="feeding",
                    scheduled_time=time,
                    status="pending",
                    priority=3,
                    pet=pet
                ))

            # Dogs get a daily walk
            if pet.species.lower() == "dog":
                self.add_task(Task(
                    task_type="walk",
                    scheduled_time=walk_time,
                    status="pending",
                    priority=2,
                    pet=pet
                ))

            # Pets with a health condition get a medication task if a time is set
            if pet.health_condition.lower() != "healthy" and med_time:
                self.add_task(Task(
                    task_type="medication",
                    scheduled_time=med_time,
                    status="pending",
                    priority=4,
                    pet=pet
                ))

        self.prioritize_tasks()
