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

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
