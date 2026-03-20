export default function PrivacyPage() {
  return (
    <main style={{ minHeight: '100vh', background: '#f8fafc', padding: '48px 16px' }}>
      <div style={{ margin: '0 auto', maxWidth: 920, background: '#fff', borderRadius: 28, padding: 32, boxShadow: '0 18px 40px rgba(15,23,42,0.08)' }}>
        <div style={{ color: '#2563eb', fontSize: 12, fontWeight: 800, letterSpacing: '0.18em', textTransform: 'uppercase' }}>
          Privacy Policy
        </div>
        <h1 style={{ margin: '12px 0 0', fontSize: 40, lineHeight: 1.08 }}>MedRoundTable 隐私说明</h1>
        <p style={{ marginTop: 18, color: '#475569', lineHeight: 1.9, fontSize: 16 }}>
          MedRoundTable 主要用于医学科研协作、SecondMe 身份回填、Agent 分诊和研究流程启动。我们只收集完成这些能力所必需的数据，
          不会把 OAuth 凭证暴露给公开页面，也不会把用户的私人研究内容用于公开训练。
        </p>
        <div style={{ marginTop: 24, display: 'grid', gap: 18 }}>
          <section>
            <h2 style={{ fontSize: 22 }}>我们处理哪些信息</h2>
            <p style={{ color: '#475569', lineHeight: 1.9 }}>
              登录后，我们可能接收并存储 SecondMe 返回的昵称、头像、邮箱，以及用户在圆桌里主动填写的研究标题、临床问题、上传文件和分析结果。
            </p>
          </section>
          <section>
            <h2 style={{ fontSize: 22 }}>这些信息用来做什么</h2>
            <p style={{ color: '#475569', lineHeight: 1.9 }}>
              用于把真人成员、SecondMe 分身和 AI 阵容带入同一场圆桌；用于保存研究上下文、导出方案草稿，以及把公开数据库与分析任务组织到一个持续会话里。
            </p>
          </section>
          <section>
            <h2 style={{ fontSize: 22 }}>数据保存与删除</h2>
            <p style={{ color: '#475569', lineHeight: 1.9 }}>
              当前黑客松演示版本以最小存储为原则。用户可以通过站内清除身份、删除草稿或联系开发团队申请移除相关数据。
            </p>
          </section>
          <section>
            <h2 style={{ fontSize: 22 }}>联系</h2>
            <p style={{ color: '#475569', lineHeight: 1.9 }}>
              如需反馈隐私相关问题，请通过支持页联系：<a href="/support" style={{ color: '#2563eb', fontWeight: 700 }}>Support</a>。
            </p>
          </section>
        </div>
      </div>
    </main>
  );
}
