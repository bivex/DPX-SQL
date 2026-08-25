import json
import os
from ....domain.detection import DetectionReport
from ....ports.outbound.exporter_port import ExporterPort


class SarifExporter(ExporterPort):
    def export(self, report: DetectionReport, output_path: str) -> None:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        rules = []
        rule_indices = {}
        results = []

        for d in report.detections:
            rule_id = f"DPX-SQL-{d.pattern_type.value.upper()}"
            if rule_id not in rule_indices:
                rule_indices[rule_id] = len(rules)
                rules.append({
                    "id": rule_id,
                    "name": d.pattern_type.name,
                    "shortDescription": {"text": d.summary},
                    "fullDescription": {"text": d.summary},
                    "properties": {
                        "category": d.category.value,
                        "confidence": d.confidence.level.value,
                    },
                })

            results.append({
                "ruleId": rule_id,
                "ruleIndex": rule_indices[rule_id],
                "level": "error" if d.category.value == "sql_security_hazards" else "note",
                "message": {"text": f"[{d.pattern_type.value}] detected on '{d.target_name}': {d.summary}"},
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {"uri": d.location.file_path},
                            "region": {
                                "startLine": d.location.line_number,
                                "startColumn": d.location.column_number,
                            },
                        }
                    }
                ],
            })

        sarif_payload = {
            "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
            "version": "2.1.0",
            "runs": [
                {
                    "tool": {
                        "driver": {
                            "name": "DPX-SQL",
                            "version": "0.1.0",
                            "informationUri": "https://github.com/bivex/DPX-SQL",
                            "rules": rules,
                        }
                    },
                    "results": results,
                }
            ],
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(sarif_payload, f, indent=2, ensure_ascii=False)
