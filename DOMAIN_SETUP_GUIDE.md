# 🌐 MedRoundTable.VIP 域名申请指南

## 📋 域名信息

| 项目 | 内容 |
|------|------|
| **申请域名** | medroundtable.vip |
| **域名后缀** | .vip |
| **用途** | MedRoundTable 医学科研协作平台 |
| **预计费用** | ¥20-50/年（不同平台价格不同） |

---

## 🛒 推荐注册平台（国内可用）

### 方案一：阿里云（推荐 🇨🇳）

**网址**: https://wanwang.aliyun.com/

**优点**:
- ✅ 国内最大域名注册商
- ✅ 备案支持完善
- ✅ 价格透明
- ✅ 解析速度快

**价格**: .vip 域名约 ¥28/年

**注册步骤**:
1. 访问 https://wanwang.aliyun.com/
2. 搜索框输入 `medroundtable.vip`
3. 点击"查域名"
4. 如果显示可注册，点击"立即购买"
5. 创建/登录阿里云账号
6. 完成实名认证（需要身份证）
7. 支付费用
8. 等待审核（通常几分钟到几小时）

---

### 方案二：腾讯云

**网址**: https://dnspod.cloud.tencent.com/

**优点**:
- ✅ 与微信生态整合
- ✅ 解析稳定
- ✅ 支持学生优惠

**价格**: .vip 域名约 ¥25/年

---

### 方案三：GoDaddy（国际）

**网址**: https://www.godaddy.com/

**优点**:
- ✅ 全球最大域名商
- ✅ 服务稳定

**缺点**:
- ❌ 需要国际支付
- ❌ 可能需要翻墙

---

## 🔍 域名查询

### 检查域名是否可用

**方法1: 阿里云查询**
```
https://wanwang.aliyun.com/domain/searchresult/?keyword=medroundtable&vip=1
```

**方法2: 腾讯云查询**
```
https://dnspod.cloud.tencent.com/
```

---

## ⚙️ 域名配置指南

### 步骤1: 注册域名
按上面的步骤在阿里云或腾讯云注册 `medroundtable.vip`

### 步骤2: 配置 DNS 解析

#### 方案 A: 指向 Vercel（推荐）

**在域名管理后台添加以下记录：**

| 记录类型 | 主机记录 | 记录值 | TTL |
|---------|---------|--------|-----|
| A | @ | 76.76.21.21 | 600 |
| CNAME | www | cname.vercel-dns.com | 600 |

**Vercel 项目设置：**
1. 登录 Vercel: https://vercel.com/dashboard
2. 找到 `medroundtable-v2` 项目
3. 点击 Settings → Domains
4. 添加域名 `medroundtable.vip`
5. 等待 DNS 生效（通常几分钟到几小时）

---

#### 方案 B: 指向 GitHub Pages

**在域名管理后台添加以下记录：**

| 记录类型 | 主机记录 | 记录值 | TTL |
|---------|---------|--------|-----|
| A | @ | 185.199.108.153 | 600 |
| A | @ | 185.199.109.153 | 600 |
| A | @ | 185.199.110.153 | 600 |
| A | @ | 185.199.111.153 | 600 |
| CNAME | www | mokangmedical.github.io | 600 |

**GitHub 仓库设置：**
1. 在仓库根目录创建 `CNAME` 文件
2. 文件内容：
   ```
   medroundtable.vip
   ```
3. 提交到 GitHub
4. 等待 DNS 生效

---

#### 方案 C: 使用 Cloudflare CDN（国内加速）

**优势**:
- ✅ 全球 CDN 加速
- ✅ 国内访问更快
- ✅ 免费的 SSL 证书

**配置步骤**:
1. 注册 Cloudflare: https://cloudflare.com
2. 添加站点 `medroundtable.vip`
3. 按提示修改域名 DNS 服务器
4. 在 DNS 设置中添加指向 Vercel/GitHub 的记录
5. 开启 CDN 加速

---

## 📱 快速检查清单

### 注册域名
- [ ] 选择平台（阿里云/腾讯云）
- [ ] 查询域名可用性
- [ ] 注册账号
- [ ] 实名认证
- [ ] 支付费用
- [ ] 等待审核

### 配置 DNS
- [ ] 添加 A 记录
- [ ] 添加 CNAME 记录
- [ ] 在 Vercel/GitHub 添加域名
- [ ] 等待 DNS 生效

### 测试访问
- [ ] 访问 http://medroundtable.vip
- [ ] 访问 http://www.medroundtable.vip
- [ ] 测试移动端访问
- [ ] 分享给朋友测试

---

## 💰 费用预算

| 项目 | 费用 | 周期 |
|------|------|------|
| .vip 域名 | ¥25-30 | 1年 |
| 阿里云解析 | 免费 | - |
| Cloudflare CDN | 免费 | - |
| **总计** | **约 ¥30** | **首年** |

---

## ⚠️ 重要提醒

### 域名实名认证
- 🇨🇳 **国内域名必须实名认证**
- 需要：身份证正反面照片
- 审核时间：几分钟到1天

### 域名备案（如需要）
- 如果服务器在国内，需要 ICP 备案
- Vercel/GitHub Pages 在境外，**无需备案**
- 但如果使用国内 CDN，可能需要备案

### 续费提醒
- 域名每年需要续费
- 建议开启自动续费
- 过期后 30 天内可赎回

---

## 🆘 常见问题

### Q: 域名被注册了怎么办？
**A:** 尝试以下变体：
- medround-table.vip
- medroundtable-ai.vip
- mrt-platform.vip
- med-research.vip

### Q: 配置后无法访问？
**A:** 检查以下：
1. DNS 记录是否正确
2. 等待 DNS 传播（最长48小时）
3. Vercel/GitHub 是否添加了域名
4. 清除浏览器缓存

### Q: 需要备案吗？
**A:** 
- 使用 Vercel/GitHub Pages：**不需要**
- 使用国内服务器：**需要**

---

## 🎯 推荐配置（最优方案）

### 国内用户最佳配置
1. **注册平台**: 阿里云
2. **DNS解析**: 阿里云 DNS + Cloudflare CDN
3. **托管平台**: Vercel
4. **预计费用**: ¥30/年

### 配置后访问地址
```
主域名: https://medroundtable.vip
www域名: https://www.medroundtable.vip
```

---

## 📞 需要帮助？

如果在注册或配置过程中遇到问题：
1. 截图错误信息
2. 告诉我当前进行到哪一步
3. 我会帮你排查解决

---

**现在就去阿里云注册域名吧！** 🚀

**第一步**: 访问 https://wanwang.aliyun.com/

注册完成后告诉我，我帮你配置 DNS！
