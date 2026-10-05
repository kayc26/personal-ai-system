# Decision log

Design decisions for the system, newest last. Each entry names what triggered it, what was decided, and what was deliberately not built.

## Layer rule

| Layer | Holds | Test |
|---|---|---|
| MCP server (code) | Facts, schema, deterministic logic (dates, sums, queries) | Would two runs of the model disagree? Put it in code. |
| Skill | Reusable procedures, general knowledge | Useful in any project, or shareable with someone else |
| Project instructions | Role, coaching rules, routing to skills | Specific to how I'm coached |
| Project file | Personal rules a skill reads | Personal, but the skill needs it |
| Chat memory | Almost nothing | If it's a fact, use a database; if it's a rule, use a file |

## Three projects merged into one

**Trigger:** separate Projects for training, pantry, and food duplicated rules and drifted apart.

- One Project now handles training, kitchen, and food, and routes each request to a skill or server.
- Nutrition guidance that was duplicated in the instructions moved into one skill. Personal rules live in a separate file the skill reads, so the skill itself stays general.
- Hardcoded schedules were removed from the instructions; the database already held them.
- Facts that had collected in chat memory moved to databases or files.

## Macro tracking stays in MacroFactor

**Trigger:** sending nutrition screenshots to Claude was tedious.

- MacroFactor stays the logger and source of targets.
- An iOS Shortcut uses MacroFactor's own "Macros Remaining" action to copy structured data, which I paste into Claude.
- Not built: a nutrition database, screenshot parsing, or Claude writing meals back into MacroFactor.

## "Cook again" recipes

- Saved recipes have a status: saved, cook_again, cooked, dropped.
- Cooking a recipe moves saved to cooked but never downgrades cook_again, or every repeat cook would knock a favorite off the list.

## Cardio and race plans

**Trigger:** training for a 10k.

- The server stores races, planned runs, and logged runs, and reports done or missed status and weekly totals.
- A skill writes and adjusts the plan. No plan content lives in instructions or docs.
- Adjustments rewrite the plan from today forward and never edit past rows.

## "This week" recipe list

**Trigger:** I'd see a recipe I wanted to make this week, without knowing which day.

- A shortlist, not a meal plan: no days, no calendar.
- "Queued" is its own field, not a status. Status is what I think of the recipe; queued is timing. A favorite can be queued without losing its status.
- No weekly reset. A recipe stays queued until it's cooked, unqueued, or dropped. A weekly review nudges anything queued 10+ days.
- Older "to cook" tools were removed because they competed with the new list for tool choice. Their data was kept.
- The kitchen server gained a get_expiring query, so the weekly review doesn't do date math in the model.

## Duplicate connectors removed

**Trigger:** every tool appeared twice (desktop config and web connector pointing at the same servers), and the model's choice between them was arbitrary.

- Daily use goes through the web connectors only.
- Server changes are tested from the coding agent against a test database, not from the desktop app.

## Recipe clipping as its own skill

**Trigger:** saving a recipe meant screenshots and manual pasting.

- Saving moved out of the food-logging skill so the two don't both trigger on "save this recipe".
- Source order: the page's schema.org Recipe data, then the page's own embedded data, then screenshots, then page text.
- The full recipe text is stored whenever it can be read, because links and subscriptions don't last. Recipes that can't be read are marked "link only".

## Workout end time

**Trigger:** a session closed the next morning recorded the wrong duration, with no way to fix it.

- Closing a session accepts an optional end timestamp. Duration is derived from start and end, so the two can't disagree.
- Not built: guessing the end from the last logged set, auto-closing old sessions, or a general edit tool.

## Recipe nutrition and time

**Trigger:** picking a new recipe that fits remaining macros and the time I have.

- Per-serving nutrition and total time are stored only as the recipe's source states them. Never estimated.
- Total time only; prep time isn't hands-on time and sites fill it inconsistently.
- No filters yet. Code narrows to a shortlist; the model weighs trade-offs. No scoring formula.

## Restaurant recommenders and lists

**Trigger:** restaurant lists from other people (published guides, blog posts), dish-level recommendations, and keeping my own Google Maps lists current.

- Structure: recommenders, then lists, then raw list entries, then canonical places (one row per restaurant, keyed on Google's feature ID). Entry dishes link to a shared dish catalog.
- The recommender lives on the list only, never repeated on entries or places.
- Entries that can't be matched to a place wait unmatched instead of creating junk places.
- Lists are dated, not kept continuously up to date. Removed entries are marked, never deleted. Closures are checked when a place is about to be recommended.
- Large Google Takeout syncs go through a file upload with the diff computed on the server. Small clipped lists use a tool call, capped at 200 entries.
- Dish matching in code is exact or alias only. Fuzzy matching waits until misses are real.
- Restaurants and recipes stay in one server and one database, because the dish catalog joins them. If tool choice degrades, split the tool surface, not the data.

## Parked

Built only when triggered: staleness tracking for inventory, gym equipment as data, coaching rules as skills, fuzzy dish matching, a nearby filter for places, run sync from Strava or Apple Health, scheduled list syncs.
