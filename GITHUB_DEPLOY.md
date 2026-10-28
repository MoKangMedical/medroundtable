# MedRoundTable GitHub 发布指南

- 仓库：`https://github.com/MoKangMedical/medroundtable`
- 生产分支：`main`
- 正式站：`https://medroundtable.cn/`

```bash
gh auth status
git fetch origin main
git status -sb
git add <本次修改的文件>
git commit -m "Describe the production change"
git push origin main
```

GitHub 只保存代码与文档。不得提交 `.env`、Token、API Key、relay SQLite、Windows 审计日志或原始科研数据。

推送后由正式 Ubuntu 服务器拉取 `main`，并按 [DEPLOYMENT.md](DEPLOYMENT.md) 验收 `medroundtable.cn`。
