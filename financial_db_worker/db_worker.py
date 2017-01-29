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
        self.__columns = ['\"{}\"'.format(c[0]) for c in columns[1:]]

    def insert(self, params):
        template = 'INSERT INTO {schema}."{table}" ({names}) VALUES ({values})'
        self.__db.query(template.format(schema=self.__schema,
                                        names=', '.join(self.__columns),
                                        table=self.__table,
                                        values=', '.join(map(str, params))))


class OperationsWorker(TableWorker):
    """Класс для работы с таблицей Operations"""

    def __init__(self, db_connection, schema):
        super().__init__(db_connection, 'Operations', schema)

    def add_operation(self, total, category_id, comment='', date=datetime.datetime.now()):
        self.insert([category_id, total, '\'{}\''.format(date), '\'{}\''.format(comment)])
