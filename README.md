# Personal AI System

A personal agent built on Claude that runs my training, kitchen inventory, recipes, and food log. I use it every day.

**[Interactive architecture map](https://kayc26.github.io/personal-ai-system/)**: tap any piece to see what it connects to, or trace a request through the system.

## The problems

1. **Food waste.** I love cooking, but I lose track of leftovers and ingredients, then buy new things for the next interesting recipe. A lot goes to waste.
2. **Recipes everywhere.** I find recipes on RedNote, NYT Cooking, blogs, and YouTube, and they scatter across apps and screenshots.
3. **Training.** I want a consistent routine, but I lose track of my weights and spend gym time looking up exercises instead of doing them.
4. **Eating out.** I've saved over 1,000 restaurants in Google Maps, but finding one for myself or recommending one to friends still takes a long time.

## What it does

- **Kitchen:** I send a photo of a grocery haul and it logs each item with a storage location and expiry date. It can tell me what's expiring and what's running low.
- **Recipes:** I save a recipe from a link, screenshots, a cookbook photo, or a cooking video. It stores the full recipe, plus nutrition and cook time when the source lists them. Recipes I want to make go on a "this week" list.
- **What to cook:** it picks from the "this week" list based on what's expiring, what I cooked recently, today's training, and my remaining macros, then gives me a recipe I can follow.
- **Training:** when I get to the gym, it picks the day's session, prescribes the weight for each exercise from my history, and logs every set as I go.
- **Eating out:** it keeps a journal of what I've cooked and eaten. When I need a restaurant, it picks from my saved places for the occasion and skips places I didn't like.

## How it's built

| Layer | Pieces | Holds |
|---|---|---|
| Interfaces | Claude app (phone, desktop, Chrome side panel); an iOS Shortcut that pastes remaining macros from MacroFactor | Where I talk to it |
| Project | One instructions file | Role, coaching rules, routing to skills |
| Skills (7) | manage-kitchen-inventory, suggest-what-to-cook, clip-recipe, recipe-from-video, log-food, suggest-where-to-eat, check-nutrition | Reusable procedures |
| MCP servers (3, on Render) | kitchen-inventory (8 tools), workout-log (19 tools), food-journal (26 tools) | Facts and deterministic logic |

## Design principle

> If two runs of the model could disagree on something, it belongs in code.

The model makes judgment calls. Everything else has one home:

| Layer | Holds | Test |
|---|---|---|
| MCP server (code) | Facts, schema, dates, sums, diffs, queries | Would two runs of the model disagree? Put it in code. |
| Skill | Reusable procedures and general knowledge | Useful in any project, or shareable with someone else |
| Project instructions | Role, coaching rules, routing | Specific to how I'm coached |
| Chat memory | Almost nothing | A fact goes in a database; a rule goes in a file |

## Selected decisions

- **Expiry checks are a query, not model math.** The weekly review asks the server what's expiring instead of having the model compare dates across the whole inventory.
- **Bulk imports skip the model.** Syncing about 1,300 saved Google Maps places is a file upload with the diff computed on the server. Passing every row through the model would be slow and error-prone.
- **Timestamps, not durations.** A workout stores its end time and derives duration from it, so the two can never disagree.
- **Fewer, clearer tools.** Overlapping tools made the model's tool choice arbitrary, so I remove or merge them instead of adding more.

Full log: [docs/decisions.md](docs/decisions.md)

## How I build it

- I only build when something breaks or becomes a weekly pain.
- Each change is a scoped prompt to a coding agent, with an explicit "do not build" list so it doesn't add features I didn't ask for. See [docs/coding-agent-prompts.md](docs/coding-agent-prompts.md).
- Every decision and its trade-offs go in the decision log.

## Status

**Live:** kitchen inventory, recipe saving, the "this week" list, cooking suggestions, lifting sessions, the food journal, restaurant suggestions.

**In progress:** a race-training skill for running plans, and syncing restaurant lists from Google Maps and published guides.

## Open questions

- How should the tool surface scale? As tools are added, tool selection gets harder. The current plan is to split one server's tools into smaller connectors over the same database, not to split the data.
- Instructions are pasted into the Project by hand, so keeping them in sync with the versioned file depends on discipline rather than tooling.
