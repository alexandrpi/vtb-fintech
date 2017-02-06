import pg
import datetime
import os
from . import helpers


class FDBWorker:
    """Класс-подключение для работы с базой данных FinancialStatements"""

    def __init__(self, host='localhost', port=5432, username='postgres', password='postgres'):
        self.__connection = pg.DB(user=username,
                                  passwd=password,
                                  host=host,
                                  port=port,
                                  dbname='FinancialStatements')
        self.query = self.__connection.query

    def create_schema(self, name):
        """Метод для создания схемы для нового пользователя"""
        with open(os.path.join(os.path.dirname(__file__), 'fs_new_schema.sql'), 'r') as schema_sql:
            self.query(schema_sql.read().format(username=name))

    def deploy_data(self, username, account_sum):
        """Заполнение таблиц заданной схемы стандартными данными, начисление на счёт первоначальной суммы"""
        here = os.path.dirname(__file__)
        with open(os.path.join(here, 'data_deploy.sql'), 'r') as fsdata:
            self.query(fsdata.read().format(username=username, path=here, account_sum=account_sum))

    def user_exist(self, username):
        """Проверяет, существует ли пользователь в базе, т.е. есть ли схема с данным именем"""
        check_sql = 'SELECT EXISTS(SELECT 1 FROM pg_namespace WHERE nspname = \'{username}\')'.format(username=username)
        result = self.query(check_sql)
        return result.dictresult()[0]['exists']

    def user_delete(self, username):
        """Удаялет схему пользователя, используется ТОЛЬКО для отладки"""
        self.query('DROP SCHEMA "{username}" CASCADE'.format(username=username))


class TableWorker:
    """Базовый класс для работы с таблицами базы FinancialStatements"""

    def __init__(self, db_connection, table, conditions, schema='public'):
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
        # TODO: исправить параметры на словарь именованных параметров
        keys, vals = [], []
        for k, v in kvals.items():
            keys.append(k)
            vals.append(v)
        template = 'INSERT INTO {schema}."{table}" ({names}) VALUES ({values})'
        self._db.query(template.format(schema=self._schema,
                                       names=', '.join(map(helpers.quote2, keys)),
                                       table=self.__table,
                                       values=', '.join(map(str, vals))))

    def _update(self, conditions, kvals):
        template = 'UPDATE {schema}."{table}" SET ({keys}) = ({vals}) {condition}'
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
        fields = [helpers.quote2(c) for c in columns if c in self._columns]
        conditions = []
        if conds:
            conditions = [self.__conds[key].format(conds[key]) for key in conds]
        condition = 'WHERE {}'.format(' AND '.join(conditions)) if conditions else ''
        template = 'SELECT {columns} FROM {schema}."{table}" {condition}'
        result = self._db.query(template.format(schema=self._schema,
                                                table=self.__table,
                                                columns='*' if not fields else ', '.join(fields),
                                                condition=condition))
        return result.dictresult()


class OperationsWorker(TableWorker):
    """Класс для работы с таблицей Operations"""

    def __init__(self, db_connection, schema):
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

    def get_operations(self, cnames=False, *columns, **conds):
        return self._get(*columns, **conds)


class AccountWorker(TableWorker):
    """Класс для работы с таблицей Accounts"""

    def __init__(self, db_connection, schema):
        acc_conds = {'acc_id': '"@Accounts = {}"'}
        super().__init__(db_connection, 'Accounts', acc_conds, schema)

    def get_accounts(self, *columns, **conds):
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
