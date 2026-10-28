# 将 MedRoundTable 更新到 GitHub

```bash
cd /path/to/medroundtable
gh auth status
git fetch origin main
git status -sb
git add <本次修改的文件>
git commit -m "Update MedRoundTable production"
git push origin main
```

不使用带 Token 的 remote URL，不使用 `git push --force`。推送完成后验证：

```bash
curl -fsS https://medroundtable.cn/api/health
curl -fsSI https://medroundtable.cn/
curl -fsSI https://medroundtable.cn/real-analysis.html
```
