# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Smarter Scheduling

The `Scheduler` class was extended with several features to make plan generation more reliable and useful:

- **Task filtering** — `get_tasks_for_pet()`, `get_tasks_by_status()`, and `get_tasks_by_time()` let any part of the app query the schedule without ad-hoc list comprehensions. The Tasks and Schedule tabs in the UI use these directly.
- **Safer plan generation** — `create_plan()` now calls `clear_plan()` before generating, so re-running never produces duplicates and never resurfaces tasks the user already removed. Manually added tasks are preserved.
- **Recurring task completion** — `complete_task()` marks a task done and, using `timedelta`, automatically adds the next occurrence for `"daily"` (tomorrow) and `"weekly"` (7 days out) tasks. One-time tasks are left as-is.
- **Conflict detection** — `detect_conflicts()` scans pending tasks and returns plain warning strings, never crashing. It distinguishes `[CONFLICT]` (same pet, same time) from `[WARNING]` (different pets overlapping), and results are shown inline in the Schedule tab.

## Testing PawPal+

### Running the tests

```bash
python -m pytest tests/test_pawpal.py -v
```

### What the tests cover

| Area | Tests |
|---|---|
| **Task status** | `mark_complete()` sets status to `"completed"` |
| **Scheduler add** | Adding a task increments `scheduler.tasks` by 1 |
| **Ownership guard** | `add_task()` raises `ValueError` for a pet not owned by the scheduler's owner |
| **Filtering** | `get_tasks_for_pet()` returns only that pet's tasks; `get_tasks_by_status()` returns only matching-status tasks |
| **Sorting** | `get_tasks_by_time()` returns tasks in chronological (ascending) order regardless of insertion order |
| **Recurrence — daily** | Completing a daily task spawns a new pending task dated today + 1 day |
| **Recurrence — weekly** | Completing a weekly task spawns a new pending task dated today + 7 days |
| **Recurrence — one-time** | Completing a `recurrence=None` task does not spawn any new task |
| **Conflict detection** | Same pet at the same time → `[CONFLICT]`; different pets at the same time → `[WARNING]` |

### Confidence level

⭐⭐⭐⭐ (4 / 5)

The core scheduling behaviors — recurrence, sorting, filtering, and conflict detection — are fully tested. One star is held back because `create_plan()` species logic (dog walk vs. cat no-walk), the no-pets/no-tasks edge cases, and `reschedule()` behavior are not yet covered by automated tests.

---

## Features
- Daily Plan Generation — create_plan() auto-generates a baseline set of tasks for every pet using the owner's preferences (walk time, feed times) and constraints (medication time). Dogs receive a daily walk; pets with non-healthy conditions receive a medication task. Re-running the plan never produces duplicates — previous auto-generated tasks are cleared first while manually added tasks are preserved.

- Task Prioritization — prioritize_tasks() sorts all tasks by priority (descending) then by scheduled time (ascending), so the most urgent tasks always surface first. Priority levels: 4 = medication, 3 = feeding, 2 = walk, 1 = appointment.

- Recurring Task Completion — complete_task() marks a task done and automatically schedules the next occurrence using timedelta: daily tasks recur tomorrow (+1 day), weekly tasks recur in 7 days (+7 days). One-time tasks (recurrence=None) are simply marked complete with no follow-up created.

- Task Filtering — Three query methods let any part of the app retrieve tasks without ad-hoc loops:
    - get_tasks_for_pet(pet) — all tasks belonging to a specific pet
    - get_tasks_by_status(status) — all tasks matching "pending", "completed", or "skipped"
    - get_tasks_by_time() — all tasks sorted chronologically by scheduled time

- Conflict Detection — detect_conflicts() scans all pending tasks for scheduling overlaps and returns plain warning strings without ever raising an exception. It distinguishes two severity levels:
    - [CONFLICT] — same pet has two tasks at the same time (physically impossible)
    - [WARNING] — two different pets overlap at the same time (owner attention split)

- Ownership Guard — add_task() raises a ValueError if the task's pet does not belong to the scheduler's owner, preventing tasks from being accidentally assigned to unregistered pets.

## 📸 Demo

<a href="PawPal+ demo.png" target="_blank"><img src='PawPal+ demo.png' title='PawPal App' width='' alt='PawPal App' class='center-block' /></a>.

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
