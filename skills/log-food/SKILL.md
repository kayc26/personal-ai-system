---
name: "log-food"
description: "Log Kay's food experiences to her food journal, keeping home cooking and dining out separate. Use whenever Kay sends a food photo or says she cooked, made, ate, tried, or had something, shares a restaurant or Maps link to save, adds thoughts to an earlier entry, asks what she has tried or where she ate something, asks what recipes she would cook again or what's ready to post, or sends saved-places screenshots or a menu photo. Not for saving a new recipe (clip-recipe), or suggesting what to cook or where to eat."
---

# Log Food

Kay is a home cook and food blogger with two Xiaohongshu accounts. Home cooking feeds
瓦克西熟了, where formula posts (万能公式) built from many variations of one dish type
perform best. Dining out feeds Chi人在消食, where city guides (十道菜吃懂X) perform best.
Every entry is a small piece that later combines into a collection. Make logging take
under 30 seconds and keep the record clean.

The food journal (the food-journal connector) owns food experiences only. Nutrition
numbers belong to MacroFactor, and ingredient stock belongs to kitchen-inventory.
Never ask about macros here.

Recommendations are not this skill's job: "what should I cook" goes to
suggest-what-to-cook and "where should I eat" goes to suggest-where-to-eat.

If a tool named below isn't available, say so in a few words and answer from the
tools that are, for example `get_dish_history`, `search_experiences`, `get_recent`,
and `list_places`.

Always pass `cuisine` and `dish_family` when logging (see "Cuisine"). `get_explored`
and the collection tools group by them, so a dish without them shows up as "(unknown)"
and never joins a formula post or city guide.

## Step 1: Identify the domain

Decide whether this is **home cooking** or **dining out** from the photo and her
message. If it isn't obvious, ask with tappable options: "Cooked at home" / "Eaten out".
Then follow only that domain's flow. Never mix the two in one entry.

A Google Maps link or a restaurant name with no food and no meal is usually a place to
save, not a meal. If it isn't clear, ask: "Save for later" / "Eating here now" / "Been
before". Save for later and Been before follow "Saving places"; Eating here now follows
the dining out flow.

## Step 2: Check for a repeat

Look at the photo and identify the likely dish, cuisine, dish family (e.g. curry,
braised pork, noodle sauce), visible techniques, and key ingredients (see "Key
ingredients" below). Write a short photo description.

Call `find_dish` once for each name form of the dish, up to 3 calls: the name Kay used,
the Chinese name, and the English name (plus the original-language name if it differs,
e.g. Phở, çılbır). Name matching only catches spelling-level similarity, so 红烧肉 will
never match "braised pork belly" unless you search both. If any search finds a close
match, ask one quick question: "Same as the [dish] from [date]?" Never silently create
a near-duplicate.

When logging, pass `name_zh` whenever you know the Chinese name, and pass every other
name form you searched as `aliases` (comma-separated), so the next search finds this
dish in any language.

## How specific a dish name should be

Name the dish at the level where different versions are still the same dish, so
repeats and variations collect under one name. That's what makes formula posts and city
guides possible.

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
- **The level above is the dish family** (e.g. tartare, braised pork, noodle sauce),
  which groups related dishes.

If it's unclear whether something is its own dish, ask one quick question with two
taps, e.g. "Log as tuna tartare?" / "Keep it separate".

## Key ingredients

Record the 4 to 8 main ingredients of every entry as a tag list, inferred by you. Every
`log_home_cook` and `log_dine_out` call includes `ingredients` unless you truly can't
tell what's in the dish; an empty list is the exception, not the default. Never
ask Kay for them and never record quantities.

- **Best source first:** what Kay says, then the menu description (see "Menu lookup"),
  then what you can see in the photo. Don't add ingredients that none of these support.
- **Main items only:** the protein, the base (rice, noodles, bread), and the ingredients
  that define the flavor (gochujang, miso, fish sauce, rose water). Skip salt, oil,
  water, and generic aromatics unless they're central to the dish.
- **Per attempt, not per dish.** Variations change ingredients, so record what went into
  this cook or this plate. If she swapped something, both the swap and the ingredient go
  in: the new ingredient in `ingredients`, the swap in `changes`.
- **Generic, consistent names:** English, lowercase, singular ("tuna", "pork belly",
  "gochujang"), so lists stay searchable. Grades, brands, and cuts follow the same rule
  as dish names and go in `note` or `changes`.
- **Update on correction.** If she mentions an ingredient later, add it with the update
  tool rather than creating a new entry.

## Cuisine

Work out cuisine yourself; never ask Kay. Show it in the confirmation line so she can
correct it.

- **Dish cuisine** comes from the dish itself first (khao soi is Thai, manti is
  Turkish), then the restaurant's Google Places category, then the menu. Store the
  dish's own cuisine even when the restaurant's differs: manti at a Mediterranean
  restaurant is Turkish.
- **Place cuisine** comes from the Places category, the menu, or the restaurant's
  site. Pass it as `cuisine` to `log_visit` and `save_place`. Whenever you work out a
  place's cuisine for any reason (answering "where should I eat Thai", say), save it
  with `update_place` or `set_place_cuisines`, so it's never worked out twice.
- **One label rule** for both: the country or well-known regional cuisine (Thai,
  Sichuan, Levantine, Southern). Use a type only when no cuisine fits: Café, Bakery,
  Dessert, Bar. Before picking a label, reuse one already in use (`get_explored` with
  `cuisine`, and the cuisines shown by `list_places`). If `set_place_cuisines` flags a
  new label, check it isn't another name for an existing one.

## Saved recipes

Saving a recipe (a link, a page she's on, a RedNote post, screenshots, a cookbook
page) is the clip-recipe skill's job. This skill handles saved recipes once they exist.

**Cooking from a saved recipe.** When she wants to make one, `get_saved_recipe`
returns everything stored, including the full recipe text.

**Cooking from a saved recipe, when logging.** Before logging a home cook, `find_dish` lists the
dish's saved recipes. If there's one, ask in one tap: "From the NYT recipe you saved
in March?" and pass `saved_recipe_id` to `log_home_cook`. If she remembers later,
link it with `update_home_cook` (field `saved_recipe_id`). Linking also takes the
recipe off her "this week" list, so always link when she cooked from one.

**Dropping.** If she's no longer interested, set status to `dropped` with
`update_saved_recipe`. There's no delete for recipes.

**Loved a dish out?** There's no recreate list. If she wants to cook something she
ate, she finds a recipe and clip-recipe saves it like any other.

**Recipe statuses.** `saved`: want to try, not cooked yet. `cook_again`: cooked it and
would make it again. `cooked`: tried it, wouldn't make it again (call this "tried"
when talking to Kay). `dropped`: lost interest before cooking.

## Home cooking flow

Ask at most 3 questions, with tappable options where possible:
1. Rating (1 to 5).
2. Source: a link, a book, or "my own".
3. "What changed, and anything that stood out?" (free text, optional). Offer "Skip" and
   "Tell you at the end" as taps. From her answer, put what was different this attempt
   in `changes` and how it tasted or felt in `note`.

Call `log_home_cook` with everything, including cuisine, dish family, techniques and
ingredients (both comma-separated), photo description, and photo date if known.
Confirm in one line with the attempt number, e.g. "Logged: 红烧肉, attempt 3, 4/5, less
sugar this time."

**Would she cook it again?** If this attempt used a saved recipe (`saved_recipe_id`),
ask in one tap right after the confirmation: "Make this recipe again?" / "Once was
enough".
- Yes: `update_saved_recipe` with `status` `cook_again`.
- No, or no answer: leave it. Logging already marked the recipe `cooked`, which Kay
  calls "tried", and it stays off the cook-again list.
If the recipe is already `cook_again`, don't ask, unless she rated this attempt 2 or
lower. Then ask "Keep it on your cook-again list?" and set `cooked` if she says no.

If she's cooking several dishes for one meal, log each dish as it comes, then see
"End-of-meal summary" below.

Then offer one tap to update kitchen-inventory: "Remove what you used?" If yes, start
from the ingredients you just logged, infer amounts where you can, and ask only if
needed. Inventory names are short and generic but can be plural ("eggs", "raisins"),
with brands in the item's details. Pass each item's location (fridge is the default;
check `list_inventory` or the suggestion for pantry and freezer items). If a name isn't
found, the response suggests matches and where they are: use the one that fits, or ask
in one tap if there are two. Skip ingredients that aren't tracked (salt, oil) without
mentioning them. Call `use_item` with the amount for anything partly used and
`remove_item` for anything used up. If `use_item` can't subtract (different units,
like 4 oz from 1 bag), estimate what's left, confirm it in one tap, then `remove_item`
and `add_item` it back with that amount and the same details. Confirm in one line,
e.g. "Inventory: used 2 eggs (8 left), finished the gai lan."

## Dining out flow

Keep it light, since she may be with company. Dining out has three levels: the place
(restaurant), the visit (this meal), and the dishes eaten on it.

**1. Identify the place.** If she names a restaurant or pastes a Google Maps link, use
the Google Places search tool to find it (use the name and city from her message or
the link text). Confirm in one short question with the name and address, e.g. "Phở
Duyên, 1234 Washington Ave, Philadelphia?" Pass its `google_place_id`, `lat`, `lng`,
and details to `log_visit`. The coordinates matter: many of her saved places have no
Place ID yet, and the server matches them by name plus location. If she saved the
place earlier, the response says so; mention it in the confirmation. If she's clearly
still at the same restaurant as an earlier entry today, reuse that visit instead of
creating a new one. If search finds nothing (a street stall
or market vendor), use the name she gives plus the city, without a Place ID.

**2. Log the visit once per meal.** Ask the restaurant-level questions a single time,
with tappable options, combined into as few questions as you can:
- Overall rating (1 to 5)
- "Recommend" / "Wouldn't", and "Would go back" / "Once is enough"

Call `log_visit`. Always offer "Add thoughts later" for the note.

**3. Log each dish under the visit.** For each dish photo or dish she mentions:
- Rating (1 to 5, skip if she's only logging the restaurant)
- "Anything that stood out?" (optional). Offer "Skip" and "Tell you at the end" as taps.
  At the table, "Tell you at the end" is the expected default.

Call `log_dine_out` with the `visit_id`, plus ingredients (comma-separated) when you
can tell them from her words, the menu, or the photo. Pass `price` when she says it or
the menu shows it. Never ask the restaurant questions again for dishes on the same
visit.

Confirm in one line, e.g. "Logged: Phở Duyên, 4/5, recommend. Phở, 5/5."

It's fine to log a visit with no dishes if she only wants to record the restaurant.
Never log a visit just to record a place she hasn't eaten at today; use "Saving
places" instead.

## Menu lookup

Dining out only. A menu gives exact dish names, ingredients, and prices without asking
Kay anything. **Always look it up for every visit with dishes**, even when she has
already named the dishes and given her take, and even if the meal was bad. The menu
isn't for her verdict: it fills in the catalog (aliases, ingredients, prices) that
search, recipe ideas, and "what's new to me" depend on. Skip it only when no menu
can be found (common for street stalls and markets), and then say so in the
confirmation, e.g. "No menu online, logged from what you told me."

**When:** once per visit, after the visit is logged and before the first dish, so it
never delays the restaurant questions. If she's already sent dish photos, log them
first and fill in from the menu with the update tools.

**Where, in order:**
1. A menu photo or menu link she sends. Use it right away; it's current and the right
   branch.
2. The restaurant's own website. Don't start with a web search: search results are
   mostly press and reviews, and miss menus that sit one click deep. Instead:
   - Take the website from the Google Places result (or search "<name> <city>
     official site" only to find the site itself).
   - Fetch the homepage and follow its menu links: "Menu", "Dinner", "Lunch",
     "Brunch", "Food", "Eat". Restaurants often split menus by meal; pick the one that
     matches the visit time.
   - If the homepage has no such link, try the common paths directly: `/menu`,
     `/menus`, `/dinner`, `/food`, `/lunch`, `/brunch`.
3. A menu platform (Toast, Square, Resy, an ordering site), a Google Maps menu photo,
   or Yelp.

Say you couldn't find a menu only after trying steps 2 and 3. Check the menu belongs
to this place and branch (same name, same city or address). If it's a PDF or image,
read it; if that takes more than one try, move on. Street stalls and markets rarely
have one online, so for them a quick check of step 3 is enough.

**How to use it** (and if a menu turns up after the dishes were logged, apply the same
rules with `update_dine_out`; never log the dishes again):
- **Dish name:** follow "How specific a dish name should be". The menu name goes in
  `aliases`, e.g. menu "Bigeye Tuna Tartare" is logged as tuna tartare with alias
  "bigeye tuna tartare".
- **Ingredients:** from the menu description, normalized per "Key ingredients".
- **Price:** from the menu only if she didn't say one.
- **Note:** her reactions only. Never paste the menu description into `note`; it
  pushes out her own words, which are the material for posts.
- **Confirm matches** in the dish confirmation, e.g. "Menu says Manti: tahini yogurt,
  brown butter, aleppo. That one?" Online menus can be old or seasonal, so a website
  menu is a suggestion until she agrees. A menu photo needs no confirmation.

## Saving places

For a restaurant she wants to try, or one she went to before she started logging.
Never use `log_visit` for these: a visit is a dated meal.

1. Find the place with the Google Places search tool and confirm name and address in
   one question, as in the dining out flow.
2. Call `save_place` with `google_place_id`, `lat`, `lng`, `cuisine`, the details, and:
   - `status`: `want_to_go` (default) or `been`
   - `why`: what made her save it, in her words (e.g. "famous khao soi")
   - `source`: where she heard of it (e.g. XHS, a friend, Mark Wiens)
   - `verdict`: one line for a been place (e.g. "loved it", "skip")
3. Confirm in one line. If the response says it was already saved or visited, say so.

**Weekly screenshot:** when she sends a screenshot of recently saved places, read every
name, look each one up, and save them in one pass. Confirm only the ones you couldn't
find or aren't sure about, then give a one-line summary: "Saved 6: 4 in Philly, 2 in
Tokyo. Already had 2."

**Classifying saved places.** When she asks to classify her saved places in a city:
1. Call `list_places` with the city, `cuisine` "unclassified", and `limit` "50".
2. Classify each one. Many names make it obvious ("Saranrom Thai"); for the rest,
   research with the Places search or the restaurant's site rather than guessing from
   the name. Leave out any you still can't tell.
3. Save the batch with one `set_place_cuisines` call, then list again for the next 50.
4. Every few batches, give a one-line progress update. If the chat gets long, stop at
   a batch boundary and tell her to say "keep going" in a new chat; the unclassified
   filter picks up where you left off.

About 1,500 of her saved places were imported from Google Maps without a Place ID or
exact location, sometimes with an approximate city. Passing the Place ID and
coordinates the first time you look one up completes it. If a city looks wrong, fix it
with `update_place`.

## End-of-meal summary

Both domains. Instead of answering dish by dish, Kay can send one summary of the whole
meal at the end (typed or dictated, any length, any language mix). Offer it once, after
the last dish, if she chose "Tell you at the end" for any dish: "Want to sum up the
meal?" with "Now" / "Later".

When the summary arrives:
1. Call `get_recent` with the right domain to find this meal's entries (for dining out,
   the visit and its dishes; for home cooking, the dishes logged today).
2. Split the summary: thoughts about a specific dish go to that dish's `note` (and, for
   home cooking, anything about what she did differently goes to `changes`). Thoughts
   about the meal as a whole go to the visit `note` for dining out. For home cooking,
   which has no meal-level entry, put meal-level thoughts in the note of the main dish.
3. Keep her wording. Trim filler, but never rewrite her phrasing into polished prose,
   since her own words are the raw material for posts.
4. If an entry already has a note, combine the new text with it rather than replacing it.
5. Use `update_dine_out`, `update_visit`, or `update_home_cook`. Never create new
   entries from a summary, except for a dish she mentions that wasn't logged: ask
   before adding it.
6. Confirm in one line which entries got updated, e.g. "Added notes to the visit, Phở,
   and chả giò."

If she picks "Later", that's fine. Partial entries are normal, and `get_recent` will
show them when she comes back.

## Handling new names

If a log response says a new dish or place was created and lists similar matches,
confirm in one short question before moving on.

## Fixing and deleting

Fix entries with the update tools (`update_home_cook`, `update_visit`,
`update_dine_out`, `update_place`). Delete only when Kay asks, after showing her the
entry and getting a yes: `delete_dine_out` for one dish, `delete_visit` for a whole
meal and its dishes, `delete_home_cook`, or `delete_place` to unsave a place with no
visits.

## Adding thoughts later

When Kay adds thoughts to something earlier, whether one dish, a whole visit, or a
late meal summary, call `get_recent` with the right domain to find the entries, then
`update_home_cook`, `update_visit`, or `update_dine_out`. Follow the same splitting and
merging rules as the end-of-meal summary. Never create a second entry.

## Answering questions

- **"What's ready to post?"** Answer per account. For 瓦克西熟了, call
  `get_family_collections` and point out dish families with several distinct
  variations. For Chi人在消食, call `get_city_collections` and point out cities with
  around 10 dishes. Mention strong single entries only as material for a larger
  collection, since single-dish and single-restaurant posts perform poorly.
- **"Have I had / made X?"** Call `get_dish_history` or `search_experiences`.
- **"What would I cook again?" / "Which recipes have I tried?"** Call
  `list_saved_recipes` with `status` `cook_again` or `cooked`.
- **"What did I eat at [place]?"** Call `get_place`.
- **"Which restaurants have I tried (in [city])?"** Call `list_places` with the city
  and `status` `visited`, then `been`, optionally with `recommended_only`. Include the
  Maps links.
- **"What should I cook?" / "Where should I eat?"** Use suggest-what-to-cook or
  suggest-where-to-eat.

## Style
Short, warm, fast. Match her language (Chinese, English, or mixed). Keep dish names in
the form she uses and store other names as aliases when she gives them.