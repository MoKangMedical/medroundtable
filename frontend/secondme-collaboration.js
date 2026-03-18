(function () {
    const humanRoles = [
        {
            id: 'research_lead',
            name: '研究发起人',
            subtitle: '我本人带题目进入',
            description: '适合 PI、临床医生或研究负责人直接带着真实课题进入圆桌。',
            accent: '#1d4ed8',
            icon: 'fa-user-doctor',
            responsibilities: ['定义真实问题', '确认优先级', '决定是否立项']
        },
        {
            id: 'coauthor',
            name: '共同作者',
            subtitle: '邀请合作者同步推进',
            description: '适合与导师、同事、研究护士或数据团队一起推进同一个题目。',
            accent: '#0f766e',
            icon: 'fa-user-group',
            responsibilities: ['共享上下文', '同步材料', '分工推进']
        },
        {
            id: 'evidence_fellow',
            name: '证据整合员',
            subtitle: '负责文献和会议纪要',
            description: '适合让一位真实研究者专门负责证据追踪、纪要整理和投稿材料。',
            accent: '#7c3aed',
            icon: 'fa-book-medical',
            responsibilities: ['文献追踪', '整理会议纪要', '维护投稿材料']
        }
    ];

    const shadeTemplates = [
        {
            id: 'clinical_memory',
            name: '临床判断分身',
            subtitle: '把你的临床偏好带进圆桌',
            description: '适合沉淀你常用的判断框架、病种关注点和成功标准。',
            accent: '#0f766e',
            icon: 'fa-brain',
            prompt: '请继承我的临床判断方式，优先从真实世界可落地与临床价值两个维度评估。 '
        },
        {
            id: 'literature_memory',
            name: '文献记忆分身',
            subtitle: '持续追踪最新证据',
            description: '适合维护某个病种、亚专科或投稿方向的长期证据记忆。',
            accent: '#7c3aed',
            icon: 'fa-scroll',
            prompt: '请优先补齐最新高分证据、指南更新和可发表的创新空白。 '
        },
        {
            id: 'omics_memory',
            name: '多组学实验分身',
            subtitle: '把复杂生信上下文固定下来',
            description: '适合承接 GWAS、PGx、单细胞或 Galaxy 工作流的长期分析上下文。',
            accent: '#ea580c',
            icon: 'fa-dna',
            prompt: '请记住我这条多组学分析链路，优先维持变量口径、QC 规则和结果解释一致。 '
        }
    ];

    const aiPacks = [
        {
            id: 'secondme_core_clinical',
            name: 'SecondMe 临床五人组',
            subtitle: '让临床主任、博士生、流调、统计和研究护士先接管',
            accent: '#1d4ed8',
            recommendedExpert: 'clinical_director',
            expertRoles: ['clinical_director', 'phd_student', 'epidemiologist', 'statistician', 'research_nurse'],
            outcomes: ['收敛研究问题', '形成 protocol 骨架', '确定统计与执行路径']
        },
        {
            id: 'hybrid_evidence_network',
            name: 'SecondMe x 14 专家混合阵容',
            subtitle: '真人 + 分身 + MedRoundTable 14 位 AI 一起推进',
            accent: '#7c3aed',
            recommendedExpert: 'phd_student',
            expertRoles: ['phd_student', 'epidemiologist', 'statistician', 'trend_researcher', 'model_qa'],
            outcomes: ['补证据空白', '做任务分诊', '准备更稳的投稿材料']
        },
        {
            id: 'clawbio_deep_dive',
            name: 'SecondMe 多组学深潜包',
            subtitle: '把真实研究者和 ClawBio 套件一起拉进来',
            accent: '#0f766e',
            recommendedExpert: 'clawbio_gwas',
            expertRoles: ['clawbio_gwas', 'clawbio_pharmgx', 'clawbio_sc_rna', 'clawbio_galaxy', 'ai_data_engineer'],
            outcomes: ['判断表型可行性', '对齐 QC 规则', '加快多组学分析落地']
        }
    ];

    const scenarios = [
        {
            id: 'clinical_cocreation',
            title: '临床共创启动',
            description: '真人研究发起人 + 临床判断分身 + SecondMe 临床五人组。',
            humanRole: 'research_lead',
            shadeId: 'clinical_memory',
            aiPackId: 'secondme_core_clinical',
            preferredExpert: 'clinical_director',
            sessionTitle: 'SecondMe 协作圆桌：临床共创启动',
            sessionQuestion: '请把我作为真实研究发起人加入本次圆桌。先由临床主任介入，结合我的临床判断分身，一起判断这个题目是否值得立项、主问题如何定义、终点怎么设。'
        },
        {
            id: 'evidence_acceleration',
            title: '证据加速协作',
            description: '共同作者 + 文献记忆分身 + 混合 14 专家阵容。',
            humanRole: 'coauthor',
            shadeId: 'literature_memory',
            aiPackId: 'hybrid_evidence_network',
            preferredExpert: 'phd_student',
            sessionTitle: 'SecondMe 协作圆桌：证据加速协作',
            sessionQuestion: '请把我的合作者和文献记忆分身一起带入圆桌。先由博士生介入，快速扫描已有研究、争议结论和创新空白，并判断后续还需要哪些专家加入。'
        },
        {
            id: 'omics_deep_dive',
            title: '多组学深潜分析',
            description: '证据整合员 + 多组学实验分身 + ClawBio 深潜包。',
            humanRole: 'evidence_fellow',
            shadeId: 'omics_memory',
            aiPackId: 'clawbio_deep_dive',
            preferredExpert: 'clawbio_gwas',
            sessionTitle: 'SecondMe 协作圆桌：多组学深潜分析',
            sessionQuestion: '请把我的多组学分析上下文和 SecondMe 分身一起带入圆桌。先由 GWAS 专家介入，判断表型定义、QC 规则、关联分析路线以及后续是否需要 scRNA 或 PGx 协同。'
        }
    ];

    function clone(value) {
        return JSON.parse(JSON.stringify(value));
    }

    function getHumanRole(id) {
        return humanRoles.find((item) => item.id === id) || null;
    }

    function getShadeTemplate(id) {
        return shadeTemplates.find((item) => item.id === id) || null;
    }

    function getAiPack(id) {
        return aiPacks.find((item) => item.id === id) || null;
    }

    function getScenario(id) {
        return scenarios.find((item) => item.id === id) || null;
    }

    function createCollaborationSetup(options) {
        const humanRole = getHumanRole(options.humanRole);
        const shade = options.shadeId ? getShadeTemplate(options.shadeId) : null;
        const aiPack = getAiPack(options.aiPackId);

        if (!humanRole || !aiPack) {
            return null;
        }

        const humanParticipants = [
            {
                id: humanRole.id,
                name: humanRole.name,
                subtitle: humanRole.subtitle,
                source: 'human'
            }
        ];

        if (options.includeCoauthor) {
            const coauthor = getHumanRole('coauthor');
            if (coauthor && coauthor.id !== humanRole.id) {
                humanParticipants.push({
                    id: coauthor.id,
                    name: coauthor.name,
                    subtitle: coauthor.subtitle,
                    source: 'human'
                });
            }
        }

        const shades = shade ? [{
            id: shade.id,
            name: shade.name,
            subtitle: shade.subtitle,
            prompt: shade.prompt,
            source: 'secondme'
        }] : [];

        return {
            label: `${humanRole.name} + ${aiPack.name}`,
            humans: humanParticipants,
            shades,
            aiPack: {
                id: aiPack.id,
                name: aiPack.name,
                subtitle: aiPack.subtitle,
                expertRoles: clone(aiPack.expertRoles)
            }
        };
    }

    function buildScenarioPayload(scenarioId) {
        const scenario = getScenario(scenarioId);
        if (!scenario) return null;
        return {
            preferredExpert: scenario.preferredExpert,
            title: scenario.sessionTitle,
            question: scenario.sessionQuestion,
            collaborationSetup: createCollaborationSetup({
                humanRole: scenario.humanRole,
                shadeId: scenario.shadeId,
                aiPackId: scenario.aiPackId
            })
        };
    }

    window.MedRoundTableSecondMe = {
        humanRoles,
        shadeTemplates,
        aiPacks,
        scenarios,
        getHumanRole,
        getShadeTemplate,
        getAiPack,
        getScenario,
        createCollaborationSetup,
        buildScenarioPayload
    };
})();
