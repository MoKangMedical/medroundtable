# MedRoundTable 快速发布

正式展示站点是 `https://medroundtable.cn/`，分析观察台是 `https://medroundtable.cn/real-analysis.html`。

```bash
gh auth status
git status -sb
git push origin main

curl -fsS https://medroundtable.cn/api/health
curl -fsS https://medroundtable.cn/api/v1/relay/health
curl -fsSI https://medroundtable.cn/real-analysis.html
```

服务器发布、验收和回滚见 [DEPLOYMENT.md](DEPLOYMENT.md)。
