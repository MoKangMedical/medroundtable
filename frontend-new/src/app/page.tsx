import Link from 'next/link';
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

export default function Home({
  searchParams,
}: {
  searchParams?: { error?: string; details?: string };
}) {
  const errorMessage = getErrorMessage(searchParams?.error, searchParams?.details);

  return (
    <main style={{ minHeight: '100vh', padding: '40px 16px' }}>
      <div style={{ margin: '0 auto', maxWidth: 1240, display: 'grid', gap: 24 }}>
        <section
          style={{
            background: 'rgba(255,255,255,0.82)',
            border: '1px solid rgba(148,163,184,0.22)',
            borderRadius: 32,
            boxShadow: '0 24px 48px rgba(15,23,42,0.08)',
            padding: 32,
          }}
        >
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 20, justifyContent: 'space-between', alignItems: 'flex-end' }}>
            <div style={{ maxWidth: 760 }}>
              <div style={{ color: '#1d4ed8', fontSize: 12, fontWeight: 800, letterSpacing: '0.22em', textTransform: 'uppercase' }}>
                SecondMe OAuth Gateway
              </div>
              <h1 style={{ margin: '14px 0 0', fontSize: 48, lineHeight: 1.05, fontWeight: 800 }}>
                把 SecondMe 登录、角色选择和
                <span style={{ color: '#1d4ed8' }}> MedRoundTable 圆桌</span>
                真正接起来
              </h1>
              <p style={{ margin: '18px 0 0', color: '#475569', fontSize: 18, lineHeight: 1.8 }}>
                这里负责承接 OAuth 登录，然后把用户带到可执行的角色选择页，再把选择结果带回正式站
                `https://mokangmedical.github.io/medroundtable` 的创建流程。
              </p>
            </div>
            <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
              <a
                href="/api/auth/login"
                style={{
                  padding: '14px 20px',
                  borderRadius: 999,
                  background: 'linear-gradient(135deg, #1d4ed8, #1e3a8a)',
                  color: '#fff',
                  fontWeight: 700,
                }}
              >
                使用 SecondMe 登录
              </a>
              <Link
                href="https://mokangmedical.github.io/medroundtable/frontend/secondme-hub.html"
                style={{
                  padding: '14px 20px',
                  borderRadius: 999,
                  border: '1px solid rgba(148,163,184,0.22)',
                  background: '#fff',
                  fontWeight: 700,
                }}
              >
                先用静态协作页体验
              </Link>
            </div>
          </div>

          {errorMessage ? (
            <div
              style={{
                marginTop: 24,
                padding: 16,
                borderRadius: 20,
                background: '#fef2f2',
                border: '1px solid #fecaca',
                color: '#b91c1c',
                fontWeight: 600,
              }}
            >
              {errorMessage}
            </div>
          ) : null}

          <div style={{ marginTop: 24, display: 'grid', gap: 16, gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))' }}>
            {quickScenarios.map((scenario) => (
              <article
                key={scenario.id}
                style={{
                  borderRadius: 28,
                  background: 'linear-gradient(180deg, rgba(255,255,255,0.94), rgba(239,246,255,0.96))',
                  border: '1px solid rgba(148,163,184,0.18)',
                  padding: 20,
                }}
              >
                <div style={{ color: '#1d4ed8', fontSize: 12, fontWeight: 800, letterSpacing: '0.16em', textTransform: 'uppercase' }}>
                  Quick Scenario
                </div>
                <h2 style={{ margin: '10px 0 0', fontSize: 24, fontWeight: 800 }}>{scenario.title}</h2>
                <p style={{ margin: '10px 0 0', color: '#475569', lineHeight: 1.8 }}>{scenario.description}</p>
              </article>
            ))}
          </div>
        </section>

        <section style={{ display: 'grid', gap: 20, gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))' }}>
          <div
            style={{
              background: 'rgba(15,23,42,0.94)',
              color: '#fff',
              borderRadius: 32,
              padding: 24,
              boxShadow: '0 24px 48px rgba(15,23,42,0.18)',
            }}
          >
            <div style={{ color: '#bae6fd', fontSize: 12, fontWeight: 800, letterSpacing: '0.16em', textTransform: 'uppercase' }}>
              Human Roles
            </div>
            <h2 style={{ margin: '12px 0 0', fontSize: 30, fontWeight: 800 }}>真人研究者加入方式</h2>
            <div style={{ marginTop: 18, display: 'grid', gap: 12 }}>
              {humanRoles.map((role) => (
                <div key={role.id} style={{ borderRadius: 24, background: 'rgba(255,255,255,0.08)', padding: 16 }}>
                  <div style={{ fontWeight: 800 }}>{role.name}</div>
                  <div style={{ marginTop: 4, fontSize: 13, color: '#cbd5e1', fontWeight: 700 }}>{role.subtitle}</div>
                  <div style={{ marginTop: 8, fontSize: 14, lineHeight: 1.8, color: '#e2e8f0' }}>{role.description}</div>
                </div>
              ))}
            </div>
          </div>

          <div
            style={{
              background: 'rgba(255,255,255,0.84)',
              border: '1px solid rgba(148,163,184,0.22)',
              borderRadius: 32,
              padding: 24,
            }}
          >
            <div style={{ color: '#0f766e', fontSize: 12, fontWeight: 800, letterSpacing: '0.16em', textTransform: 'uppercase' }}>
              SecondMe Shades
            </div>
            <h2 style={{ margin: '12px 0 0', fontSize: 30, fontWeight: 800 }}>可带入的分身模板</h2>
            <div style={{ marginTop: 18, display: 'grid', gap: 12 }}>
              {shadeTemplates.map((shade) => (
                <div key={shade.id} style={{ borderRadius: 24, background: '#fff', border: '1px solid rgba(148,163,184,0.18)', padding: 16 }}>
                  <div style={{ fontWeight: 800 }}>{shade.name}</div>
                  <div style={{ marginTop: 4, fontSize: 13, color: '#64748b', fontWeight: 700 }}>{shade.subtitle}</div>
                  <div style={{ marginTop: 8, fontSize: 14, lineHeight: 1.8, color: '#475569' }}>{shade.description}</div>
                </div>
              ))}
            </div>
          </div>

          <div
            style={{
              background: 'rgba(255,255,255,0.84)',
              border: '1px solid rgba(148,163,184,0.22)',
              borderRadius: 32,
              padding: 24,
            }}
          >
            <div style={{ color: '#7c3aed', fontSize: 12, fontWeight: 800, letterSpacing: '0.16em', textTransform: 'uppercase' }}>
              AI Packs
            </div>
            <h2 style={{ margin: '12px 0 0', fontSize: 30, fontWeight: 800 }}>首轮 AI 协作底盘</h2>
            <div style={{ marginTop: 18, display: 'grid', gap: 12 }}>
              {aiPacks.map((pack) => (
                <div key={pack.id} style={{ borderRadius: 24, background: '#fff', border: '1px solid rgba(148,163,184,0.18)', padding: 16 }}>
                  <div style={{ fontWeight: 800 }}>{pack.name}</div>
                  <div style={{ marginTop: 8, fontSize: 14, lineHeight: 1.8, color: '#475569' }}>{pack.subtitle}</div>
                </div>
              ))}
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}
