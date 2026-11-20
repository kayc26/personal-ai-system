<!-- adr template version: "seed 3.10.0" -->

# SEED: Separating inventory, workouts, and restaurants

- **Date**: 2026-11-20
- **From**: Kay

<!-- MODEL INSTRUCTIONS: look for "Model Response Request" and engage dialogically and epistemically until chunking the seed into ADRs following `adr.md` + referencing ADRs in "Derived Into" section, see instructions below.
-->

---

## Brain Dump

- Who uses each part: 
    workout: me 
    kitchen inventory: me and my two other roommates
    restaurants: me and potentially whoever asks for restaurant recommendations
- How they'd use it: Claude Code plugin, Claude app (custom connector), or both?
    me: app or plugin
    others: plugin
- What bothers me about the current setup?
    I want my roommates to be able to use the kitchen inventory without long set ups in claude app, nor tons of bells and whsitles which is going to burn a lot of tokens,
    we probablly will have different recepie inboxes too.
    also language preferences will be different
    workout coach is not very "smart"
    recipe recommendation is not very smart
    not using restaurnats recommendation, really, probably need to redesign
- What must stay connected across areas (e.g. suggest-what-to-cook reads training + expiring inventory; recipes and restaurants share the dish catalog)?
    suggest-what-to-cook reads training (if available) +  inventory
- Showcase: does personal-ai-system stay the public overview, or does each area get its own README / map?
    each area can be kept in thir current repo. personal ai-systme can potentailly be sunset, but I do want to have a personal website which include it
- CIS7000: does the course require a particular structure?
    no

---

**Model Response Request:**
<!-- literal sensor block — parser-significant: tooling reads these exact checkbox labels as the seed's declared lifecycle state; do not reword them -->

- [ ] Chunk this into ADRs (I'm ready to formalize)
- [ ] Iterate with me (keep exploring)
- [ ] Structure in place (organize but don't split)

---

## Thread

### Ari (Claude Opus 5.5) - 2026-11-20

No box was ticked; I'm treating this as "Iterate with me". My read of your notes, a recommended shape, and the questions that block it.

**What your notes say, in short.** The three areas have three different user models:

| Area | Users | Shape |
|---|---|---|
| Workout | Kay only | Single-user. Coach needs to get smarter (separate topic). |
| Kitchen | Kay + 2 roommates | Shared household. Recipe inboxes and language differ per person. Must be light: short setup, few tokens. |
| Restaurants | Kay; others ask Kay for recs | Barely used. Redesign (separate topic). |

Only one cross-area link must survive: suggest-what-to-cook reads training (if available) and inventory.

**The big consequence: recipes move to kitchen.** Today recipes live in food-journal next to restaurants, kept together because the dish catalog joins them (decision "Restaurants and recipes stay in one server and one database"). Your notes put recipes on the kitchen side (per-person inboxes, suggest-what-to-cook), and the dish-catalog link isn't on your must-keep list. So that decision gets reversed. What would move from food-journal (35 tools) to kitchen-inventory (8 tools): saved recipes (save/update/get/list_saved_recipes) and probably home cooks (log/update/delete_home_cook, which suggest-what-to-cook uses for "cooked recently"). Restaurants, visits, lists, and the dish catalog stay in food-journal.

**Recommended shape: one repo = one plugin = one area.**

| Repo | Becomes | Skills | Users |
|---|---|---|---|
| kitchen-inventory | kitchen plugin: inventory + recipes + home cooks | manage-kitchen-inventory, clip-recipe, suggest-what-to-cook | multi-user |
| workout-log | workout plugin | coaching skill (to design) | Kay only |
| food-journal | restaurants plugin, after recipes leave | suggest-where-to-eat (to redesign) | Kay only for now |
| personal-ai-system | sunset; the story and map move to your website | none | none |

- The suggest-what-to-cook → training link stays a **skill-level** link: the skill calls workout-log's tools if that connector is installed, and skips training if not. No server talks to another server. Your roommates get the same skill without training.
- Only kitchen needs the multi-user work (user_id, per-user tests). Workout and restaurants need just a single owner token, because **all three servers are open today**.
- Unplaced skills: check-nutrition (your macros; workout plugin?) and log-food (splits: home cooks → kitchen, dine-out → restaurants).

**Auth facts (checked 2026-11-20 against the Claude Code and connector docs):**
- Claude Code plugins can send a per-user bearer token: `userConfig` with `"sensitive": true` prompts on enable, stores it in the OS credential store, and the plugin's MCP config uses `"Authorization": "Bearer ${user_config.<name>}"`. Setup for a roommate: install the plugin, paste one token. Short.
- **That token path works only in Claude Code** (terminal, or the Code tab of the desktop app). In claude.ai chat, desktop chat, and mobile, plugin skills load, but remote servers connect as connectors, which need OAuth. The only alternative there, org-wide `static_headers`, is a shared, not per-user, beta.
- Token cost: Claude Code loads MCP tools on demand by default (tool search), so tool count costs little there. Skill length matters more. Reply language per person is a built-in Claude Code setting (`"language"` in their own settings).

**The friction I want to raise.** Kitchen is a phone activity: a photo of the grocery haul, checking the fridge. Once kitchen-inventory requires a token, **your current Claude-app connector stops working**, and the roommates can't use it from their phones either, unless the server supports OAuth. So the real choice for kitchen is:
- **A, token only**: everyone uses Claude Code on a laptop. Least work; no phone.
- **B, OAuth via Neon Auth**: works in the app, on the phone, and in Claude Code, with one auth path for everyone. Checked 2026-11-20 (neon.com/docs/auth/guides/plugins/oauth-provider): Neon's Managed Better Auth has an OAuth provider plugin built to protect MCP servers. It supports Client ID Metadata Documents, which Claude's connectors accept (`oauth_cimd`), so no per-client setup. The work: enable Auth on the Neon project; host a login page and a consent page on an https domain (none are provided); make the Python server return 401 with protected-resource metadata and verify each token's signature, `iss`, and `aud`; map the token's user (`sub`) to `user_id`. Neon's examples are TypeScript; the servers use the Python `mcp` SDK, whose token-verifier support I still need to confirm for the pinned version.

Leaning B: it covers the phone and removes the separate token path. A only if you want the multi-user data model first and auth after.

**Questions for you:**
1. Phone: do you and your roommates need kitchen from the phone (A or B above)?
yes

2. Inventory: one shared fridge list for the household, or does each item have an owner (mine / yours / shared)? Or both?
one shared

3. Language: does the data's language matter too? If one roommate adds "鸡蛋" and you add "eggs", that's two items unless something normalizes names.
they should count as the same thing

4. Home cooks: move them to kitchen with recipes (my lean), or stay in food-journal?
just mark recipes as cooked

5. Your app setup: workout and restaurants stay Kay-only. Keep using them from the Claude app (owner token or OAuth for you alone), or move to Claude Code?
keep using from claude app

6. Order: kitchen first (it has the users waiting), then coach and restaurants as their own seeds?
yes

---

**Model Response Request:**

- [ ] Chunk this into ADRs
- [ ] Iterate with me
- [ ] Structure in place

### Kay - 2026-11-20

Answers inline above (1–6).

### Ari (Claude Opus 5.5) - 2026-11-20

**What's settled by your answers:**
- Kitchen: OAuth (phone matters). One shared inventory for the household. Recipes per person. No home-cook journal on the kitchen side: a recipe gets marked cooked (with a date, so "cooked recently" still works).
- Workout and restaurants: Kay only, from the Claude app. The Claude app needs OAuth for any authenticated connector, so **all three servers get OAuth**, not just kitchen. On the Kay-only servers, the server accepts only your account.
- Order: kitchen first.

**Two new findings (checked 2026-11-20):**
1. **One Neon Auth issuer can self-onboard only one MCP server.** The OAuth provider takes a single `mcp.resource`, and CIMD (what Claude's connectors use) works only for that resource. Three servers means three issuers: Auth enabled on each server's own Neon project or branch. Kay signs in once per server; roommates only on kitchen.
2. **Your Neon org already has a `personal-ai-auth` project**, created 2026-10-15 and idle since. Was that a start on this? Also: I see projects for kitchen (`my-fridge-inventory`) and workout (`workout-tracker`), but none for food-journal. Where does its database live?

**Same item across languages.** Two model runs could disagree on whether "葱" is "scallion" or "green onion", so per the layer rule, the match belongs in code; only the translation is a judgment. Options for the ADR:
- **A, canonical name + aliases**: each item has one canonical name (English) and stored aliases in any language. The tool takes the name as said plus the model's canonical guess; the server matches exactly on canonical or alias, and adds the spoken name as an alias. kitchen-inventory already uses `difflib` for near matches; this extends it.

- **B, the model normalizes, nothing stored**: cheaper, but the next run may pick a different English word and create a duplicate.
- Leaning A.

why so complicated? right now it supports multiple languages already

**Proposed ADRs when you tick "Chunk":**
- **0001 Split by area**: one repo = one plugin = one area; recipes move from food-journal to kitchen (reverses "Restaurants and recipes stay in one server"); suggest-what-to-cook reads training only if that connector is present; personal-ai-system sunsets into your website.
- **0002 Auth: OAuth through Neon Auth on all three servers**: one issuer per server, login and consent pages (where hosted: open), Kay-only allowlist on workout and food-journal, how the Python server verifies tokens.
- **0003 Kitchen multi-user data model**: `user_id` on recipes, shared inventory, cooked marker on recipes, cross-language item names, migrating your existing rows to your user.
- Later, as their own seeds: smarter workout coach, restaurant redesign, the personal website.

---

**Model Response Request:**

- [x] Chunk this into ADRs
- [ ] Iterate with me
- [ ] Structure in place

### Kay - 2026-11-20

Inline above: "why so complicated? right now it supports multiple languages already"

### Ari (Claude Opus 5.5) - 2026-11-20

You're right; I proposed it without reading the code. kitchen-inventory already handles this: `add_item` asks for the everyday name (in practice English), other-language names can sit in `details`, and every add or miss lists similar items, matching by words, spelling, or a name found in details ("皮蛋" finds century eggs). The model then merges into the existing row. That works the same with three users as with one. **Cross-language names: no change**; dropped from ADR 0003. If roommates start creating duplicates in practice, revisit then.

Still open from my last entry: the `personal-ai-auth` Neon project (earlier start on this?) and where food-journal's database lives.

### Kay - 2026-11-20 (in chat)

1. `personal-ai-auth` was an earlier attempt at auth; it didn't work out.
2. food-journal has its own database, `kayfoodlab`, inside the same Neon project as kitchen (`my-fridge-inventory`). kitchen-inventory uses the default `neondb` database.

### Ari (Claude Opus 5.5) - 2026-11-20

What this changes:
- **Auth placement.** Neon Auth is configured per branch, and one branch's issuer can self-onboard only one MCP server. kitchen and food-journal share a project, so they can't both use its default branch's issuer. But the issuer doesn't have to live next to the data: a server only verifies tokens from whatever issuer it's configured with. So the ADR can put each server's issuer wherever is cleanest, e.g. kitchen on `my-fridge-inventory`, food-journal on `personal-ai-auth` (reused), workout on `workout-tracker`.
- **Recipe move is simpler.** Recipes go from `kayfoodlab` to `neondb` inside the same project: a table copy, not a cross-provider migration.
- **The earlier attempt matters for ADR 0002.** Whatever stopped `personal-ai-auth` (pages? token verification in Python? the Claude connector not completing sign-in?) is the risk to plan around. Neon's OAuth provider docs were updated 2026-11-06, after that attempt, and CIMD is now on by default; that may be what was missing.

### Kay - 2026-11-20 (in chat)

Separate kitchen and food-journal into two Neon projects. In the future, food-journal may be open to the public with view access.

### Ari (Claude Opus 5.5) - 2026-11-20

Agreed; it fits the split. Recorded for ADR 0001:
- **Order matters.** Recipes first move from `kayfoodlab` to kitchen's `neondb` (same project, simple copy). Then `kayfoodlab`, now restaurants only, moves to its own new Neon project. Moving it first would mean copying recipes across projects later.
- **Each server owns its own Neon project and its own auth issuer.** That also resolves the one-issuer-per-branch limit without borrowing `personal-ai-auth`. I'd start the new project fresh rather than reuse `personal-ai-auth`, which may hold half-finished config from the earlier attempt; delete it once nothing uses it (your call).
- **Public view access changes food-journal's auth later, not now.** It would mean reads without sign-in and writes for Kay only. It also raises what the public may see: recommendations and places, probably not your visits, ratings, or notes. That goes in the restaurant-redesign seed. For now: Kay-only, but keep reads and writes as separate checks so opening reads later is a small change.

---

**Model Response Request:**

- [ ] Chunk this into ADRs
- [ ] Iterate with me
- [ ] Structure in place

### Kay - 

---

## Derived Into

- ADR-0001: [Split the system by area](0001-split-the-system-by-area.md)
- ADR-0002: [OAuth through Neon Auth on all three servers](0002-oauth-through-neon-auth.md)
- ADR-0003: [Kitchen multi-user data model](0003-kitchen-multi-user-data-model.md)

Not processed here, by design (each gets its own seed): smarter workout coach, restaurant redesign (including public read access), the personal website.

<!-- MODEL INSTRUCTIONS: When this seed is processed, the AI should update this section with:
- ADR-NNNN: Brief title
- ADR-NNNN: Brief title

If anything in the seed remains unprocessed, make a note of what has note been processed yet at the end of this section.
-->
