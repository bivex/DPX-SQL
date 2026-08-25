import os
import re
from typing import List, Dict, Optional, Tuple
from ....domain.code_model import (
    SqlColumn,
    SqlTable,
    SqlIndex,
    SqlView,
    SqlFunction,
    SqlTrigger,
    SqlQuery,
    SqlFile,
    CodeModel,
)
from ....ports.inbound.parser_port import SqlParserPort


class RegexSqlParser(SqlParserPort):
    """
    Robust, single-pass SQL parser supporting ANSI SQL, PostgreSQL, MySQL, SQLite, T-SQL, and PL/SQL.
    """

    def parse_file(self, file_path: str, content: str) -> SqlFile:
        sql_file = SqlFile(file_path=file_path, raw_content=content)
        
        # 1. Parse Sequences
        self._parse_sequences(content, sql_file)

        # 2. Parse Tables & Columns & Constraints
        self._parse_tables(content, sql_file)

        # 3. Parse ALTER TABLE Constraints (pg_dump format)
        self._parse_alter_tables(content, sql_file)

        # 4. Parse Indexes
        self._parse_indexes(content, sql_file)

        # 5. Parse Views
        self._parse_views(content, sql_file)

        # 6. Parse Functions & Stored Procedures
        self._parse_functions(content, sql_file)

        # 7. Parse Triggers
        self._parse_triggers(content, sql_file)

        # 8. Parse Queries & CTEs
        self._parse_queries(content, sql_file)

        return sql_file

    def parse_code_model(self, paths: List[str]) -> CodeModel:
        model = CodeModel()
        sql_extensions = {".sql", ".psql", ".ddl", ".dml", ".plsql", ".tsql", ".prc"}
        
        for path in paths:
            if os.path.isfile(path):
                ext = os.path.splitext(path)[1].lower()
                if ext in sql_extensions or not ext:
                    try:
                        with open(path, "r", encoding="utf-8", errors="replace") as f:
                            content = f.read()
                        sql_file = self.parse_file(path, content)
                        model.add_file(sql_file)
                    except Exception:
                        pass
            elif os.path.isdir(path):
                for root, _, files in os.walk(path):
                    for file in files:
                        ext = os.path.splitext(file)[1].lower()
                        if ext in sql_extensions:
                            full_path = os.path.join(root, file)
                            try:
                                with open(full_path, "r", encoding="utf-8", errors="replace") as f:
                                    content = f.read()
                                sql_file = self.parse_file(full_path, content)
                                model.add_file(sql_file)
                            except Exception:
                                pass
        return model

    def _get_line_number(self, content: str, match_start: int) -> int:
        return content.count("\n", 0, match_start) + 1

    def _parse_sequences(self, content: str, sql_file: SqlFile) -> None:
        pattern = re.compile(r'\bcreate\s+sequence\s+(if\s+not\s+exists\s+)?([a-zA-Z0-9_\.]+)', re.IGNORECASE)
        for match in pattern.finditer(content):
            seq_name = match.group(2)
            sql_file.sequences.append(seq_name)

    def _parse_tables(self, content: str, sql_file: SqlFile) -> None:
        # Match start of CREATE TABLE
        header_pattern = re.compile(
            r'\bcreate\s+(?:(unlogged|temporary|temp)\s+)?table\s+(?:if\s+not\s+exists\s+)?([a-zA-Z0-9_\.]+)\s*\(',
            re.IGNORECASE,
        )

        for match in header_pattern.finditer(content):
            qualifier = match.group(1) or ""
            table_name = match.group(2)
            header_end = match.end() - 1  # position of opening '('
            line_num = self._get_line_number(content, match.start())

            # Find matching closing parenthesis
            paren_depth = 1
            idx = header_end + 1
            body_start = idx
            body_end = -1
            while idx < len(content) and paren_depth > 0:
                if content[idx] == '(':
                    paren_depth += 1
                elif content[idx] == ')':
                    paren_depth -= 1
                    if paren_depth == 0:
                        body_end = idx
                        break
                idx += 1

            if body_end == -1:
                continue

            body = content[body_start:body_end]
            rest_clause = content[body_end+1:body_end+200]
            part_m = re.match(r'^\s*partition\s+by\s+([a-zA-Z0-9_\s\(\),]+)', rest_clause, re.IGNORECASE)
            partition_clause = part_m.group(1) if part_m else None

            is_unlogged = "unlogged" in qualifier.lower()
            is_temp = "temp" in qualifier.lower() or "temporary" in qualifier.lower()
            is_partitioned = bool(partition_clause)

            tbl = SqlTable(
                name=table_name,
                is_unlogged=is_unlogged,
                is_temporary=is_temp,
                is_partitioned=is_partitioned,
                partition_by=partition_clause.strip() if partition_clause else None,
                line_number=line_num,
            )

            # Parse columns and constraints within table body
            self._parse_table_body(body, tbl, line_num)
            sql_file.tables.append(tbl)

    def _parse_table_body(self, body: str, tbl: SqlTable, start_line: int) -> None:
        # Split statements in table body taking into account nested parenthesis
        lines = [line.strip() for line in body.splitlines() if line.strip()]
        
        # Extract constraints and column definitions
        # Clean inline commas outside parentheses
        chunks = []
        current = []
        paren_depth = 0
        for char in body:
            if char == '(':
                paren_depth += 1
                current.append(char)
            elif char == ')':
                paren_depth -= 1
                current.append(char)
            elif char == ',' and paren_depth == 0:
                chunks.append("".join(current).strip())
                current = []
            else:
                current.append(char)
        if current:
            chunks.append("".join(current).strip())

        for chunk in chunks:
            chunk_clean = chunk.strip().rstrip(",")
            if not chunk_clean or chunk_clean.startswith("--"):
                continue

            # Check PRIMARY KEY constraint: CONSTRAINT pk_name PRIMARY KEY (col1, col2) or PRIMARY KEY (col1)
            pk_match = re.search(r'\bprimary\s+key\s*\(([^)]+)\)', chunk_clean, re.IGNORECASE)
            if pk_match:
                pks = [c.strip().strip('"\'') for c in pk_match.group(1).split(",")]
                tbl.primary_keys.extend(pks)
                continue

            # Check FOREIGN KEY constraint: CONSTRAINT fk_name FOREIGN KEY (col) REFERENCES target_tbl (target_col) [ON DELETE ...]
            fk_match = re.search(
                r'\bforeign\s+key\s*\(([^)]+)\)\s+references\s+([a-zA-Z0-9_\.]+)\s*(?:\(([^)]+)\))?(?:\s+on\s+delete\s+([a-zA-Z\s]+))?',
                chunk_clean,
                re.IGNORECASE,
            )
            if fk_match:
                from_col = fk_match.group(1).strip().strip('"\'')
                to_tbl = fk_match.group(2).strip()
                to_col = (fk_match.group(3) or "id").strip().strip('"\'')
                on_delete = (fk_match.group(4) or "").strip()
                tbl.foreign_keys.append({
                    "from_col": from_col,
                    "to_table": to_tbl,
                    "to_col": to_col,
                    "on_delete": on_delete,
                })
                continue

            # Check CHECK constraint: CONSTRAINT chk_name CHECK (...) or CHECK (...)
            chk_match = re.search(r'\bcheck\s*\((.*)\)', chunk_clean, re.IGNORECASE | re.DOTALL)
            if chk_match:
                tbl.check_constraints.append(chk_match.group(1).strip())
                continue

            # Otherwise, this is a column definition: col_name data_type [DEFAULT ...] [NOT NULL] [PRIMARY KEY] [REFERENCES ...]
            col_match = re.match(r'^([a-zA-Z0-9_"]+)\s+([a-zA-Z0-9_\(\)]+)(.*)$', chunk_clean, re.IGNORECASE)
            if col_match:
                col_name = col_match.group(1).strip('"\'')
                data_type = col_match.group(2)
                rest = col_match.group(3)

                is_pk = "primary key" in rest.lower()
                is_fk = "references" in rest.lower()
                ref_tbl = None
                ref_col = None
                if is_fk:
                    ref_m = re.search(r'\breferences\s+([a-zA-Z0-9_\.]+)\s*(?:\(([^)]+)\))?', rest, re.IGNORECASE)
                    if ref_m:
                        ref_tbl = ref_m.group(1)
                        ref_col = ref_m.group(2) or "id"
                        on_del_m = re.search(r'\bon\s+delete\s+([a-zA-Z\s]+)', rest, re.IGNORECASE)
                        tbl.foreign_keys.append({
                            "from_col": col_name,
                            "to_table": ref_tbl,
                            "to_col": ref_col,
                            "on_delete": on_del_m.group(1).strip() if on_del_m else "",
                        })

                if is_pk:
                    tbl.primary_keys.append(col_name)

                is_nullable = "not null" not in rest.lower() and not is_pk
                default_val = None
                def_m = re.search(r'\bdefault\s+([^\s,]+)', rest, re.IGNORECASE)
                if def_m:
                    default_val = def_m.group(1)

                col = SqlColumn(
                    name=col_name,
                    data_type=data_type,
                    is_primary_key=is_pk,
                    is_foreign_key=is_fk,
                    references_table=ref_tbl,
                    references_column=ref_col,
                    is_nullable=is_nullable,
                    default_value=default_val,
                    line_number=start_line,
                )
                tbl.columns.append(col)

    def _parse_alter_tables(self, content: str, sql_file: SqlFile) -> None:
        # Matches ALTER TABLE [ONLY] [schema.]table_name ADD CONSTRAINT ...
        alter_pattern = re.compile(
            r'\balter\s+table\s+(?:only\s+)?([a-zA-Z0-9_\.]+)\s+add\s+constraint\s+([a-zA-Z0-9_]+)\s+(.*?)(?:;|\Z)',
            re.IGNORECASE,
        )

        table_dict = {t.name.lower(): t for t in sql_file.tables}
        # Also map without schema prefix e.g. public.users -> users
        for t in sql_file.tables:
            if "." in t.name:
                table_dict[t.name.split(".")[-1].lower()] = t

        for match in alter_pattern.finditer(content):
            tbl_name = match.group(1).strip()
            constraint_name = match.group(2).strip()
            body = match.group(3).strip()

            target_tbl = table_dict.get(tbl_name.lower()) or table_dict.get(tbl_name.split(".")[-1].lower())
            if not target_tbl:
                continue

            # Foreign key: FOREIGN KEY (from_col) REFERENCES to_table (to_col) [ON DELETE ...]
            fk_m = re.search(
                r'\bforeign\s+key\s*\(([^)]+)\)\s+references\s+([a-zA-Z0-9_\.]+)\s*(?:\(([^)]+)\))?(?:\s+on\s+delete\s+([a-zA-Z\s]+))?',
                body,
                re.IGNORECASE,
            )
            if fk_m:
                from_col = fk_m.group(1).strip().strip('"\'')
                to_tbl = fk_m.group(2).strip()
                to_col = (fk_m.group(3) or "id").strip().strip('"\'')
                on_delete = (fk_m.group(4) or "").strip()
                target_tbl.foreign_keys.append({
                    "from_col": from_col,
                    "to_table": to_tbl,
                    "to_col": to_col,
                    "on_delete": on_delete,
                })
                # Mark column as FK
                for c in target_tbl.columns:
                    if c.name.lower() == from_col.lower():
                        c.is_foreign_key = True
                        c.references_table = to_tbl
                        c.references_column = to_col
                continue

            # Primary key: PRIMARY KEY (col1, col2)
            pk_m = re.search(r'\bprimary\s+key\s*\(([^)]+)\)', body, re.IGNORECASE)
            if pk_m:
                pks = [c.strip().strip('"\'') for c in pk_m.group(1).split(",")]
                target_tbl.primary_keys.extend(pks)
                for c in target_tbl.columns:
                    if c.name.lower() in [p.lower() for p in pks]:
                        c.is_primary_key = True
                continue

            # Check constraint: CHECK (...)
            chk_m = re.search(r'\bcheck\s*\((.*)\)', body, re.IGNORECASE | re.DOTALL)
            if chk_m:
                target_tbl.check_constraints.append(chk_m.group(1).strip())
                continue

    def _parse_indexes(self, content: str, sql_file: SqlFile) -> None:
        # Matches CREATE [UNIQUE] INDEX [IF NOT EXISTS] idx_name ON tbl [USING method] (cols) [INCLUDE (cols)] [WHERE ...]
        index_pattern = re.compile(
            r'\bcreate\s+(unique\s+)?index\s+(?:if\s+not\s+exists\s+)?([a-zA-Z0-9_]+)\s+on\s+([a-zA-Z0-9_\.]+)(?:\s+using\s+([a-zA-Z0-9_]+))?\s*\(([^)]+)\)(?:\s+include\s*\(([^)]+)\))?(?:\s+where\s+([^;\n]+))?',
            re.IGNORECASE,
        )

        for match in index_pattern.finditer(content):
            is_unique = bool(match.group(1))
            idx_name = match.group(2)
            tbl_name = match.group(3)
            idx_type = match.group(4) or "BTREE"
            raw_cols = match.group(5)
            includes_raw = match.group(6)
            where_clause = match.group(7)
            line_num = self._get_line_number(content, match.start())

            cols = [c.strip().strip('"\'') for c in raw_cols.split(",")]
            inc_cols = [c.strip().strip('"\'') for c in includes_raw.split(",")] if includes_raw else []

            idx = SqlIndex(
                name=idx_name,
                table_name=tbl_name,
                columns=cols,
                is_unique=is_unique,
                is_partial=bool(where_clause),
                where_clause=where_clause.strip() if where_clause else None,
                index_type=idx_type.upper(),
                includes=inc_cols,
                line_number=line_num,
            )
            sql_file.indexes.append(idx)

    def _parse_views(self, content: str, sql_file: SqlFile) -> None:
        # Matches CREATE [OR REPLACE] [MATERIALIZED] VIEW view_name AS select_query
        view_pattern = re.compile(
            r'\bcreate\s+(?:or\s+replace\s+)?(materialized\s+)?view\s+([a-zA-Z0-9_\.]+)\s+as\s+(.*?)(?:;|\Z)',
            re.IGNORECASE | re.DOTALL,
        )

        for match in view_pattern.finditer(content):
            is_mat = bool(match.group(1))
            view_name = match.group(2)
            query_body = match.group(3).strip()
            line_num = self._get_line_number(content, match.start())

            view = SqlView(
                name=view_name,
                is_materialized=is_mat,
                query_body=query_body,
                line_number=line_num,
            )
            sql_file.views.append(view)

    def _parse_functions(self, content: str, sql_file: SqlFile) -> None:
        # Matches CREATE [OR REPLACE] FUNCTION/PROCEDURE name(...) RETURNS ... AS $$ body $$ LANGUAGE lang
        func_pattern = re.compile(
            r'\bcreate\s+(?:or\s+replace\s+)?(?:function|procedure)\s+([a-zA-Z0-9_\.]+)\s*\((.*?)\)(?:\s+returns\s+([a-zA-Z0-9_\.\s\(\)]+?))?\s+(?:as\s+\$\$|as\s+begin|as\s+\'|is\s+begin)(.*?)(?:\$\$\s*language\s*([a-zA-Z0-9_]+)|end\s*;\s*language\s*([a-zA-Z0-9_]+)|end\s*;|\$\$;)',
            re.IGNORECASE | re.DOTALL,
        )

        for match in func_pattern.finditer(content):
            fn_name = match.group(1)
            params_raw = match.group(2) or ""
            ret_type = (match.group(3) or "void").strip()
            body = match.group(4) or ""
            lang = match.group(5) or match.group(6) or "plpgsql"
            line_num = self._get_line_number(content, match.start())
            lines_count = len(body.splitlines())

            params = [p.strip() for p in params_raw.split(",") if p.strip()]

            fn = SqlFunction(
                name=fn_name,
                parameters=params,
                return_type=ret_type,
                language=lang.lower(),
                body=body,
                line_number=line_num,
                lines_count=lines_count,
                has_dynamic_exec=bool(re.search(r'\bexecute\b|\bsp_executesql\b', body, re.IGNORECASE)),
                has_cursor=bool(re.search(r'\bcursor\b|\bfetch\b', body, re.IGNORECASE)),
                has_savepoint=bool(re.search(r'\bsavepoint\b', body, re.IGNORECASE)),
            )
            sql_file.functions.append(fn)

    def _parse_triggers(self, content: str, sql_file: SqlFile) -> None:
        # Matches CREATE [OR REPLACE] TRIGGER name BEFORE/AFTER/INSTEAD OF events ON tbl FOR EACH ROW/STATEMENT EXECUTE FUNCTION fn()
        trigger_pattern = re.compile(
            r'\bcreate\s+(?:or\s+replace\s+)?trigger\s+([a-zA-Z0-9_]+)\s+(before|after|instead\s+of)\s+(.*?)\s+on\s+([a-zA-Z0-9_\.]+)(?:\s+for\s+each\s+(row|statement))?\s+execute\s+(?:function|procedure)\s+([a-zA-Z0-9_\.]+)',
            re.IGNORECASE,
        )

        for match in trigger_pattern.finditer(content):
            trg_name = match.group(1)
            timing = match.group(2).upper()
            events_raw = match.group(3).upper().strip()
            tbl_name = match.group(4)
            for_each = (match.group(5) or "ROW").upper()
            fn_name = match.group(6)
            line_num = self._get_line_number(content, match.start())

            events = [e.strip() for e in re.split(r'\s+OR\s+|\s*,\s*', events_raw, flags=re.IGNORECASE) if e.strip()]

            trg = SqlTrigger(
                name=trg_name,
                table_name=tbl_name,
                timing=timing,
                events=events,
                for_each=for_each,
                function_name=fn_name,
                line_number=line_num,
            )
            sql_file.triggers.append(trg)

    def _parse_queries(self, content: str, sql_file: SqlFile) -> None:
        # Extract top-level queries (SELECT, WITH, INSERT, UPDATE, DELETE, MERGE)
        query_pattern = re.compile(
            r'\b(with\s+recursive|with|select|insert\s+into|update|delete\s+from|merge\s+into)\b.*?(?:;|\Z)',
            re.IGNORECASE | re.DOTALL,
        )

        for match in query_pattern.finditer(content):
            q_type = match.group(1).upper()
            raw_q = match.group(0).strip()
            line_num = self._get_line_number(content, match.start())

            has_window = bool(re.search(r'\bover\s*\(', raw_q, re.IGNORECASE))
            has_recursive = bool(re.search(r'\bwith\s+recursive\b', raw_q, re.IGNORECASE))
            has_upsert = bool(re.search(r'\bon\s+conflict\b|\bmerge\s+into\b', raw_q, re.IGNORECASE))
            has_lateral = bool(re.search(r'\blateral\b|\bapply\b', raw_q, re.IGNORECASE))
            has_select_star = bool(re.search(r'\bselect\s+\*\s+from\b', raw_q, re.IGNORECASE))
            has_for_update = bool(re.search(r'\bfor\s+(update|share)\b', raw_q, re.IGNORECASE))
            has_order_by = bool(re.search(r'\border\s+by\b', raw_q, re.IGNORECASE))

            q = SqlQuery(
                query_type=q_type,
                raw_text=raw_q,
                line_number=line_num,
                has_window_func=has_window,
                has_recursive_cte=has_recursive,
                has_upsert=has_upsert,
                has_lateral=has_lateral,
                has_select_star=has_select_star,
                has_for_update=has_for_update,
                has_order_by=has_order_by,
            )
            sql_file.queries.append(q)
