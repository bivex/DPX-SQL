import os
from ....domain.detection import DetectionReport
from ....ports.outbound.exporter_port import ExporterPort


class MarkdownExporter(ExporterPort):
    def export(self, report: DetectionReport, output_path: str) -> None:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        md_lines = [
            f"# 🐘 DPX-SQL Analysis Report",
            f"",
            f"- **Target Path**: `{report.target_path}`",
            f"- **Scanned Files**: `{report.scanned_files_count}`",
            f"- **Execution Time**: `{report.execution_time_seconds:.4f}s`",
            f"- **Total Detections**: `{report.total_detections}`",
            f"",
            f"## 📊 Category Breakdown",
            f"",
            f"| Category | Detections |",
            f"|---|:---:|",
        ]

        for cat, count in sorted(report.category_counts.items(), key=lambda x: x[1], reverse=True):
            md_lines.append(f"| `{cat}` | {count} |")

        md_lines.extend([
            f"",
            f"## 🔍 Findings & Detections",
            f"",
            f"| # | Category | Pattern Type | Target | Confidence | Location | Summary |",
            f"|---|---|---|---|:---:|---|---|",
        ])

        for idx, d in enumerate(report.detections, start=1):
            loc_str = f"`{os.path.basename(d.location.file_path)}:{d.location.line_number}`"
            md_lines.append(
                f"| {idx} | `{d.category.value}` | `{d.pattern_type.value}` | `{d.target_name}` | **{d.confidence.percentage}%** [{d.confidence.level.value}] | {loc_str} | {d.summary} |"
            )

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(md_lines) + "\n")
