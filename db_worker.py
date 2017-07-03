import pg
from typing import List, Dict
from helpers import load_config, prepared, quote2

# TODO: Написать подробные комментарии и логирование

# загрузим параметры подключения к БД
CONFIG_PARAMS = load_config()

# region: Константы сообщений-ошибок
REQUIRED_PARAM_ERROR = 'Не указаны обязательные параметры!'
# endregion

# Возвращаемый тип результата запроса
QueryResult = List[Dict]


class Users:
    """
    Класс для работы с таблицей Organizations.
    Поля таблицы:
    @Organizations: int — внутренний идентификатор организации;
    PhoneNumber: str — номер телефона пользователя в формате 7XXXXXXXXXX (для РФ);
    TelegramID: int? — идентификатор пользователя Telegram;
    VTBClient: bool — флаг, является ли пользователь клиентов ВТБ;
    CLIENT_ID: int — идентификатор клиента ВТБ;
    CLIENT_SECRET: str — необходимое поле для идентификации клиента;
    INN: str — ИНН организации;
    KPPs: List[str] — список КПП организации;
    OrgName: str — наименование организации;
    Account: str — номер счёта организации;
    BankName: str — полное наименование банка организации;
    BankCity: str — город банка организации;
    BankBIC: str — БИК банка организации;
    BankCorrAccount: str — корреспондентский счёт банка.
    """

    @staticmethod
    def new(user_data: dict):
        """
        Метод для создания нового пользователя
        :param user_data: dict
        Ключи словаря — имена столбцов таблицы.
        Поля TelegramID, PhoneNumber, VTBClient — обязательны.
        Подробное описание полей см. в описании класса.
        :type user_data: dict
        :return: None
        """
        cols = user_data.keys()
        required = 'TelegramID', 'PhoneNumber', 'VTBClient'
        if any(param not in cols for param in required):
            raise TypeError(REQUIRED_PARAM_ERROR)
        query_tmpl = 'INSERT INTO "Organizations" ({columns}) VALUES ({values})'
        ins_query = query_tmpl.format(columns=', '.join(quote2(k) for k in cols),
                                      values=', '.join(prepared(len(cols))))
        vals = [user_data[k] for k in cols]
        with pg.DB(**CONFIG_PARAMS) as conn:
            conn.query(ins_query, *vals)

    @staticmethod
    def delete(user_id: int):
        """
        Метод для удаления пользователя.
        !!!Используется в отладочных целях!!!
        :param user_id: int
        :type user_id: int
        :return:
        """
        del_query = 'DELETE FROM "Orgranizations" WHERE "@Organizations" = $1'
        with pg.DB(**CONFIG_PARAMS) as conn:
            conn.query(del_query, user_id)

    @staticmethod
    def get(user_data: dict) -> QueryResult:
        """
        Получить пользователя по данным
        :param user_data:
        Ключи словаря — имена столбцов таблицы.
        Подробное описание полей см. в описании класса.
        В случае, если передан пустой словарь, метод вернёт пустой список.
        :type user_data: dict
        :return: Возвращает список словарей, соответствующих переданным условиям.
        Ключи словаря — имена столбцов таблицы.
        Подробное описание полей см. в описании класса.
        Пустой список означает отсутствие данного пользователя в БД.
        :rtype List[Dict]
        """
        result = []
        if user_data:
            query_tmpl = 'SELECT * FROM "Organizations" WHERE {where_expr}'
            cols = user_data.keys()
            conditions = zip(map(quote2, cols), prepared(len(cols)))
            where_expr = ' AND '.join(' = '.join(cond) for cond in conditions)
            vals = [user_data[k] for k in cols]
            sel_query = query_tmpl.format(where_expr=where_expr)
            with pg.DB(**CONFIG_PARAMS) as conn:
                result = conn.query(sel_query, *vals).dictresult()
        return result

    @staticmethod
    def update_with_data(user_id: int, user_data: dict):
        """
        Метод для обновления данных существующего пользователя.
        :param user_id: int
        Внутренний идентификатор пользователя (поле @Organizations).
        :type user_id: int
        :param user_data: dict
        Ключи словаря — имена столбцов таблицы.
        Поля TelegramID, PhoneNumber, VTBClient — обязательны.
        Подробное описание полей см. в описании класса.
        :type user_data: dict
        :return: None
        """
        if user_data:
            query_tmpl = 'UPDATE "Organizations" SET ({columns}) = ({values}) WHERE "@Organizations" = ${user_param}'
            cols = user_data.keys()
            upd_query = query_tmpl.format(columns=', '.join(quote2(k) for k in cols),
                                          values=', '.join(prepared(len(cols))),
                                          user_param=len(cols) + 1)
            vals = [user_data[k] for k in cols] + [user_id]
            with pg.DB(**CONFIG_PARAMS) as conn:
                conn.query(upd_query, *vals)
