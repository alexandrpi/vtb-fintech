import pgdb


class FDBWorker:
    """Класс для работы с базой данных FinancialStatements"""
    def __init__(self, host='localhost', port=5432, username='postgres', password='postgres'):
        try:
            self.__connection =  pgdb.connect(user=username,
                                              password=password,
                                              host='{host}:{port}'.format(host=host,
                                                                          port=port),
                                              database='FinancialStatements')
        except:
            self.__connection = None