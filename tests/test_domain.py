import pytest
from pattern_detector.domain.value_objects import (
    PatternCategory,
    PatternType,
    ConfidenceLevel,
    Confidence,
    SourceLocation,
    EvidenceItem,
)
from pattern_detector.domain.pattern import PATTERN_CATALOG
from pattern_detector.domain.code_model import SqlTable, SqlColumn, SqlIndex, SqlView, SqlFunction, SqlTrigger, SqlQuery, SqlFile, CodeModel
from pattern_detector.domain.detection import Detection, DetectionReport


def test_confidence_levels():
    c1 = Confidence(0.95)
    assert c1.level == ConfidenceLevel.VERY_HIGH
    assert c1.percentage == 95

    c2 = Confidence(0.75)
    assert c2.level == ConfidenceLevel.HIGH

    c3 = Confidence(0.55)
    assert c3.level == ConfidenceLevel.MEDIUM

    c4 = Confidence(0.30)
    assert c4.level == ConfidenceLevel.LOW


def test_source_location_str():
    loc = SourceLocation(file_path="schema.sql", line_number=42, column_number=5)
    assert str(loc) == "schema.sql:42:5"


def test_pattern_catalog_integrity():
    assert len(PATTERN_CATALOG) >= 43
    for p_type, meta in PATTERN_CATALOG.items():
        assert meta.pattern_type == p_type
        assert meta.name
        assert meta.description
        assert 0.0 < meta.default_weight <= 1.0


def test_code_model_indexing():
    model = CodeModel()
    file = SqlFile(file_path="test.sql", raw_content="-- test")
    tbl = SqlTable(name="users", columns=[SqlColumn(name="id", data_type="bigint", is_primary_key=True)])
    idx = SqlIndex(name="idx_users_id", table_name="users", columns=["id"])
    file.tables.append(tbl)
    file.indexes.append(idx)
    model.add_file(file)

    assert model.get_table("users") == tbl
    assert model.get_table("USERS") == tbl
    assert len(model.get_indexes_for_table("users")) == 1


def test_detection_report_aggregation():
    loc = SourceLocation("test.sql", 10)
    d1 = Detection(
        pattern_type=PatternType.RECURSIVE_CTE_HIERARCHY,
        target_name="WITH_RECURSIVE",
        location=loc,
        confidence=Confidence(0.95),
    )
    d2 = Detection(
        pattern_type=PatternType.SQL_INJECTION_DYNAMIC_CONCAT_HAZARD,
        target_name="bad_func",
        location=loc,
        confidence=Confidence(0.95),
    )
    report = DetectionReport(
        target_path="test.sql",
        scanned_files_count=1,
        execution_time_seconds=0.012,
        detections=[d1, d2],
    )

    assert report.total_detections == 2
    assert "sql_idiomatic_optimization" in report.category_counts
    assert "sql_security_hazards" in report.category_counts
    assert report.pattern_counts[PatternType.RECURSIVE_CTE_HIERARCHY.value] == 1
    
    d_dict = report.to_dict()
    assert d_dict["total_detections"] == 2
