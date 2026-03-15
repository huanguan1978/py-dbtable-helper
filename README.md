[English](https://github.com/huanguan1978/py-dbtable-helper/blob/main/README.md) | [Chinese
](https://github.com/huanguan1978/py-dbtable-helper/blob/main/README_ZH.md)

# py_dbtable_helper

py_dbtable_helper is an ultra-lightweight, dependency-free Python library designed to build SQL queries programmatically without the overhead of heavy ORMs.

## Why py_dbtable_helper?
While full-stack ORMs like SQLAlchemy or Django ORM are powerful, they often introduce significant complexity and performance overhead. py_dbtable_helper follows a **"SQL-First"** philosophy:
* **Zero Dependencies**: Pure Python standard library only.
* **SQL-Transparent**: Generates clean, readable SQL strings that are easy to debug and optimize.
* **Security-Focused**: Enforces parameterization by default to prevent **SQL Injection** attacks.

## 🎯 Core Features
* **Flexible Parameterization**: Supports both `named` (`:name`) and `pyformat` (`%(key)s`) styles to ensure compatibility with any DB-API 2.0 driver (e.g., sqlite3, psycopg2, PyMySQL, ...).
* **AnyDict & AnyPair**: A simple, intuitive API for defining `WHERE` clauses using nested dictionaries, returning a `(sql, params)` tuple ready for `cursor.execute()`.

## Configuration
You can switch the parameter placeholder style globally to match your database driver:

```python
import py_dbtable_helper as table

# Default is NAMED (:name) - compatible with sqlite3, oracledb
# Switch to PYFORMAT (%(key)s) for psycopg2, PyMySQL, etc.
table.paramstyle = table.ParamStyle.PYFORMAT
```

## Quick Start
Here is how to perform standard database operations:

```python
import sqlite3
import py_dbtable_helper as table

# Setup
conn = sqlite3.connect(":memory:")
cursor = conn.cursor()
cursor.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, balance REAL)")

# 1. INSERT: Secure parameter binding
sql, params = table.insert("users", {"id": 1, "name": "Alice", "balance": 100.5})
cursor.execute(sql, params)

# 2. SELECT: Powerful WHERE clauses using AnyDict
# Supports _and, _or, IN, and standard comparisons
where_cond = {
    "_or": [
        {"balance": (">", 50)},
        {"id": ("IN", [1, 2, 3])}
    ]
}
sql, params = table.select("users", cols=["name"], where=where_cond)
print(cursor.execute(sql, params).fetchone())

# 3. UPDATE: Clean and safe updates
sql, params = table.update("users", {"balance": 250}, where={"id": ("=", 1)})
cursor.execute(sql, params)

# 4. DELETE: Precise data removal
sql, params = table.delete("users", where={"id": ("=", 1)})
cursor.execute(sql, params)

# 5. RETURNING
sql, params = table.insert("users", {"name": "Alan", "balance": 90})

# Appends a RETURNING clause to INSERT, UPDATE, or DELETE statements (supports sqlite3, psycopg2, and psycopg3)
# default: returning * ; spec fields, e.g. table.returning(sql, ['id','name'])
sql = table.returning(sql)
cursor.execute(sql, params)
```

## 🪄 How it works (The Technical Details)
* **`AnyDict`**: A recursive dictionary structure used to build `WHERE` or `HAVING` clauses. It maps column names to operator-value tuples.
* **`AnyPair`**: The library returns a tuple containing the SQL string and a dictionary of parameters, ensuring that your application code remains decoupled from the specific SQL construction logic.


## ⛱ Security & Robustness
`py_dbtable_helper` goes beyond simple parameterization to ensure your database operations are safe and resilient:

*   **SQL Injection Prevention**: All inputs are automatically converted to named placeholders (e.g., `:w_id_0`). This eliminates the risk of string-concatenation-based SQL injection.
*   **Placeholder Safety**: The library generates deterministic, unique placeholder names to prevent naming collisions when using the same column multiple times in a single query.
*   **Defensive SQL Construction**:
    *   **Empty `IN` Clauses**: If you pass an empty list to an `IN` operator (e.g., `{"id": ("IN", [])}`), the library automatically generates `1=0` instead of a syntax-breaking `IN ()`. This ensures your query returns an empty result set safely rather than crashing.
    *   **Empty `WHERE` Logic**: If no conditions are provided, the library defaults to `1=1` to ensure valid SQL syntax, preventing unexpected syntax errors in your execution flow.

---
*`py_dbtable_helper` — Simple, safe, and native SQL building for modern Python projects.*