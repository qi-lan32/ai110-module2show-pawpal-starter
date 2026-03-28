# PawPal+ UML Class Diagram (Final)

```mermaid
classDiagram
    class Owner {
        +String name
        +String location
        +Dict preferences
        +Dict constraints
        +addPet(pet Pet) void
        +removePet(pet Pet) void
        +editPreference(key, value) void
        +editConstraint(key, value) void
    }

    class Pet {
        +String name
        +String species
        +String breed
        +int age
        +String gender
        +String healthCondition
        +List tasks
        +editInfo() void
    }

    class Task {
        +String task_type
        +String scheduledTime
        +String status
        +int priority
        +Pet pet
        +String recurrence
        +String scheduled_date
        +mark_complete() void
        +reschedule() void
    }

    class Scheduler {
        +Owner owner
        +List~Task~ tasks
        +createPlan() void
        +clearPlan() void
        +prioritizeTasks() void
        +addTask(task Task) void
        +removeTask(task Task) void
        +getNextTask() Task
        +getTasksByTime() List
        +getTasksForPet(pet Pet) List
        +getTasksByStatus(status String) List
        +detectConflicts() List
        +completeTask(task Task) void
    }

    Owner "1" --> "0..*" Pet : owns
    Scheduler "1" --> "1" Owner : uses
    Scheduler "1" --> "1..*" Task : manages
    Task "1" --> "1" Pet : for
```
