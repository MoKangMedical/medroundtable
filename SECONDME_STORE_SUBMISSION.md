# MedRoundTable 第二阶段上架资料

这份资料用于 `https://develop.second.me/store/list` 的应用上架，以及 Integration 提审前的字段核对。

## 1. 提交文件

- Integration manifest: [secondme-integration-manifest.json](/Users/linzhang/Desktop/%20%20%20%20%20%20OPC/medroundtable-fixes/secondme-integration-manifest.json)
- App listing JSON: [secondme-app-listing.json](/Users/linzhang/Desktop/%20%20%20%20%20%20OPC/medroundtable-fixes/secondme-app-listing.json)

## 2. 上架口径

- App Name: `MedRoundTable-临床科研圆桌会`
- Listing Slug: `medroundtable`
- Subtitle: `3 步把真人、分身与 14 位医学科研 Agent 带进同一场圆桌`
- Category: `health`
- Tags:
  - `medical-research`
  - `clinical-study`
  - `multi-agent`
  - `secondme`
  - `openclaw`
- Developer Name: `MoKangMedical`
- 一句话说明: `先登录真人身份，再选分身与 AI 阵容，最后把圆桌计划回填到正式站直接开始讨论。`
- 详细说明:
  - `MedRoundTable 面向临床科研协作场景，把真人研究者、SecondMe 分身、14 位医学科研 Agent 和公开数据库入口收成一条短路径。`
  - `登录完成后，用户只需再做一次分身与 AI 选择，就能把协作阵容带回主站开始圆桌、上传材料和继续分析。`

## 3. 公开链接

- App URL: `https://medroundtable-secondme.vercel.app/`
- Website: `https://mokangmedical.github.io/medroundtable/`
- Login: `https://medroundtable-secondme.vercel.app/api/auth/login`
- MCP Endpoint: `https://medroundtable-secondme.vercel.app/api/mcp`
- Support: `https://medroundtable-secondme.vercel.app/support`
- Privacy Policy: `https://medroundtable-secondme.vercel.app/privacy`

## 4. OAuth / App 信息

- Client ID: `19b5f08b-2256-41aa-b196-2f98491099f7`
- App ID: `19b5f08b-2256-41aa-b196-2f98491099f7`
- Redirect URIs:
  - `https://medroundtable-secondme.vercel.app/api/auth/callback`
  - `http://localhost:3000/api/auth/callback`
- Allowed Scopes:
  - `user.info`
  - `user.info.shades`
  - `user.info.softmemory`
  - `chat`
  - `note.add`
  - `voice`

## 5. Integration 口径

- skill.key: `mokang-medroundtable-research-copilot`
- MCP auth mode: `bearer_token`
- oauth.appId: `19b5f08b-2256-41aa-b196-2f98491099f7`
- 可调用工具:
  - `triage_research_question`
  - `build_roundtable_plan`
  - `list_agent_roster`
  - `search_public_databases`
  - `get_platform_snapshot`

## 6. 审核时的亮点

- 演示路径只有 3 步：登录真人身份、选择分身与 AI、带回主站开始圆桌。
- 真人登录后，可以把身份回填到主页和圆桌流程。
- 14 位 Agent 不是纯展示，能直接按问题进行分诊。
- MCP 工具暴露了圆桌计划、专家名册、公开数据库和平台快照。
- GitHub Pages 和 Vercel 分工清晰，审核页里能直接走完一轮真实演示。

## 7. 商店截图

- `https://mokangmedical.github.io/medroundtable/assets/secondme-store/secondme-login-portal.png`
  - 用途：展示登录入口与 3 步流
- `https://mokangmedical.github.io/medroundtable/assets/secondme-store/secondme-collaboration-hub.png`
  - 用途：展示 Step 2 的分身与 AI 配置页
- `https://mokangmedical.github.io/medroundtable/assets/secondme-store/secondme-home-handoff.png`
  - 用途：展示回到主页后的真人协作入口

## 8. 仍需平台侧回填

这些字段在本地仓库里只能先留占位，提交前需要在 SecondMe 后台确认：

- External App 的平台 `appId`
- 若平台要求，Integration 的最终 `releaseVersion`
- 若平台要求，商店最终 `iconUrl` / `ogImageUrl`

## 9. 当前部署状态

- `websiteUrl`: live
- `loginUrl`: live
- `mcpEndpoint`: live
- `supportUrl`: live
- `privacyPolicyUrl`: live
