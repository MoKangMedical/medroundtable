import { aiPacks, humanRoles, quickScenarios, shadeTemplates } from '../lib/secondme';

function getErrorMessage(error?: string | null, details?: string | null) {
  const messages: Record<string, string> = {
    auth_failed: '登录失败，请重试。',
    no_code: '未收到授权码，请检查回调地址配置。',
    invalid_state: '安全验证失败，请重新发起登录。',
    access_denied: '你取消了授权流程。',
  };

  const base = error ? (messages[error] || '登录失败，请重试。') : '';
  return details ? `${base} (${details})` : base;
}

function SectionLabel({ title, subtitle, tone }: { title: string; subtitle: string; tone: string }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
      <div style={{ color: tone, fontSize: 12, fontWeight: 800, letterSpacing: '0.22em', textTransform: 'uppercase' }}>{title}</div>
      <div style={{ color: '#0f172a', fontSize: 24, fontWeight: 800, lineHeight: 1.2 }}>{subtitle}</div>
    </div>
  );
}

function BulletList({ items }: { items: string[] }) {
  return (
    <div style={{ display: 'grid', gap: 10 }}>
      {items.map((item) => (
        <div key={item} style={{ display: 'flex', alignItems: 'flex-start', gap: 10, color: '#475569', lineHeight: 1.8, fontSize: 15 }}>
          <span style={{ color: '#1d4ed8', fontWeight: 800 }}>•</span>
          <span>{item}</span>
        </div>
      ))}
    </div>
  );
}

export default function Home({
  searchParams,
}: {
  searchParams?: { error?: string; details?: string };
}) {
  const errorMessage = getErrorMessage(searchParams?.error, searchParams?.details);

  return (
    <main
      style={{
        minHeight: '100vh',
        padding: '32px 16px 48px',
        background: 'radial-gradient(circle at top left, rgba(59,130,246,0.16), transparent 30%), radial-gradient(circle at 85% 12%, rgba(14,165,233,0.12), transparent 24%), linear-gradient(180deg, #f8fbff 0%, #eef4ff 100%)',
        color: '#0f172a',
      }}
    >
      <div style={{ margin: '0 auto', maxWidth: 1280, display: 'grid', gap: 22 }}>
        <section
          style={{
            borderRadius: 36,
            padding: 32,
            background: 'rgba(255,255,255,0.84)',
            border: '1px solid rgba(148,163,184,0.22)',
            boxShadow: '0 28px 60px rgba(15,23,42,0.08)',
          }}
        >
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 18, justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div style={{ maxWidth: 760, display: 'grid', gap: 16 }}>
              <div style={{ display: 'inline-flex', alignItems: 'center', gap: 8, width: 'fit-content', padding: '8px 14px', borderRadius: 999, background: 'rgba(219,234,254,0.8)', color: '#1d4ed8', fontSize: 12, fontWeight: 800, letterSpacing: '0.18em', textTransform: 'uppercase' }}>
                SecondMe Login Portal
              </div>
              <h1 style={{ margin: 0, fontSize: 'clamp(36px, 5vw, 58px)', lineHeight: 1.02, fontWeight: 900, letterSpacing: '-0.04em' }}>
                3 步把真人、分身和 AI agent 带进同一场圆桌
              </h1>
              <p style={{ margin: 0, color: '#475569', fontSize: 18, lineHeight: 1.9, maxWidth: 720 }}>
                第 1 步先登录真人身份，第 2 步选这轮要不要带上你的 SecondMe 分身，第 3 步把协作阵容回填到 MedRoundTable 主站，直接开始圆桌讨论。
              </p>
              {errorMessage ? (
                <div style={{ padding: 16, borderRadius: 20, background: '#fef2f2', border: '1px solid #fecaca', color: '#b91c1c', fontWeight: 700, lineHeight: 1.8 }}>
                  {errorMessage}
                </div>
              ) : null}
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 12 }}>
                <a
                  href="/api/auth/login"
                  style={{
                    padding: '14px 20px',
                    borderRadius: 999,
                    background: 'linear-gradient(135deg, #1d4ed8, #1e3a8a)',
                    color: '#fff',
                    fontWeight: 800,
                    boxShadow: '0 18px 36px rgba(29,78,216,0.22)',
                  }}
                >
                  第 1 步：登录 SecondMe 真人身份
                </a>
                <a
                  href="https://mokangmedical.github.io/medroundtable/frontend/secondme-hub.html"
                  target="_blank"
                  rel="noreferrer"
                  style={{
                    padding: '14px 20px',
                    borderRadius: 999,
                    border: '1px solid rgba(148,163,184,0.22)',
                    background: '#fff',
                    fontWeight: 800,
                  }}
                >
                  第 3 步预览：查看协作配置页
                </a>
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 10, alignItems: 'center', marginTop: 4 }}>
                <div style={{ fontSize: 12, fontWeight: 800, letterSpacing: '0.16em', textTransform: 'uppercase', color: '#64748b' }}>
                  Review Assets
                </div>
                {[
                  { href: '/api/mcp', label: 'MCP Endpoint' },
                  { href: '/skill.md', label: 'Skill.md' },
                  { href: '/secondme-integration-manifest.json', label: 'Integration Manifest' },
                  { href: '/secondme-app-listing.json', label: 'Store Listing JSON' },
                ].map((item) => (
                  <a
                    key={item.href}
                    href={item.href}
                    target="_blank"
                    rel="noreferrer"
                    style={{
                      padding: '10px 14px',
                      borderRadius: 999,
                      border: '1px solid rgba(148,163,184,0.22)',
                      background: '#fff',
                      fontWeight: 800,
                      fontSize: 13,
                    }}
                  >
                    {item.label}
                  </a>
                ))}
              </div>
            </div>

            <div
              style={{
                minWidth: 280,
                flex: '1 1 280px',
                borderRadius: 28,
                padding: 20,
                background: 'linear-gradient(180deg, rgba(15,23,42,0.96), rgba(30,64,175,0.96))',
                color: '#fff',
                boxShadow: '0 24px 48px rgba(15,23,42,0.18)',
              }}
            >
              <div style={{ color: '#bae6fd', fontSize: 12, fontWeight: 800, letterSpacing: '0.18em', textTransform: 'uppercase' }}>
                3-Step Demo Flow
              </div>
              <div style={{ marginTop: 12, display: 'grid', gap: 12 }}>
                <div style={{ padding: 14, borderRadius: 20, background: 'rgba(255,255,255,0.08)' }}>
                  <div style={{ fontWeight: 800 }}>1. 登录真人身份</div>
                  <div style={{ marginTop: 6, color: '#cbd5e1', lineHeight: 1.8, fontSize: 14 }}>确认你是谁，姓名、头像和邮箱才能作为真人成员带回主站。</div>
                </div>
                <div style={{ padding: 14, borderRadius: 20, background: 'rgba(255,255,255,0.08)' }}>
                  <div style={{ fontWeight: 800 }}>2. 选择分身与 AI 阵容</div>
                  <div style={{ marginTop: 6, color: '#cbd5e1', lineHeight: 1.8, fontSize: 14 }}>装载你的临床判断、文献记忆或多组学上下文，并指定谁先接手。</div>
                </div>
                <div style={{ padding: 14, borderRadius: 20, background: 'rgba(255,255,255,0.08)' }}>
                  <div style={{ fontWeight: 800 }}>3. 带回主页并开始圆桌</div>
                  <div style={{ marginTop: 6, color: '#cbd5e1', lineHeight: 1.8, fontSize: 14 }}>把真人、分身和 AI pack 一起回填到 MedRoundTable，直接进入讨论。</div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section style={{ display: 'grid', gap: 18, gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))' }}>
          <div
            style={{
              borderRadius: 30,
              padding: 22,
              background: 'rgba(15,23,42,0.96)',
              color: '#fff',
              boxShadow: '0 22px 42px rgba(15,23,42,0.14)',
            }}
          >
            <SectionLabel title="真人入口" subtitle="先选谁来主导圆桌" tone="#bae6fd" />
            <div style={{ marginTop: 16 }}>
              <BulletList items={['研究发起人适合带题目进入。', '共同作者适合多人协作推进。', '证据整合员适合文献和纪要管理。']} />
            </div>
          </div>

          <div
            style={{
              borderRadius: 30,
              padding: 22,
              background: 'rgba(255,255,255,0.9)',
              border: '1px solid rgba(148,163,184,0.22)',
            }}
          >
            <SectionLabel title="SecondMe 分身" subtitle="把你的经验装进去" tone="#0f766e" />
            <div style={{ marginTop: 16 }}>
              <BulletList items={['临床判断分身：把真实判断框架带进来。', '文献记忆分身：持续追踪证据空白。', '多组学分身：稳定承接复杂分析上下文。']} />
            </div>
          </div>

          <div
            style={{
              borderRadius: 30,
              padding: 22,
              background: 'rgba(255,255,255,0.9)',
              border: '1px solid rgba(148,163,184,0.22)',
            }}
          >
            <SectionLabel title="AI 阵容" subtitle="让 agent 按任务分工" tone="#7c3aed" />
            <div style={{ marginTop: 16 }}>
              <BulletList items={['临床五人组：先做立项和 protocol 骨架。', '14 专家阵容：补齐证据和任务分诊。', 'ClawBio 深潜包：处理多组学和代码链路。']} />
            </div>
          </div>
        </section>

        <section
          style={{
            borderRadius: 34,
            padding: 28,
            background: 'rgba(255,255,255,0.84)',
            border: '1px solid rgba(148,163,184,0.22)',
            boxShadow: '0 22px 44px rgba(15,23,42,0.08)',
          }}
        >
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 18, justifyContent: 'space-between', alignItems: 'flex-end' }}>
            <SectionLabel title="Step 3 Shortcuts" subtitle="最常见的 3 条带回主页路径" tone="#1d4ed8" />
            <div style={{ color: '#64748b', fontSize: 14 }}>登录完成后，点任一场景就能直接把阵容回填到主页。</div>
          </div>
          <div style={{ marginTop: 18, display: 'grid', gap: 16, gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))' }}>
            {quickScenarios.map((scenario) => (
              <article
                key={scenario.id}
                style={{
                  borderRadius: 26,
                  border: '1px solid rgba(148,163,184,0.18)',
                  background: 'linear-gradient(180deg, rgba(255,255,255,0.96), rgba(239,246,255,0.98))',
                  padding: 18,
                }}
              >
                <div style={{ color: '#1d4ed8', fontSize: 12, fontWeight: 800, letterSpacing: '0.16em', textTransform: 'uppercase' }}>
                  Scenario
                </div>
                <h2 style={{ margin: '10px 0 0', fontSize: 22, fontWeight: 800 }}>{scenario.title}</h2>
                <p style={{ margin: '10px 0 0', color: '#475569', lineHeight: 1.8 }}>{scenario.description}</p>
              </article>
            ))}
          </div>
        </section>

        <section style={{ display: 'grid', gap: 18, gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))' }}>
          <div style={{ borderRadius: 30, background: 'rgba(255,255,255,0.88)', border: '1px solid rgba(148,163,184,0.22)', padding: 22 }}>
            <SectionLabel title="角色列表" subtitle="真人研究者怎么进入" tone="#1d4ed8" />
            <div style={{ marginTop: 16, display: 'grid', gap: 12 }}>
              {humanRoles.map((role) => (
                <div key={role.id} style={{ borderRadius: 22, background: '#fff', border: '1px solid rgba(148,163,184,0.18)', padding: 16 }}>
                  <div style={{ fontWeight: 800 }}>{role.name}</div>
                  <div style={{ marginTop: 4, color: '#64748b', fontSize: 13, fontWeight: 700 }}>{role.subtitle}</div>
                  <div style={{ marginTop: 8, color: '#475569', lineHeight: 1.8, fontSize: 14 }}>{role.description}</div>
                </div>
              ))}
            </div>
          </div>

          <div style={{ borderRadius: 30, background: 'rgba(255,255,255,0.88)', border: '1px solid rgba(148,163,184,0.22)', padding: 22 }}>
            <SectionLabel title="分身模板" subtitle="SecondMe 会带来什么" tone="#0f766e" />
            <div style={{ marginTop: 16, display: 'grid', gap: 12 }}>
              {shadeTemplates.map((shade) => (
                <div key={shade.id} style={{ borderRadius: 22, background: '#fff', border: '1px solid rgba(148,163,184,0.18)', padding: 16 }}>
                  <div style={{ fontWeight: 800 }}>{shade.name}</div>
                  <div style={{ marginTop: 4, color: '#64748b', fontSize: 13, fontWeight: 700 }}>{shade.subtitle}</div>
                  <div style={{ marginTop: 8, color: '#475569', lineHeight: 1.8, fontSize: 14 }}>{shade.description}</div>
                </div>
              ))}
            </div>
          </div>

          <div style={{ borderRadius: 30, background: 'rgba(255,255,255,0.88)', border: '1px solid rgba(148,163,184,0.22)', padding: 22 }}>
            <SectionLabel title="AI Packs" subtitle="首轮协作底盘" tone="#7c3aed" />
            <div style={{ marginTop: 16, display: 'grid', gap: 12 }}>
              {aiPacks.map((pack) => (
                <div key={pack.id} style={{ borderRadius: 22, background: '#fff', border: '1px solid rgba(148,163,184,0.18)', padding: 16 }}>
                  <div style={{ fontWeight: 800 }}>{pack.name}</div>
                  <div style={{ marginTop: 6, color: '#475569', lineHeight: 1.8, fontSize: 14 }}>{pack.subtitle}</div>
                </div>
              ))}
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}
