(function () {
  const toneStyles = {
    amber: {
      badge: 'bg-amber-100 text-amber-700',
      soft: 'bg-amber-50 border-amber-200',
      accent: 'text-amber-600',
      button: 'bg-amber-600 hover:bg-amber-700',
    },
    blue: {
      badge: 'bg-blue-100 text-blue-700',
      soft: 'bg-blue-50 border-blue-200',
      accent: 'text-blue-600',
      button: 'bg-blue-600 hover:bg-blue-700',
    },
    emerald: {
      badge: 'bg-emerald-100 text-emerald-700',
      soft: 'bg-emerald-50 border-emerald-200',
      accent: 'text-emerald-600',
      button: 'bg-emerald-600 hover:bg-emerald-700',
    },
    teal: {
      badge: 'bg-teal-100 text-teal-700',
      soft: 'bg-teal-50 border-teal-200',
      accent: 'text-teal-600',
      button: 'bg-teal-600 hover:bg-teal-700',
    },
    rose: {
      badge: 'bg-rose-100 text-rose-700',
      soft: 'bg-rose-50 border-rose-200',
      accent: 'text-rose-600',
      button: 'bg-rose-600 hover:bg-rose-700',
    },
    violet: {
      badge: 'bg-violet-100 text-violet-700',
      soft: 'bg-violet-50 border-violet-200',
      accent: 'text-violet-600',
      button: 'bg-violet-600 hover:bg-violet-700',
    },
    indigo: {
      badge: 'bg-indigo-100 text-indigo-700',
      soft: 'bg-indigo-50 border-indigo-200',
      accent: 'text-indigo-600',
      button: 'bg-indigo-600 hover:bg-indigo-700',
    },
    cyan: {
      badge: 'bg-cyan-100 text-cyan-700',
      soft: 'bg-cyan-50 border-cyan-200',
      accent: 'text-cyan-600',
      button: 'bg-cyan-600 hover:bg-cyan-700',
    },
    lime: {
      badge: 'bg-lime-100 text-lime-700',
      soft: 'bg-lime-50 border-lime-200',
      accent: 'text-lime-600',
      button: 'bg-lime-600 hover:bg-lime-700',
    },
    red: {
      badge: 'bg-red-100 text-red-700',
      soft: 'bg-red-50 border-red-200',
      accent: 'text-red-600',
      button: 'bg-red-600 hover:bg-red-700',
    },
    orange: {
      badge: 'bg-orange-100 text-orange-700',
      soft: 'bg-orange-50 border-orange-200',
      accent: 'text-orange-600',
      button: 'bg-orange-600 hover:bg-orange-700',
    },
    slate: {
      badge: 'bg-slate-200 text-slate-700',
      soft: 'bg-slate-100 border-slate-200',
      accent: 'text-slate-700',
      button: 'bg-slate-800 hover:bg-slate-900',
    },
  };

  function getToneStyle(tone) {
    return toneStyles[tone] || toneStyles.blue;
  }

  async function loadCatalog(relativePrefix) {
    const response = await fetch(`${relativePrefix}/data/platform-catalog.json`);
    if (!response.ok) {
      throw new Error(`无法加载平台目录: ${response.status}`);
    }
    return response.json();
  }

  function buildCategorySummary(databases) {
    const counts = databases.reduce((map, database) => {
      map[database.category] = (map[database.category] || 0) + 1;
      return map;
    }, {});
    return Object.entries(counts)
      .map(([name, count]) => ({ name, count }))
      .sort((a, b) => b.count - a.count || a.name.localeCompare(b.name, 'zh-Hans-CN'));
  }

  window.MRTPlatformCatalog = {
    loadCatalog,
    getToneStyle,
    buildCategorySummary,
  };
})();
