export default function SupportPage() {
  return (
    <main style={{ minHeight: '100vh', background: 'linear-gradient(180deg, #eef4ff 0%, #f8fafc 100%)', padding: '48px 16px' }}>
      <div style={{ margin: '0 auto', maxWidth: 960, display: 'grid', gap: 20 }}>
        <section style={{ background: '#0f172a', color: '#fff', borderRadius: 32, padding: 32, boxShadow: '0 24px 52px rgba(15,23,42,0.16)' }}>
          <div style={{ color: '#7dd3fc', fontSize: 12, fontWeight: 800, letterSpacing: '0.18em', textTransform: 'uppercase' }}>
            Support
          </div>
          <h1 style={{ margin: '12px 0 0', fontSize: 40, lineHeight: 1.08 }}>MedRoundTable 支持与问题反馈</h1>
          <p style={{ marginTop: 16, color: '#cbd5e1', lineHeight: 1.9, fontSize: 16 }}>
            如果你在 SecondMe 登录、MCP 调用、圆桌创建、文件上传或数据库分析过程中遇到问题，优先把问题场景、页面链接和报错截图一起发给我们。
          </p>
        </section>

        <section style={{ background: '#fff', borderRadius: 28, padding: 28, boxShadow: '0 18px 40px rgba(15,23,42,0.08)' }}>
          <h2 style={{ margin: 0, fontSize: 24 }}>推荐反馈内容</h2>
          <ul style={{ marginTop: 16, color: '#475569', lineHeight: 1.9 }}>
            <li>你当时访问的页面或功能入口</li>
            <li>希望达成的目标，以及系统现在实际做了什么</li>
            <li>是否使用了 SecondMe 登录，是否带入了分身和 AI 阵容</li>
            <li>浏览器控制台报错、接口返回或截图</li>
          </ul>
        </section>

        <section style={{ background: '#fff', borderRadius: 28, padding: 28, boxShadow: '0 18px 40px rgba(15,23,42,0.08)' }}>
          <h2 style={{ margin: 0, fontSize: 24 }}>联系通道</h2>
          <div style={{ marginTop: 16, display: 'grid', gap: 14 }}>
            <a href="https://github.com/MoKangMedical/medroundtable/issues" target="_blank" rel="noreferrer" style={{ color: '#2563eb', fontWeight: 700 }}>
              GitHub Issues
            </a>
            <a href="https://mokangmedical.github.io/medroundtable/index.html" target="_blank" rel="noreferrer" style={{ color: '#2563eb', fontWeight: 700 }}>
              正式站入口
            </a>
            <a href="https://medroundtable-secondme.vercel.app/" target="_blank" rel="noreferrer" style={{ color: '#2563eb', fontWeight: 700 }}>
              SecondMe 登录入口
            </a>
          </div>
        </section>
      </div>
    </main>
  );
}
