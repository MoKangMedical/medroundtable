import { aiPacks, buildHandoffUrl, quickScenarios, type SecondMeProfile } from './secondme';

export interface ExpertProfile {
  id: string;
  name: string;
  group: string;
  title: string;
  description: string;
  keywords: string[];
  aiPackId: string;
  scenarioId?: string;
  suggestedOpening: string;
}

export interface DatabaseProfile {
  id: string;
  name: string;
  category: string;
  accessMode: string;
  description: string;
  integration: string;
  recommendedAgent: string;
  url: string;
  tags: string[];
}

export interface CapabilityLane {
  id: string;
  name: string;
  count: number;
  description: string;
  ownerRoles: string[];
  deliverables: string[];
}

export const expertRoster: ExpertProfile[] = [
  {
    id: 'clinical_director',
    name: '临床主任',
    group: '核心临床团队',
    title: '研究价值判断与总体方向',
    description: '适合先判断问题是否值得做、临床终点该怎么定、研究故事能不能成立。',
    keywords: ['临床', '立项', '终点', '价值', '假设', '治疗', '疗效', '疾病', '值得做'],
    aiPackId: 'secondme_core_clinical',
    scenarioId: 'clinical_cocreation',
    suggestedOpening: '请先判断这个临床问题是否值得立项，并明确主要终点、核心对照和预期临床意义。'
  },
  {
    id: 'phd_student',
    name: '博士生',
    group: '核心临床团队',
    title: '文献检索与证据综述',
    description: '适合先拉文献、补创新点、整理投稿叙事和证据缺口。',
    keywords: ['文献', '综述', '证据', '创新点', '投稿', '检索', '总结', '空白'],
    aiPackId: 'hybrid_evidence_network',
    scenarioId: 'evidence_acceleration',
    suggestedOpening: '请先做证据缺口梳理，告诉我现有文献怎么说、创新点在哪里、还缺哪几类证据。'
  },
  {
    id: 'epidemiologist',
    name: '流行病学家',
    group: '核心临床团队',
    title: '研究设计与偏倚控制',
    description: '适合明确研究类型、纳排标准、暴露与结局定义。',
    keywords: ['研究设计', '队列', '病例对照', 'RCT', '纳入', '排除', '偏倚', '混杂', '流行病学'],
    aiPackId: 'secondme_core_clinical',
    suggestedOpening: '请先把研究类型、纳排标准、暴露定义和主要偏倚风险定下来。'
  },
  {
    id: 'statistician',
    name: '统计学家',
    group: '核心临床团队',
    title: '样本量、统计计划与表格',
    description: '适合把指标变成可分析数据结构，提前明确样本量和统计方法。',
    keywords: ['统计', '样本量', '分析', '模型', 'SAP', '表格', 'CRF', '置信区间', 'P值'],
    aiPackId: 'secondme_core_clinical',
    suggestedOpening: '请先明确主要分析指标、样本量估算思路、统计模型和需要采集的关键表格。'
  },
  {
    id: 'research_nurse',
    name: '研究护士',
    group: '核心临床团队',
    title: '执行落地、质控与随访',
    description: '适合把方案变成 SOP、随访表和现场执行清单。',
    keywords: ['执行', '随访', '质控', 'SOP', '采集', '现场', '护士', '依从性'],
    aiPackId: 'secondme_core_clinical',
    suggestedOpening: '请先把现场执行流程、随访节点、质控点和异常反馈机制拆出来。'
  },
  {
    id: 'clawbio_pharmgx',
    name: '药物基因组学专家',
    group: 'ClawBio 生信套件',
    title: '药物反应与个体化用药',
    description: '适合药物代谢、基因型-表型关联和个体化治疗分析。',
    keywords: ['药物', '基因组', 'pgx', '药代', '代谢', '个体化', '不良反应'],
    aiPackId: 'clawbio_deep_dive',
    scenarioId: 'omics_deep_dive',
    suggestedOpening: '请先判断这个题目是否需要药物基因组学切入，给出关键基因、药物和临床解释。'
  },
  {
    id: 'clawbio_gwas',
    name: 'GWAS 专家',
    group: 'ClawBio 生信套件',
    title: '变异关联与遗传风险',
    description: '适合遗传关联、SNP 筛选、风险评分与公开队列深挖。',
    keywords: ['gwas', '遗传', 'snp', '变异', '基因', '风险评分', '多态性'],
    aiPackId: 'clawbio_deep_dive',
    scenarioId: 'omics_deep_dive',
    suggestedOpening: '请先从遗传变异和风险关联角度判断这个题目可不可做，优先看哪些公开数据和变异位点。'
  },
  {
    id: 'clawbio_scrna',
    name: '单细胞测序专家',
    group: 'ClawBio 生信套件',
    title: '单细胞与细胞状态解析',
    description: '适合 scRNA-seq、多组学分群和细胞通讯分析。',
    keywords: ['单细胞', 'scrna', '细胞', '聚类', '轨迹', '通讯', '空间转录组'],
    aiPackId: 'clawbio_deep_dive',
    scenarioId: 'omics_deep_dive',
    suggestedOpening: '请先从单细胞角度评估样本设计、关键细胞群和分析输出物。'
  },
  {
    id: 'clawbio_galaxy',
    name: 'Galaxy 桥接器',
    group: 'ClawBio 生信套件',
    title: '把 8000+ 工具串进工作流',
    description: '适合复杂管线、工具编排和批量自动化分析。',
    keywords: ['galaxy', '工作流', '工具', 'pipeline', '自动化', '批量分析'],
    aiPackId: 'clawbio_deep_dive',
    suggestedOpening: '请先判断这个题目是否需要接 Galaxy 工具链，并拆出最小分析管线。'
  },
  {
    id: 'ux_researcher',
    name: 'UX 研究员',
    group: '专业研究支持团队',
    title: '体验、访谈与用户研究',
    description: '适合数字医疗、随访产品、医生工具和患者体验优化。',
    keywords: ['体验', '访谈', '可用性', '界面', '流程', '用户研究', '依从性'],
    aiPackId: 'hybrid_evidence_network',
    suggestedOpening: '请先判断目标用户是谁、痛点发生在什么流程节点、应该先测哪几个关键动作。'
  },
  {
    id: 'ai_data_engineer',
    name: 'AI 数据工程师',
    group: '专业研究支持团队',
    title: '数据接入、清洗与特征组织',
    description: '适合把多源公开数据和本地数据整理成可分析状态。',
    keywords: ['数据', '清洗', '表结构', 'etl', '特征', '接入', '字段', 'pipeline'],
    aiPackId: 'hybrid_evidence_network',
    suggestedOpening: '请先拆出数据来源、表结构、主键联接和最容易出错的清洗步骤。'
  },
  {
    id: 'trend_researcher',
    name: '趋势研究员',
    group: '专业研究支持团队',
    title: '热点追踪与竞争格局',
    description: '适合找趋势、看竞品、补强新兴方向和会议热点。',
    keywords: ['趋势', '热点', '竞品', '会议', '前沿', '方向', '情报'],
    aiPackId: 'hybrid_evidence_network',
    suggestedOpening: '请先把这个方向最近一年的热点、竞品和最容易被期刊认可的新角度梳理出来。'
  },
  {
    id: 'experiment_tracker',
    name: '实验追踪员',
    group: '专业研究支持团队',
    title: '任务里程碑与风险跟踪',
    description: '适合长周期项目、跨团队任务推进和风险预警。',
    keywords: ['进度', '风险', '里程碑', '任务', '追踪', '排期', '协作'],
    aiPackId: 'hybrid_evidence_network',
    suggestedOpening: '请先把任务里程碑、依赖关系和最容易延期的风险点拆出来。'
  },
  {
    id: 'model_qa',
    name: '模型 QA 专家',
    group: '专业研究支持团队',
    title: '质量门禁、偏差与可靠性',
    description: '适合方法学审查、模型偏差排查和发表前质量门禁。',
    keywords: ['qa', '偏差', '可靠性', '验证', '门禁', '风险', '鲁棒性'],
    aiPackId: 'hybrid_evidence_network',
    suggestedOpening: '请先从偏差、复现性和质量门禁角度指出这个方案最大的风险。'
  }
];

export const databaseProfiles: DatabaseProfile[] = [
  {
    id: 'pubmed',
    name: 'PubMed',
    category: '文献',
    accessMode: '工作流接入',
    description: '权威生物医学文献检索数据库，适合快速构建检索式和证据综述。',
    integration: '博士生证据链路、参考文献导出、创新点预检。',
    recommendedAgent: '博士生',
    url: 'https://pubmed.ncbi.nlm.nih.gov/',
    tags: ['权威', '文献', '证据']
  },
  {
    id: 'clinicaltrials',
    name: 'ClinicalTrials.gov',
    category: '临床试验',
    accessMode: '工作流接入',
    description: '全球核心临床试验注册库，用于核对同类试验设计、终点与进度。',
    integration: '试验设计对照、终点参考、竞争项目扫描。',
    recommendedAgent: '流行病学家',
    url: 'https://clinicaltrials.gov/',
    tags: ['临床试验', '全球', '设计对照']
  },
  {
    id: 'nhanes',
    name: 'NHANES',
    category: '流行病学/队列',
    accessMode: '深度集成',
    description: '美国国家健康与营养调查，适合横断面和人群健康研究。',
    integration: 'NHANES 智能分析平台、Lancet 风格结果输出。',
    recommendedAgent: '流行病学家',
    url: 'https://wwwn.cdc.gov/nchs/nhanes/',
    tags: ['流行病学', '队列', '深度集成']
  },
  {
    id: 'seer',
    name: 'SEER',
    category: '肿瘤/登记',
    accessMode: '深度集成',
    description: '肿瘤登记数据库，适合预后、生存和真实世界肿瘤研究。',
    integration: 'SEER-BMJ 肿瘤研究、预后建模、生存曲线。',
    recommendedAgent: '统计学家',
    url: 'https://seer.cancer.gov/',
    tags: ['肿瘤', '预后', '生存分析']
  },
  {
    id: 'charls',
    name: 'CHARLS',
    category: '流行病学/队列',
    accessMode: '深度集成',
    description: '中国健康与养老追踪调查，适合老龄化、慢病和社会医学研究。',
    integration: '中国人群研究、健康经济学和纵向随访。',
    recommendedAgent: '趋势研究员',
    url: 'https://charls.charlsdata.com/',
    tags: ['中国', '老龄化', '队列']
  },
  {
    id: 'drugbank',
    name: 'DrugBank',
    category: '药物/转化',
    accessMode: '目录直连',
    description: '药物、靶点与作用机制知识库，适合药物再利用和机制研究。',
    integration: '药物基因组学、靶点优选、转化医学分析。',
    recommendedAgent: '药物基因组学专家',
    url: 'https://go.drugbank.com/',
    tags: ['药物', '靶点', '机制']
  }
];

export const capabilityLanes: CapabilityLane[] = [
  {
    id: 'evidence_synthesis',
    name: '证据合成引擎',
    count: 289,
    description: '覆盖检索式、系统综述、证据分级和论文叙事搭建。',
    ownerRoles: ['博士生', '趋势研究员', '临床主任'],
    deliverables: ['检索式', '证据综述', '论文提纲']
  },
  {
    id: 'trial_design',
    name: '试验与方案设计引擎',
    count: 280,
    description: '围绕研究问题拆解、终点设计、随机化、CRF 和临床可行性评估。',
    ownerRoles: ['临床主任', '流行病学家', '研究护士'],
    deliverables: ['研究设计', '终点定义', 'CRF 模板']
  },
  {
    id: 'bioinformatics',
    name: '多组学生信引擎',
    count: 128,
    description: '承接单细胞、GWAS、多组学融合、变异优选和功能注释。',
    ownerRoles: ['GWAS 专家', '单细胞测序专家', 'Galaxy 桥接器'],
    deliverables: ['质控结果', '差异分析', '注释报告']
  },
  {
    id: 'data_fabric',
    name: '数据库与数据织网引擎',
    count: 83,
    description: '统一编排公共数据库、队列数据和本地结构化数据接入。',
    ownerRoles: ['AI 数据工程师', '实验追踪员'],
    deliverables: ['数据库清单', '联接视图', '可分析数据集']
  }
];

function normalizeText(value?: string) {
  return (value || '').trim().toLowerCase();
}

function scoreExpert(question: string, expert: ExpertProfile) {
  const haystack = normalizeText(question);
  if (!haystack) return 0;
  return expert.keywords.reduce((score, keyword) => score + (haystack.includes(normalizeText(keyword)) ? 2 : 0), 0);
}

export function recommendExpert(question: string) {
  const ranked = expertRoster
    .map((expert) => ({ expert, score: scoreExpert(question, expert) }))
    .sort((a, b) => b.score - a.score);

  return ranked[0]?.score ? ranked[0].expert : expertRoster[0];
}

export function listAgentRoster(args?: { group?: string; query?: string }) {
  const group = normalizeText(args?.group);
  const query = normalizeText(args?.query);
  return expertRoster.filter((expert) => {
    if (group && !normalizeText(expert.group).includes(group)) return false;
    if (!query) return true;
    return [expert.name, expert.group, expert.title, expert.description, ...expert.keywords]
      .some((item) => normalizeText(item).includes(query));
  });
}

export function searchDatabases(args?: { query?: string; category?: string; limit?: number }) {
  const query = normalizeText(args?.query);
  const category = normalizeText(args?.category);
  const limit = Math.min(Math.max(Number(args?.limit || 5), 1), 12);

  return databaseProfiles
    .filter((database) => {
      if (category && !normalizeText(database.category).includes(category)) return false;
      if (!query) return true;
      return [database.name, database.category, database.description, database.integration, database.recommendedAgent, ...database.tags]
        .some((item) => normalizeText(item).includes(query));
    })
    .slice(0, limit);
}

export function buildRoundtablePlan(args: {
  clinicalQuestion: string;
  title?: string;
  includeSecondMe?: boolean;
  profile?: SecondMeProfile | null;
  baseUrl?: string;
}) {
  const question = args.clinicalQuestion.trim();
  const expert = recommendExpert(question);
  const aiPack = aiPacks.find((pack) => pack.id === expert.aiPackId) || aiPacks[0];
  const scenario = quickScenarios.find((item) => item.id === expert.scenarioId) || quickScenarios[0];
  const title = args.title?.trim() || `MedRoundTable 圆桌：${question.slice(0, 26)}${question.length > 26 ? '…' : ''}`;
  const baseUrl = args.baseUrl || 'https://mokangmedical.github.io/medroundtable';

  return {
    title,
    clinicalQuestion: question,
    recommendedExpert: expert,
    aiPack,
    scenario,
    suggestedOpening: expert.suggestedOpening,
    nextActions: [
      `先由${expert.name}判断问题边界和第一步决策。`,
      `再由 ${aiPack.name} 补齐证据、设计和执行视角。`,
      '把需要上传的数据、方案或文献目录提前准备好，进入圆桌后可直接继续。'
    ],
    handoffUrl: buildHandoffUrl(baseUrl, {
      scenario: scenario.id,
      human: scenario.humanRole,
      shade: scenario.shadeId,
      pack: aiPack.id,
      profile: args.includeSecondMe ? (args.profile || null) : null
    })
  };
}

export function buildCapabilitySnapshot() {
  const expertGroups = expertRoster.reduce<Record<string, number>>((acc, expert) => {
    acc[expert.group] = (acc[expert.group] || 0) + 1;
    return acc;
  }, {});

  const databaseCategories = databaseProfiles.reduce<Record<string, number>>((acc, database) => {
    acc[database.category] = (acc[database.category] || 0) + 1;
    return acc;
  }, {});

  return {
    platform: 'MedRoundTable',
    website: 'https://mokangmedical.github.io/medroundtable',
    secondMePortal: 'https://medroundtable-secondme.vercel.app',
    expertsTotal: expertRoster.length,
    aiPacksTotal: aiPacks.length,
    databasesTotal: databaseProfiles.length,
    capabilityLanesTotal: capabilityLanes.length,
    expertGroups,
    databaseCategories,
    highlights: capabilityLanes,
  };
}
