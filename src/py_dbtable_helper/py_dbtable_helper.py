#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
py_dbtable_helper
=================
GitHub: https://github.com/huanguan1978/py-dbtable-helper
Author: crown.hg@gmail.com
License: LGPLv3

Overview
--------
An ultra-lightweight, zero-dependency SQL builder. It generates SQL strings and 
parameter dictionaries using Python dictionaries, preventing SQL injection 
via mandatory parameterization. Perfect for raw SQL control without heavy ORM overhead.

Core Types
----------
- `AnyDict`: Used for WHERE/HAVING clauses.
    - Simple: {"column": ("=", 10)}  => "column = :column"
    - IN: {"id": ("IN", [1, 2, 3])}  => "id IN (:id_0, :id_1, :id_2)"
    - Logic: {"_or": [{"a": (">", 1)}, {"b": ("<", 10)}]} => "(a > :a_0 OR b < :b_0)"
- `AnyPair`: A tuple `(sql: str, params: dict)`. 
    Pass it directly: `cursor.execute(*table.select(...))`

Parameter Styles
----------------
1. `ParamStyle.NAMED` (Default): Uses `:name`. (sqlite3, oracledb, pyodbc)
2. `ParamStyle.PYFORMAT`: Uses `%(key)s`. (psycopg2, PyMySQL, mysqlclient)

Switch globally:
    import py_dbtable_helper as table
    table.paramstyle = table.ParamStyle.PYFORMAT

Quick Start
-----------
import sqlite3
import py_dbtable_helper as table

conn = sqlite3.connect(":memory:")
cursor = conn.cursor()
cursor.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, balance REAL)")

# 1. INSERT
sql, params = table.insert("users", {"id": 1, "name": "Alice", "balance": 100})
cursor.execute(sql, params)

# 2. SELECT
where = {"_or": [{"balance": (">", 50)}, {"id": ("IN", [1, 2, 3])}]}
sql, params = table.select("users", cols=["name"], where=where)
cursor.execute(sql, params)

# 3. UPDATE
sql, params = table.update("users", {"balance": 200}, where={"id": ("=", 1)})
cursor.execute(sql, params)

# 4. DELETE
sql, params = table.delete("users", where={"id": ("=", 1)})
cursor.execute(sql, params)

# 5. RETURNING
sql, params = table.insert("users", {"name": "Alan", "balance": 90})

# Appends a RETURNING clause to INSERT, UPDATE, or DELETE statements (supports sqlite3, psycopg2, and psycopg3)
# default: returning * ; spec fields, e.g. table.returning(sql, ['id','name'])
sql = table.returning(sql, ['id']) # returning id
cur = cursor.execute(sql, params)
print(cur.fetchone())
"""

from typing import TypeAlias, Any
from enum import Enum

class ParamStyle(Enum):
    NAMED = 'named'
    PYFORMAT = 'pyformat'

AnyDict: TypeAlias = dict[str, Any]
AnyPair: TypeAlias = tuple[str, AnyDict]

# global paramstyle
paramstyle = ParamStyle.NAMED

def _placeholder(key: str) -> str:
    """Unified placeholder generation logic"""
    return f":{key}" if paramstyle == ParamStyle.NAMED else f"%({key})s"

def _build_where(where: AnyDict, prefix: str = "w") -> AnyPair:
    """Internal helper to build WHERE/HAVING clause with defensive checks."""
    clauses, params, counter = [], {}, 0

    def parse(key: str, val: Any, idx: int) -> str:
        if key in ["_or", "_and"]:
            logic = " OR " if key == "_or" else " AND "
            subs = [_build_where(s, f"{prefix}_{idx}_{i}")
                    for i, s in enumerate(val)]
            params.update({p: v for _, d in subs for p, v in d.items()})
            return f"({logic.join([s for s, _ in subs])})"

        op, value = val
        p_name = f"{prefix}_{key}_{idx}"
        if op.upper() == "IN":
            if not isinstance(value, (list, tuple)) or len(value) == 0:
                return '1=0'
            p_list = [f":{p_name}_{i}" for i in range(len(value))] if paramstyle == ParamStyle.NAMED else [
                f"%({p_name}_{i})s" for i in range(len(value))]
            params.update({f"{p_name}_{i}": v for i, v in enumerate(value)})
            return f"{key} IN ({', '.join(p_list)})"
        params[p_name] = value

        return f"{key} {op} {_placeholder(p_name)}"

    for k, v in where.items():
        clauses.append(parse(k, v, counter))
        counter += 1
    return " AND ".join(clauses) if clauses else "1=1", params


def select(table: str,
           cols: list[str] = ["*"],
           where: AnyDict | None = None,
           group_by: list[str] | None = None,
           having: AnyDict | None = None,
           order: AnyDict | None = None,
           limit: int | tuple[int, int] | None = None) -> AnyPair:
    """Build SELECT statement."""
    sql = f"SELECT {', '.join(cols)} FROM {table}"
    params = {}
    if where:
        w_sql, w_params = _build_where(where)
        sql += f" WHERE {w_sql}"
        params = w_params
    if group_by:
        sql += f" GROUP BY {', '.join(group_by)}"
    if having:
        h_sql, h_params = _build_where(having, "h")
        sql += f" HAVING {h_sql}"
        params.update(h_params)
    if order:
        sql += f" ORDER BY {', '.join([f'{k} {v}' for k, v in order.items()])}"
    if limit:
        sql += f" LIMIT {limit[0]}, {limit[1]}" if isinstance(
            limit, tuple) else f" LIMIT {limit}"
    return sql, params


def update(table: str, data: AnyDict, where: AnyDict) -> AnyPair:
    """Build UPDATE statement."""
    if not data:
        raise ValueError("update data cannot be empty.")

    set_sql = ', '.join([f"{k}={_placeholder(k)}" for k in data.keys()])
    w_sql, w_params = _build_where(where)
    return f"UPDATE {table} SET {set_sql} WHERE {w_sql}", {**data, **w_params}


def delete(table: str, where: AnyDict) -> AnyPair:
    """Build DELETE statement."""
    w_sql, w_params = _build_where(where)
    return f"DELETE FROM {table} WHERE {w_sql}", w_params


def insert(table: str, data: AnyDict) -> AnyPair:
    """Build INSERT statement."""
    if not data:
        raise ValueError("insert data cannot be empty.")
        
    keys = ", ".join(data.keys())
    vals = ", ".join([f"{_placeholder(k)}" for k in data.keys()])
    return f"INSERT INTO {table} ({keys}) VALUES ({vals})", data


def returning(sql:str, cols: list[str] = ["*"]) -> str:
    """Appends a RETURNING clause to INSERT, UPDATE, or DELETE statements (supports sqlite3, psycopg2, and psycopg3)"""
    if not sql:
        return sql
    if not sql.lstrip().startswith(('INSERT', 'UPDATE', 'DELETE')):
        raise ValueError("returning clause is only supported for insert, update, and delete statements.")

    return f"{sql} RETURNING {', '.join(cols)}"