# MedRoundTable 第二阶段上架资料

这份资料用于 `https://develop.second.me/store/list` 的应用上架，以及 Integration 提审前的字段核对。

## 1. 提交文件

- Integration manifest: [secondme-integration-manifest.json](/Users/linzhang/Desktop/%20%20%20%20%20%20OPC/medroundtable-fixes/secondme-integration-manifest.json)
- App listing JSON: [secondme-app-listing.json](/Users/linzhang/Desktop/%20%20%20%20%20%20OPC/medroundtable-fixes/secondme-app-listing.json)

## 2. 上架口径

- App Name: `MedRoundTable`
- Display Name: `临床科研圆桌会`
- Subtitle: `14 位医学科研 Agent 驱动的临床研究协作入口`
- Category: `Medical / Research / AI Collaboration`
- 一句话说明: `把真人研究者、SecondMe 登录身份、14 位医学科研 Agent 和公开数据库入口放进同一条协作流。`

## 3. 公开链接

- Website: `https://mokangmedical.github.io/medroundtable/index.html`
- Login: `https://medroundtable-secondme.vercel.app/api/auth/login`
- MCP Endpoint: `https://medroundtable-secondme.vercel.app/api/mcp`
- Support: `https://medroundtable-secondme.vercel.app/support`
- Privacy Policy: `https://medroundtable-secondme.vercel.app/privacy`

## 4. OAuth 信息

- Client ID: `19b5f08b-2256-41aa-b196-2f98491099f7`
- Redirect URIs:
  - `https://medroundtable-secondme.vercel.app/api/auth/callback`
  - `http://localhost:3000/api/auth/callback`
- Scopes:
  - `profile`
  - `email`
  - `shades:read`
  - `softmemory:read`

## 5. Integration 口径

- skill.key: `medroundtable-research-copilot`
- MCP auth mode: `bearer_token`
- 可调用工具:
  - `triage_research_question`
  - `build_roundtable_plan`
  - `list_agent_roster`
  - `search_public_databases`
  - `get_platform_snapshot`

## 6. 审核时的亮点

- 真人登录后，可以把身份回填到主页和圆桌流程。
- 14 位 Agent 不是纯展示，能直接按问题进行分诊。
- MCP 工具暴露了圆桌计划、专家名册、公开数据库和平台快照。
- GitHub Pages 和 Vercel 分工清晰，演示路径短。

## 7. 仍需平台侧回填

这些字段在本地仓库里只能先留占位，提交前需要在 SecondMe 后台确认：

- External App 的平台 `appId`
- 商店截图的最终 CDN URL
- 若平台要求，Integration 的最终 `releaseVersion`
- 若平台要求，商店最终 `iconUrl` / `ogImageUrl`

## 8. 当前部署状态

- `websiteUrl`: live
- `loginUrl`: live
- `mcpEndpoint`: live
- `supportUrl`: live
- `privacyPolicyUrl`: live
