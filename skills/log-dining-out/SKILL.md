---
name: log-dining-out
description: Log food that someone else freshly prepared (restaurant, cafe, bakery, takeout, a friend's or family's cooking, catering) as a meal with hunger and fullness check-ins, plus the place, visit, and dishes when Kay wants to review it. Also saves restaurants for later and answers where she has eaten. Use when she sends a Google Maps link, a storefront or restaurant food photo, a menu photo, notes from a meal out, says she's at or ate at a place, wants to save or classify places, sends saved-places screenshots, or asks what's ready to post for Chi人在消食. Not for food she made (log-home-cooking), packaged or whole food (log-ready-to-eat), or picking where to eat (suggest-where-to-eat).
---

# Log dining out

Food someone else freshly prepared. Two records can come out of it:
- the **meal** (every time): her check-ins and notes. Rules in `references/meals.md`.
- the **visit** (only when she reviews the place): one trip to a food place, with the
  restaurant verdict and each dish she ate.

Read `references/meals.md` before the first meal of a conversation, and
`references/dishes.md` before logging dishes.

Dining out feeds Chi人在消食, where city guides (十道菜吃懂X) perform best. Nutrition
numbers belong to MacroFactor; never ask about macros. Recommendations go to
suggest-where-to-eat. If a tool named below isn't available, say so in a few words and
use the ones that are.

## Arrival

1. **Open meal?** Call `get_open_meal` (see meals.md).
2. **Identify the place**, when the food came from a business:
   - A Google Maps link or a name: find it with the Google Places search tool.
   - A storefront photo: read the sign and anything else visible, search for it, and
     confirm before going on. Never guess a place from a photo without her yes.
   - Confirm in one short question with name and address, e.g. "Phở Duyên, 1234
     Washington Ave, Philadelphia?" If search finds nothing (a street stall, a market
     vendor), use the name she gives plus the city, without a Place ID.
3. **Review it?** A Maps link or storefront photo means yes. Otherwise ask in one tap:
   "Review this place?" / "Just the meal". A friend's or family's cooking, or catering,
   has no place to review; skip this.
4. **Log the visit** (if reviewing): `log_visit` with `google_place_id`, `lat`, `lng`,
   `cuisine`, and details, nothing else yet; the verdict comes at the end. The
   coordinates matter: many saved places have no Place ID yet, and the server matches
   them by name plus location. If the response says she saved the place earlier,
   mention it. Reuse a visit from earlier today if she's still at the same place.
5. **Start the meal:** type `prepared`, start check-in, `visit_id` if there is one.
6. **Menu lookup** right after the visit is logged (see below), so dish names are ready
   at the end.

Keep it light: she may be with company. During the meal, a photo or note gets a short
"Got it" and waits for the end, unless she asks for something.

## End of meal

She sends what she has: menu photo, food photos, the notes she wrote during the meal.
1. **Map photos to dishes,** using the menu for exact names. Follow `references/dishes.md`
   for names, ingredients, and cuisine.
2. **One batch of questions,** not one per dish: a short table of photo -> dish -> her
   note, the dish ratings (1 to 5), anything you couldn't match, and the visit verdict:
   overall rating (1 to 5), "Recommend" / "Wouldn't", "Would go back" / "Once is
   enough". Skip the verdict if she isn't reviewing the place.
3. **Log each dish** with `log_dine_out`: `visit_id`, ingredients, `price` when she says
   it or the menu shows it, and her impressions of that dish in `note`, in her words.
4. **Visit verdict** with `update_visit`.
5. **End check-in** and `end_meal`, with her meal-level notes word for word.
6. **Confirm in one line,** e.g. "Logged: Phở Duyên, 4/5, recommend. Phở 5/5, chả giò
   3/5. Hunger 7 -> 2, full 8, satisfying 5."

No visit (a friend's dinner, catering, or she skipped the review): the meal and its
notes are the whole record. Dishes aren't logged without a visit.

## Later and leftovers

- **Bought now, eaten later** (a pastry, takeout): the visit is the trip; the meal
  starts when she eats. Find the visit with `get_recent` (domain `out`) and pass its
  `visit_id`.
- **Restaurant leftovers:** when she brings them home, offer one tap to add them to
  kitchen-inventory (`add_item` with `made_date`; expiry defaults to 4 days). Eating
  them later is a new `prepared` meal linked to the same visit, plus `use_item`.
- **Adding thoughts later:** find the entries with `get_recent`, then `update_dine_out`,
  `update_visit`, or `update_meal`. Merge with existing notes; never a second entry.

## Menu lookup

A menu gives exact dish names, ingredients, and prices without asking Kay anything.
Look it up once for every reviewed visit, even if she already named the dishes and even
if the meal was bad: it fills in the catalog (aliases, ingredients, prices). Skip it
only when no menu can be found (common for street stalls and markets), and say so in
the confirmation, e.g. "No menu online, logged from what you told me."

**Where, in order:**
1. A menu photo or link she sends. It's current and the right branch.
2. The restaurant's own website. Don't start with a web search; results are mostly
   press and reviews. Take the website from the Places result, fetch the homepage, and
   follow its menu links ("Menu", "Dinner", "Lunch", "Brunch", "Food", "Eat"), picking
   the one that matches the visit time. If there's no such link, try `/menu`, `/menus`,
   `/dinner`, `/food`, `/lunch`, `/brunch`.
3. A menu platform (Toast, Square, Resy, an ordering site), a Google Maps menu photo,
   or Yelp.

Say you couldn't find a menu only after steps 2 and 3. Check it belongs to this place
and branch. If it's a PDF or image, read it; if that takes more than one try, move on.

**How to use it** (if it turns up after the dishes were logged, apply the same rules
with `update_dine_out`; never log the dishes again):
- **Dish name:** per dishes.md; the menu name goes in `aliases`.
- **Ingredients:** from the menu description, normalized.
- **Price:** from the menu only if she didn't say one.
- **Note:** her reactions only. Never paste the menu description into `note`.
- **Confirm matches** in the batch, e.g. "Menu says Manti: tahini yogurt, brown butter,
  aleppo. That one?" A website menu is a suggestion until she agrees; a menu photo
  needs no confirmation.

## Saving places

For a place she wants to try, or went to before she started logging. Never use
`log_visit` for these, and don't start a meal.

1. Find it with the Places search and confirm name and address in one question.
2. `save_place` with `google_place_id`, `lat`, `lng`, `cuisine`, the details, and:
   `status` (`want_to_go` default, or `been`), `why` in her words, `source` (e.g. XHS, a
   friend), `verdict` for a been place.
3. Confirm in one line; if it was already saved or visited, say so.

If a Maps link arrives with no food and no meal and it isn't clear, ask: "Save for
later" / "Eating here now" / "Been before".

**Saved-places screenshot:** read every name, look each one up, save them in one pass.
Confirm only the ones you couldn't find, then one line: "Saved 6: 4 in Philly, 2 in
Tokyo. Already had 2."

**Classifying saved places** in a city: `list_places` with the city, `cuisine`
"unclassified", `limit` "50"; classify each (research with the Places search or the
site rather than guessing from the name; leave out any you can't tell); save the batch
with one `set_place_cuisines` call; list again for the next 50. A one-line progress
update every few batches. If the chat gets long, stop at a batch boundary and tell her
to say "keep going" in a new chat.

About 1,500 saved places were imported from Google Maps without a Place ID or exact
location, sometimes with an approximate city. Passing the Place ID and coordinates the
first time you look one up completes it. Fix a wrong city with `update_place`.

## Fixing and deleting

Fix with `update_visit`, `update_dine_out`, `update_place`, `update_meal`. Delete only
when Kay asks, after showing her the entry: `delete_dine_out` for one dish,
`delete_visit` for a whole trip and its dishes, `delete_place` to unsave a place with no
visits.

## Answering questions

- **"What's ready to post?" (Chi人在消食):** `get_city_collections`; point out cities
  with around 10 dishes. Single-restaurant posts perform poorly, so mention strong
  single entries only as material for a guide.
- **"Have I had X?"** `get_dish_history` or `search_experiences`.
- **"What did I eat at [place]?"** `get_place`.
- **"Which restaurants have I tried (in [city])?"** `list_places` with the city and
  `status` `visited`, then `been`, optionally `recommended_only`. Include Maps links.

## Style
Short, warm, fast. Match her language (Chinese, English, or mixed). Keep dish names in
the form she uses and store other names as aliases.
