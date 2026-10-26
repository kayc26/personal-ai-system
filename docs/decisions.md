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


## recipe-from-video removed

**Trigger:** it overlapped with clip-recipe on YouTube links and ended in markdown files, so video recipes never reached the food journal.

- clip-recipe is the only path for saving recipes, video included. For a video whose steps aren't in the caption or description, it saves what's there and notes the gap.
- Not built: transcript fetching. Revisit only if video recipes keep getting lost.

## Live stats on the showcase page

**Trigger:** the page's usage numbers were counted by hand once, with no fixed definitions, and went stale.

- Each server exposes a read-only stats endpoint with its own counts. No server reads another's database.
- A scheduled GitHub Action snapshots the counts daily into a JSON file the page reads. Visitors never wait on a cold server.
- Monthly history comes from existing timestamps; bulk imports are counted separately so they don't show as one spike.
- Not built: auth on the endpoint (counts only), caching, a dashboard.

## Training procedure moved into a skill

**Trigger:** about 70% of the project instructions were training procedure, loaded on every message, including food and kitchen ones.

- A coach-training skill holds session choice, set-by-set coaching, progression, cardio, and the end-of-block review. The instructions shrank to role, routing, and global rules.
- The weekly check-in was dropped. Body weight, waist, and calorie targets stay in MacroFactor; no skill asks for them.
- The layer rule changed in practice: instructions hold routing and global rules, not procedure.

## Skills live in this repo

**Trigger:** skills existed only in my Claude account, with no history and no way to tell whether the loaded copy was current.

- `skills/` is the source of truth. A script compares it with the loaded skills and zips anything out of date for upload.
- Skills are uploaded as zips built from the repo, never from a proposal card (a card stores a shortened description).
- Skills that share rules keep identical reference files; the script fails if the copies drift.
- Removed skills are listed in `skills/RETIRED.txt`, and the script flags any still loaded. New and retired skills go up in the same sitting so they never compete.

## Meals and mindful-eating check-ins

**Trigger:** logging food meant questions mid-meal, I wanted to practice mindful eating, and later I want to compare how satisfying meals are with their macros.

- A meal is its own record, separate from a home cook (one dish cooked once) and a visit (one trip to a food place). One pot can feed several meals; one dinner can include several dishes. Meals link to both.
- Meal type answers one question, who prepared the food, in a fixed order where the first match wins: prepared, packaged, whole, homemade. No catch-all: if nothing fits, Claude asks. Near-zero-calorie drinks aren't meals.
- Every meal gets hunger and fullness at the start, and hunger, fullness, and satisfaction at the end, asked as separate questions, recorded without judgment.
- Only one meal can be open at a time, enforced in the database. While it's open, food photos and notes go to it, and its type decides which skill handles them.
- Times are always a full date and time; a date-only meal would land at midnight and break the time-based analysis.
- Numbers are always asked, never inferred. A snack once got a 5/5 guessed from a comparison in my note; the rule came from that.
- One logging skill became three, one per group of meal types, so routing is mechanical.
- No macros stored: MacroFactor's data export already has per-entry times and macros, so the later analysis is one join.
- Not built: a products record, meal-occasion fields (derived from the start time later), auto-closing forgotten meals, a separate rating field for snacks.

## Tests never touch production

**Trigger:** a coding agent's first test run for the meals change wrote test rows to the live database.

- Tests read a separate test database variable and refuse to run against the production endpoint.
- A permanent test branch of the database is reset from production before each task, so tests run on a fresh copy of real data.

## Recommender lists, revised

**Trigger:** the step 0 review of the recommender change, before anything was built.

- Lists are recommender-only (Michelin Guide, YouTube creators). My own Google Maps lists are how I organized saves, which status, city, and cuisine already capture, so they don't become lists, and I'm not a recommender.
- Two signals kept apart: status is my intent (want to go, been); a list is someone else's endorsement. A place only on recommender lists is "recommended, not saved", even if I copied the list into Google Maps.
- Places with list entries survive deleting a visit.
- "Been" (went before I started logging) isn't bulk-converted to "visited", which requires a logged visit. Fake dates and empty ratings would look like evidence. I backfill the ones I remember.
- Picking a restaurant becomes three layers: recommenders supply candidates, I promote the ones I like, and the picker chooses from those, citing who recommended it and what to order.

## Race training dropped

**Trigger:** running isn't a priority, and the 10k plan was being scheduled separately from lifting.

- The race was closed and its planned runs cleared. Cardio is general conditioning, planned together with lifting.
- The planned race-planning skill won't be built. The cardio logging tools stay.

## Expert-grounded coaching

**Trigger:** the coach was too rigid in some places and improvised in others. It scheduled an afternoon lifting session after a morning 8K, and when I dropped it, suggested moving triceps work to my pull day.

- Advice comes from named experts I chose (Jeff Nippard, Dr. Andy Galpin, Dr. Stacy Sims, Dr. Lauren Colenso-Semple, Dr. Kristen Holmes), not from the model's general knowledge.
- Each expert gets one neutral note, in my own words with sources: only what they say, training and nutrition together, nothing about me. Lines from secondary sources are flagged for checking. These live in a private repo.
- Separate guidance files for training and nutrition apply the notes to me. That's where conflicts between experts are resolved, once, with a line saying who won and why, so two runs can't disagree. Skills read only the guidance.
- The training skill keeps procedure (running a session, planning the week, the steps for any program change) and takes its numbers from the guidance.
- Trade-off: sources are read when the guidance is written, not on every question, so the guidance can go stale. A script will flag guidance older than its notes.
- Compared with Google's Personal Health Agent paper, the same bet on citations, curated sources, and enforced procedure; the difference is resolving conflicts once, by me, instead of per answer by the model.
- Add an expert only for a different view or a missing topic, not a second voice on the same one.

## Parked

Built only when triggered: staleness tracking for inventory, gym equipment as data, fuzzy dish matching, a nearby filter for places, run sync from Strava or Apple Health, scheduled list syncs, a products record for packaged food, a rating field for snacks, stall detection in code, fixing mislocated imported places (they correct themselves when looked up).
