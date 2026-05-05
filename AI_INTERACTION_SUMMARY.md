# AI Interaction Summary

**Tool:** Claude Code (Anthropic)

---

I used Claude Code throughout the entire project — from planning to deployment. 

## How I Approached It

Before writing any code, I asked Claude to present a clear plan for the entire project and explain how we should approach it. I specifically requested to work
 **step by step, one page and one feature at a time**, so I could understand and approve each decision before moving forward. I did not ask Claude to generate the whole project at once.
I also asked Claude to explain the important parts of each file **before** creating it — not after. 
This meant every router, model, service, and component was explained to me first, and I gave explicit approval before it was written.

## Planning and Technical Decisions

Before starting the database layer, I asked Claude to explain the tradeoffs between different options so I could make informed decisions:
- **Database:** I asked about SQLite vs. PostgreSQL.
 We agreed to use SQLite locally and PostgreSQL in production, with SQLAlchemy as the ORM so the same code runs against both using a single environment variable.
- **CSS:** I chose plain CSS over Tailwind to keep things simple and readable.
- **Authentication:** We discussed JWT vs. session-based auth and I chose JWT for its stateless simplicity.

## Tests

I asked for tests at every layer, not just at the end. I specifically requested three separate groups of backend tests:
1. **API tests** — covering signup, login, onboarding, dashboard, and voting through the full HTTP stack
2. **Service tests** — testing each external API integration (CoinGecko, CryptoPanic, OpenRouter, Reddit) and their fallback mechanisms independently
3. **Model tests** — verifying database constraints such as duplicate email prevention and the unique vote constraint
For the frontend, I asked for a complete test suite covering all main user flows: auth redirects, error message display, loading states, onboarding form validation, 
dashboard rendering, vote button behavior, and protected route access. This resulted in 26 frontend tests across 6 files using Vitest and Testing Library.
In total the project has **66 tests** (40 backend, 26 frontend).

## Reusable Skill
After we built the first external API service, I noticed we were repeating the same pattern — try the live API, fall back to static data on failure. 
I asked Claude to create a **reusable Claude Skill** for this pattern so it would be documented and consistent across all four services.
 The skill was saved as `/add-api-service` in the project's `.claude/commands/` folder.

## Full Code Walkthrough

After the project was complete and deployed, I asked Claude to walk me through the entire codebase file by file — not to make changes, but to fully understand what every file does, why it exists, and how it connects to everything else.
We went through each file in order: the React entry point (`main.jsx`, `App.jsx`), the auth context and route guard, every page component and its form, every backend router, every service, and every database model. For each file I wanted to know: who calls it, what does it call, what data travels between them, and how it connects to the database.
This session gave me a complete mental model of the project — I can now trace any user action from a button click all the way to the database and back.

## Bugs Found During Testing

During manual testing I caught several issues and brought them to Claude to fix:
- **CORS error on signup** — the backend only allowed `localhost:3000` but Vite runs on `localhost:5173`.
 I reported the "Failed to fetch" error and Claude identified the cause.
- **Vote buttons reset on refresh** — I noticed that thumbs up/down votes didn't persist across page reloads.
 The votes were being saved to the database but not returned to the frontend. 
 I raised this and we added a `votes` dict to the dashboard response and an `initialVote` prop to the VoteButtons component.
- **Login error flashing and disappearing** — after deploying, I noticed that a login error appeared for a split second and then disappeared. 
Claude had introduced a 401 redirect handler that was too aggressive — it was firing on wrong-password errors too, causing a full page reload.
 I reported it and we scoped the redirect to only fire when a token already exists (expired session).
- **Vercel 404 on page refresh** — refreshing any route returned a 404 because Vercel looks for a matching file instead of serving `index.html`. 
I reported this and Claude added a `vercel.json` rewrite rule.
- **Signup form looked frozen during cold start** — the server wake-up warning that existed on the login form was missing from the signup form. The screen appeared stuck with no feedback. The same 4-second timer and warning message was added to the signup form.

This workflow allowed me to stay in control of the architecture and implementation while using AI as a tool for acceleration, validation, and structured thinking — rather than as a code generator.