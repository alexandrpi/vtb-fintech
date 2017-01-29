import pg
import datetime


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
        pass


class TableWorker:
    """Базовый класс для работы с таблицами базы FinancialStatements"""

    def __init__(self, db_connection, table, schema='public'):
        self.__db = db_connection
        self.__schema = schema
        self.__table = table
        columns_query = 'SELECT column_name FROM information_schema.columns WHERE table_name=\'{table}\''
        columns = self.__db.query(columns_query.format(table=self.__table)).getresult()
        self._columns = ['\"{}\"'.format(c[0]) for c in columns[1:]]

    def _insert(self, params):
        template = 'INSERT INTO {schema}."{table}" ({names}) VALUES ({values})'
        self.__db.query(template.format(schema=self.__schema,
                                        names=', '.join(self._columns),
                                        table=self.__table,
                                        values=', '.join(map(str, params))))

    def _get(self, conditions, columns):
        condition = ''
        if len(conditions) > 0:
            condition = 'WHERE {}'.format(' AND '.join(conditions))
        template = 'SELECT {columns} FROM {schema}."{table}" {condition}'
        result = self.__db.query(template.format(schema=self.__schema,
                                                 table=self.__table,
                                                 columns='*' if not len(columns) else ', '.join(columns),
                                                 condition=condition))
        return result.dictresult()


class OperationsWorker(TableWorker):
    """Класс для работы с таблицей Operations"""
    __OPERATION_CONDS = {'start_date': '"OperationDate" > \'{}\'',
                         'end_date': '"OperationDate" < \'{}\'',
                         'total_start': '"OperationTotal" > {}',
                         'total_end': '"OperationTotal" < {}'}

    def __init__(self, db_connection, schema):
        super().__init__(db_connection, 'Operations', schema)

    def add_operation(self, total, category_id, comment='', date=datetime.datetime.now()):
        self._insert([category_id, total, '\'{}\''.format(date), '\'{}\''.format(comment)])

    def get_operations(self, *columns, **conds):
        fields = ['\"{}\"'.format(c) for c in columns if c in self._columns]
        conditions = []
        if conds:
            conditions = [self.__OPERATION_CONDS[key].format(conds[key]) for key in conds]
        return self._get(conditions, fields)
