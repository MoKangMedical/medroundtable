(function () {
    const expertSkillBlueprints = {
        clinical_director: { laneIds: ['evidence-synthesis', 'trial-design', 'quality-compliance'], sourcePackageIds: ['medrt-local-core', 'ai-research-suite', 'medrt-enhanced-suite'], note: '从题目判断、方案路径到发表门槛，适合作为首位临床总控入口。' },
        phd_student: { laneIds: ['evidence-synthesis', 'data-fabric', 'research-automation'], sourcePackageIds: ['medrt-local-core', 'ai-research-suite'], note: '偏文献、证据和背景搭建，也适合把一句研究想法推进成自动化研究议程。' },
        epidemiologist: { laneIds: ['trial-design', 'data-fabric', 'quality-compliance'], sourcePackageIds: ['medrt-local-core', 'ai-research-suite', 'medrt-enhanced-suite'], note: '把临床问题转成规范 protocol，并提前控制偏倚和执行风险。' },
        statistician: { laneIds: ['trial-design', 'ai-modeling', 'workflow-export'], sourcePackageIds: ['medrt-local-core', 'ai-research-suite', 'medrt-enhanced-suite'], note: '适合在终点、样本量和结果表达已经开始成型时接手。' },
        research_nurse: { laneIds: ['trial-design', 'quality-compliance', 'workflow-export'], sourcePackageIds: ['medrt-local-core', 'medrt-enhanced-suite'], note: '主要盯访视、CRF、现场执行与合规质量，保障研究落地。' },
        clawbio_pharmgx: { laneIds: ['translational-drug', 'bioinformatics'], sourcePackageIds: ['openclaw-medical-wrapper', 'ai-research-suite'], note: '药物暴露和基因变异同时出现时，优先看这一组技能面。' },
        clawbio_gwas: { laneIds: ['bioinformatics', 'ai-modeling'], sourcePackageIds: ['openclaw-medical-wrapper', 'ai-research-suite'], note: '适合遗传关联、表型定义和 GWAS 结果解读任务。' },
        clawbio_sc_rna: { laneIds: ['bioinformatics', 'data-fabric'], sourcePackageIds: ['openclaw-medical-wrapper', 'ai-research-suite'], note: '偏单细胞样本、聚类和亚群注释时，从这里进入最直接。' },
        clawbio_galaxy: { laneIds: ['bioinformatics', 'workflow-export', 'data-fabric'], sourcePackageIds: ['openclaw-medical-wrapper', 'medrt-enhanced-suite'], note: '负责把多组学与工作流工具真正串起来，降低实验型试错。' },
        ux_researcher: { laneIds: ['ai-modeling', 'workflow-export'], sourcePackageIds: ['medrt-enhanced-suite', 'ai-research-suite'], note: '当你在研究流程、页面路径或协作体验上卡住时，用这组技能面。' },
        ai_data_engineer: { laneIds: ['data-fabric', 'ai-modeling', 'workflow-export', 'research-automation'], sourcePackageIds: ['openclaw-medical-wrapper', 'ai-research-suite', 'medrt-enhanced-suite'], note: '更偏数据口径、结构整理、联接与下游模型管道，也负责把自动科研流程接到真实算力和实验环境。' },
        trend_researcher: { laneIds: ['evidence-synthesis', 'translational-drug', 'research-automation'], sourcePackageIds: ['ai-research-suite', 'medrt-enhanced-suite'], note: '适合快速判断研究热点、竞品方向与投稿窗口，并把想法推进成可自动执行的研究路线。' },
        experiment_tracker: { laneIds: ['workflow-export', 'data-fabric', 'quality-compliance'], sourcePackageIds: ['medrt-local-core', 'medrt-enhanced-suite'], note: '看里程碑、偏差追踪和任务接力，防止项目执行失控。' },
        model_qa: { laneIds: ['quality-compliance', 'ai-modeling', 'research-automation'], sourcePackageIds: ['medrt-enhanced-suite', 'ai-research-suite'], note: '当你担心模型结论、偏差和鲁棒性时，从 QA 技能面进入；也适合给自动科研流程加质量门禁。' }
    };

    function needsParentPrefix() {
        return window.location.pathname.includes('/frontend/')
            || window.location.pathname.includes('/roundtables/');
    }

    function skillsMarketUrl(role) {
        const suffix = role ? `?expert=${encodeURIComponent(role)}` : '';
        if (window.location.pathname.includes('/frontend/')) {
            return `./skills-market.html${suffix}`;
        }
        if (window.location.pathname.includes('/roundtables/')) {
            return `../frontend/skills-market.html${suffix}`;
        }
        return `./frontend/skills-market.html${suffix}`;
    }

    function resolveAgentSkillDecks(catalog, expertCatalog) {
        if (!catalog || !expertCatalog) return [];

        const capabilityLanes = Array.isArray(catalog.capability_lanes) ? catalog.capability_lanes : [];
        const sourcePackages = Array.isArray(catalog.source_packages) ? catalog.source_packages : [];
        const laneMap = new Map(capabilityLanes.map((lane) => [lane.id, lane]));
        const sourcePackageMap = new Map(sourcePackages.map((item) => [item.id, item]));

        return expertCatalog.experts.map((expert) => {
            const blueprint = expertSkillBlueprints[expert.role] || { laneIds: [], sourcePackageIds: [], note: expert.summary };
            const group = expertCatalog.getGroup(expert.groupId) || null;
            const directLaneIds = capabilityLanes
                .filter((lane) => Array.isArray(lane.owner_roles) && lane.owner_roles.includes(expert.name))
                .map((lane) => lane.id);
            const laneIds = [...new Set([...(blueprint.laneIds || []), ...directLaneIds])]
                .filter((laneId) => laneMap.has(laneId));
            const lanes = laneIds.map((laneId) => laneMap.get(laneId));
            const packages = [...new Set(blueprint.sourcePackageIds || [])]
                .map((packageId) => sourcePackageMap.get(packageId))
                .filter(Boolean);
            const laneCoverageCount = lanes.reduce((sum, lane) => sum + Number(lane.count || 0), 0);
            const deliverables = [...new Set(lanes.flatMap((lane) => lane.deliverables || []))];

            return {
                expert,
                group,
                blueprint,
                lanes,
                packages,
                laneCoverageCount,
                deliverables
            };
        });
    }

    window.MedRoundTableAgentSkills = {
        expertSkillBlueprints,
        resolveAgentSkillDecks,
        skillsMarketUrl,
        needsParentPrefix
    };
}());
