"""Idempotently add the observatory banner to the production homepage."""
from pathlib import Path
import sys

path = Path(sys.argv[1] if len(sys.argv) > 1 else "frontend/index.html")
source = path.read_text()
marker = "<!-- Full research observatory entry -->"
needle = '<p class="text-slate-600 mb-10 px-4 text-xl max-w-2xl mx-auto">AI 医学科研协作平台，多位专家共同为您的研究出谋划策</p>'
production_needle = '<div class="mt-8 max-w-4xl mx-auto">'
block = """
                <!-- Full research observatory entry -->
                <a href="real-analysis.html" class="group max-w-5xl mx-auto mb-10 text-left block overflow-hidden rounded-2xl bg-slate-950 text-white shadow-2xl shadow-slate-900/20 border border-emerald-400/30 hover:-translate-y-1 transition-all">
                    <div class="grid md:grid-cols-[1.3fr_.7fr] items-stretch">
                        <div class="p-7 md:p-9 bg-[radial-gradient(circle_at_top_right,rgba(16,185,129,.22),transparent_45%)]">
                            <div class="text-emerald-300 text-xs font-bold tracking-[.18em] mb-3">LIVE RESEARCH OBSERVATORY</div>
                            <h3 class="text-2xl md:text-3xl font-bold mb-3">打开全流程分析观察台</h3>
                            <p class="text-slate-300 max-w-2xl">实时查看 14 Agents 决策、Windows 本地执行、森林图、KM 曲线、基线表、统计结果和论文草稿。</p>
                        </div>
                        <div class="p-7 md:p-9 border-t md:border-t-0 md:border-l border-slate-700 flex items-center justify-between gap-5 bg-emerald-950/30">
                            <div><div class="text-3xl font-mono font-bold">6</div><div class="text-xs text-slate-400">研究阶段全程留痕</div></div>
                            <span class="w-12 h-12 rounded-full bg-emerald-500 grid place-items-center text-xl group-hover:translate-x-1 transition">→</span>
                        </div>
                    </div>
                </a>"""

if marker in source:
    print("observatory banner already present")
elif needle in source:
    path.write_text(source.replace(needle, needle + block, 1))
    print("observatory banner inserted")
elif production_needle in source:
    path.write_text(source.replace(production_needle, production_needle + block, 1))
    print("observatory banner inserted in production hero")
else:
    raise SystemExit("homepage insertion point not found")
