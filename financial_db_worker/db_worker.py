import pg
import datetime
import os
from . import helpers

# TODO: Написать докстринги и логирование!


class FDBWorker:
    """Класс-подключение для работы с базой данных FinancialStatements"""

    def __init__(self, host='localhost', port=5432, username='postgres', password='postgres'):
        self.__connection = pg.DB(user=username,
                                  passwd=password,
                                  host=host,
                                  port=port,
                                  dbname='FinancialStatements')

    def __del__(self):
        self.__connection.close()

    def close(self):
        self.__connection.close()

    def query(self, sql_command):
        return self.__connection.query(sql_command)

    def __create_schema(self, name):
        """Метод для создания схемы для нового пользователя"""
        with open(os.path.join(os.path.dirname(__file__), 'fs_new_schema.sql'), 'r') as schema_sql:
            self.query(schema_sql.read().format(username=name))

    def __deploy_data(self, username, account_sum):
        """Заполнение таблиц заданной схемы стандартными данными, начисление на счёт первоначальной суммы"""
        here = os.path.dirname(__file__)
        with open(os.path.join(here, 'data_deploy.sql'), 'r') as fsdata:
            self.query(fsdata.read().format(username=username, path=here, account_sum=account_sum))

    def user_exist(self, username):
        """Проверяет, существует ли пользователь в базе, т.е. есть ли схема с данным именем"""
        check_sql = 'SELECT EXISTS(SELECT 1 FROM pg_namespace WHERE nspname = \'{username}\')'.format(username=username)
        result = self.query(check_sql)
        return result.dictresult()[0]['exists']

    def create_user(self, username, acccount_sum):
        """Метод для создания нового пользователя"""
        self.__create_schema(username)
        self.__deploy_data(username, acccount_sum)

    def user_delete(self, username):
        """Удаялет схему пользователя, используется ТОЛЬКО для отладки"""
        self.query('DROP SCHEMA "{username}" CASCADE'.format(username=username))


class TableWorker:
    """Базовый класс для работы с таблицами базы FinancialStatements"""

    def __init__(self, db_connection, table, conditions, schema='test_user'):
        self._db = db_connection
        self._schema = schema
        self.__table = table
        self.__conds = {'ids': '{k}={v}'.format(k='"@{table}"'.format(table=self.__table),
                                                v='ANY(ARRAY{})')}
        self.__conds.update(conditions)
        columns_query = 'SELECT DISTINCT column_name FROM information_schema.columns WHERE table_name={table}'
        columns = self._db.query(columns_query.format(table=helpers.quote(self.__table))).getresult()
        self._columns = [c[0] for c in columns]

    def _insert(self, kvals):
        keys, vals = [], []
        for k, v in kvals.items():
            keys.append(k)
            vals.append(v)
        template = 'INSERT INTO "{schema}"."{table}" ({names}) VALUES ({values})'
        self._db.query(template.format(schema=self._schema,
                                       names=', '.join(map(helpers.quote2, keys)),
                                       table=self.__table,
                                       values=', '.join(map(str, vals))))

    def _update(self, conditions, kvals):
        template = 'UPDATE "{schema}"."{table}" SET ({keys}) = ({vals}) {condition}'
        condition = 'WHERE {}'.format(' AND '.join(conditions)) if conditions else ''
        keys, vals = [], []
        for k, v in kvals.items():
            keys.append(k)
            vals.append(v)
        self._db.query(template.format(schema=self._schema,
                                       keys=', '.join(keys),
                                       vals=', '.join(vals),
                                       condition=condition))

    def _get(self, *columns, **conds):
        """Базовый SELECT-запрос"""
        # TODO: доработать стандартный метод _get для использования пользовательских условий (JOIN и т.п.)
        join = None
        order_by = None
        group_by = None
        fields = [helpers.quote2(c) for c in columns if c in self._columns]
        conditions = []
        if conds:
            if conds.get('extra'):
                join = conds.pop('extra')
                conditions.extend(join.get('conds', []))
                fields.extend(join.get('columns', []))
                group_by = join.get('group_by')
                order_by = join.get('order_by')
            conditions = [self.__conds[key].format(conds[key]) for key in conds]
        condition = 'WHERE {}'.format(' AND '.join(conditions)) if conditions else ''
        template = 'SELECT {columns} FROM "{schema}"."{table}" {alias} {join} {condition} {group_by} {order_by}'
        result = self._db.query(template.format(schema=self._schema,
                                                table=self.__table,
                                                columns='*' if not fields else ', '.join(fields),
                                                condition=condition,
                                                alias='ops' if join else '',
                                                join=join['join'] if join else '',
                                                group_by='GROUP BY {}'.format(', '.join(group_by)) if group_by else '',
                                                order_by='ORDER BY {}'.format(', '.join(order_by)) if order_by else ''))
        return result.dictresult()


class OperationsWorker(TableWorker):
    """Класс для работы с таблицей Operations"""

    def __init__(self, db_connection, schema):
        # TODO: продумать функционал с единственной датой, или не надо?
        op_conds = {'start_date': '"OperationDate" > \'{}\'',
                    'end_date': '"OperationDate" < \'{}\'',
                    'total_start': '"OperationTotal" > {}',
                    'total_end': '"OperationTotal" < {}'}
        super().__init__(db_connection, 'Operations', op_conds, schema)

    def add_operation(self, **kwargs):
        kvals = {}
        err_tmpl = 'Не указан обязательный параметр: {param} ({desc})!'
        if kwargs.get('category_id'):
            kvals['@Categories'] = kwargs['category_id']
        else:
            raise TypeError(err_tmpl.format(param='category_id', desc='идентификатор категории'))
        if kwargs.get('total'):
            kvals['OperationTotal'] = kwargs['total']
        else:
            raise TypeError(err_tmpl.format(param='total', desc='сумма операции'))
        kvals['OperationDate'] = helpers.quote(kwargs['date'] if kwargs.get('comment') else datetime.datetime.now())
        kvals['Commentary'] = helpers.quote(kwargs['comment'] if kwargs.get('comment') else '')
        self._insert(kvals)

    def get_operations(self, *columns, **conds):
        return self._get(*columns, **conds)

    def get_by_cat_type(self, **conds):
        # TODO: проверить работоспособность метода вообще и на сгенерированных данных
        start_date, end_date, cat_type = conds.get('start_date'), conds.get('end_date'), conds.get('cat_type')
        if not all([start_date, end_date, cat_type]):
            raise TypeError('Не указаны обязательные параметры!')
        x_query = '''
        LEFT JOIN "{user}"."Categories" cats
        ON ops."@Categories" = cats."@Categories"
        '''.format(user=self._schema)
        x_conds = ['"CategoryType = {}"'.format(cat_type)]
        x_columns = ['"Name"', 'SUM("OperationTotal")']
        x_group_by = ['"Name"']
        x = {'columns': x_columns,
             'join': x_query,
             'conds': x_conds,
             'group_by': x_group_by}
        return self._get(start_date=start_date, end_date=end_date, extra=x)


class AccountWorker(TableWorker):
    """Класс для работы с таблицей Accounts"""

    def __init__(self, db_connection, schema):
        acc_conds = {'acc_id': '"@Accounts = {}"'}
        super().__init__(db_connection, 'Accounts', acc_conds, schema)

    def get_accounts(self, *columns, **conds):
        # TODO: доработать получение счетов в "красивом" виде + суммирование 58 и 59 счетов
        return self._get(*columns, **conds)


class CategoriesWorker(TableWorker):
    """Класс для работы с таблицей Categories"""

    def __init__(self, db_connection, schema):
        cat_conds = {'cat_id': '"@Categories = {}"'}
        super().__init__(db_connection, 'Categories', cat_conds, schema)

    def get_categories(self, *columns, **conds):
        return self._get(*columns, **conds)


class AssetsWorker(TableWorker):
    def __init__(self, db_connection, schema):
        assets_conds = {}
        super().__init__(db_connection, 'Assets', assets_conds, schema)

    def get_balance(self, ids=None):
        acc_totals = AccountWorker(self._db, self._schema).get_accounts('@Accounts', 'AccountTotal')
        totals = {'@{:03d}'.format(at['@Accounts']): at['AccountTotal'] for at in acc_totals}
        assets = self._get(**({'ids': ids} if ids else {}))
        for a in assets:
            a['CurrentTotal'] = eval(a.pop('AssetFormula').format(**totals))
        return assets
