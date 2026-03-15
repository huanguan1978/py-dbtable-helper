import unittest

import src.py_dbtable_helper.py_dbtable_helper as table

class TestWhere(unittest.TestCase):

    def setUp(self) -> None:
        return super().setUp()

    def tearDown(self) -> None:
        return super().tearDown()

    def test_standard_comparison(self):
        whereEQ = {"age": (">=", 25)}
        whereLIKE = {"name": ("LIKE", "Admin%")}
        paramEQ = {'w_age_0': 25}
        paramLIKE = {'w_name_0': 'Admin%'}

        table.paramstyle = table.ParamStyle.NAMED
        sql, dat = table._build_where(whereEQ)
        self.assertEqual(sql, 'age >= :w_age_0')
        self.assertDictEqual(dat, paramEQ)
        sql, dat = table._build_where(whereLIKE)
        self.assertEqual(sql, 'name LIKE :w_name_0')
        self.assertDictEqual(dat, paramLIKE)

        table.paramstyle = table.ParamStyle.PYFORMAT
        sql, dat = table._build_where(whereEQ)
        self.assertEqual(sql, 'age >= %(w_age_0)s')
        self.assertDictEqual(dat, paramEQ)
        sql, dat = table._build_where(whereLIKE)
        self.assertEqual(sql, 'name LIKE %(w_name_0)s')
        self.assertDictEqual(dat, paramLIKE)

    def test_in_clause(self):
        whereIN = {"status": ("IN", ['active', 'pending'])}
        paramIN = {'w_status_0_0': 'active', 'w_status_0_1': 'pending'}

        table.paramstyle = table.ParamStyle.NAMED
        sql, dat = table._build_where(whereIN)
        self.assertEqual(sql, 'status IN (:w_status_0_0, :w_status_0_1)')
        self.assertDictEqual(dat, paramIN)

        table.paramstyle = table.ParamStyle.PYFORMAT
        sql, dat = table._build_where(whereIN)
        self.assertEqual(sql, 'status IN (%(w_status_0_0)s, %(w_status_0_1)s)')
        self.assertDictEqual(dat, paramIN)

    def test_logic_nodes(self):
        whereOR = {
            "_or": [
                {"score": (">", 90)},
                {"status": ("=", "excellent")}
            ]
        }
        whereAND = {
            "_and": [
                {"score": (">", 90)},
                {"age": (">=", 18)}
            ]
        }

        paramOR = {'w_0_0_score_0': 90, 'w_0_1_status_0': 'excellent'}
        paramAND = {'w_0_0_score_0': 90, 'w_0_1_age_0': 18}

        table.paramstyle = table.ParamStyle.NAMED
        sql, dat = table._build_where(whereOR)
        self.assertEqual(
            sql, '(score > :w_0_0_score_0 OR status = :w_0_1_status_0)')
        self.assertDictEqual(dat, paramOR)
        sql, dat = table._build_where(whereAND)
        self.assertEqual(
            sql, '(score > :w_0_0_score_0 AND age >= :w_0_1_age_0)')
        self.assertDictEqual(dat, paramAND)

        table.paramstyle = table.ParamStyle.PYFORMAT
        sql, dat = table._build_where(whereOR)
        self.assertEqual(
            sql, '(score > %(w_0_0_score_0)s OR status = %(w_0_1_status_0)s)')
        self.assertDictEqual(dat, paramOR)
        sql, dat = table._build_where(whereAND)
        self.assertEqual(
            sql, '(score > %(w_0_0_score_0)s AND age >= %(w_0_1_age_0)s)')
        self.assertDictEqual(dat, paramAND)


class TestStmt(unittest.TestCase):

    def setUp(self) -> None:
        return super().setUp()

    def tearDown(self) -> None:
        return super().tearDown()

    def test_select(self):
        name = 'users'
        cols = ['name']
        where = {'balance': ('>', 50)}
        param = {'w_balance_0': 50}

        table.paramstyle = table.ParamStyle.NAMED
        sql, dat = table.select(name, cols=cols, where=where)
        self.assertEqual(
            sql, 'SELECT name FROM users WHERE balance > :w_balance_0')
        self.assertDictEqual(dat, param)

        table.paramstyle = table.ParamStyle.PYFORMAT
        sql, dat = table.select(name, cols=cols, where=where)
        self.assertEqual(
            sql, 'SELECT name FROM users WHERE balance > %(w_balance_0)s')
        self.assertDictEqual(dat, param)

    def test_insert(self):
        name = 'users'
        data = {"id": 1, "name": "Alice", "balance": 100.5}

        table.paramstyle = table.ParamStyle.NAMED
        sql, dat = table.insert(name, data=data)
        self.assertEqual(
            sql, 'INSERT INTO users (id, name, balance) VALUES (:id, :name, :balance)')
        self.assertDictEqual(dat, data)

        table.paramstyle = table.ParamStyle.PYFORMAT
        sql, dat = table.insert(name, data=data)
        self.assertEqual(
            sql, 'INSERT INTO users (id, name, balance) VALUES (%(id)s, %(name)s, %(balance)s)')
        self.assertDictEqual(dat, data)

    def test_update(self):
        name = 'users'
        data = {"balance": 200}
        where = {"id": ("=", 1)}
        param = {'balance': 200, 'w_id_0': 1}

        table.paramstyle = table.ParamStyle.NAMED
        sql, dat = table.update(name, data=data, where=where)
        self.assertEqual(
            sql, 'UPDATE users SET balance=:balance WHERE id = :w_id_0')
        self.assertDictEqual(dat, param)

        table.paramstyle = table.ParamStyle.PYFORMAT
        sql, dat = table.update(name, data=data, where=where)
        self.assertEqual(
            sql, 'UPDATE users SET balance=%(balance)s WHERE id = %(w_id_0)s')
        self.assertDictEqual(dat, param)

    def test_delete(self):
        name = 'users'
        where = {"id": ("IN", [1, 2, 3])}
        param = {'w_id_0_0': 1, 'w_id_0_1': 2, 'w_id_0_2': 3}

        table.paramstyle = table.ParamStyle.NAMED
        sql, dat = table.delete(name, where=where)
        self.assertEqual(
            sql, 'DELETE FROM users WHERE id IN (:w_id_0_0, :w_id_0_1, :w_id_0_2)')
        self.assertDictEqual(dat, param)

        table.paramstyle = table.ParamStyle.PYFORMAT
        sql, dat = table.delete(name, where=where)
        self.assertEqual(
            sql, 'DELETE FROM users WHERE id IN (%(w_id_0_0)s, %(w_id_0_1)s, %(w_id_0_2)s)')
        self.assertDictEqual(dat, param)

    def test_returning(self):
        name = 'users'
        data = {"name": "Alice", "balance": 80}

        table.paramstyle = table.ParamStyle.NAMED
        sql, dat = table.insert(name, data=data)
        self.assertEqual(
            sql, 'INSERT INTO users (name, balance) VALUES (:name, :balance)')
        self.assertDictEqual(dat, data)

        stmt = table.returning(sql)
        self.assertEqual(
            stmt, 'INSERT INTO users (name, balance) VALUES (:name, :balance) RETURNING *')

        stmt = table.returning(sql, ['id'])
        self.assertEqual(
            stmt, 'INSERT INTO users (name, balance) VALUES (:name, :balance) RETURNING id')
        stmt = table.returning(sql, ['id','name','balance'])
        self.assertEqual(
            stmt, 'INSERT INTO users (name, balance) VALUES (:name, :balance) RETURNING id, name, balance')