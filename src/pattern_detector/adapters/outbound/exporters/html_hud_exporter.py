import json
import os
from ....domain.detection import DetectionReport
from ....ports.outbound.exporter_port import ExporterPort


class HtmlHudExporter(ExporterPort):
    def export(self, report: DetectionReport, output_path: str) -> None:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        report_json = json.dumps(report.to_dict(), ensure_ascii=False)

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DPX-SQL | Architecture & Pattern HUD</title>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;800&family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-dark: #080c14;
            --card-bg: #0f172a;
            --border-color: #1e293b;
            --primary: #00d2ff;
            --primary-glow: rgba(0, 210, 255, 0.25);
            --sql-blue: #0064a5;
            --accent-green: #10b981;
            --accent-yellow: #f59e0b;
            --accent-red: #ef4444;
            --accent-purple: #8b5cf6;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
        }}

        * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: 'Inter', sans-serif; }}
        body {{ background-color: var(--bg-dark); color: var(--text-main); line-height: 1.6; padding: 24px; }}
        .hud-container {{ max-width: 1500px; margin: 0 auto; display: flex; flex-direction: column; gap: 24px; }}

        /* Top Header */
        .hud-header {{
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.9), rgba(0, 100, 165, 0.3));
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 24px 32px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
            backdrop-filter: blur(12px);
        }}
        .brand-title {{ display: flex; align-items: center; gap: 16px; }}
        .brand-logo {{
            font-size: 32px;
            background: linear-gradient(135deg, #00d2ff, #0064a5);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
            font-family: 'JetBrains Mono', monospace;
        }}
        .target-tag {{
            background: rgba(0, 210, 255, 0.1);
            color: var(--primary);
            border: 1px solid rgba(0, 210, 255, 0.3);
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 13px;
            font-family: 'JetBrains Mono', monospace;
        }}

        /* Metrics Bar */
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 16px;
        }}
        .metric-card {{
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 8px;
            transition: all 0.2s ease;
        }}
        .metric-card:hover {{
            border-color: var(--primary);
            box-shadow: 0 4px 20px var(--primary-glow);
        }}
        .metric-label {{ font-size: 12px; text-transform: uppercase; color: var(--text-muted); font-weight: 600; letter-spacing: 0.5px; }}
        .metric-value {{ font-size: 28px; font-weight: 800; color: var(--text-main); font-family: 'JetBrains Mono', monospace; }}

        /* Controls & Filter Bar */
        .filter-section {{
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 16px 20px;
            display: flex;
            flex-wrap: wrap;
            gap: 16px;
            align-items: center;
            justify-content: space-between;
        }}
        .search-input {{
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 10px 16px;
            color: var(--text-main);
            font-size: 14px;
            width: 320px;
            outline: none;
            transition: border-color 0.2s;
        }}
        .search-input:focus {{ border-color: var(--primary); }}
        .pills-container {{ display: flex; flex-wrap: wrap; gap: 8px; }}
        .filter-pill {{
            background: rgba(30, 41, 59, 0.6);
            border: 1px solid var(--border-color);
            color: var(--text-muted);
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }}
        .filter-pill.active, .filter-pill:hover {{
            background: rgba(0, 210, 255, 0.15);
            color: var(--primary);
            border-color: var(--primary);
        }}

        /* Findings Table */
        .findings-card {{
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            overflow: hidden;
        }}
        table {{ width: 100%; border-collapse: collapse; text-align: left; }}
        th {{
            background: #1e293b;
            color: var(--text-muted);
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            padding: 14px 20px;
            font-weight: 700;
        }}
        td {{ padding: 14px 20px; border-top: 1px solid var(--border-color); font-size: 14px; vertical-align: middle; }}
        tr:hover {{ background: rgba(0, 210, 255, 0.03); }}

        .badge-cat {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            font-family: 'JetBrains Mono', monospace;
        }}
        .cat-sql_idiomatic_optimization {{ background: rgba(0, 210, 255, 0.15); color: #00d2ff; border: 1px solid #00d2ff; }}
        .cat-relational_indexing_schema {{ background: rgba(16, 185, 129, 0.15); color: #10b981; border: 1px solid #10b981; }}
        .cat-procedural_transaction_control {{ background: rgba(139, 92, 246, 0.15); color: #8b5cf6; border: 1px solid #8b5cf6; }}
        .cat-creational {{ background: rgba(59, 130, 246, 0.15); color: #3b82f6; border: 1px solid #3b82f6; }}
        .cat-structural {{ background: rgba(245, 158, 11, 0.15); color: #f59e0b; border: 1px solid #f59e0b; }}
        .cat-behavioral {{ background: rgba(236, 72, 153, 0.15); color: #ec4899; border: 1px solid #ec4899; }}
        .cat-sql_security_hazards {{ background: rgba(239, 68, 68, 0.2); color: #ef4444; border: 1px solid #ef4444; }}
        .cat-solid_principles {{ background: rgba(234, 179, 8, 0.15); color: #eab308; border: 1px solid #eab308; }}

        .confidence-bar {{
            width: 80px;
            height: 6px;
            background: #1e293b;
            border-radius: 3px;
            overflow: hidden;
            display: inline-block;
            vertical-align: middle;
            margin-right: 8px;
        }}
        .confidence-fill {{ height: 100%; background: linear-gradient(90deg, #0064a5, #00d2ff); }}

        .btn-copy {{
            background: rgba(0, 210, 255, 0.1);
            color: var(--primary);
            border: 1px solid var(--primary);
            padding: 6px 12px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 12px;
            font-weight: 600;
            transition: all 0.2s;
        }}
        .btn-copy:hover {{ background: var(--primary); color: #000; }}
    </style>
</head>
<body>
    <div class="hud-container">
        <!-- Top Header -->
        <header class="hud-header">
            <div class="brand-title">
                <span class="brand-logo">🐘 DPX-SQL</span>
                <span class="target-tag" id="headerPath">Schema & Query Analyzer</span>
            </div>
            <div>
                <button class="btn-copy" onclick="copyAiSummary()">🤖 Copy for AI Context</button>
            </div>
        </header>

        <!-- Metrics Grid -->
        <section class="metrics-grid">
            <div class="metric-card">
                <div class="metric-label">Total Detections</div>
                <div class="metric-value" id="metricTotal">0</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Scanned Files</div>
                <div class="metric-value" id="metricFiles">0</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Execution Time</div>
                <div class="metric-value" id="metricTime">0.00s</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Security Hazards</div>
                <div class="metric-value" style="color: var(--accent-red)" id="metricHazards">0</div>
            </div>
        </section>

        <!-- Search and Filter Pills -->
        <section class="filter-section">
            <input type="text" class="search-input" id="searchInput" placeholder="Search tables, patterns, rules..." oninput="filterResults()">
            <div class="pills-container" id="pillsContainer">
                <div class="filter-pill active" onclick="setCategoryFilter('ALL')">ALL</div>
            </div>
        </section>

        <!-- Findings Table -->
        <section class="findings-card">
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Category</th>
                        <th>Pattern Type</th>
                        <th>Target Symbol</th>
                        <th>Confidence</th>
                        <th>Location</th>
                        <th>Summary</th>
                    </tr>
                </thead>
                <tbody id="findingsBody">
                    <!-- Injected via JS -->
                </tbody>
            </table>
        </section>
    </div>

    <script>
        const reportData = {report_json};
        let activeCategory = 'ALL';

        function initDashboard() {{
            document.getElementById('headerPath').innerText = reportData.target_path;
            document.getElementById('metricTotal').innerText = reportData.total_detections;
            document.getElementById('metricFiles').innerText = reportData.scanned_files_count;
            document.getElementById('metricTime').innerText = reportData.execution_time_seconds + 's';
            
            const hazards = reportData.category_counts['sql_security_hazards'] || 0;
            document.getElementById('metricHazards').innerText = hazards;

            // Generate filter pills
            const pillsContainer = document.getElementById('pillsContainer');
            Object.keys(reportData.category_counts || {{}}).forEach(cat => {{
                const pill = document.createElement('div');
                pill.className = 'filter-pill';
                pill.innerText = `${{cat}} (${{reportData.category_counts[cat]}})`;
                pill.onclick = () => setCategoryFilter(cat);
                pillsContainer.appendChild(pill);
            }});

            renderTable(reportData.detections);
        }}

        function setCategoryFilter(cat) {{
            activeCategory = cat;
            document.querySelectorAll('.filter-pill').forEach(el => {{
                if (el.innerText.startsWith(cat) || (cat === 'ALL' && el.innerText === 'ALL')) {{
                    el.classList.add('active');
                }} else {{
                    el.classList.remove('active');
                }}
            }});
            filterResults();
        }}

        function filterResults() {{
            const query = document.getElementById('searchInput').value.toLowerCase();
            const filtered = reportData.detections.filter(d => {{
                const matchesCat = activeCategory === 'ALL' || d.category === activeCategory;
                const matchesQuery = d.target_name.toLowerCase().includes(query) ||
                    d.pattern_type.toLowerCase().includes(query) ||
                    d.summary.toLowerCase().includes(query) ||
                    d.location.file_path.toLowerCase().includes(query);
                return matchesCat && matchesQuery;
            }});
            renderTable(filtered);
        }}

        function renderTable(detections) {{
            const tbody = document.getElementById('findingsBody');
            tbody.innerHTML = '';
            detections.forEach((d, idx) => {{
                const tr = document.createElement('tr');
                const catClass = 'cat-' + d.category;
                const fileName = d.location.file_path.split('/').pop();
                
                tr.innerHTML = `
                    <td>${{idx + 1}}</td>
                    <td><span class="badge-cat ${{catClass}}">${{d.category}}</span></td>
                    <td style="font-family: 'JetBrains Mono'; font-weight: 600;">${{d.pattern_type}}</td>
                    <td><code style="color: var(--primary); font-weight: 600;">${{d.target_name}}</code></td>
                    <td>
                        <div class="confidence-bar"><div class="confidence-fill" style="width: ${{d.confidence.percentage}}%"></div></div>
                        <span style="font-size: 12px; font-weight: 700;">${{d.confidence.percentage}}%</span>
                    </td>
                    <td style="font-family: 'JetBrains Mono'; font-size: 12px; color: var(--text-muted);">${{fileName}}:${{d.location.line_number}}</td>
                    <td style="font-size: 13px; color: #cbd5e1;">${{d.summary}}</td>
                `;
                tbody.appendChild(tr);
            }});
        }}

        function copyAiSummary() {{
            const text = JSON.stringify(reportData, null, 2);
            navigator.clipboard.writeText(text).then(() => {{
                alert('Copied full analysis JSON to clipboard for AI Prompt injection!');
            }});
        }}

        window.onload = initDashboard;
    </script>
</body>
</html>
"""
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)
