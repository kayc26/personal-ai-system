---
name: log-home-cooking
description: Log food Kay made or assembled herself, as cooking entries (one per dish cooked) and as meals with hunger and fullness check-ins, including leftovers eaten later. Handles cooking from a saved recipe, whether she'd cook it again, and updating kitchen-inventory after cooking. Use when she says she cooked, made, or is about to eat something she made, sends a photo of her own cooking or leftovers, adds thoughts to something she cooked, asks what recipes she'd cook again, or asks what's ready to post for 瓦克西熟了. Not for food someone else prepared (log-dining-out), packaged or whole food eaten as is (log-ready-to-eat), saving a new recipe (clip-recipe), or deciding what to cook (suggest-what-to-cook).
---

# Log home cooking

Two records, kept apart:
- **Home cook** (`log_home_cook`): one dish cooked once. Rated and described once.
- **Meal** (`start_meal` / `end_meal`): one time she eats, type `homemade`. Rules in
  `references/meals.md`.

One pot can feed several meals (leftovers), and one dinner can include several dishes,
so a meal links to its home cooks with `update_meal` (`add_home_cook_ids`). Read
`references/meals.md` before the first meal of a conversation, and
`references/dishes.md` before logging a dish.

Home cooking feeds 瓦克西熟了, where formula posts (万能公式) built from many variations
of one dish type perform best. Nutrition numbers belong to MacroFactor; never ask about
macros. If a tool named below isn't available, say so in a few words and use the ones
that are.

## Eating something she just cooked

1. **Open meal?** `get_open_meal` (see meals.md). If none and she's about to eat, start
   one: type `homemade`, start check-in. If she's logging after eating, do the start and
   end check-ins together with real times.
2. **Log each dish cooked** (once per dish, per dishes.md for names, ingredients,
   cuisine). At most 3 questions, with taps where possible:
   1. Rating (1 to 5).
   2. Source: a link, a book, or "my own". If `find_dish` lists a saved recipe for the
      dish, ask in one tap: "From the NYT recipe you saved in March?" and pass
      `saved_recipe_id`. Linking also takes the recipe off "this week", so always link
      when she cooked from one.
   3. "What changed, and anything that stood out?" (optional; offer "Skip" and "Tell
      you at the end"). What was different goes in `changes`, how it tasted in `note`.
   Call `log_home_cook` with everything, including dish family, techniques and
   ingredients (comma-separated), photo description, and photo date if known.
3. **Link the dishes to the meal:** `update_meal` with `add_home_cook_ids`.
4. **Would she cook it again?** If the dish came from a saved recipe, one tap after
   logging: "Make this recipe again?" / "Once was enough". Yes: `update_saved_recipe`
   status `cook_again`. No or no answer: leave it (logging already marked it `cooked`,
   which Kay calls "tried"). If it's already `cook_again`, ask only when she rated this
   attempt 2 or lower: "Keep it on your cook-again list?"; no sets `cooked`.
5. **Inventory** (below).
6. **End of meal:** end check-in and `end_meal` with her meal-level notes word for word.
   Thoughts about one dish go to that dish's `note` or `changes` with
   `update_home_cook`.
7. **Confirm in one line,** e.g. "Logged: 红烧肉, attempt 3, 4/5, less sugar. Hunger
   6 -> 1, full 7, satisfying 4."

## Leftovers

- **Extra after cooking:** offer one tap: "Store the leftovers?" Yes: `add_item` in
  kitchen-inventory with the dish name, location (fridge default), and `made_date`
  today (expiry defaults to 4 days).
- **Eating leftovers later:** a new `homemade` meal. Don't log the dish again: find
  the original home cook with `get_recent` (domain `home`) or `get_dish_history`, link
  it with `add_home_cook_ids`, and `use_item` on the leftover (or `remove_item` if it's
  finished).

## Inventory after cooking

Offer one tap: "Remove what you used?" If yes, start from the ingredients you just
logged, infer amounts where you can, and ask only if needed. Inventory names are short
and generic but can be plural ("eggs", "raisins"), with brands in the item's details.
Pass each item's location (fridge default; check `list_inventory` or the suggestion for
pantry and freezer items). If a name isn't found, the response suggests matches: use
the one that fits, or ask in one tap if there are two. Skip untracked ingredients (salt,
oil) without mentioning them. `use_item` for anything partly used, `remove_item` for
anything used up. If `use_item` can't subtract (different units, like 4 oz from 1 bag),
estimate what's left, confirm in one tap, then `remove_item` and `add_item` it back with
that amount and the same details. Confirm in one line, e.g. "Inventory: used 2 eggs (8
left), finished the gai lan."

## Saved recipes

Saving a recipe is clip-recipe's job. Here:
- **Cooking from one:** `get_saved_recipe` returns the full recipe text.
- **Linked later:** if she remembers after logging, `update_home_cook` with field
  `saved_recipe_id`.
- **Dropping:** status `dropped` with `update_saved_recipe`. There's no delete.
- **Statuses:** `saved` (not cooked yet), `cook_again` (would make again), `cooked`
  (tried, wouldn't; say "tried" to Kay), `dropped` (lost interest).
- **Loved a dish out?** There's no recreate list; she finds a recipe and clip-recipe
  saves it.

## Adding thoughts later

Find the entries with `get_recent` (domain `home` or `meals`), then `update_home_cook`
or `update_meal`. Merge with existing notes; never a second entry. A dish she mentions
that wasn't logged: ask before adding it.

## Fixing and deleting

Fix with `update_home_cook` or `update_meal`. Delete only when Kay asks, after showing
her the entry: `delete_home_cook`.

## Answering questions

- **"What's ready to post?" (瓦克西熟了):** `get_family_collections`; point out dish
  families with several distinct variations. Single-dish posts perform poorly.
- **"Have I made X?"** `get_dish_history` or `search_experiences`.
- **"What would I cook again?" / "Which recipes have I tried?"** `list_saved_recipes`
  with status `cook_again` or `cooked`.

## Style
Short, warm, fast. Match her language (Chinese, English, or mixed). Keep dish names in
the form she uses and store other names as aliases.
