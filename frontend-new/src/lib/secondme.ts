export interface HumanRole {
  id: string;
  name: string;
  subtitle: string;
  description: string;
  accent: string;
}

export interface ShadeTemplate {
  id: string;
  name: string;
  subtitle: string;
  description: string;
}

export interface AiPack {
  id: string;
  name: string;
  subtitle: string;
  recommendedExpert: string;
}

export interface SecondMeProfile {
  id?: string;
  name?: string;
  email?: string;
  avatar?: string;
}

export const humanRoles: HumanRole[] = [
  {
    id: 'research_lead',
    name: '研究发起人',
    subtitle: '我本人带题目进入',
    description: '适合 PI、临床医生或研究负责人直接带着真实课题进入圆桌。',
    accent: '#1d4ed8'
  },
  {
    id: 'coauthor',
    name: '共同作者',
    subtitle: '邀请合作者同步推进',
    description: '适合导师、同事或研究护士与 AI 阵容一起推进同一个题目。',
    accent: '#0f766e'
  },
  {
    id: 'evidence_fellow',
    name: '证据整合员',
    subtitle: '负责文献和会议纪要',
    description: '适合让一位真实研究者专门维护证据地图、纪要和投稿材料。',
    accent: '#7c3aed'
  }
];

export const shadeTemplates: ShadeTemplate[] = [
  {
    id: 'clinical_memory',
    name: '临床判断分身',
    subtitle: '继承你的临床判断偏好',
    description: '适合把你常用的病种关注点、成功标准和判断方式带入每次会话。'
  },
  {
    id: 'literature_memory',
    name: '文献记忆分身',
    subtitle: '持续追踪新近证据',
    description: '适合维护某个病种或投稿方向的长期证据记忆。'
  },
  {
    id: 'omics_memory',
    name: '多组学实验分身',
    subtitle: '固定复杂分析上下文',
    description: '适合承接 GWAS、PGx、单细胞和 Galaxy 工作流的长期上下文。'
  }
];

export const aiPacks: AiPack[] = [
  {
    id: 'secondme_core_clinical',
    name: 'SecondMe 临床五人组',
    subtitle: '临床主任、博士生、流调、统计和研究护士先接管。',
    recommendedExpert: 'clinical_director'
  },
  {
    id: 'hybrid_evidence_network',
    name: 'SecondMe x 14 专家混合阵容',
    subtitle: '更适合证据梳理、任务分诊和投稿准备。',
    recommendedExpert: 'phd_student'
  },
  {
    id: 'clawbio_deep_dive',
    name: 'SecondMe 多组学深潜包',
    subtitle: '适合 GWAS、PGx、单细胞和数据工程并行推进。',
    recommendedExpert: 'clawbio_gwas'
  }
];

export const quickScenarios = [
  {
    id: 'clinical_cocreation',
    title: '临床共创启动',
    description: '研究发起人 + 临床判断分身 + SecondMe 临床五人组',
    humanRole: 'research_lead',
    shadeId: 'clinical_memory',
    aiPackId: 'secondme_core_clinical'
  },
  {
    id: 'evidence_acceleration',
    title: '证据加速协作',
    description: '共同作者 + 文献记忆分身 + 混合 14 专家阵容',
    humanRole: 'coauthor',
    shadeId: 'literature_memory',
    aiPackId: 'hybrid_evidence_network'
  },
  {
    id: 'omics_deep_dive',
    title: '多组学深潜分析',
    description: '证据整合员 + 多组学实验分身 + ClawBio 深潜包',
    humanRole: 'evidence_fellow',
    shadeId: 'omics_memory',
    aiPackId: 'clawbio_deep_dive'
  }
];

export function buildHandoffUrl(baseUrl: string, options: {
  human?: string;
  shade?: string;
  pack?: string;
  scenario?: string;
  profile?: SecondMeProfile | null;
}) {
  const normalizedBase = baseUrl.endsWith('/') ? baseUrl : `${baseUrl}/`;
  const url = new URL('frontend/secondme-hub.html', normalizedBase);
  if (options.human) url.searchParams.set('human', options.human);
  if (options.shade) url.searchParams.set('shade', options.shade);
  if (options.pack) url.searchParams.set('pack', options.pack);
  if (options.scenario) url.searchParams.set('scenario', options.scenario);
  if (options.profile?.id) url.searchParams.set('sm_id', options.profile.id);
  if (options.profile?.name) url.searchParams.set('sm_name', options.profile.name);
  if (options.profile?.email) url.searchParams.set('sm_email', options.profile.email);
  if (options.profile?.avatar) url.searchParams.set('sm_avatar', options.profile.avatar);
  return url.toString();
}
