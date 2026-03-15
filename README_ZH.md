# py_dbtable_helper

一个极其轻量、简洁且功能强大的 Python SQL 构建辅助工具库。

## 为什么需要这个包？

在 Python 生态中，SQLAlchemy、Peewee 和 Django ORM 等全能型框架确实功能强大，但它们通常存在以下“负担”：
* **重型依赖**：引入庞大的 ORM 往往会显著增加项目体积。
* **黑盒效应**：复杂的 ORM 语法有时会屏蔽 SQL 原生逻辑，难以直观预测生成的 SQL。
* **场景局限**：对于快速原型开发、微服务组件或仅需轻量级 CRUD 操作时，ORM 显得过于冗余。

**py_dbtable_helper** 旨在填补“原生 SQL”与“重型 ORM”之间的空白。它不绑定任何数据库驱动，仅使用 Python 标准库，让您在保持 SQL 原生执行力的同时，通过 Python 数据结构优雅地构建 SQL。

## ⛱ 安全与防御性编程 (Security & Robustness)

**py_dbtable_helper** 在设计之初就融入了防御性编程理念，确保您的数据库操作既安全又稳健：

* **防范 SQL 注入**：所有输入数据均被强制参数化。库会自动将其转换为命名占位符（如 `:w_id_0`），彻底杜绝拼接 SQL 字符串带来的注入风险。
* **占位符安全性**：库会生成确定性的、唯一的占位符名称，有效防止在复杂查询中多次引用同一字段时产生的命名冲突。
* **防御性 SQL 构建**：
    * **处理空 `IN` 子句**：当 `IN` 操作符对应的列表为空（例如 `{"id": ("IN", [])}`）时，库会自动生成 `1=0` 替代无效的 `IN ()` 语法。这确保查询将安全地返回空结果集，而不是导致 SQL 语法错误。
    * **处理空 `WHERE` 逻辑**：当未提供查询条件时，库会自动填充 `1=1`，确保生成的 SQL 语句语法完整。

## 🪄 核心概念

1. **AnyDict (定义条件)**：通过一种嵌套的字典结构，以极低的心智负担定义 `WHERE` 子句。支持 `=`、`>`、`<`、`LIKE`、`IN` 以及 `_and`/`_or` 逻辑组合。
2. **AnyPair (SQL 输出)**：函数返回一个 `(sql_string, parameters)` 元组，可直接透传给数据库驱动的 `execute()` 方法。
3. **全局配置**：可通过 `table.paramstyle` 切换参数风格（默认风格为 `named :name`，适用于 sqlite3 等；若使用 psycopg2 等，可切换风格为 `pyformat %(key)s`）。

## 完整操作示例

```python
import sqlite3
import py_dbtable_helper as table

# 1. 全局配置（按需切换）
# table.paramstyle = table.ParamStyle.PYFORMAT  # 若使用 psycopg2 等

# 2. 准备连接
conn = sqlite3.connect(":memory:")
cursor = conn.cursor()
cursor.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, balance REAL)")

# 3. INSERT: 自动参数化插入
data = {"id": 1, "name": "Alice", "balance": 100.5}
sql, params = table.insert("users", data)
cursor.execute(sql, params)

# 4. SELECT: 复杂逻辑组合查询
# 自动防注入，支持嵌套查询
where_cond = {
    "_or": [
        {"balance": (">", 50)},
        {"id": ("IN", [1, 2, 3])}
    ]
}
sql, params = table.select("users", cols=["name", "balance"], where=where_cond)
print(cursor.execute(sql, params).fetchall())

# 5. UPDATE: 结构化更新
sql, params = table.update("users", {"balance": 200}, where={"id": ("=", 1)})
cursor.execute(sql, params)

# 6. DELETE: 精确删除
sql, params = table.delete("users", where={"id": ("=", 1)})
cursor.execute(sql, params)

conn.commit()
```

## 特性速览

* **极度轻量**：仅一个 Python 文件，无外部依赖，可直接放入源码中复用。
* **SQL 原生感**：生成的 SQL 清晰易读，方便在数据库中直接调试。
* **完全解耦**：兼容任何支持 DB-API 2.0 的数据库驱动。


*`py_dbtable_helper` — 让 Python 的数据库操作回归简单、安全与高效。*