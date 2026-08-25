from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from .value_objects import PatternType, PatternCategory, Confidence, SourceLocation, EvidenceItem
from .pattern import PATTERN_CATALOG


@dataclass
class Detection:
    pattern_type: PatternType
    target_name: str
    location: SourceLocation
    confidence: Confidence
    evidence: List[EvidenceItem] = field(default_factory=list)
    custom_summary: Optional[str] = None

    @property
    def category(self) -> PatternCategory:
        meta = PATTERN_CATALOG.get(self.pattern_type)
        return meta.category if meta else PatternCategory.SQL_IDIOMATIC_OPTIMIZATION

    @property
    def summary(self) -> str:
        if self.custom_summary:
            return self.custom_summary
        meta = PATTERN_CATALOG.get(self.pattern_type)
        return meta.description if meta else ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pattern_type": self.pattern_type.value,
            "category": self.category.value,
            "target_name": self.target_name,
            "location": {
                "file_path": self.location.file_path,
                "line_number": self.location.line_number,
                "column_number": self.location.column_number,
            },
            "confidence": {
                "score": self.confidence.value,
                "percentage": self.confidence.percentage,
                "level": self.confidence.level.value,
            },
            "summary": self.summary,
            "evidence": [
                {
                    "rule_name": e.rule_name,
                    "weight": e.weight,
                    "description": e.description,
                    "location": str(e.location) if e.location else None,
                }
                for e in self.evidence
            ],
        }


@dataclass
class DetectionReport:
    target_path: str
    scanned_files_count: int
    execution_time_seconds: float
    detections: List[Detection] = field(default_factory=list)

    @property
    def total_detections(self) -> int:
        return len(self.detections)

    @property
    def category_counts(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for d in self.detections:
            cat = d.category.value
            counts[cat] = counts.get(cat, 0) + 1
        return counts

    @property
    def pattern_counts(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for d in self.detections:
            pt = d.pattern_type.value
            counts[pt] = counts.get(pt, 0) + 1
        return counts

    def to_dict(self) -> Dict[str, Any]:
        return {
            "target_path": self.target_path,
            "scanned_files_count": self.scanned_files_count,
            "execution_time_seconds": round(self.execution_time_seconds, 4),
            "total_detections": self.total_detections,
            "category_counts": self.category_counts,
            "detections": [d.to_dict() for d in self.detections],
        }
