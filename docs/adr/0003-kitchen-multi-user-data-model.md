# ADR-0003: Kitchen multi-user data model

- **Date**: 2026-11-20
- **Iteration**: 2
- **Status**: Draft
- **Deciders**: Kay (decides), Ari (Claude Opus 5.5, recommends)
- **Source**: [seed-2026-11-20-separating-the-system](seed-2026-11-20-separating-the-system.md)

**TL;DR**: One kitchen server serves one household. The inventory is shared by everyone signed in. Recipes, the "this week" list, and home cooks belong to each person; roommates can read each other's recipes but only change their own. Each person's profile lives on the server. Kay's existing rows become hers.

---

## Context

Kitchen gets three users (Kay and two roommates), signing in per [ADR-0002](0002-oauth-through-neon-auth.md), with recipes and home cooks moving in from food-journal per [ADR-0001](0001-split-the-system-by-area.md). From the seed:
- One shared inventory for the household.
- Recipe inboxes are per person.
- Languages differ. Item names need **no change**: `add_item` already takes the everyday name, other-language names can go in `details`, and every add or miss lists similar items (by words, spelling, or a name in details), so the model merges duplicates.

From the current repo (iteration 1 missed these): the decision "One profile per person" puts each person's facts in one `PROFILE.md` (who they are, diet, training setup, goals, chosen experts), kept in Kay's private repo and uploaded as a Project file. Numbers and principles live in guidance files (`TRAINING_GUIDANCE.md`; nutrition guidance planned). check-nutrition reads `PROFILE.md` from the Project, and coach-training reads both.

## Decision

1. **One deployment = one household.** Everyone allowed on the server shares one inventory. No households table.
2. **Inventory is shared.** No owner on items. Every allowed user can add, use, and remove anything.
3. **Recipes and home cooks are per person.** Saved recipes, the "this week" list, and home cooks get a `user_id`. Writes are scoped to the signed-in user server-side.
4. **Roommates can read each other's recipes** (QST-RECIPE-VISIBILITY: B). By default each person sees their own; asking for a roommate's ("what's on Mia's list?") is a read. Only the owner can change, queue, or delete a recipe.
5. **Cooking is one record: the home cook** (QST-HOME-COOKS in ADR-0001: C). Marking a recipe cooked creates a home cook (at minimum: recipe and date); log-home-cooking adds rating and notes when the person wants them. "Cooked recently" and the recipe's status both come from home cooks, so there's one source. This replaces iteration 1's separate cooked marker.
6. **Kay's data migrates to Kay.** Kay's recipes and home cooks copied from `kayfoodlab` get her user id once she has one. Tests prove that one user can't change another's recipes or home cooks.
7. **Each person's profile lives on the server** (QST-PERSONAL-RULES: A): a short free-text profile per user, read and written with a tool, so it works the same in the app, on the phone, and in Claude Code with no setup. How this meets Kay's existing `PROFILE.md` is QST-PROFILE-SOURCE.
8. **Skills become general.** "Kay" leaves skill text. Reply language follows the user (the model matches their language; in Claude Code, the `language` setting).

Do not build: households, item owners, editing someone else's recipes, a shared recipe box, name normalization or translation tables, roles or admin users.

---

## Questions

### QST-RECIPE-VISIBILITY: Can roommates see each other's recipes?
- Status: answered
- Why asking: decision 3 makes recipes private. If roommates cook for each other, private inboxes might get in the way. If not, shared ones add clutter and token cost.
- Need: pick a letter (or override — any shape answers)

Options:
- **A — Private**: each person sees only their own recipes and "this week" list.
- **B — Readable by the household**: you see your own by default and can ask for a roommate's ("what's on Mia's list?"). Only the owner can change them.
- **C — One shared recipe box**: like the inventory.

**Recommendation**: (by Ari, Claude Opus 5.5, 2026-11-20)
**A — Private.** Rationale: Kay said inboxes differ, and private is the simplest rule to test. Opening reads later is a query change; taking visibility away after people have used it is harder.
Confidence: 0.7, because I don't know how the roommates cook together. If wrong: if they plan meals together, B.

**ANS:** (by kayc26)
b

---

### QST-PERSONAL-RULES: Where do per-person rules live?
- Status: answered
- Why asking: skills must be general, but suggest-what-to-cook and check-nutrition use personal rules (macros, diet, schedule). Kay keeps them in a Project file today. Roommates on the phone don't want a long setup, and a Claude Project with a file is setup.
- Need: pick a letter (or override — any shape answers)

Options:
- **A — A profile on the server**: each user has a short free-text profile, read and written with a tool. Works the same in the app, on the phone, and in Claude Code, with zero setup. Content is the person's own rules, never Kay's.
- **B — A file each person keeps**: a Project file in the Claude app, or `CLAUDE.md` in Claude Code. Matches today's layer table ("personal rules a skill reads"), but costs setup on every surface.
- **C — No personal rules for roommates yet**: only Kay has a file; roommates get general suggestions.

**Recommendation**: (by Ari, Claude Opus 5.5, 2026-11-20)
**C — none for roommates yet**, with A as the path if they ask. Rationale: nothing in the seed says the roommates have rules, and the build-only-what's-decided rule applies. Kay keeps her Project file.
Confidence: 0.6, because roommates may well want dietary notes (allergies, vegetarian) as soon as they use suggestions. If wrong: if any roommate has a dietary rule on day one, A.

**ANS:** (by kayc26)
a

---

### QST-PROFILE-SOURCE: How does the server profile meet Kay's `PROFILE.md`?
- Status: answered
- Why asking: decision 7 puts profiles on the kitchen server, but Kay's `PROFILE.md` already holds her facts for every skill, including coach-training in the workout plugin. Two copies of Kay's profile could disagree; moving it into kitchen would make the coach depend on kitchen.
- Need: pick a letter (or override — any shape answers)

Options:
- **A — File first, server as fallback**: skills read `PROFILE.md` from the Project when it exists (Kay), and the kitchen server profile otherwise (roommates). Kay's profile stays one file; roommates get zero setup.
- **B — Everyone on the server, Kay included**: Kay's `PROFILE.md` moves into kitchen's profile. coach-training reads it from kitchen, so the workout plugin needs the kitchen connector.
- **C — Split by area**: food facts (diet, preferences) in kitchen's server profile for everyone; Kay's training facts stay in `PROFILE.md` for the coach. Kay's profile is split in two.

**Recommendation**: (by Ari, Claude Opus 5.5, 2026-11-20)
**A — File first, server as fallback.** Rationale: it keeps Kay's single profile ("One profile per person") and the "no server calls another" rule (ADR-0001 decision 3), and check-nutrition already has a fallback path when no profile file is found (skills/check-nutrition/SKILL.md, "Not found"). Roommates get the server profile, which is what QST-PERSONAL-RULES: A was for.
Confidence: 0.6, because a fallback chain means two places a skill looks, and a model could pick the wrong one. If wrong: if Kay wants to stop uploading `PROFILE.md` to the Project, B; if the coach should never see food facts, C.

**ANS:** (by kayc26)
b

---

## Iterations

### Iteration 1 — 2026-11-20
- **Trigger**: seed chunked into ADRs.
- **Contributors**: Kay, Ari (Claude Opus 5.5).
- **Changes**: first draft; two questions.
- **Outcome**: Draft. Kay answered both (RECIPE-VISIBILITY B, PERSONAL-RULES A).

### Iteration 2 — 2026-11-20
- **Trigger**: Kay's answers in ADRs 0001 and 0003, and iteration 1 found to be written from a checkout 59 commits behind `origin/main`.
- **Contributors**: Kay, Ari (Claude Opus 5.5).
- **Changes**: Context adds "One profile per person" and guidance files. Decision: home cooks are per person and are the one record of cooking (replaces the separate cooked marker); household can read each other's recipes; profiles live on the server. New question: QST-PROFILE-SOURCE.
- **Outcome**: Draft.
