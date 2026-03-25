from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass
class Pet:
    name: str
    species: str
    breed: str
    age: int
    gender: str
    health_condition: str

    def get_owner(self) -> Owner:
        pass

    def edit_info(self) -> None:
        pass


@dataclass
class Task:
    task_type: str       # e.g. "feeding", "walk", "medication", "appointment"
    scheduled_time: str
    status: str          # e.g. "pending", "completed", "skipped"
    priority: int
    pet: Pet

    def complete(self) -> None:
        pass

    def reschedule(self) -> None:
        pass


class Owner:
    def __init__(self, name: str, location: str):
        self.name = name
        self.location = location

    def add_pet(self, pet: Pet) -> None:
        pass

    def remove_pet(self, pet: Pet) -> None:
        pass

    def edit_preference(self) -> None:
        pass

    def edit_constraint(self) -> None:
        pass


class Scheduler:
    def __init__(self, owner: Owner):
        self.owner = owner
        self.pets: list[Pet] = []
        self.tasks: list[Task] = []

    def create_plan(self) -> None:
        pass

    def prioritize_tasks(self) -> None:
        pass

    def add_task(self, task: Task) -> None:
        pass

    def remove_task(self, task: Task) -> None:
        pass

    def get_next_task(self) -> Optional[Task]:
        pass
