# Phase 2 comparison + ScientistOne + ARS design QA

## Scope and truth sources

- Prototype: `frontend/phase2-comparison.html`, opened locally at `http://127.0.0.1:3000/phase2-comparison.html`.
- Existing-product visual baseline: `frontend/index.html` and the supplied desktop captures under `02_产品截图与演示资产/`.
- Direction 1 reference: `/Users/linzhang/.codex/generated_images/019f6e68-3a4f-78c3-b009-a7844cbcf26b/exec-cfd3d9ec-81a6-49e0-a1a8-473e4143a05f.png`.
- Direction 2 reference: `/Users/linzhang/.codex/generated_images/019f6e68-3a4f-78c3-b009-a7844cbcf26b/exec-bc02f128-acd8-4e82-828e-66d6e49033b1.png`.
- Direction 3 reference: `/Users/linzhang/.codex/generated_images/019f6e68-3a4f-78c3-b009-a7844cbcf26b/exec-3dd65617-c921-4426-adf8-84dd3630f5f8.png`.
- ScientistOne reference: `/var/folders/q4/db4kwpwx2kl8s8vc3n81f7d80000gp/T/codex-clipboard-00e6ed5e-7800-4f61-ab27-1825266bca70.png`.
- ARS source specification: `/Users/linzhang/.codex/attachments/0cf7581e-bdd6-4742-9f02-53b9df55e8bc/pasted-text.txt` and [official Codex package](https://github.com/Imbad0202/academic-research-skills-codex).

All displayed records are clearly labelled as simulated research examples. The comparison UI makes no request to a Windows data root, Ollama, or a remote platform.

## Render and interaction validation

- Desktop viewport: `1280 x 720`; no horizontal overflow in each of the five views.
- Direction 1 — guided discussion: verified initial discussion layout and the `确认并进入本地计算` action. The action locked the decision card, advanced the stage to local computation, and created the simulated local-run request.
- Direction 2 — evidence-to-data: verified the three-column evidence / analysis-plan / local-result layout, local validation completion, and decision-record state.
- Direction 3 — mission control: verified the four work packages, selection of `WP-04`, reviewer handoff, and the one-way `发起复核` -> `复核已发起` state.
- ScientistOne — evidence-chain workflow: verified `载入当前圆桌`, generation of the simulated research brief, parallel branch evaluation, best-branch selection, four CoE audit checks, and handoff to roundtable review.
- ARS — academic research skills: verified five route cards, workflow detail switching, `载入 academic-pipeline`, Material Passport state, and Socratic 5-round start action.
- Navigation: the five side-rail entries switch the active view and URL hash; the original `frontend/index.html` includes `Phase 2 工作区对比`, `ScientistOne 证据链`, and `ARS 学术研究技能` entry points.
- Browser console: no error-level messages after exercising the primary flows.

## Visual comparison

Comparison used matching desktop states, with the reference and the rendered prototype supplied together for review:

| View | Focused regions checked | Result |
| --- | --- | --- |
| Direction 1 | stage timeline, discussion chronology, decision card, local-analysis side panel | Passed — retains the established navy rail, cobalt interaction color, pale-blue work surface, white cards, and expert-avatar language. |
| Direction 2 | the critical three-column evidence-to-plan-to-result workspace, validation call-to-action, reviewable conclusion | Passed — the most information-dense view keeps all three research objects visible without horizontal scrolling. |
| Direction 3 | work-package cards, ownership/status treatment, human-review panel | Passed — task orchestration remains visually distinct from the directed discussion while retaining the same product system. |
| ScientistOne | three-lane workflow, evidence ledger, parallel branch cards, CoE audit gate | Passed — the reference's Problem Investigator / Discovery / Paper Writer & Claim Verifier semantics are translated into the existing MedRoundTable rail, card, pill, and review language. |
| ARS | five workflow routes, Material Passport, Socratic mode, local-source footer | Passed — the external skill package is represented as a clear adapter/router layer without pretending that the full runtime is already installed. |

The first internal draft used a hand-drawn causal diagram. This was removed before the final comparison because it would not satisfy the supplied-asset/icon-library requirement. The final relation matrix is semantic UI rather than a custom graphic and is intentionally simpler than the concept image.

## Final result

final result: passed

No P0, P1, or P2 visual or functional defects remain in the desktop comparison flow. The ScientistOne metrics are explicitly labelled as paper/reference metrics, not platform guarantees. ARS is currently a route/Material Passport UI adapter; full runtime execution remains a Windows Hermes integration task. Future production QA should add real Windows-node API integration tests and a narrow mobile review after the preferred direction is selected.
