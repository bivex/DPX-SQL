from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from .value_objects import SourceLocation


@dataclass
class SqlColumn:
    name: str
    data_type: str
    is_primary_key: bool = False
    is_foreign_key: bool = False
    references_table: Optional[str] = None
    references_column: Optional[str] = None
    is_nullable: bool = True
    default_value: Optional[str] = None
    line_number: int = 1


@dataclass
class SqlIndex:
    name: str
    table_name: str
    columns: List[str]
    is_unique: bool = False
    is_partial: bool = False
    where_clause: Optional[str] = None
    index_type: str = "BTREE"  # BTREE, GIN, GIST, BRIN, HASH
    includes: List[str] = field(default_factory=list)
    line_number: int = 1


@dataclass
class SqlView:
    name: str
    is_materialized: bool = False
    query_body: str = ""
    referenced_tables: List[str] = field(default_factory=list)
    line_number: int = 1


@dataclass
class SqlFunction:
    name: str
    parameters: List[str] = field(default_factory=list)
    return_type: str = "void"
    language: str = "plpgsql"  # plpgsql, sql, pltsql, c
    body: str = ""
    line_number: int = 1
    lines_count: int = 1
    has_dynamic_exec: bool = False
    has_cursor: bool = False
    has_savepoint: bool = False


@dataclass
class SqlTrigger:
    name: str
    table_name: str
    timing: str = "BEFORE"  # BEFORE, AFTER, INSTEAD OF
    events: List[str] = field(default_factory=list)  # INSERT, UPDATE, DELETE
    for_each: str = "ROW"  # ROW, STATEMENT
    function_name: str = ""
    line_number: int = 1


@dataclass
class SqlTable:
    name: str
    columns: List[SqlColumn] = field(default_factory=list)
    primary_keys: List[str] = field(default_factory=list)
    foreign_keys: List[Dict[str, str]] = field(default_factory=list)  # {from_col, to_table, to_col}
    check_constraints: List[str] = field(default_factory=list)
    is_unlogged: bool = False
    is_temporary: bool = False
    is_partitioned: bool = False
    partition_by: Optional[str] = None
    line_number: int = 1

    @property
    def column_count(self) -> int:
        return len(self.columns)


@dataclass
class SqlQuery:
    query_type: str  # SELECT, INSERT, UPDATE, DELETE, MERGE, WITH_RECURSIVE
    raw_text: str
    line_number: int = 1
    has_window_func: bool = False
    has_recursive_cte: bool = False
    has_upsert: bool = False
    has_lateral: bool = False
    has_select_star: bool = False
    has_for_update: bool = False
    has_order_by: bool = False


@dataclass
class SqlFile:
    file_path: str
    raw_content: str
    tables: List[SqlTable] = field(default_factory=list)
    indexes: List[SqlIndex] = field(default_factory=list)
    views: List[SqlView] = field(default_factory=list)
    functions: List[SqlFunction] = field(default_factory=list)
    triggers: List[SqlTrigger] = field(default_factory=list)
    queries: List[SqlQuery] = field(default_factory=list)
    sequences: List[str] = field(default_factory=list)


@dataclass
class CodeModel:
    files: List[SqlFile] = field(default_factory=list)
    table_index: Dict[str, SqlTable] = field(default_factory=dict)
    index_map: Dict[str, List[SqlIndex]] = field(default_factory=dict)  # table_name -> list of indexes

    def add_file(self, file: SqlFile) -> None:
        self.files.append(file)
        for tbl in file.tables:
            self.table_index[tbl.name.lower()] = tbl
        for idx in file.indexes:
            tbl_key = idx.table_name.lower()
            if tbl_key not in self.index_map:
                self.index_map[tbl_key] = []
            self.index_map[tbl_key].append(idx)

    def get_table(self, name: str) -> Optional[SqlTable]:
        return self.table_index.get(name.lower())

    def get_indexes_for_table(self, table_name: str) -> List[SqlIndex]:
        return self.index_map.get(table_name.lower(), [])
