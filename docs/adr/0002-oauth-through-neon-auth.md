# ADR-0002: OAuth through Neon Auth on all three servers

- **Date**: 2026-11-20
- **Iteration**: 3
- **Status**: Draft
- **Deciders**: Kay (decides), Ari (Claude Opus 5.5, recommends)
- **Source**: [seed-2026-11-20-separating-the-system](seed-2026-11-20-separating-the-system.md)

**TL;DR**: Every server requires a signed-in user through OAuth, with Neon Auth as the issuer and sign-in by an emailed code. Each server has its own issuer and serves its own login and consent pages. Each server allowlists its users (the household for kitchen, Kay for the others) and closes sign-ups in Neon. Step 0 proved it end to end from the Claude iPhone app.

---

## Context

- **All three servers are open today.** Anyone with a URL can read and write.
- **Users connect from different places.** Kay and the roommates need kitchen from the phone. Kay uses workout and restaurants from the Claude app.
- **Facts checked 2026-11-20:**
  - Claude app, web, and mobile connectors authenticate with OAuth. They accept Client ID Metadata Documents (`oauth_cimd`); static headers are an org-wide shared beta, not per user. Source: claude.com/docs/connectors/building/authentication.
  - Claude Code supports a per-user token through plugin `userConfig`, but only in Claude Code, so it can't cover the phone.
  - Neon's Managed Better Auth has an OAuth provider plugin made for MCP servers, with CIMD on by default. Each branch has one issuer and one `mcp.resource`, and CIMD works only for that resource. You host the login and consent pages yourself; none are provided. Source: neon.com/docs/auth/guides/plugins/oauth-provider (updated 2026-11-06).
- **An earlier attempt failed.** Kay started one in Neon project `personal-ai-auth` (2026-10-15), and it didn't work out. What stopped it is unknown (QST-PRIOR-ATTEMPT: B).
- **Today's plugin** (`.mcp.json` in this repo) sends only URLs from env vars, no credentials.
- **Step 0 ran on kitchen, 2026-11-20.** Report: `kitchen-inventory/docs/agent-tasks/14-oauth-step-0-report.md` on its `auth-spike` branch. The spike was torn down afterward.
  - **Google sign-in failed inside the Claude iPhone app**: after Google, Neon's callback returned `State integrity check failed`. It worked from claude.ai in desktop Chrome and from Claude Code, and the phone app could then use the connector. Root cause not found. That may be what stopped the earlier attempt, but nothing confirms it.
  - **Sign-in by emailed code worked inside the iPhone app**, with `whoami` and `list_inventory` working. Every sign-in call is a `fetch` from our own page, so nothing depends on cookies on Neon's domain.
  - **The pages must use Neon's browser client, `@neon/auth`.** Hand-written calls to the issuer never saw the session, because Neon's cookies are `Partitioned` and the client does a session hand-off they skip.
  - **Closing sign-ups:** Neon's `disable_sign_up` blocks new emails (no code sent, no user created) while existing users still sign in. It does **not** block Google sign-ups.
  - **SDK:** `mcp>=1.17` serves the metadata and takes a token verifier, so no custom middleware is needed. Neon's OAuth server works on a child branch, and CIMD needed no setup.

## Decision

1. **One auth path for every surface: OAuth via Neon Auth.** No separate token setup.
2. **One issuer per server**, each in that server's own Neon project ([ADR-0001](0001-split-the-system-by-area.md)).
3. **The server verifies every request.** It returns 401 with protected-resource metadata when there's no token. It checks each access token's signature (JWKS), `iss` (exact), and `aud` (contains the server's URL), then maps `sub` to a user. Every query is scoped server-side. No tool takes a user argument.
4. **Kay-only servers check the user.** workout-log and food-journal accept only Kay's account. Reads and writes are separate checks, so food-journal can open reads to the public later.
5. **Rollout is one server at a time.** Kitchen goes first. Turning auth on breaks the existing connector until Kay re-adds it and signs in, so each switch is a planned step.
6. **food-journal's upload endpoint keeps `IMPORT_TOKEN`.** It isn't an MCP route.
7. **Each server serves its own `/login` and `/consent` pages** on its Render URL, added as a trusted domain on its issuer (QST-PAGES-HOST: A). The pages use Neon's browser client, `@neon/auth`, not hand-written calls (step 0).
8. **Sign in with a code sent by email** (Neon's email OTP). No Google, and no passwords (QST-SIGNIN-AFTER-SPIKE: B, which supersedes QST-SIGNIN-METHOD).
9. **Two locks on who may use a server** (QST-WHO-MAY-SIGN-UP: C): an allowlist of user ids per server in an env var, checked in code and covered by tests (the guarantee), and sign-ups closed in Neon with `disable_sign_up` once the allowed people have registered (reduces junk accounts; step 0 confirmed it works for email sign-ups).

### Step 0, before the first build prompt (done 2026-11-20)
Because the earlier attempt's failure is unknown (QST-PRIOR-ATTEMPT: B), step 0 is the test, and a failure stops the work and comes back here. Results are under Context. Google sign-in failed in the iPhone app and came back here as QST-SIGNIN-AFTER-SPIKE.
- Confirm that the Python `mcp` SDK can serve protected-resource metadata and plug in a token verifier. Kitchen pins `mcp[cli]>=1.2,<2`, and the version may need raising. If it can't, use a small middleware that does the 401 and the verification.
- Confirm how Google sign-in is set up in Neon Auth (shared development credentials or Kay's own Google OAuth client) and whether sign-ups can be closed.
- Prove one server end to end before building pages for all three: sign in with Google from the Claude app on the phone, call one tool, and see the user id.

---

## Questions

### QST-PRIOR-ATTEMPT: What stopped the `personal-ai-auth` attempt?
- Status: answered
- Why asking: if the same wall is still there (for example, the Claude connector never finishing sign-in), this plan hits it too. Neon's docs changed on 2026-11-06, so it may be gone.
- Need: pick a letter (or override — any shape answers)

Options:
- **A — Kay remembers**: write down what failed, and step 0 tests that point first.
- **B — Unknown**: step 0's end-to-end proof is the test. If it fails, stop and come back here before building more.

**Recommendation**: (by Ari, Claude Opus 5.5, 2026-11-20)
**A — Kay remembers**, if possible. Rationale: a known failure point turns step 0 into one targeted check.
Confidence: 0.5, because it depends on memory. If wrong: B costs only one more failed attempt, caught early.

**ANS:** (by kayc26)
b

---

### QST-PAGES-HOST: Where do the login and consent pages live?
- Status: answered
- Why asking: Neon requires both pages on an https domain you control, added as a trusted domain. Without them nobody can sign in.
- Need: pick a letter (or override — any shape answers)

Options:
- **A — Each server serves its own**: `/login` and `/consent` on the server's Render URL. One deploy, one domain per server, no new hosting.
- **B — One small shared site**: for example on GitHub Pages or the future personal website, used by all three issuers.
- **C — The personal website**: wait for it.

**Recommendation**: (by Ari, Claude Opus 5.5, 2026-11-20)
**A — Each server serves its own.** Rationale: the pages are tiny (a sign-in form and an approve button), each issuer is separate anyway (decision 2), and it adds no new deploy target. C blocks kitchen on a website that doesn't exist.
Confidence: 0.7, because serving static pages from the Python server is easy, but I haven't checked the trusted-domain and cookie behaviour across Render and Neon domains. If wrong: if cross-site cookies break sign-in from the server's domain, B on one domain set up for it.

**ANS:** (by kayc26)
a

---

### QST-SIGNIN-METHOD: How do people sign in?
- Status: superseded — by QST-SIGNIN-AFTER-SPIKE (step 0: Google sign-in fails inside the Claude iPhone app)
- Why asking: the roommates sign in on their phones, so it has to be painless. Some methods need extra setup (a Google OAuth app, an email sender).
- Need: pick a letter (or override — any shape answers)

Options:
- **A — Email and password**: works with no extra setup. People manage one more password.
- **B — Google sign-in**: one tap on a phone. It needs a Google OAuth client set up in Neon Auth.
- **C — Email code or magic link**: no password. It needs an email provider configured.

**Recommendation**: (by Ari, Claude Opus 5.5, 2026-11-20)
**A — Email and password** to start. Rationale: nothing else to configure, and sign-in happens once per connector, with refresh tokens lasting 30 days.
Confidence: 0.6, because I haven't checked whether Neon offers Google sign-in with shared development credentials, which would make B just as cheap. If wrong: if Google sign-in needs no app setup, B.

**ANS:** (by kayc26)
b, neon offers google sign in

---

### QST-WHO-MAY-SIGN-UP: How does each server limit who can use it?
- Status: answered
- Why asking: if anyone can sign up on kitchen's issuer, a stranger gets a valid token and lands in the household's shared inventory.
- Need: pick a letter (or override — any shape answers)

Options:
- **A — Allowlist in the server**: an env var of allowed user ids per server. Anyone else gets "not allowed" even with a valid token.
- **B — Close sign-ups in Neon**: after the household (or Kay) has registered, disable sign-ups. Not yet checked whether Neon Auth supports this.
- **C — Both**.

**Recommendation**: (by Ari, Claude Opus 5.5, 2026-11-20)
**C — Both**, with A as the guarantee. Rationale: the layer rule puts who-may-access in code. A is testable in the server's suite; B only reduces junk accounts.
Confidence: 0.8, because A is simple and fully under our control. If wrong: if Neon can't close sign-ups, A alone still holds.

**ANS:** (by kayc26)
c

---

### QST-SIGNIN-AFTER-SPIKE: Google sign-in fails in the iPhone app. What now?
- Status: answered
- Why asking: step 0 found that Google sign-in breaks inside the Claude iPhone app at Neon's callback (`State integrity check failed`), even with Neon's own browser client. The roommates connect from their phones.
- Need: pick a letter (or override — any shape answers)

Options:
- **A — Keep Google, sign in once on a computer**: works today from claude.ai in Chrome or from Claude Code, and the phone app then uses the connector. Someone with only a phone can't connect. Sign-in lasts while the connector is used at least every 30 days.
- **B — Sign in with an emailed code**: Neon's email OTP. The user types an email address, then a 6-digit code. Every call is a `fetch` from our page, which avoids the failing step completely. It drops Google.
- **C — Keep Google, add a same-origin proxy**: our server relays Neon's auth calls, copying Neon's Next.js session hand-off in Python. That flow is undocumented, Neon's guidance says not to re-implement it, and it may not fix the iPhone failure, since the cause isn't known.

**Recommendation**: (by Ari, Claude Opus 5.5, 2026-11-20)
**B — Sign in with an emailed code**, if anyone using it may have only a phone. Rationale: it removes the step that fails, instead of working around it, and uses only documented Neon features. A is free but leaves phone-only users out. C costs the most, and its fix isn't proven.
Confidence: 0.7, because B was untested when recommended. If wrong: if email codes fail in the iPhone app too, A, and go back to C only if phone-only sign-in is a must.

**ANS:** (by kayc26, 2026-11-20)
b

---

### QST-EMAIL-SENDER: Who sends the sign-in codes?
- Status: answered
- Why asking: Neon's shared sender (`auth@mail.myneon.app`) worked in step 0 with no setup, but Neon recommends your own email provider for production. A roommate whose code goes to spam can't sign in.
- Need: pick a letter (or override — any shape answers)

Options:
- **A — Neon's shared sender**: nothing to set up. Emails come from Neon's address with Neon's template and may land in spam. Sign-in happens rarely, since refresh tokens last 30 days.
- **B — Your own email provider (SMTP)**: for example Resend or a Gmail app password, configured per issuer. Emails come from your address. It needs an account and per-branch setup.

**Recommendation**: (by Ari, Claude Opus 5.5, 2026-11-20)
**A — Neon's shared sender** to start. Rationale: step 0 showed it works, the household is a few people, and each person signs in about once a month at most.
Confidence: 0.6, because I haven't checked the shared sender's limits or how its emails fare with school and Gmail spam filters. If wrong: if a roommate's code doesn't arrive or keeps landing in spam, B.

**ANS:** (by kayc26)
a

---

## Iterations

### Iteration 1 — 2026-11-20
- **Trigger**: seed chunked into ADRs.
- **Contributors**: Kay, Ari (Claude Opus 5.5).
- **Changes**: first draft; four questions.
- **Outcome**: Draft. Kay answered all four (PRIOR-ATTEMPT B, PAGES-HOST A, SIGNIN-METHOD B, WHO-MAY-SIGN-UP C).

### Iteration 2 — 2026-11-20
- **Trigger**: Kay's answers.
- **Contributors**: Kay, Ari (Claude Opus 5.5).
- **Changes**: Decision gains 7–9 (pages per server, Google sign-in, allowlist plus closed sign-ups). Step 0 now treats the unknown earlier failure as the test and checks Google sign-in setup. Context notes today's plugin `.mcp.json`.
- **Outcome**: Draft. No open questions remain in this ADR; the next step is step 0 on kitchen.

### Iteration 3 — 2026-11-20
- **Trigger**: step 0 on kitchen (prompt #14). Google sign-in failed inside the Claude iPhone app; email-code sign-in worked.
- **Contributors**: Kay, Ari (Claude Opus 5.5, in the kitchen-inventory session).
- **Changes**: Context gains the step-0 results. Decision 7 requires `@neon/auth` in the pages. Decision 8 changes from Google to an emailed code. Decision 9 confirms `disable_sign_up` works for email sign-ups. QST-SIGNIN-METHOD is superseded by QST-SIGNIN-AFTER-SPIKE (Kay: B, given in the session). New QST-EMAIL-SENDER.
- **Outcome**: Draft. One open question (QST-EMAIL-SENDER). The next step is the kitchen build prompt, written from the step-0 report.
