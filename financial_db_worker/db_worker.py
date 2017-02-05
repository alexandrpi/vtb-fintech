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

    def __init__(self, db_connection, table, schema='public'):
        self.__db = db_connection
        self.__schema = schema
        self.__table = table
        columns_query = 'SELECT column_name FROM information_schema.columns WHERE table_name={table}'
        columns = self.__db.query(columns_query.format(table=helpers.quote(self.__table))).getresult()
        self._columns = [c[0] for c in columns]

    def _insert(self, params):
        template = 'INSERT INTO {schema}."{table}" ({names}) VALUES ({values})'
        self.__db.query(template.format(schema=self.__schema,
                                        names=', '.join(map(helpers.quote2, self._columns[1:])),
                                        table=self.__table,
                                        values=', '.join(map(str, params))))

    def _update(self, conditions, kvals):
        template = 'UPDATE {schema}."{table}" SET ({keys}) = ({vals}) {condition}'
        condition = 'WHERE {}'.format(' AND '.join(conditions)) if conditions else ''
        keys, vals = [], []
        for k, v in kvals.items():
            keys.append(k)
            vals.append(v)
        self.__db.query(template.format(schema=self.__schema,
                                        keys=', '.join(keys),
                                        vals=', '.join(vals),
                                        condition=condition))

    def _get(self, conditions, columns):
        """Базовый SELECT-запрос"""
        condition = 'WHERE {}'.format(' AND '.join(conditions)) if conditions else ''
        template = 'SELECT {columns} FROM {schema}."{table}" {condition}'
        result = self.__db.query(template.format(schema=self.__schema,
                                                 table=self.__table,
                                                 columns='*' if not len(columns) else ', '.join(columns),
                                                 condition=condition))
        return result.dictresult()


class OperationsWorker(TableWorker):
    """Класс для работы с таблицей Operations"""
    __OP_CONDS = {'start_date': '"OperationDate" > \'{}\'',
                         'end_date': '"OperationDate" < \'{}\'',
                         'total_start': '"OperationTotal" > {}',
                         'total_end': '"OperationTotal" < {}'}

    def __init__(self, db_connection, schema):
        super().__init__(db_connection, 'Operations', schema)

    def add_operation(self, total, category_id, comment='', date=datetime.datetime.now()):
        self._insert([category_id, total, helpers.quote(date), helpers.quote(comment)])

    def get_operations(self, cnames=False, *columns, **conds):
        # TODO: доработать стандартный метод _get для использования пользовательских условий
        fields = [helpers.quote2(c) for c in columns if c in self._columns]
        conditions = []
        if conds:
            conditions = [self.__OP_CONDS[key].format(conds[key]) for key in conds]
        return self._get(conditions, fields)


class AccountWorker(TableWorker):
    """Класс для работы с таблицей Accounts"""
    __ACC_CONDS = {'acc_id': '"@Accounts = {}"'}

    def __init__(self, db_connection, schema):
        super().__init__(db_connection, 'Accounts', schema)

    def get_categories(self, *columns, **conds):
        # TODO: стоит вынести этот код в метод _get
        fields = [helpers.quote2(c) for c in columns if c in self._columns]
        conditions = []
        if conds:
            conditions = [self.__ACC_CONDS[key].format(conds[key]) for key in conds]
        return self._get(conditions, fields)


class CategoriesWorker(TableWorker):
    """Класс для работы с таблицей Accounts"""
    __CAT_CONDS = {'cat_id': '"@Categories = {}"'}

    def __init__(self, db_connection, schema):
        super().__init__(db_connection, 'Categories', schema)

    def get_categories(self, *columns, **conds):
        fields = [helpers.quote2(c) for c in columns if c in self._columns]
        conditions = []
        if conds:
            conditions = [self.__CAT_CONDS[key].format(conds[key]) for key in conds]
        return self._get(conditions, fields)
