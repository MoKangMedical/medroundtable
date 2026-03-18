# AGENTS.md

## Scope

These instructions apply to the repository rooted at `/Users/linzhang/Desktop/      OPC/medroundtable`.

## Project Snapshot

- This repo is a mixed codebase, not a single-framework app.
- The current live entry points are split across:
  - `server.js`: lightweight Express API for uploads, file listing, and simple analysis helpers.
  - `backend/main.py`: FastAPI app with roundtable, agent, database, and analysis routes.
  - `frontend/` and root-level `.html` files: static/demo UI assets.
  - `frontend-new/`: a newer Next.js-style frontend subtree for OAuth-related work.
- The top-level `README.md` is only partially aligned with the actual repository layout. Verify behavior from code before making structural assumptions.

## Working Rules

- Prefer small, targeted changes. Do not restructure the repository unless the task explicitly requires it.
- Check whether the requested work belongs to `server.js`, `backend/`, `frontend/`, `frontend-new/`, or static HTML before editing.
- Preserve existing Chinese product language in user-facing copy unless the task asks for a rewrite.
- Treat root `.env`, `.env.production`, `frontend-new/.env.local`, and database files as sensitive. Do not print secrets into summaries or new docs.
- Note: some sensitive files are currently tracked by Git. Do not remove or rewrite repository history unless the user explicitly asks.

## Common Commands

### Git

```bash
git status --short --branch
git pull --ff-only
git checkout -b codex/<task-name>
```

### Node API

```bash
npm install
npm run dev
# or
npm start
```

Default Express port: `3001` unless overridden by `PORT`.

### FastAPI

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 backend/main.py
```

Default FastAPI port: `8000`.

### Docker

```bash
docker-compose up -d
docker-compose logs --tail=200
```

## High-Risk Areas

- `docker-compose.yml` currently contains real-looking credentials and secrets. Avoid copying them into commits, issues, or chat summaries.
- Root-level deployment scripts and platform config files (`vercel.json`, `render.yaml`, `railway.toml`, `zeabur.toml`, shell scripts) affect production or previews; edit only when the task is deployment-related.
- `medroundtable.db`, `data/`, `uploads/`, and temporary analysis outputs may contain local runtime state. Avoid committing new generated artifacts.

## Change Checklist

Before finishing a task:

1. Confirm you edited the correct app surface.
2. Run the narrowest relevant validation you can.
3. Report any unverified areas explicitly.
4. Check `git diff --stat` so accidental large changes are caught early.

## Preferred Update Flow

For future Codex-driven work on this repo:

1. Pull latest `main`.
2. Create a branch named `codex/<short-task-name>`.
3. Make the requested change.
4. Run targeted validation.
5. Summarize the diff and any remaining risks.
6. Commit and push only when the user explicitly asks for it.
