(function () {
    const groups = [
        {
            id: 'core_clinical',
            name: '核心临床团队',
            summary: '5 位专家负责把临床问题翻译成可执行的研究设计、统计框架与落地路径。',
            accent: '#9f1239',
            surface: '#fff1f2',
            border: 'rgba(190, 24, 93, 0.2)',
            icon: 'fa-stethoscope',
            countLabel: '5 位 · 驱动临床落地'
        },
        {
            id: 'clawbio_suite',
            name: 'ClawBio 生物信息学套件',
            summary: '4 位生信专家打通药物基因组学、GWAS、单细胞和 Galaxy 工作流。',
            accent: '#0f766e',
            surface: '#ecfeff',
            border: 'rgba(13, 148, 136, 0.24)',
            icon: 'fa-dna',
            countLabel: '4 位 · 攻克多组学壁垒'
        },
        {
            id: 'research_support',
            name: '专业研究支持团队',
            summary: '5 位保障型角色处理体验、数据工程、趋势追踪、实验管理与模型 QA。',
            accent: '#1d4ed8',
            surface: '#eff6ff',
            border: 'rgba(37, 99, 235, 0.2)',
            icon: 'fa-layer-group',
            countLabel: '5 位 · 保障模型与数据质量'
        }
    ];

    const experts = [
        {
            role: 'clinical_director',
            name: '临床主任',
            subtitle: '研究策略制定',
            title: 'Clinical Director / 首席临床架构师',
            groupId: 'core_clinical',
            accent: '#9f1239',
            avatarAsset: 'assets/doctor1.png',
            fallback: '临',
            stage: '研究问题定义',
            summary: '负责把临床痛点收敛成可发表、可执行、可协作的研究方向。',
            highlights: ['临床价值判断', '研究目标拆解', '跨专家裁决'],
            responsibilities: [
                '定义研究主问题、主要终点与临床转化价值。',
                '协调博士生、流行病学家和统计学家的方法意见。',
                '把早期探索题目收敛成可执行的 protocol 骨架。',
                '评估研究周期、中心协作难度和资源匹配度。',
                '在关键分歧上给出最终研究策略判断。'
            ],
            deliverables: ['研究定位说明', 'PI 级研究问题声明', '目标与终点优先级清单'],
            path: ['先判断题目是否值得做', '再定义临床问题与成功标准', '最后分配后续专家协作顺序'],
            tags: ['研究策略', '终点设计', '多学科协调', '临床转化'],
            prompt: '请帮我判断这个临床问题是否值得立项，并给出可发表的研究定位。'
        },
        {
            role: 'phd_student',
            name: '博士生',
            subtitle: '文献综述',
            title: 'PhD Student / 文献与证据整合专家',
            groupId: 'core_clinical',
            accent: '#7c3aed',
            avatarAsset: 'assets/doctor2.png',
            fallback: '博',
            stage: '证据扫描',
            summary: '负责系统检索文献、梳理现状、识别证据空白和潜在创新点。',
            highlights: ['系统检索', '证据分层', '空白定位'],
            responsibilities: [
                '完成 PubMed、Cochrane、指南与高分期刊的系统检索。',
                '整理研究现状、热点与争议结论。',
                '输出证据矩阵，识别可切入的创新空间。',
                '为研究假设、讨论部分和引言提供支撑。',
                '跟踪新近发表结果，避免重复选题。'
            ],
            deliverables: ['文献证据矩阵', '知识空白总结', '研究背景综述草案'],
            path: ['先设定检索问题', '再搭建证据地图', '最后回填到研究设计与写作框架'],
            tags: ['系统综述', '文献检索', '证据整合', '研究背景'],
            prompt: '围绕这个题目帮我做一轮文献扫描，告诉我还有哪些空白可以切入。'
        },
        {
            role: 'epidemiologist',
            name: '流行病学家',
            subtitle: '方案设计',
            title: 'Clinical Epidemiologist / 方案与偏倚控制专家',
            groupId: 'core_clinical',
            accent: '#db2777',
            avatarAsset: 'assets/doctor3.png',
            fallback: '流',
            stage: '设计定型',
            summary: '负责研究方案结构、队列设计、偏倚控制和方法学可行性判断。',
            highlights: ['偏倚控制', '队列设计', '方法学评审'],
            responsibilities: [
                '设计研究流程、暴露定义与纳排标准。',
                '识别选择偏倚、信息偏倚和混杂风险。',
                '判断真实世界数据与临床试验设计的适配方式。',
                '把临床问题翻译成规范的研究方案结构。',
                '对方案可执行性和伦理风险做方法学审查。'
            ],
            deliverables: ['研究方案框架', '偏倚控制清单', '纳排与变量定义建议'],
            path: ['先明确研究类型', '再控制关键偏倚', '最后打磨 protocol 细节'],
            tags: ['研究设计', '偏倚控制', '队列方法', '可行性评估'],
            prompt: '请把这个研究想法转成规范方案，并指出最需要规避的偏倚。'
        },
        {
            role: 'statistician',
            name: '统计学家',
            subtitle: '统计分析',
            title: 'Biostatistician / 生物统计方案专家',
            groupId: 'core_clinical',
            accent: '#ea580c',
            avatarAsset: 'assets/doctor4.png',
            avatarPosition: '75% center',
            fallback: '统',
            stage: '统计建模',
            summary: '负责样本量、统计分析计划、CRF 字段逻辑和结果表达方式。',
            highlights: ['SAP', '样本量计算', '结果表达'],
            responsibilities: [
                '给出样本量、效能与关键假设参数建议。',
                '制定主要终点、次要终点与敏感性分析路径。',
                '设计统计分析计划和模型选择逻辑。',
                '推动 CRF 字段与分析变量定义保持一致。',
                '提前设计图表、表格和结果呈现标准。'
            ],
            deliverables: ['统计分析计划', '样本量估算', '结果表图模板'],
            path: ['先定义终点与比较方式', '再设计模型和敏感性分析', '最后固化输出格式'],
            tags: ['样本量', '统计建模', 'SAP', 'CRF 变量'],
            prompt: '请基于我的终点与样本来源，给我一个可发表的统计分析计划。'
        },
        {
            role: 'research_nurse',
            name: '研究护士',
            subtitle: '数据管理',
            title: 'Research Nurse / 访视与数据质量专家',
            groupId: 'core_clinical',
            accent: '#0284c7',
            avatarAsset: 'assets/doctor5.png',
            fallback: '护',
            stage: '执行准备',
            summary: '负责访视流程、数据采集口径、GCP 合规和现场执行协同。',
            highlights: ['访视流程', '数据口径', 'GCP 合规'],
            responsibilities: [
                '规划招募、随访、访视窗口和脱落应对方式。',
                '梳理 CRF 填报字段与现场采集流程。',
                '检查数据完整性与质量控制节点。',
                '提示 GCP 合规、伦理提交和研究护士执行细节。',
                '为多中心执行准备操作层 SOP。'
            ],
            deliverables: ['访视计划表', 'CRF 采集流程建议', '现场执行 SOP 要点'],
            path: ['先看执行场景', '再定义采集与质控规则', '最后固化研究现场 SOP'],
            tags: ['GCP', 'CRF', '访视管理', '现场执行'],
            prompt: '请按临床现场执行角度检查我的采集流程和访视计划。'
        },
        {
            role: 'clawbio_pharmgx',
            name: '药物基因组学',
            subtitle: 'PGx 分析',
            title: 'Pharmacogenomics Specialist / 个体化用药分析专家',
            groupId: 'clawbio_suite',
            accent: '#0f766e',
            avatarAsset: 'assets/expert-avatars/clawbio_pharmgx.png',
            fallback: '药',
            stage: '药物反应解释',
            summary: '将基因变异、药物反应和临床结局关联起来，支持个体化用药研究。',
            highlights: ['PGx 解释', 'CPIC 路径', '药物反应预测'],
            responsibilities: [
                '解析药物代谢相关基因变异与临床反应之间的联系。',
                '对接 CPIC 等指南给出可解释的分析思路。',
                '支持药效、毒性和个体化用药研究设计。',
                '协助定义药物基因组学变量与分层方法。',
                '为投稿中的转化价值段落提供证据支持。'
            ],
            deliverables: ['PGx 变量策略', '药物反应分析建议', '指南映射摘要'],
            path: ['先识别药物相关基因', '再定义表型和结局', '最后输出可发表的 PGx 框架'],
            tags: ['PGx', 'CPIC', '药物反应', '精准用药'],
            prompt: '我有药物暴露和基因信息，帮我判断能否做一篇 PGx 方向研究。'
        },
        {
            role: 'clawbio_gwas',
            name: 'GWAS 专家',
            subtitle: '变异查询',
            title: 'GWAS Specialist / 全基因组关联分析专家',
            groupId: 'clawbio_suite',
            accent: '#2563eb',
            avatarAsset: 'assets/expert-avatars/clawbio_gwas.png',
            fallback: 'GW',
            stage: '遗传关联发现',
            summary: '负责遗传变异关联分析、表型选择和 GWAS 结果解读。',
            highlights: ['GWAS 建模', '变异注释', '表型定义'],
            responsibilities: [
                '识别与疾病或结局相关的遗传变异位点。',
                '协助进行表型定义、QC 与人群分层判断。',
                '解释 Manhattan / QQ plot 与显著性阈值。',
                '结合功能注释筛选重点候选变异。',
                '把遗传发现转成可写入论文的结果结构。'
            ],
            deliverables: ['GWAS 分析路径', '显著位点说明', '遗传发现摘要'],
            path: ['先清楚表型和 QC 规则', '再跑关联分析', '最后把结果翻译成科研故事'],
            tags: ['GWAS', '变异注释', '表型设计', '人群分层'],
            prompt: '帮我判断这个表型能否做 GWAS，并给出分析与结果解读框架。'
        },
        {
            role: 'clawbio_sc_rna',
            name: '单细胞测序',
            subtitle: '细胞聚类',
            title: 'scRNA Specialist / 单细胞分析专家',
            groupId: 'clawbio_suite',
            accent: '#9333ea',
            avatarAsset: 'assets/expert-avatars/clawbio_sc_rna.png',
            fallback: '单',
            stage: '多组学深入分析',
            summary: '负责 scRNA-seq 数据的聚类、差异表达和细胞亚群解释。',
            highlights: ['细胞聚类', '差异表达', '亚群注释'],
            responsibilities: [
                '梳理单细胞样本设计、质控和标准分析路径。',
                '执行细胞聚类、标记基因筛选与亚群注释。',
                '识别关键差异表达模式和细胞状态变化。',
                '生成可用于论文的图形和叙事逻辑。',
                '协助把单细胞发现与临床问题对应起来。'
            ],
            deliverables: ['单细胞分析路径', '细胞亚群解释', '图形清单建议'],
            path: ['先定义样本与质控', '再完成聚类和注释', '最后对接临床问题解释'],
            tags: ['scRNA-seq', '聚类', '差异表达', '细胞注释'],
            prompt: '我有单细胞数据，想做细胞亚群和差异表达分析，帮我规划路径。'
        },
        {
            role: 'clawbio_galaxy',
            name: 'Galaxy 桥接器',
            subtitle: '8000+ 工具编排',
            title: 'Galaxy Bridge / 生信流程编排专家',
            groupId: 'clawbio_suite',
            accent: '#7c3aed',
            avatarAsset: 'assets/expert-avatars/clawbio_galaxy.png',
            fallback: '桥',
            stage: '工作流编排',
            summary: '连接 Galaxy 生态与 OpenClaw 医疗技能，把生信任务编排成可复用流程。',
            highlights: ['流程封装', '工具编排', '复现性'],
            responsibilities: [
                '选择适合的 Galaxy 工具链与分析顺序。',
                '把分散的分析步骤整理成可追踪工作流。',
                '设计输入输出规范，降低重复试错成本。',
                '帮助团队复用已有流程并积累技能模板。',
                '对接更大规模的生信任务调度和自动化执行。'
            ],
            deliverables: ['Galaxy 工作流建议', '输入输出规范', '技能组合方案'],
            path: ['先定义分析目标', '再拼装工作流模块', '最后封装成可复用技能路径'],
            tags: ['Galaxy', '工作流', '工具生态', '自动化编排'],
            prompt: '我要把多个生信步骤串成稳定工作流，帮我设计 Galaxy 编排方案。'
        },
        {
            role: 'ux_researcher',
            name: 'UX 研究员',
            subtitle: '研究体验设计',
            title: 'UX Researcher / 研究流程体验专家',
            groupId: 'research_support',
            accent: '#d97706',
            avatarAsset: 'assets/expert-avatars/ux_researcher.png',
            fallback: 'UX',
            stage: '流程优化',
            summary: '从研究者体验出发，优化页面路径、任务引导和操作反馈。',
            highlights: ['流程梳理', '体验诊断', '页面转化'],
            responsibilities: [
                '审视用户从立项到分析再到导出的路径阻塞点。',
                '设计更直观的页面结构和任务导航。',
                '减少“点了没下一页”的断点体验。',
                '为首页、专家页和功能页提供信息层级建议。',
                '把复杂流程压缩成可理解的任务流。'
            ],
            deliverables: ['任务流梳理', '交互改版建议', '入口优先级排序'],
            path: ['先识别断点', '再重组导航路径', '最后沉淀成稳定页面结构'],
            tags: ['交互设计', '任务流', '页面结构', '转化优化'],
            prompt: '请从研究者使用路径出发，帮我找出首页最该修的体验断点。'
        },
        {
            role: 'ai_data_engineer',
            name: 'AI 数据工程师',
            subtitle: '数据管道修复',
            title: 'AI Data Engineer / 数据与语义管道专家',
            groupId: 'research_support',
            accent: '#0891b2',
            avatarAsset: 'assets/expert-avatars/ai_data_engineer.png',
            fallback: '数',
            stage: '数据工程',
            summary: '负责数据结构整理、字段标准化、语义聚类和下游 AI 分析可用性。',
            highlights: ['数据清洗', '结构标准化', '语义聚类'],
            responsibilities: [
                '梳理原始数据到可分析数据集的转换路径。',
                '修正字段映射、命名规范和数据质量问题。',
                '把非结构化材料转为适配 AI 分析的输入。',
                '为后续统计、可视化和写作输出统一数据口径。',
                '提升多来源数据整合和复用能力。'
            ],
            deliverables: ['数据字段映射', '清洗规范', '分析前置数据准备方案'],
            path: ['先盘点数据源', '再统一字段与口径', '最后交给统计和写作链路使用'],
            tags: ['ETL', '数据标准化', '语义聚类', '字段治理'],
            prompt: '请帮我把现有杂乱数据整理成适合统计和 AI 协作的结构。'
        },
        {
            role: 'trend_researcher',
            name: '趋势研究员',
            subtitle: '研究趋势监测',
            title: 'Trend Researcher / 趋势与竞品情报专家',
            groupId: 'research_support',
            accent: '#e11d48',
            avatarAsset: 'assets/expert-avatars/trend_researcher.png',
            fallback: '趋',
            stage: '方向校准',
            summary: '追踪研究热点、竞品路线和期刊偏好，帮助题目选择更贴近发表窗口。',
            highlights: ['趋势追踪', '竞品分析', '期刊匹配'],
            responsibilities: [
                '分析近期高分期刊主题和选题偏好。',
                '监测竞品团队的研究动作与热点转向。',
                '帮助团队避开拥挤赛道或寻找侧翼切入点。',
                '为投稿目标期刊提供选题和表达建议。',
                '把趋势判断转为研究优先级决策。'
            ],
            deliverables: ['趋势扫描摘要', '期刊偏好建议', '竞品方向分析'],
            path: ['先看热点与竞品', '再校准题目角度', '最后输出投稿导向建议'],
            tags: ['趋势研究', '竞品分析', '期刊偏好', '选题判断'],
            prompt: '我想知道这个题目现在是不是热点，适合投哪些方向的期刊。'
        },
        {
            role: 'experiment_tracker',
            name: '实验追踪员',
            subtitle: '实验设计管理',
            title: 'Experiment Tracker / 实验与试验追踪专家',
            groupId: 'research_support',
            accent: '#65a30d',
            avatarAsset: 'assets/expert-avatars/experiment_tracker.png',
            fallback: '追',
            stage: '执行跟踪',
            summary: '负责实验或试验过程跟踪、里程碑管理和方案偏差记录。',
            highlights: ['试验追踪', '里程碑管理', '偏差记录'],
            responsibilities: [
                '梳理试验时间线、关键里程碑和依赖项。',
                '记录实验设计变更、方案偏差和原因。',
                '协助团队追踪全球临床试验动态与竞品动作。',
                '为阶段复盘和中期调整提供结构化记录。',
                '让试验执行信息可视、可回顾、可交接。'
            ],
            deliverables: ['研究追踪台账', '里程碑计划', '偏差记录模板'],
            path: ['先建立时间线', '再持续记录变更', '最后沉淀成可复盘的追踪体系'],
            tags: ['里程碑', '试验跟踪', '偏差记录', '动态监测'],
            prompt: '请帮我把这个研究的执行节点和追踪机制整理清楚。'
        },
        {
            role: 'model_qa',
            name: '模型 QA 专家',
            subtitle: '偏差检测',
            title: 'Model QA Specialist / 模型质量保障专家',
            groupId: 'research_support',
            accent: '#2563eb',
            avatarAsset: 'assets/expert-avatars/model_qa.png',
            fallback: 'QA',
            stage: '质量兜底',
            summary: '对模型输出、研究结论和自动化流程进行偏差、漂移和稳定性检查。',
            highlights: ['质量复核', '偏差检测', '稳定性验证'],
            responsibilities: [
                '检查模型或自动化输出是否存在系统性偏差。',
                '识别结论与证据链之间的薄弱点。',
                '验证研究流程在不同输入下的稳定性。',
                '提供上线前的 QA 审核意见和修复建议。',
                '降低自动化流程带来的不可解释风险。'
            ],
            deliverables: ['QA 审核清单', '偏差风险说明', '稳定性复核意见'],
            path: ['先定义质量标准', '再做偏差与稳定性检查', '最后形成上线前复核意见'],
            tags: ['质量保证', '偏差检测', '稳定性', '结论复核'],
            prompt: '请站在 QA 角度审查这套输出，告诉我哪里最可能出错。'
        }
    ];

    const expertMap = Object.fromEntries(experts.map((expert) => [expert.role, expert]));
    const groupMap = Object.fromEntries(groups.map((group) => [group.id, group]));

    function needsParentPrefix() {
        return window.location.pathname.includes('/frontend/')
            || window.location.pathname.includes('/roundtables/');
    }

    function rootPrefix() {
        return needsParentPrefix() ? '../' : './';
    }

    function toRootPath(path) {
        return `${rootPrefix()}${path}`;
    }

    function resolveAvatar(expert) {
        if (expert.avatarUrl) {
            return expert.avatarUrl;
        }
        if (expert.avatarAsset) {
            return toRootPath(expert.avatarAsset);
        }
        return '';
    }

    function expertProfileUrl(role) {
        const encodedRole = encodeURIComponent(role);
        if (window.location.pathname.includes('/frontend/')) {
            return `./expert-profile.html?role=${encodedRole}`;
        }
        if (window.location.pathname.includes('/roundtables/')) {
            return `../frontend/expert-profile.html?role=${encodedRole}`;
        }
        return `./frontend/expert-profile.html?role=${encodedRole}`;
    }

    function expertsOverviewUrl() {
        return needsParentPrefix() ? '../experts.html' : './experts.html';
    }

    function sessionLaunchpadUrl(role) {
        const suffix = role ? `?expert=${encodeURIComponent(role)}` : '';
        if (window.location.pathname.includes('/frontend/')) {
            return `./session-launchpad.html${suffix}`;
        }
        if (window.location.pathname.includes('/roundtables/')) {
            return `../frontend/session-launchpad.html${suffix}`;
        }
        return `./frontend/session-launchpad.html${suffix}`;
    }

    function getExpert(role) {
        return expertMap[role] || null;
    }

    function getGroup(groupId) {
        return groupMap[groupId] || null;
    }

    function getExpertsByGroup(groupId) {
        return experts.filter((expert) => expert.groupId === groupId);
    }

    function getRelatedExperts(role) {
        const current = getExpert(role);
        if (!current) {
            return [];
        }
        return experts.filter((expert) => expert.groupId === current.groupId && expert.role !== role);
    }

    window.MedRoundTableExperts = {
        groups,
        experts,
        getExpert,
        getGroup,
        getExpertsByGroup,
        getRelatedExperts,
        resolveAvatar,
        expertProfileUrl,
        expertsOverviewUrl,
        sessionLaunchpadUrl,
        toRootPath
    };
}());
