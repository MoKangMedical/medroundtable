---
name: medroundtable-research-copilot
description: Use when the user wants to triage a clinical research question, choose the right MedRoundTable expert, build a roundtable kickoff plan, or find suitable public biomedical databases before entering MedRoundTable.
---

# MedRoundTable Research Copilot

MedRoundTable is a clinical research collaboration copilot built for SecondMe and OpenClaw discovery.

It is designed for users who want to:

- decide which of the 14 medical research agents should enter first
- turn a clinical question into a concrete roundtable kickoff plan
- bring a real researcher identity, SecondMe context, and AI agent roster into one workflow
- find matching public biomedical databases before starting deeper analysis

## When To Use This Skill

Trigger this skill when the user asks any of the following:

- 这个临床问题先找谁讨论
- 帮我判断这个课题值不值得做
- 先生成一个圆桌启动方案
- 我该用哪些公开数据库
- 哪位 Agent 最适合这个研究问题
- 帮我把问题带回 MedRoundTable

## What This Skill Can Do

This integration exposes the following MCP tools:

1. `triage_research_question`
   Purpose: recommend the first expert, suggest the opening move, and assemble a SecondMe-aware kickoff roster.

2. `build_roundtable_plan`
   Purpose: generate a MedRoundTable kickoff plan and a handoff URL that can be taken back to the live site.

3. `list_agent_roster`
   Purpose: inspect all 14 medical research agents by team, specialty, and question type.

4. `search_public_databases`
   Purpose: match a topic with suitable public biomedical databases and a recommended expert.

5. `get_platform_snapshot`
   Purpose: return a compact snapshot of MedRoundTable's experts, databases, and capability lanes.

## Runtime Rules

- MCP endpoint: `https://medroundtable-secondme.vercel.app/api/mcp`
- Auth mode: `bearer_token`
- Tool calls require `Authorization: Bearer <SecondMe access token>`
- The integration resolves the current SecondMe user before generating user-scoped handoff output

## Live Links

- Website: `https://mokangmedical.github.io/medroundtable/index.html`
- Login: `https://medroundtable-secondme.vercel.app/api/auth/login`
- MCP: `https://medroundtable-secondme.vercel.app/api/mcp`
- Support: `https://medroundtable-secondme.vercel.app/support`
- Privacy: `https://medroundtable-secondme.vercel.app/privacy`

## Handoff Behavior

The expected workflow is:

1. the user signs in with SecondMe
2. this skill chooses the best starting expert or database path
3. MedRoundTable builds a kickoff plan
4. the user returns to the live MedRoundTable site to continue the roundtable, uploads, analysis, and export flow

## Notes For Review

- This is a focused MCP surface, not the whole MedRoundTable product
- The goal is quick research triage and handoff, not full report generation inside the skill
- The integration is intentionally small so it is easy for OpenClaw and SecondMe users to discover and invoke
