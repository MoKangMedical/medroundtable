import Link from 'next/link';
import { cookies } from 'next/headers';
import { aiPacks, buildHandoffUrl, humanRoles, quickScenarios, shadeTemplates } from '../../lib/secondme';

function readProfile() {
  const raw = cookies().get('secondme_profile')?.value;
  if (!raw) return null;
  try {
    return JSON.parse(decodeURIComponent(raw)) as {
      id?: string;
      name?: string;
      email?: string;
      avatar?: string;
    };
  } catch {
    return null;
  }
}

export default function RoleSelectPage() {
  const profile = readProfile();
  const baseUrl = process.env.MEDROUNDTABLE_WEB_URL || 'https://mokangmedical.github.io/medroundtable';

  return (
    <main style={{ minHeight: '100vh', padding: '40px 16px' }}>
      <div style={{ margin: '0 auto', maxWidth: 1240, display: 'grid', gap: 24 }}>
        <section
          style={{
            background: 'rgba(15,23,42,0.94)',
            color: '#fff',
            borderRadius: 32,
            padding: 32,
            boxShadow: '0 24px 48px rgba(15,23,42,0.18)',
          }}
        >
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 20, justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ maxWidth: 760 }}>
              <div style={{ color: '#bae6fd', fontSize: 12, fontWeight: 800, letterSpacing: '0.22em', textTransform: 'uppercase' }}>
                Logged In With SecondMe
              </div>
              <h1 style={{ margin: '14px 0 0', fontSize: 46, lineHeight: 1.05, fontWeight: 800 }}>
                {profile?.name ? `${profile.name}，现在决定你要以什么身份进入圆桌` : '选择你的进入方式'}
              </h1>
              <p style={{ margin: '18px 0 0', color: '#e2e8f0', fontSize: 18, lineHeight: 1.8 }}>
                OAuth 已完成，下一步不是停在“已登录”，而是把你本人、SecondMe 分身和 AI 阵容一起带回正式站。
              </p>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8, minWidth: 260 }}>
              <div style={{ borderRadius: 24, background: 'rgba(255,255,255,0.08)', padding: 16 }}>
                <div style={{ fontSize: 12, fontWeight: 800, letterSpacing: '0.16em', textTransform: 'uppercase', color: '#bae6fd' }}>
                  Current Profile
                </div>
                <div style={{ marginTop: 8, fontSize: 22, fontWeight: 800 }}>{profile?.name || 'SecondMe User'}</div>
                <div style={{ marginTop: 4, color: '#cbd5e1', fontSize: 14 }}>{profile?.email || '未公开邮箱'}</div>
              </div>
              <Link
                href={buildHandoffUrl(baseUrl, {
                  human: 'research_lead',
                  shade: 'clinical_memory',
                  pack: 'secondme_core_clinical',
                  profile,
                })}
                style={{
                  padding: '14px 18px',
                  borderRadius: 999,
                  background: '#fff',
                  color: '#0f172a',
                  fontWeight: 800,
                  textAlign: 'center',
                }}
              >
                直接进入默认协作阵容
              </Link>
            </div>
          </div>
        </section>

        <section style={{ display: 'grid', gap: 20, gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))' }}>
          {quickScenarios.map((scenario) => (
            <Link
              key={scenario.id}
              href={buildHandoffUrl(baseUrl, {
                scenario: scenario.id,
                human: scenario.humanRole,
                shade: scenario.shadeId,
                pack: scenario.aiPackId,
                profile,
              })}
              style={{
                borderRadius: 32,
                background: 'rgba(255,255,255,0.84)',
                border: '1px solid rgba(148,163,184,0.22)',
                padding: 24,
                boxShadow: '0 24px 48px rgba(15,23,42,0.08)',
              }}
            >
              <div style={{ color: '#1d4ed8', fontSize: 12, fontWeight: 800, letterSpacing: '0.16em', textTransform: 'uppercase' }}>
                Quick Scenario
              </div>
              <div style={{ marginTop: 10, fontSize: 24, fontWeight: 800 }}>{scenario.title}</div>
              <div style={{ marginTop: 10, color: '#475569', lineHeight: 1.8 }}>{scenario.description}</div>
              <div style={{ marginTop: 18, fontWeight: 800, color: '#1d4ed8' }}>带回正式站</div>
            </Link>
          ))}
        </section>

        <section style={{ display: 'grid', gap: 20, gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))' }}>
          <div style={{ background: 'rgba(255,255,255,0.84)', border: '1px solid rgba(148,163,184,0.22)', borderRadius: 32, padding: 24 }}>
            <div style={{ color: '#1d4ed8', fontSize: 12, fontWeight: 800, letterSpacing: '0.16em', textTransform: 'uppercase' }}>
              Human Roles
            </div>
            <div style={{ marginTop: 12, display: 'grid', gap: 12 }}>
              {humanRoles.map((role) => (
                <Link
                  key={role.id}
                  href={buildHandoffUrl(baseUrl, { human: role.id, profile })}
                  style={{ borderRadius: 24, background: '#fff', border: '1px solid rgba(148,163,184,0.18)', padding: 16 }}
                >
                  <div style={{ fontWeight: 800 }}>{role.name}</div>
                  <div style={{ marginTop: 4, fontSize: 13, color: '#64748b', fontWeight: 700 }}>{role.subtitle}</div>
                  <div style={{ marginTop: 8, fontSize: 14, lineHeight: 1.8, color: '#475569' }}>{role.description}</div>
                </Link>
              ))}
            </div>
          </div>

          <div style={{ background: 'rgba(255,255,255,0.84)', border: '1px solid rgba(148,163,184,0.22)', borderRadius: 32, padding: 24 }}>
            <div style={{ color: '#0f766e', fontSize: 12, fontWeight: 800, letterSpacing: '0.16em', textTransform: 'uppercase' }}>
              SecondMe Shades
            </div>
            <div style={{ marginTop: 12, display: 'grid', gap: 12 }}>
              {shadeTemplates.map((shade) => (
                <Link
                  key={shade.id}
                  href={buildHandoffUrl(baseUrl, { shade: shade.id, profile })}
                  style={{ borderRadius: 24, background: '#fff', border: '1px solid rgba(148,163,184,0.18)', padding: 16 }}
                >
                  <div style={{ fontWeight: 800 }}>{shade.name}</div>
                  <div style={{ marginTop: 4, fontSize: 13, color: '#64748b', fontWeight: 700 }}>{shade.subtitle}</div>
                  <div style={{ marginTop: 8, fontSize: 14, lineHeight: 1.8, color: '#475569' }}>{shade.description}</div>
                </Link>
              ))}
            </div>
          </div>

          <div style={{ background: 'rgba(255,255,255,0.84)', border: '1px solid rgba(148,163,184,0.22)', borderRadius: 32, padding: 24 }}>
            <div style={{ color: '#7c3aed', fontSize: 12, fontWeight: 800, letterSpacing: '0.16em', textTransform: 'uppercase' }}>
              AI Packs
            </div>
            <div style={{ marginTop: 12, display: 'grid', gap: 12 }}>
              {aiPacks.map((pack) => (
                <Link
                  key={pack.id}
                  href={buildHandoffUrl(baseUrl, { pack: pack.id, profile })}
                  style={{ borderRadius: 24, background: '#fff', border: '1px solid rgba(148,163,184,0.18)', padding: 16 }}
                >
                  <div style={{ fontWeight: 800 }}>{pack.name}</div>
                  <div style={{ marginTop: 8, fontSize: 14, lineHeight: 1.8, color: '#475569' }}>{pack.subtitle}</div>
                </Link>
              ))}
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}
