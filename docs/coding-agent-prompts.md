# Coding agent prompts

One prompt per connector change. Paste each into a coding agent opened in that server's
repo. They are scoped on purpose: only what's needed now. Deferred ideas are listed as
"do not build" so the agent doesn't add them.

Done and removed: #1-3 (renames to kitchen-inventory, workout-log, food-journal, plus
my_tool removal, leftover expiry, cook_again status) and #4 (workout-log cardio and race
plans). Decisions for those stay in system/CHANGES.md. Numbering continues so CHANGES.md
references still match. Each prompt is also saved in its repo as
docs/agent-tasks/NN-name.md; commit it with the change.

---

## 5. food-journal: "this week" list (decided 2026-09-27, see CHANGES section 10)

```
You're working on my MCP server "food-journal", a food journal (home cooks, restaurant
visits and dishes, saved places, saved recipes, one shared dish catalog) used by
Claude as a connector.

Add a "this week" list: saved recipes I mean to cook soon, with no day attached. It's
a separate field from status (status is what I think of the recipe; queued is timing).

Do these things, nothing else:

1. Schema: add a nullable `queued_at` (date) to saved recipes. Migration; existing
   rows stay null.

2. update_saved_recipe: accept field "queued".
   - Any non-empty value (e.g. "yes") queues it: set queued_at = today, only if it's
     currently null (re-queuing keeps the original date).
   - Empty value unqueues it: queued_at = null.
   - Setting status to "dropped" also clears queued_at.
   - Update the description: "queued puts the recipe on the 'this week' list (recipes
     Kay means to cook soon, no day assigned); empty takes it off."

3. list_saved_recipes: add a `queued` parameter (default empty = no filter).
   - queued=true returns every queued recipe regardless of status (saved,
     cook_again, cooked), oldest queued first. The status filter is ignored in this
     mode. Dropped recipes can't be queued (see 2).
   - Every recipe in list_saved_recipes and get_saved_recipe output includes
     queued_at and days_queued (null when not queued).
   - Update the description to say queued=true is the "this week" list.

4. log_home_cook: when it links a saved recipe (saved_recipe_id, or a source that
   matches a saved recipe's link), clear queued_at, in addition to the existing
   status rule (saved/dropped -> cooked; cook_again and cooked unchanged). Say so in
   the description.

5. Remove the recreate-list tools: get_to_cook, get_recreate_list,
   set_recreate_status. Keep the underlying data and columns; don't drop anything.
   Tell me how many dishes currently have a recreate status (want_to_recreate or
   attempted) so I know what's there.

6. Server instructions: add one line: "Saved recipes can be queued on a 'this week'
   list (update_saved_recipe field queued; list_saved_recipes queued=true). Cooking a
   linked recipe takes it off."

Do not build: a day or date-planned field, a meal-plan table, a weekly reset,
recommendation or ranking logic, or anything else new.

Constraints:
- No other behavior changes. Existing data must keep working.
- Update docs/KAYFOODLAB_SPEC_SAVED_RECIPES.md (and the README tool list) to match:
  the queued field, the queued filter, and the removed recreate-list tools.
- Tests: queue/unqueue; re-queue keeps the original date; queued=true lists across
  statuses, oldest first; log_home_cook with a linked queued cook_again recipe clears
  queued_at and leaves status cook_again; dropping clears queued_at; the removed
  tools are no longer exposed.
- When done, give me: a short summary of changes, the recreate-status count, test
  results, and the exact deploy steps.
```

---

## 6. kitchen-inventory: get_expiring (unparked 2026-09-27, see CHANGES section 10)

get_stale stays parked.

```
You're working on my MCP server "kitchen-inventory", a food inventory (items, storage
location, quantity, expiry, low-stock threshold) used by Claude as a connector.

Add one tool, nothing else:

get_expiring(days=7, include_expired=true)
- Items whose expiry is on or before today + days, sorted by expiry (soonest first).
- Each item: id, name, location, quantity, expiry, days_left (negative = already
  expired).
- include_expired=false leaves out items with days_left < 0.
- Items with no expiry are not listed; return their count as no_expiry_count.
- Use the same timezone handling as the rest of the server.
- Description: "Items expiring within `days` days, plus already-expired ones. Use this
  for 'what's expiring' and the weekly review instead of scanning list_inventory."

Do not build: get_stale, last_updated tracking, or any other new tool.

Constraints:
- No behavior changes to existing tools.
- Update the README's tool list.
- Tests: boundary day (expiry = today + days is included), expired items with and
  without include_expired, items with no expiry excluded and counted.
- When done, give me: a short summary, test results, and the exact deploy steps.
```

---

## 7. workout-log: end_session ended_at (decided 2026-09-29, see CHANGES section 13)

Fill in yesterday's date and end time in step 5 before pasting.

```
You're working on my MCP server "workout-log", a training log (program, sessions,
sets, cardio, race plans) used by Claude as a connector.

Problem: end_session stamps the end time as "now". If I forget to close a session
and close it later, the duration is wrong and can't be fixed.

Do these things, nothing else:

1. First tell me how duration is computed today (stored column or computed on read)
   and where.

2. end_session: add an optional `ended_at` ("YYYY-MM-DD HH:MM", local time, same
   timezone handling as the rest of the server). Empty = now (current behavior).
   Reject an ended_at before the session's start or in the future.
   Add to the description: "If the workout didn't just end, ask Kay when she
   finished and pass ended_at."

3. Sessions store `duration_minutes`, set from ended_at - started_at when the
   session closes. end_session returns started_at, ended_at, duration_minutes.

4. Backfill duration_minutes for existing closed sessions from their timestamps.

5. Give me a one-off SQL statement to set ended_at (and duration_minutes) for the
   session on <YESTERDAY'S DATE> to <TIME>. Don't run it.

Do not build: editing other session fields, auto-closing open sessions, a
separate update_session tool, or anything else new.

Constraints:
- No other behavior changes. Existing data must keep working.
- Update the README tool list and any spec doc that describes end_session.
- Tests: no ended_at (uses now); valid ended_at; ended_at before start rejected;
  future ended_at rejected; duration_minutes returned and stored.
- When done, give me: a short summary, how duration was computed before, test
  results, and the exact deploy steps.
```

---

## 8. food-journal: recipe nutrition and time (decided 2026-09-30, see CHANGES section 14)

Save in the repo as docs/agent-tasks/08-recipe-nutrition-time.md.

```
You're working on my MCP server "food-journal", a food journal (home cooks, restaurant
visits and dishes, saved places, saved recipes, one shared dish catalog) used by
Claude as a connector.

Add optional nutrition and total time to saved recipes, so Claude can pick a recipe
that fits my remaining macros and the time I have. Values come only from the
recipe's own source (NYT Cooking and The Doctor's Kitchen publish them). Nothing is
estimated.

Do these things, nothing else:

1. Schema: add nullable columns to saved recipes: servings (int), calories (int),
   protein_g, carbs_g, fat_g, fiber_g (numeric, one decimal), total_minutes (int).
   Nutrition is per serving. Migration; existing rows stay null.

2. save_recipe and update_saved_recipe: accept these as fields. Reject negative
   values and non-numbers. In update_saved_recipe an empty value clears the field.
   Add to both descriptions: "Nutrition is per serving and total_minutes is total
   time, exactly as the recipe's source states them (e.g. the page's schema.org
   Recipe nutrition and totalTime). Fill only from the source; never estimate.
   Leave empty when the source doesn't give them."

3. list_saved_recipes and get_saved_recipe: include the new fields for every recipe
   (null when missing). In list output keep it to one compact line, e.g.
   "per serving: 520 kcal, 38 P, 45 C, 18 F, 6 fiber · 35 min".

Do not build: filters or sorting by nutrition or time, fit or ranking logic,
estimation, a prep/cook time split, a separate nutrition table, or anything else new.

Constraints:
- No other behavior changes. Existing data must keep working.
- Update docs/KAYFOODLAB_SPEC_SAVED_RECIPES.md and the README tool list to match.
- Tests: save with all fields; save with none; partial fields; update and clear one
  field; negative and non-numeric values rejected; list and get output show the
  fields and nulls.
- When done, give me: a short summary of changes, test results, and the exact
  deploy steps.
```

---

## 9. food-journal: recommenders, lists, and recommended dishes (decided 2026-09-30, see CHANGES section 14)

Save in the repo as docs/agent-tasks/09-place-lists.md. Deploy #8 first.

```
You're working on my MCP server "food-journal", a food journal (home cooks, restaurant
visits and dishes, saved places, saved recipes, one shared dish catalog) used by
Claude as a connector.

Goal: places can be recommended by different people through lists (my own Google
Maps lists, J. Kenji López-Alt's Seattle guide, a blog post), and a recommendation
can name specific dishes. Claude should answer "who recommends this place and what
should I order" and "which places make this dish". My own journal (visits, dishes
eaten, ratings) stays exactly as it is, attached directly to places.

Structure (staging, then canonical):
recommenders -> lists -> list entries (raw, per source) -> places (canonical, one row
per restaurant). Entry dishes link entries to the dish catalog. The recommender is
stored on the list only, never repeated on entries or places.

Step 0, before any change, tell me:
- How the existing ~1,313 Google Maps places were imported (script, where it lives,
  which CSV columns it read). Reuse that parser below.
- How many places have a Google feature ID in their Maps URL (the "0x...:0x..." after
  "!1s"), how many don't, and any feature IDs that appear on more than one place.
  If there are duplicates, list them and stop before step 1's unique index; ask me.

Do these things, nothing else:

1. Schema (migration):
   - recommenders: id, name, aliases (list), created_at.
   - lists: id, recommender_id, title, source ("Google Maps", "Apple Maps", a site
     name), source_url, last_synced_at. Unique on (recommender_id, title).
   - list_entries: id, list_id, place_id (nullable: unmatched), raw_name, raw_note,
     raw_city, maps_url, feature_id, entry_date, status ("on_list" or "removed"),
     removed_at, dishes_extracted_at (nullable).
   - entry_dishes: id, entry_id, dish_name_raw, dish_id (nullable).
   - places: add nullable feature_id, unique when present.
   - Indexes: feature_id on places and entries, all foreign keys, normalized dish
     names and aliases in the catalog.

2. Migration of existing data. Keep every existing places column (source, list_name,
   why, status, etc.) unchanged; nothing is dropped.
   - Fill places.feature_id from each Maps URL.
   - Create recommender "Kay". For each distinct list_name among places with source
     "Google Maps", create a list (Kay, that title, source "Google Maps").
   - One on_list entry per such place: raw_name = place name, raw_note = why,
     maps_url, feature_id, place_id linked, entry_date = the place's saved date if
     stored, else migration date.
   - Report: recommenders, lists, entries created, places without a feature ID.

3. One sync function in code, used by both entry points below. Input: recommender
   name, list title, source, source_url, and the full current list of entries
   (name, note, maps_url?, city?, entry_date?). It diffs against that list only:
   - Entry identity within a list: feature_id when the Maps URL parses; otherwise
     normalized name + city.
   - New: create the entry. Link a place by feature_id (create the place if none
     exists, status want_to_go only if the recommender is Kay; otherwise status
     empty/not saved). No feature_id: leave place_id null (unmatched).
   - Missing from the input: status removed, removed_at = today. Never delete.
     Removed entries that come back are set on_list again.
   - Note changed: update raw_note and clear dishes_extracted_at and its
     entry_dishes so the entry is re-extracted.
   - Unchanged: write nothing.
   - Resolve the recommender by name or alias, case-insensitive. If none matches,
     create one and flag it in the result as new, so Claude can check for drift
     ("Kenji" vs "J. Kenji López-Alt").
   - Set last_synced_at. Return counts: added, removed, restored, notes changed,
     unchanged, unmatched, plus the new recommender flag.
   Short Maps links (maps.app.goo.gl): resolve the redirect to get the feature ID.
   Report any URL format you can't parse; don't guess.

4. Entry point A, file upload (for my Google Takeout exports, too big to pass
   through a tool call): POST /import/google-maps-list, authenticated by a bearer
   token from env var IMPORT_TOKEN. Accepts one Saved-list CSV or a Takeout zip
   containing Saved/*.csv. Each CSV is one list; title from the file name;
   recommender "Kay", source "Google Maps". Lists not present in the upload are not
   touched. Returns the sync summary per list as JSON. Give me a curl example.

5. Entry point B, MCP tool sync_list(recommender, list_title, source, source_url,
   entries) for small lists Claude clips from a page (guides, blog posts). entries is
   a JSON array as in step 3. Cap at 200 entries per call; larger lists must use the
   upload. Description: "Sync one recommendation list: pass the FULL current list;
   the server adds, removes, and updates only what changed. For Google Takeout files
   use the upload endpoint, not this tool."

6. Dish extraction support (Claude reads notes and names the dishes; code matches):
   - list_pending_entries(limit): on_list entries with a non-empty raw_note and
     dishes_extracted_at null, plus unmatched entries (place_id null), each with
     list, recommender, raw name, note, city.
   - set_entry_dishes(entry_id, dishes): dishes is a list of names as written. Match
     each to the catalog by normalized name or alias only (exact, no fuzzy); store
     dish_id or null, always keep dish_name_raw. Set dishes_extracted_at, including
     when the list is empty (a place-level recommendation). Return which matched.
   - set_entry_place(entry_id, maps_url): link an unmatched entry to a place by
     feature ID, creating the place if needed.

7. Reads:
   - get_place: add "Recommended by": for each on_list entry, recommender, list,
     entry date, note, and its dishes. Keep everything it shows today (my visits and
     ratings).
   - list_places: add a recommender filter (name or alias): places with an on_list
     entry in any list by that recommender.
   - New find_places_for_dish(dish, dish_family, city, limit=10): one of dish or
     dish_family. dish resolves through the catalog like find_dish; if there's no
     exact or alias match, return the find_dish candidates instead of results.
     Returns places where an on_list entry names that dish (or any dish in the
     family), or where I logged that dish on a visit. Each place shows which
     recommenders named it and my latest rating of that dish there. Sort by number
     of distinct recommenders, then places I rated it, then name.

8. save_place: if the new place's Maps URL has a feature ID that already exists,
   return the existing place and say it was already saved (no duplicate). If
   list_name is given, also create or update an on_list entry in Kay's list of that
   name (creating the list if needed). Otherwise unchanged.

9. Server instructions: add "Places can be recommended through lists (recommender ->
   list -> entries, with dishes). get_place shows who recommends a place and what to
   order; find_places_for_dish finds places by dish; sync_list or the upload endpoint
   update a list."

Do not build: a shortcut/inbox endpoint, fixing place cities, scheduled syncs, fuzzy
or semantic dish matching, scoring beyond the sort in step 7, multi-user support,
splitting the server, dropping or renaming existing places columns, or anything
else new.

Constraints:
- No behavior changes beyond the above. Existing data and tools must keep working.
- Update the README tool list and any spec doc that describes places.
- Tests: migration on a copy of real data (counts match; no place changed except
  feature_id); sync adds, removes, restores, and detects a changed note; unchanged
  entries write nothing; lists absent from an upload are untouched; entry without a
  feature ID stays unmatched and set_entry_place links it; recommender alias
  resolution and the new-recommender flag; set_entry_dishes exact/alias match and
  unmatched raw names kept; find_places_for_dish by dish and by family, sort order,
  city filter; get_place shows recommenders and dishes; save_place duplicate
  feature ID returns the existing place; upload rejects a missing or wrong token.
- When done, give me: the step 0 answers, migration report, a short summary of
  changes, test results, the curl example, and the exact deploy steps (including
  setting IMPORT_TOKEN on Render).
```
