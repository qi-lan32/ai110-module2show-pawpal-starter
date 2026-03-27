from pawpal_system import Owner, Pet, Task, Scheduler


def test_mark_complete_updates_status():
    """Calling mark_complete() on a task should set its status to 'completed'."""
    pet = Pet("Buddy", "dog", "Golden Retriever", 4, "male", "healthy")
    task = Task(task_type="feeding", scheduled_time="08:00", status="pending", priority=3, pet=pet)

    task.mark_complete()

    assert task.status == "completed"


def test_add_task_increases_pet_task_count():
    """Adding a task via the scheduler should increase the pet's task count by 1."""
    owner = Owner(name="Sarah", location="Austin, TX")
    pet = Pet("Buddy", "dog", "Golden Retriever", 4, "male", "healthy")
    owner.add_pet(pet)
    scheduler = Scheduler(owner=owner)

    assert len(pet.tasks) == 0

    scheduler.add_task(Task(task_type="walk", scheduled_time="08:00", status="pending", priority=2, pet=pet))

    assert len(pet.tasks) == 1
