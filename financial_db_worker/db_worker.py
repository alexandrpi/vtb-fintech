import pgdb


class FDBWorker:
    """Класс-подключение для работы с базой данных FinancialStatements"""

    def __init__(self, host='localhost', port=5432, username='postgres', password='postgres'):
        try:
            self.__connection = pgdb.connect(user=username,
                                             password=password,
                                             host='{host}:{port}'.format(host=host,
                                                                         port=port),
                                             database='FinancialStatements')
        except:
            self.__connection = None


class TableWorker:
    """Базовый класс для работы с таблицами базы FinancialStatements"""

    def __init__(self, db_connection, table, schema='public'):
        self.__db = db_connection
        self.__schema = schema
        self.__table = table


class OperationsWorker(TableWorker):
    """Класс для работы с таблицей Operations"""

    def __init__(self, db_connection, schema):
        super().__init__(db_connection, 'Operations', schema)

    def add_operation(self):
        pass
