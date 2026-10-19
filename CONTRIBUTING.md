# Contributing

Every member is questioned on their own code, so authorship must be clear in
the git history.

## Branches

- One branch per member: `member1`, `member2`, `member3`.
- `main` holds only reviewed, merged work. Never commit directly to `main`.

```bash
git checkout main && git pull
git checkout member1            # first time: git checkout -b member1
git merge main                  # bring in teammates' merged work
```

## What you may commit

- Commit **only your own files**. The owner of every file is written in its
  header (`Owner: memberN`) and in every stub (`TODO(memberN)`). The
  README flow table lists them too.
- Replace `TODO(memberN)` comments as you implement them, so leftover TODOs
  are easy to find with `git grep "TODO(member1)"`.
- Shared files (`main.cpp`, `pins.h`, `topics.h`, `backend/src/topics.ts`,
  `docs/topics.md`, `README.md`, `docker-compose.yml`) change only
  through a pull request that every member has seen.
- Need a change in someone else's file? Open an issue or ask them. Do not edit it yourself.
- Never commit secrets: `firmware/include/secrets.h` and `backend/.env` are gitignored.
- Adding a dependency (npm package or PlatformIO library) needs team agreement first.

## Merging to main

1. Push your branch: `git push -u origin member1`.
2. Open a pull request `member1 → main`.
3. At least one other member reviews it.
4. Merge, then everyone runs `git merge main` into their own branch.

## Commit messages

Use a short prefix and the flow name, e.g. `feat(dht): publish readings every 5s`,
`fix(timer): validate minutes`, `docs(topics): define light levels`.
