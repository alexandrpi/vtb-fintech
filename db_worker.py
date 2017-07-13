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
    Класс для работы с таблицей Users — пользователями.
    Поля таблицы:
    @Users: int — идентификатор пользователя в Telegram;
    PhoneNumber: str — номер телефона пользователя в формате 7XXXXXXXXXX (для РФ);
    VTBClient: bool — флаг, является ли пользователь клиентов ВТБ;
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
        :param user_data:
        Ключи словаря — имена столбцов таблицы.
        Поля @Users, PhoneNumber, VTBClient — обязательны.
        Подробное описание полей см. в описании класса.
        :type user_data: dict
        :return: None
        """
        cols = user_data.keys()
        required = '@Users', 'PhoneNumber', 'VTBClient'
        if any(param not in cols for param in required):
            raise TypeError(REQUIRED_PARAM_ERROR)
        query_tmpl = 'INSERT INTO "Users" ({columns}) VALUES ({values})'
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
        :param user_id: Telegram-идентификатор пользователя.
        :type user_id: int
        :return:
        """
        del_query = 'DELETE FROM "Users" WHERE "@Users" = $1'
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
        :rtype: List[Dict]
        """
        result = []
        if user_data:
            query_tmpl = 'SELECT * FROM "Users" WHERE {where_expr}'
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
        :param user_id:
        Telegram-идентификатор пользователя (поле @Users).
        :type user_id: int
        :param user_data: dict
        Ключи словаря — имена столбцов таблицы.
        Подробное описание полей см. в описании класса.
        :type user_data: dict
        :return: None
        """
        if user_data:
            query_tmpl = 'UPDATE "Users" SET ({columns}) = ({values}) WHERE "@Users" = ${user_param}'
            cols = user_data.keys()
            upd_query = query_tmpl.format(columns=', '.join(quote2(k) for k in cols),
                                          values=', '.join(prepared(len(cols))),
                                          user_param=len(cols) + 1)
            vals = [user_data[k] for k in cols] + [user_id]
            with pg.DB(**CONFIG_PARAMS) as conn:
                conn.query(upd_query, *vals)


class Drafts:
    """
    Класс для работы с таблицей Drafts — черновиками платёжных поручений.
    Поля таблицы:
    @Drafts: int — внутренний идентификатор платёжного поручения;
    PayerID: int — идентификатор пользователя-плательщика в Telegram / @Users плательщика;
    ReceiverID: int — идентификатор пользователя-получателя в Telegram / @Users получателя;
    PayerPN: str — номер телефона пользователя-плательщика в формате 7XXXXXXXXXX (для РФ);
    ReceiverPN: str — номер телефона пользователя-получателя в формате 7XXXXXXXXXX (для РФ);
    Reason: str — назначение платежа;
    Total: float — сумма платежа;
    DateFrom: datetime — дата и время создания платежа;
    Confirmed: bool — подтверждённость платёжного поручения получателем;
    """

    @staticmethod
    def new(draft_data: dict) -> int:
        """
        Метод для создания нового черновика платёжного поручения.
        :param draft_data:
        Ключи словаря — имена столбцов таблицы.
        Поле PayerID — обязательное.
        Подробное описание полей см. в описании класса.
        :type draft_data: dict
        :return: Идентификатор созданного платёжного поручения.
        :rtype: int
        """
        draft_id = 0
        cols = draft_data.keys()
        required = ('PayerID',)
        if any(param not in cols for param in required):
            raise TypeError(REQUIRED_PARAM_ERROR)
        if draft_data:
            query_tmpl = 'INSERT INTO "Drafts" ({columns}) VALUES ({values}) RETURNING "@Drafts"'
            ins_query = query_tmpl.format(columns=', '.join(quote2(k) for k in cols),
                                          values=', '.join(prepared(len(cols))))
            vals = [draft_data[k] for k in cols]
            with pg.DB(**CONFIG_PARAMS) as conn:
                draft_id = conn.query(ins_query, *vals).dictresult()[0]['@Drafts']
        return draft_id

    @staticmethod
    def get(draft_data: dict) -> QueryResult:
        """
        Получить платёжные поручения по данным
        :param draft_data:
        Ключи словаря — имена столбцов таблицы.
        Подробное описание полей см. в описании класса.
        В случае, если передан пустой словарь, метод вернёт пустой список.
        :type draft_data: dict
        :return: Возвращает список словарей, соответствующих переданным условиям.
        Ключи словаря — имена столбцов таблицы.
        Подробное описание полей см. в описании класса.
        Пустой список означает отсутствие данного платёжного поручения в БД.
        :rtype: List[Dict]
        """
        result = []
        if draft_data:
            query_tmpl = 'SELECT * FROM "Drafts" WHERE {where_expr}'
            cols = draft_data.keys()
            conditions = zip(map(quote2, cols), prepared(len(cols)))
            where_expr = ' AND '.join(' = '.join(cond) for cond in conditions)
            vals = [draft_data[k] for k in cols]
            sel_query = query_tmpl.format(where_expr=where_expr)
            with pg.DB(**CONFIG_PARAMS) as conn:
                result = conn.query(sel_query, *vals).dictresult()
        return result

    @staticmethod
    def update_with_data(draft_id: int, draft_data: dict):
        """
        Метод для обновления данных платёжного поручения.
        :param draft_id: Внутренний идентификатор платёжного поручения (поле @Drafts).
        :type draft_id: int
        :param draft_data: Данные о платёжном поручении
        Ключи словаря — имена столбцов таблицы.
        Подробное описание полей см. в описании класса.
        :type draft_data: dict
        :return: None
        """
        if draft_id:
            query_tmpl = 'UPDATE "Drafts" SET ({columns}) = ({values}) WHERE "@Drafts" = ${draft_param}'
            cols = draft_data.keys()
            upd_query = query_tmpl.format(columns=', '.join(quote2(k) for k in cols),
                                          values=', '.join(prepared(len(cols))),
                                          draft_param=len(cols) + 1)
            vals = [draft_data[k] for k in cols] + [draft_id]
            with pg.DB(**CONFIG_PARAMS) as conn:
                conn.query(upd_query, *vals)

    @staticmethod
    def update_last_with_data(user_id: int, draft_data: dict):
        """
        Метод для обновления данных последнего черновика платёжного поручения,
        созданного заданным пользователем.
        :param user_id: Telegram-идентификатор пользователя, создавшего платёжное поручение (поле PayerID).
        :type user_id: int
        :param draft_data: Данные о платёжном поручении
        Ключи словаря — имена столбцов таблицы.
        Подробное описание полей см. в описании класса.
        :type draft_data: dict
        :return: Внутренний идентификатор обновлённого платёжного поручения (поле @Drafts).
        В случае неуспеха возвращает 0.
        :rtype: int
        """
        updated_draft_id = 0
        if user_id and draft_data:
            query_tmpl = '''
            WITH DID AS (
            SELECT "@Drafts" FROM "Drafts"
            WHERE "PayerID" = ${user_param}
            ORDER BY "DateFrom" DESC
            LIMIT 1
            )
            UPDATE "Drafts" SET ({columns}) = ({values})
            WHERE "@Drafts" = (SELECT "@Drafts" FROM DID)
            RETURNING "@Drafts"
            '''
            cols = draft_data.keys()
            upd_query = query_tmpl.format(columns=', '.join(quote2(k) for k in cols),
                                          values=', '.join(prepared(len(cols))),
                                          user_param=len(cols) + 1)
            vals = [draft_data[k] for k in cols] + [user_id]
            with pg.DB(**CONFIG_PARAMS) as conn:
                updated_draft_id = conn.query(upd_query, *vals).dictresult()[0]['@Drafts']
        return updated_draft_id
