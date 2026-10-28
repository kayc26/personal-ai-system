---
name: "check-nutrition"
description: "Check food choices against a person's nutrition rules, using their nutrition profile plus built-in evidence-based modules (glucose management, strength training, active women). Use when the user asks whether a meal or recipe fits their goals, what to eat before or after a workout, how to make a dish healthier, or about supplements. Also used by other skills to shape food suggestions. Not for picking what to cook or where to eat."
---

# Check Nutrition

Turn a person's nutrition rules into practical food choices. This skill holds the
method and the rules. The person's objective facts (sex, age, height, training
experience, medical conditions, approved supplements) live in their nutrition
profile, so the skill can be shared without carrying anyone's personal information.

Picking what to cook or where to eat belongs to other skills (suggest-what-to-cook,
suggest-where-to-eat). They call this skill to judge their options.

## Step 1: Load the profile

Look for a file named `NUTRITION_PROFILE.md` in the project files (`/mnt/project/`).

- **Found:** read it. It holds facts only, no rules. Pick the modules from the facts:
  - prediabetes, insulin resistance, or a stated wish for steadier blood sugar:
    Glucose management
  - lifts regularly or wants to build muscle: Strength training
  - a woman who trains regularly: Active women
- **Not found:** say in one line that no profile is available here. Apply only what
  they state in the message, or offer to build a profile with a few quick questions:
  sex, age, height, training experience, health conditions and what a doctor handles,
  approved supplements, food intolerances. Never guess at health conditions.

## Step 2: Get today's context

Only when it changes the answer:

- **Training:** if a workout-log tool is available, call `get_training_status` to
  see whether today is a training day, rest day, or cardio day. Pre and post workout
  rules depend on it.
- **On hand:** if a kitchen-inventory tool is available and the answer names specific
  foods, check `list_inventory` (all locations) and build from what's there,
  favoring items close to expiry. If a protein staple is running low
  (`check_low_stock`), mention it in one line.
- **Targets:** calorie and macro targets come from MacroFactor, never from you. On
  food questions, ask once for the "Macros Remaining" paste; if it isn't given, answer
  without macros and don't ask again. In the pasted JSON, read
  `remaining.<nutrient>.target` as what's left (negative means past target) and
  `remaining.<nutrient>.maximum` as headroom under a cap. Ignore amino acids
  (incomplete).

If a tool isn't available, say so in a few words and answer without it.

## Step 3: Apply the rules

Judge the meal, recipe, or idea against the profile's facts and the modules picked, and
give practical changes, not lectures:

- **Lead with the answer:** fits well, fits with a tweak, or better another time
  (e.g. "better as a post-workout meal").
- **One or two tweaks, most useful first:** swap, add, reorder, or retime. "Add an egg
  and eat the greens first" beats a list of principles.
- **Work within their targets.** Advice covers food choice, timing, pairing, and
  distribution, not new numbers. Per-meal protein ranges from the modules are fine.
- **Respect what they want to eat.** If they want to try a new or indulgent recipe,
  help it fit (pairing, timing, a post-meal walk) rather than steering them away. Most
  meals matter more than any single one.
- **Explain briefly when useful.** Don't comment on body weight, waist, or
  appearance; those are tracked in MacroFactor.

## Modules

Apply only the modules picked in Step 1. Evidence levels in brackets.

### Glucose management
For prediabetes, insulin resistance, or anyone wanting steadier blood sugar.
- **Carb quality over carb cutting.** Favor fiber-rich, minimally processed carbs
  (whole grains, legumes, fruit, starchy vegetables). [Well established]
- **Pair carbs** with protein, fat, or fiber rather than eating them alone. [Well
  established]
- **Food order.** Protein and vegetables before the carb portion of a meal blunt the
  glucose rise. [Promising]
- **Drinks.** Limit sugary drinks and juice; prefer whole fruit. [Well established]
- **Post-meal walk.** 10 to 15 minutes after larger meals lowers post-meal glucose,
  especially useful on rest days. [Well established]
- **Lifestyle.** Regular daily movement and good sleep improve insulin sensitivity.
  [Well established]
- **Muscle helps.** Building muscle improves glucose uptake, so under-fueling training
  works against glucose goals. [Well established]
- **Monitor readings.** If they share glucose readings, help interpret patterns in
  plain terms. Never adjust medication or diagnose.
- **Retesting.** Encourage following their doctor's retesting schedule (e.g. A1c).
- Don't default to low-carb advice. Reducing carbs is the doctor's call, not this
  skill's.

### Strength training
For people who lift regularly or want to build muscle.
- **Pre-workout.** A meal with carbs and some protein 1 to 3 hours before, or a small
  carb plus protein snack 30 to 60 minutes before if short on time. Real food over
  sugary drinks or candy, except in a genuine pinch. [Well established]
- **Avoid fasted training as a habit.** [Promising to well established, depending on
  outcome]
- **Post-workout.** Total daily protein matters most. A protein-rich meal within a few
  hours is good practice; sooner matters more after fasted training. The "anabolic
  window" is wider than commonly believed. [Well established]
- **Protein distribution.** 3 to 4 meals of roughly 20 to 30 g protein each, adjusted
  for body size. [Well established]
- **Carb timing.** When also managing glucose, place a larger share of daily carbs
  around training, when muscles take up glucose most readily. [Well established]
- **Creatine.** 3 to 5 g daily; timing doesn't matter. [Well established]
- **Caffeine.** About 3 mg/kg, 30 to 60 minutes before training; avoid late in the day
  if it affects sleep. [Well established]
- **Hydration.** Consistent through the day; bring water to sessions. [Well
  established]

### Active women
For women who train regularly.
- **Energy availability.** Under-fueling around training raises the risk of low energy
  availability, with evidence weighted more toward women. Treat skipped pre-workout
  fuel and fasted training as a bigger concern. [Well established]
- **Post-lifting protein.** Aim for a protein-rich meal within about 1 hour after
  lifting, tighter than the strength module's "few hours." The women-specific case
  for a narrower window is thin, but it costs nothing and helps hit daily protein.
  Total daily protein still matters most. [Mostly tradition as a women-specific rule]
- **Menstrual cycle.** Appetite and cravings often rise in the luteal phase. This is
  normal. Don't change macros by phase; evidence doesn't support it. [Well established]
- **Micronutrients.** Iron, calcium, and vitamin D are common gaps, especially for
  active women. Favor food sources; supplements go through a doctor. [Well
  established]
- **Warning signs** (refer, don't manage): irregular or missed periods, persistent
  fatigue, falling strength over weeks.

## Evidence standards

The modules hold well-supported defaults. When a question goes beyond them:

- **Search for current evidence**, favoring systematic reviews, meta-analyses, and
  position stands (e.g. ISSN, ACSM), and cite what you find.
- **Match the evidence to the person.** Prefer studies on people like them (for women,
  female or mixed-sex samples). When evidence comes mostly from men, say so and whether
  it's likely to apply.
- **Label strength:** well established, promising, or mostly tradition.

## Safety rules (always apply, override everything above)

- **Stress around food comes first.** If eating seems to be becoming stressful,
  restrictive, or anxious, drop optimization, say so gently, and suggest talking to a
  professional.
- **Defer to a doctor for:** diagnosis, testing schedules (e.g. A1c), medication, any
  supplement beyond what the profile lists as approved, and any new symptom.
- **Red flags to name and refer, not manage:** unusual thirst, frequent urination,
  blurred vision, shaky or faint episodes, irregular or missed periods, persistent
  fatigue, or weeks of falling strength (possible under-fueling).
- This is general guidance for everyday food decisions, not medical advice.

## Style

Short and practical unless they ask for depth. Give real food examples, not just
macro numbers. Match the user's language. No em dashes.