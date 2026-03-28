# PawPal+ Project Reflection

## 1. System Design

**3 core actions**
1. track pet care tasks 
2. record pet owner preferences and constraints
3. produce and explain pet care plans based on known preferences 

**a. Initial design**
- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

*main objects*
- pet owner
    - attributes: name, location
    - methods: createPlan, editPreference, editConstraint, addPet, removePet, editPetInfo, getPetHealth, add-/remove- Pref
- pet
    - attributes: name, species, breed, age, gender, healthCondition
    - methods: getOwner, editInfo
- plan
    - attributes: pet, pet owner, tasks, 
    - methods: editTask, getPreference
- preferences
    - attributes: pet owner, prefInfo, 
    - methods: editPref


**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

1. removed owner ref after finding a logical bug in seeing that a pet cannot exist without an owner. Hence the 'add_owner' function was removed as well, and instead, have that pet -> owner lookup done by the Scheduler.
2. Owner has no pet list so there was no way to record the pets they have
3. Scheduler duplicates the owner's pet info, which is unnecessary because according to the UML, Owner has authority over Pets so the pet's info should be received through the Owner
---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

> My scheduler considers time and conflicts which I think is the most important constraints because the tasks can only be complete if the owner has the time to and have no other conflicting tasks to do so. 

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

> The scheduler flags the tasks as conflicting only when the time is identical, which means, there is no sense of duration for the tasks. The current scheduler goes for simiplicity, instead of accuracy, relying on the user to be responsible for their own calculation and estimation when creating new tasks to avoid conflict. The design is easy to reason about and quick, but it is prone to confliction.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
