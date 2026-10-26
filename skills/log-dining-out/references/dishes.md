# Dishes: shared rules

Identical copy in log-dining-out and log-home-cooking. Edit both together
(check_skills.py flags drift).

Every dish entry (`log_dine_out`, `log_home_cook`) is a small piece that later combines
into a collection: formula posts (万能公式) for 瓦克西熟了 and city guides (十道菜吃懂X)
for Chi人在消食. Clean names, cuisines, and ingredients are what make that work.

Always pass `cuisine` and `dish_family`. `get_explored` and the collection tools group
by them, so a dish without them shows up as "(unknown)" and never joins a post.

## Check for a repeat

Look at the photo and identify the likely dish, cuisine, dish family (e.g. curry,
braised pork, noodle sauce), visible techniques, and key ingredients. Write a short
photo description.

Call `find_dish` once for each name form of the dish, up to 3 calls: the name Kay used,
the Chinese name, and the English name (plus the original-language name if it differs,
e.g. Phở, çılbır). Name matching only catches spelling-level similarity, so 红烧肉 will
never match "braised pork belly" unless you search both. If any search finds a close
match, ask one quick question: "Same as the [dish] from [date]?" Never silently create
a near-duplicate.

When logging, pass `name_zh` whenever you know the Chinese name, and every other name
form you searched as `aliases` (comma-separated), so the next search finds the dish in
any language.

## How specific a dish name should be

Name the dish at the level where different versions are still the same dish, so
repeats and variations collect under one name.

- **Drop modifiers that describe one version:** ingredient grades or cuts (big eye,
  wagyu, A5), brands, sizes, restaurant flourishes ("house special", "grandma's",
  "chef's signature"). "Big eye tuna tartare" is logged as **tuna tartare**.
- **Keep what makes it a different dish:** the main ingredient when it changes the
  dish (tuna tartare vs beef tartare), and established names for distinct dishes (东坡肉
  is not 红烧肉, even though both are braised pork).
- **A twist is a variation, not a new dish.** 可乐红烧肉 is 红烧肉 with cola, logged as
  红烧肉 with the twist in `changes`.
- **Never lose the detail.** The specifics go in `note` for dining out (e.g. "big eye
  tuna, menu called it the house tartare") or `changes` for home cooking.
- **The level above is the dish family** (e.g. tartare, braised pork, noodle sauce).

If it's unclear whether something is its own dish, ask one quick question with two
taps, e.g. "Log as tuna tartare?" / "Keep it separate".

## Key ingredients

Record the 4 to 8 main ingredients of every entry as a tag list, inferred by you.
Every `log_home_cook` and `log_dine_out` call includes `ingredients` unless you truly
can't tell. Never ask Kay for them and never record quantities.

- **Best source first:** what Kay says, then the menu description, then what you can
  see in the photo. Don't add ingredients none of these support.
- **Main items only:** the protein, the base (rice, noodles, bread), and the
  ingredients that define the flavor (gochujang, miso, fish sauce, rose water). Skip
  salt, oil, water, and generic aromatics unless they're central to the dish.
- **Per attempt, not per dish.** Record what went into this cook or this plate. A swap
  goes in both: the new ingredient in `ingredients`, the swap in `changes`.
- **Generic, consistent names:** English, lowercase, singular ("tuna", "pork belly",
  "gochujang"). Grades, brands, and cuts go in `note` or `changes`.
- **Update on correction** with the update tool; never a new entry.

## Cuisine

Work out cuisine yourself; never ask Kay. Show it in the confirmation line so she can
correct it.

- **Dish cuisine** comes from the dish itself first (khao soi is Thai, manti is
  Turkish), then the restaurant's Google Places category, then the menu. Store the
  dish's own cuisine even when the restaurant's differs.
- **Place cuisine** comes from the Places category, the menu, or the restaurant's site.
  Pass it as `cuisine` to `log_visit` and `save_place`. Whenever you work out a place's
  cuisine for any reason, save it with `update_place` or `set_place_cuisines`.
- **One label rule** for both: the country or well-known regional cuisine (Thai,
  Sichuan, Levantine, Southern). Use a type only when no cuisine fits: Café, Bakery,
  Dessert, Bar. Reuse a label already in use (`get_explored` with `cuisine`, and the
  cuisines shown by `list_places`). If `set_place_cuisines` flags a new label, check it
  isn't another name for an existing one.

## New names

If a log response says a new dish or place was created and lists similar matches,
confirm in one short question before moving on.
