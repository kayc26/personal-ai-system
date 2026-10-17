---
name: "clip-recipe"
description: "Clip a recipe into Kay's food journal from the page she's on or anything she shares: RedNote, NYT, blogs, YouTube, screenshots, cookbook photos. Use for get, save, or clip this recipe, 存这个食谱."
---

# Clip Recipe

Kay finds recipes on RedNote (XHS, 小红书), NYT Cooking, Serious Eats, blogs, YouTube,
and cookbooks. She should be able to open Claude on any of them, say "get the recipe",
and have it saved with nothing else to do. You know what to collect; don't ask her
for it.

This skill only saves recipes. Logging a cook, answering "which recipes have I tried",
and statuses after cooking belong to log-food. "What should I cook" belongs to
suggest-what-to-cook.

## What to collect

Everything `save_recipe` takes:

| Field | What goes in |
|---|---|
| `title` | The recipe's or post's own title, as written |
| `url` | The page URL (for RedNote, the full URL including its token) |
| `source` | nyt, seriouseats.com, xhs, youtube, a book name, the blog's domain |
| `dish` | The generic dish (see "Naming") |
| `name_zh` | The Chinese name, when there is one |
| `aliases` | Other name forms you searched with `find_dish` |
| `cuisine`, `dish_family` | Inferred, never asked (see "Cuisine") |
| `ingredients` | 4 to 8 main ingredients: lowercase, singular, English, no amounts |
| `techniques` | Comma-separated, e.g. braise, sear, simmer |
| `recipe` | The full recipe text, whenever you can read it (see step 2) |
| `why` | Only if she says why, in her words |
| `note` | What's missing or uncertain about the clip (see step 4) |

## Step 1: Read the recipe, best source first

Stop at the first source that gives the whole recipe (ingredients and steps).

**In Chrome (she's on the page):**

1. **Structured recipe data.** Most recipe sites (NYT Cooking, Serious Eats, Bon
   Appétit, most blogs) embed a schema.org Recipe block. Run this on the page:

   ```js
   (() => {
     const found = [];
     const walk = n => {
       if (!n || typeof n !== 'object') return;
       if (Array.isArray(n)) return n.forEach(walk);
       const t = n['@type'];
       if (t === 'Recipe' || (Array.isArray(t) && t.includes('Recipe'))) found.push(n);
       if (n['@graph']) walk(n['@graph']);
     };
     document.querySelectorAll('script[type="application/ld+json"]')
       .forEach(s => { try { walk(JSON.parse(s.textContent)); } catch (e) {} });
     const r = found[0];
     if (!r) return null;
     const steps = x => typeof x === 'string' ? [x]
       : Array.isArray(x) ? x.flatMap(steps)
       : x && x.itemListElement ? steps(x.itemListElement)
       : x && x.text ? [x.text] : [];
     return JSON.stringify({ name: r.name, yield: r.recipeYield,
       totalTime: r.totalTime, ingredients: r.recipeIngredient,
       steps: steps(r.recipeInstructions) });
   })()
   ```

   Because this runs in her logged-in Chrome, paywalled sites she subscribes to work.

2. **RedNote post data.** On xiaohongshu.com, run:

   ```js
   (() => {
     const id = location.pathname.split('/').pop();
     let n = null;
     try {
       const m = window.__INITIAL_STATE__?.note?.noteDetailMap;
       const e = m && (m[id] || Object.values(m)[0]);
       n = e?.note || null;
     } catch (e) {}
     const text = sel => document.querySelector(sel)?.innerText?.trim() || '';
     return JSON.stringify({
       title: n?.title || text('#detail-title'),
       caption: n?.desc || text('#detail-desc'),
       type: n?.type || (document.querySelector('video') ? 'video' : 'normal'),
       images: n?.imageList?.length ?? null,
       url: location.href
     });
   })()
   ```

   Drop trailing hashtags (`#…[话题]#`) from the caption; keep everything else.
   If this returns nothing, read the page text instead.

3. **Carousel images.** If the caption has no ingredient list or no steps (e.g.
   "配方在图里"), the recipe is in the images. Click through the slides, take a
   screenshot of each, zoom in where text is small, and transcribe the ones with
   ingredients or steps. Photos with no recipe text are fine to skip; say so in `note`.

4. **Page text.** For anything else, read the page text and pick out the recipe.

5. **Video.** You can't watch a video. For a RedNote video post, save what the caption
   gives and put "video: steps not in caption" in `note`, then offer: "Save the video
   and send it here if you want the full recipe." For YouTube, save what the title
   and description give, and if the steps aren't there, put "video: steps not in
   description" in `note`.

If a script fails (logged out, blocked, page changed), don't retry it. Move to the next
source, and if nothing works, ask her for screenshots and the link.

**Outside Chrome (she shares something in chat):**
- A link: read the page if it opens. RedNote links rarely do; ask for screenshots of
  the cover and the ingredient and step images, plus the caption (long-press to copy).
- A paywalled link (NYT Cooking, ATK) that won't open: don't stall. Save from the
  title and URL slug, which is enough for the dish, put "link only: paywalled" in
  `note`, and say "Open it in Chrome and say 'get the recipe' to fill it in." Clipping
  the same link again fills blanks instead of duplicating.
- Screenshots or pasted text: use them as the source.
- A cookbook: a photo of the page, or the title and book.

## Step 2: Store the full text whenever you can read it

Fill `recipe` whenever you got the recipe, from any source, NYT and Serious Eats
included. Other parts of the system read it: the Sunday shopping list checks every
ingredient against the inventory, and suggest-what-to-cook gives her the recipe in chat
when she cooks. Links break, posts get deleted, and subscriptions lapse. It's her
private archive for her own cooking.

Leave it empty only when you couldn't read the recipe (a paywalled link outside
Chrome, a video with nothing in the caption). Then put "link only" and the reason in
`note`, so the gap is visible later.

When you fill it: yield and total time on the first line if the source gives them,
then every ingredient with its amount, then the numbered steps, in the source's own
words and language. Transcribe faithfully. Don't rewrite, translate, or fill gaps. If
an amount isn't shown, leave it out rather than guess.

## Step 3: Name it and check for a repeat

**Naming.** Name the dish at the level where different versions are still the same
dish, so versions collect under one name. The recipe's full title goes in `title`; the
generic dish goes in `dish` (NYT "Miso-Glazed Salmon With Scallions" is miso salmon).
Drop modifiers that describe one version (cuts, brands, "grandma's"). Keep what makes
it a different dish: the main ingredient when it changes the dish, and established
names for distinct dishes (东坡肉 is not 红烧肉). A twist is a variation, not a new
dish (可乐红烧肉 is 红烧肉).

**Repeat check.** Call `find_dish` for each name form, up to 3 calls: the English name,
the Chinese name, and the original-language name if different. Pass the forms you
searched as `aliases`. If a close match exists, ask one quick question: "Same as
[dish]?" If `save_recipe` returns `created_new_dish: true`, show the closest matches
and confirm it's really new; if she picks an existing dish, fix it with
`update_saved_recipe` (field `dish`).

**Cuisine.** The country or well-known regional cuisine (Thai, Sichuan, Yunnan,
Levantine). Reuse labels already in use (`get_explored` with `cuisine`). Never ask;
show it in the confirmation so she can correct it.

**Ingredients.** The protein, the base, and the ingredients that define the flavor.
Skip salt, oil, water, and generic aromatics unless central. Grades and brands don't go
in the tags.

## Step 4: Save and confirm

Call `save_recipe`. In `note`, record what the clip couldn't get, so she knows before
she cooks: which source it came from if not the whole page ("caption only"), missing
amounts, ingredients used in the steps but not in the list, image or video content not
transcribed. Leave `note` empty when the clip is complete.

Confirm in one line, saying whether the full recipe is stored or it's link only, then
flag gaps and the new-dish question if there is one:
"Saved: 夏威夷果煮鸡 (macadamia chicken soup, Yunnan, XHS): chicken, macadamia,
guanciale, ginger. Full recipe stored; only the guanciale has an amount."
If the response says `already_saved`, say so; it filled blanks instead of duplicating.

## Style
Short and fast. Match her language (Chinese, English, or mixed).