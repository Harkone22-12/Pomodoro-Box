# Team rules for AI assistants: Study Station

This is a university project. **Every member is questioned individually on the
code they own**, so an AI assistant must help members learn and must not write
their flow code for them. These rules apply to every session in this repo.

## 1. Know who you are working with

- The current git branch tells you the member: `minh`, `duong`, `hao` (names in the README "Team" table).
- On `main` or any other branch, ask "Which member are you?" before doing any work.
- Ownership of each file is in its header (`Owner: <handle>`) and its stubs
  (`TODO(<handle>)`). The README "Flows" and "Shared foundation" tables list it too.

## 2. Flow code: explain, don't write

In any file marked `TODO(<handle>)` or `Owner: <handle>`:

- **Do not write or complete the implementation**, even when the owner asks.
  That includes filling in stub bodies, pasting a "full solution", or making
  edits that implement the TODO.
- **You may:** explain concepts and library APIs, point to official docs,
  answer questions, review the member's own code and point out bugs (say what
  is wrong and why, and let them write the fix), suggest how to debug, and give
  small generic examples that are not this project's flow (e.g. how `millis()`
  timing works in general, not the DHT publish loop).
- If asked to "just write it", decline briefly, remind them they will be
  questioned on it, and offer to walk through it step by step instead.

## 3. Never touch a teammate's files

- Only work in files owned by the current member.
- If a change is needed in a teammate's file, or in a shared file (`main.cpp`,
  `pins.h`, `topics.h`, `backend/src/topics.ts`, `backend/src/flows/index.ts`,
  `docs/topics.md`, `README.md`, `docker-compose.yml`), describe the change
  for a pull request instead of editing it.

## 4. Contracts are fixed

- MQTT topics and JSON payloads are defined in `docs/topics.md`. Do not invent
  new topics or fields. If one is needed, propose a PR that updates
  `docs/topics.md`, `topics.h` and `topics.ts` together.
- The pin map in `firmware/include/pins.h` changes only via PR. Remember that the
  buzzer is active-LOW and that the LDR must stay on an ADC1 pin.

## 5. Dependencies and secrets

- Never add an npm package or PlatformIO library without the team's
  agreement (see README "Pending dependencies"). Ask first.
- Never read out, print, or commit `firmware/include/secrets.h` or
  `backend/.env`. Use the `.example` files.

## 6. Git

- Follow CONTRIBUTING.md: commit only on the member's own branch, merge to
  `main` only through a pull request, never push to `main` directly.
- Do not commit or push unless the member asks.
