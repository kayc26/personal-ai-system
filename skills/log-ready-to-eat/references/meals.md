# Meals: shared rules

Identical copy in log-dining-out, log-home-cooking, and log-ready-to-eat. Edit all
three together (check_skills.py flags drift).

A meal is one eating event in the food-journal: a start check-in (hunger), an end
check-in (hunger and satisfaction), Kay's raw notes, and links to what she ate (a visit,
home cooks). The check-ins are her mindful-eating practice, so they matter more than
speed.

## Check for an open meal first

Before handling any food photo or meal notes, call `get_open_meal`.
- **A meal is open:** the photo or notes belong to it. Its type decides which skill
  handles them (prepared: log-dining-out; homemade: log-home-cooking; packaged or
  whole: log-ready-to-eat). A chocolate bar during a home dinner is part of that
  dinner; note it on the meal, don't start another.
- **No open meal:** decide the type from the food (below) and start one.
- **Open for hours:** if it has been open more than about 3 hours, it was probably
  never closed. Ask when she finished and close it with `end_meal` and `ended_at`
  before starting anything new. `start_meal` won't open a second meal; it returns the
  open one.

## Meal types

Who prepared the food. Apply in order; the first match wins:
1. **prepared:** freshly made by anyone other than Kay (restaurant, cafe, bakery,
   takeout, a friend or family member, catering).
2. **packaged:** a commercially produced food or drink consumed largely as sold.
3. **whole:** a minimally processed food eaten largely as is, at most washed or cut.
4. **homemade:** a dish or drink Kay prepared or assembled herself, including her
   leftovers.

If nothing fits, ask Kay; there is no catch-all. A mixed meal takes the type of its
main item, and the links record the rest.

**Not meals:** near-zero-calorie drinks (water, black coffee, plain tea, sparkling
water, diet soda). No meal, no check-in. To review a place for one, log a visit
without a meal (log-dining-out).

## Start check-in

One question, briefly, with tappable numbers where possible:
"How hungry are you, 0 to 10?" (0 not at all, 5 moderately, 10 as hungry as ever)

Then `start_meal` with the type, her answer as `hunger`, `visit_id` when there is one,
and any notes she already gave, word for word. Don't ask about fullness.

## End check-in

When she says she's done, or sends her end-of-meal batch, ask two questions, each on
its own:
1. "How hungry are you now, 0 to 10?"
2. "How satisfying was it, 1 to 5?" (enjoyment, not how full she is)

Then `end_meal` with `hunger`, `satisfaction`, and her notes, word for word. Don't ask
about fullness. `end_meal` adds notes to the meal; it never replaces them.

## Tone

The check-ins are for noticing, not judging. Never comment on whether a number is good
or bad, never suggest eating less or more, and never compare with past meals unless she
asks. Record and move on.

## Times

- Default is now. When she's logging a meal after the fact, find the real time:
  1. The photo's capture time, if the file is available and its metadata has one.
  2. Otherwise ask "Roughly when did you start (and finish)?" An estimate is fine.
- Times are always a full date and time. Never log a meal at midnight because only
  the date is known.
- Logging after the fact: ask "Before you ate, how hungry were you?", then "And
  after?" and "How satisfying was it?", then `start_meal` with `started_at` and
  `end_meal` with `ended_at` in one go.

## Notes

Kay's notes are raw material for her posts. Store them as she wrote them: trim filler,
never rewrite her phrasing. Thoughts about one dish also go to that dish's entry
(`log_dine_out` or `log_home_cook` note); thoughts about the meal go to the meal.

## Fixing

Use `update_meal` with the meal id (from `get_recent`, domain `meals`). Its notes
replace the old notes, so merge first. To link home cooks, use `add_home_cook_ids`.
