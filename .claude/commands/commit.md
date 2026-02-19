---
allowed-tools:
  - Bash(git status:*)
  - Bash(git diff --cached:*)
  - Bash(git add:*)
  - Bash(git commit:*)
  - Bash(git log:*)
  - Bash(git branch:*)
  - Bash(git checkout:*)
  - Bash(git push:*)

description: Create a git commit on the current branch according to our git styleguide (no branch creation)
---

# Agent Guide: Prepare and Create a Commit (Current Branch)

> **Use this when you want to commit directly to the current branch.**
> For creating a new branch first, use `/commit-branch` instead.

## 0) General Rules
- Use **Conventional Commits + emoji** format:
  `<emoji> <type>(<scope>): <short summary>`
  Example: `✨ feat(auth): add refresh token rotation`
- **Short summary ≤ 72 chars**, no period at the end.
- The body should briefly explain **why** and **what** changed; add `BREAKING CHANGE: ...` if applicable.
- Commit **only relevant** changes (exclude IDE artifacts, `.env`, caches, etc.).

## 1) Run quality gates **before** committing
1. Ruff (format + lint):
   ```bash
   # If Ruff formatter is enabled:
   ruff format .
   # Lint and auto-fix simple issues:
   ruff check . --fix
   ```

## 2) Compose the commit message
Decide on **type** and **scope** (see table). Craft a concise summary (**what**), and write a short body explaining **why/how**.
If there are API changes or incompatibilities, add:

```
BREAKING CHANGE: <brief description and migration notes>
```

### Commit message template
```
<emoji> <type>(<scope>): <short summary>

<why/what/how — 1–3 short paragraphs; bullet points if helpful>
- <key change 1>
- <key change 2>

Refs: <issue/PR links or IDs>
```

### Create the commit
```bash
git commit -m "<emoji> <type>(<scope>): <short summary>" -m "<body>"
```

## 3) Types and emojis

| Type     | Emoji | Use for                                | Example headline                                         |
|----------|-------|----------------------------------------|----------------------------------------------------------|
| feat     | ✨    | New feature / behavior change          | `✨ feat(parser): support CSV delimiter option`          |
| fix      | 🐞    | Bug fix                                | `🐞 fix(auth): handle expired refresh token`             |
| docs     | 📝    | Docs, README, comments                 | `📝 docs(readme): add setup section`                     |
| refactor | ♻️    | Code restructuring w/o behavior change | `♻️ refactor(api): extract service layer`                |
| perf     | ⚡    | Performance improvements               | `⚡ perf(query): add composite index`                    |
| test     | ✅    | Tests, fixtures                        | `✅ test(user): add repository edge cases`               |
| chore    | 🧹    | Maintenance, configs, no logic changes | `🧹 chore(repo): update pre-commit hooks`                |
| build    | 🛠️    | Build system, dependencies             | `🛠️ build: bump sqlalchemy to 2.0.35`                   |
| ci       | 🤖    | CI/CD pipelines                        | `🤖 ci: add pytest cache artifact`                       |
| style    | 🎨    | Formatting / style (no logic)          | `🎨 style: reorder imports with ruff`                    |

> **scope** — a concrete module/layer/service, e.g., `auth`, `user`, `api`, `db`, `bot`, `course`, `infra`, `ci`, `docs`, etc.

## 4) Good summary rules
- Imperative mood verbs: *add*, *fix*, *update*, *remove*, *refactor*, *adjust*.
- No trailing period; keep to ≤ 72 characters.
- Avoid vague phrases like "minor fixes", "small changes".

## 5) Commit body (when needed)
- Explain **why** the change is needed; **what** exactly changed; **side effects**.
- For bug fixes — include reproduction conditions.
- For perf/refactor — mention motivation/metrics/scope of impact.
- Add `Refs: #123` or a link to the ticket when applicable.

## 6) Post-commit (optional)
- If on a feature/fix branch and you plan a PR, push the branch:
  ```bash
  git push --set-upstream origin "$(git branch --show-current)"
  ```

---

### Quick checklist for the agent
1. **Inspect changes**: `git status`, commit only staged files.
2. **Quality gates**: `ruff format .` → `ruff check . --fix`. If failing → fix, then rerun.
3. **Message**: `<emoji> <type>(<scope>): <short summary>` + body and `BREAKING CHANGE` if needed.
4. **Commit**: `git commit -m ... -m ...`.
5. **Push** (if you plan a PR): `git push -u origin <branch>`.
