import time
from typing import List, Optional
from ....domain.code_model import CodeModel
from ....domain.detection import Detection, DetectionReport
from ....domain.rules.base import Rule
from ....domain.rules import get_default_rules
from ....ports.inbound.detector_port import PatternDetectorPort


class SqlPatternDetector(PatternDetectorPort):
    def detect(self, model: CodeModel, custom_rules: Optional[List[Rule]] = None) -> DetectionReport:
        start_time = time.time()
        rules = custom_rules if custom_rules is not None else get_default_rules()
        
        all_detections: List[Detection] = []
        for rule in rules:
            try:
                results = rule.evaluate(model)
                all_detections.extend(results)
            except Exception:
                pass

        elapsed = time.time() - start_time
        target_path = model.files[0].file_path if model.files else "memory"
        
        return DetectionReport(
            target_path=target_path,
            scanned_files_count=len(model.files),
            execution_time_seconds=elapsed,
            detections=all_detections,
        )
