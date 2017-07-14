import requests
from consts import VTB_HOST, CLIENT_ID, CLIENT_SECRET, CLIENT_HOST
from db_worker import Users as usr, Drafts as drft


class VTBProfile:

    @staticmethod
    def tokenize(auth_code: str, user_id: int):
        route = 'token'
        params = {'grant_type': 'authorization_code',
                  'code': auth_code,
                  'redirect_uri': f'https://{CLIENT_HOST}/vtb24/auth',
                  'client_id': CLIENT_ID,
                  'client_secret': CLIENT_SECRET}
        headers = {'Host': CLIENT_HOST}
        resp = requests.post(f'http://{VTB_HOST}/{route}', data=params, headers=headers)
        resp_data = resp.json()
        if resp.status_code == 200:
            from datetime import datetime, timedelta
            # Если токен получен, запишем его и срок действия
            token_data = {'AccessToken': resp_data['access_token'],
                          'TokenExpires': datetime.now() + timedelta(seconds=resp_data['expires_in'])}
            # Запросим данные пользователя для проверки реквизитов
            user_data = usr.get({'@Users': user_id})[0]
            if not user_data['INN']:
                # Если их не окажется, воспользуемся свежим токеном и получим их
                user_data = VTBProfile.get_user_data(token_data['AccessToken'])
            # В любом случае, дополним данные пользователя токеном и сроком действия
            user_data.update(token_data)
            # Избавимся от Telegram-идентификатора пользователя, если он есть
            user_data.pop('@Users', None)
            # Обновим данные пользователя
            usr.update_with_data(user_id, user_data)
        file = open('index.html', 'r')
        text_html = file.read()
        file.close()
        return text_html

    @staticmethod
    def get_user_data(access_token: str) -> dict:
        """Метод получения реквизитов пользователя из кабинета ВТБ24"""
        route = 'accounts'
        headers = {'Authorization': f'Bearer {access_token}',
                   'Host': CLIENT_HOST}
        accs = requests.get(f'http://{VTB_HOST}/{route}', headers=headers)
        user_data = {}
        if accs.status_code == 200:
            orgs_data = accs.json()
            # Пока что будем исходить из предположения,
            # что на один телефон-аккаунт приходится одна организация
            if orgs_data and len(orgs_data) > 0:
                org_data = orgs_data[0]
                # Соберем полученные данные пользователя в словарь с ключами из нашей БД
                user_data = {'Account': org_data['Acc'],
                             'INN': org_data['INN'],
                             'KPPs': org_data['KPP'],
                             'BankName': org_data['Name_Bank'],
                             'BankBIC': org_data['BIC'],
                             'OrgName': org_data['Name_org']
                             }
        return user_data

    @staticmethod
    def new_draft(draft_id: int, access_token: str):
        """Метод для создания нового платёжного поручения"""
        # Здесь по-идиотски получается всё:
        # 1) Артём мне даёт токен, т.е. идёт за ним в БД для начала;
        # 2) Я в свою очередь опять иду в БД и в итоге мы получаем лишний запрос;
        # FIXME: Нужно перенести проверку токена в данный метод.
        # Данная функция должна возвращать разные коды завершения (успешно, неуспешно, токен просрочен и т.д.)
        route = 'payment'
        headers = {'Authorization': f'Bearer {access_token}',
                   'Host': CLIENT_HOST}
        # Получим данные о платёжном поручении
        draft_data = drft.get({'@Drafts': draft_id})[0]
        # Получим данные о плательщике и получателе платежа
        payer_data = usr.get({'@Users': draft_data['PayerID']})[0]
        if not payer_data['INN']:
            # Если реквизитов пользователя не окажется,
            # воспользуемся свежим токеном и получим их
            user_update = VTBProfile.get_user_data(access_token)
            if user_update:
                # Если данные успешно получены, пробросим их дальше и обновим в БД
                payer_data.update(user_update)
                usr.update_with_data(draft_data['PayerID'], user_update)
            else:
                return
        receiver_data = usr.get({'@Users': draft_data['ReceiverID']})[0]
        # Заполним данные для сервера
        payment = {'document_number': draft_id,  # номер документа
                   'sum': draft_data['Total'],  # сумма платежа
                   'purpose': draft_data['Reason'],  # назначение платежа
                   'payer_name': payer_data['OrgName'],  # наименование отправителя
                   'payer_inn': payer_data['INN'],  # ИНН отправителя
                   'payer_kpp': payer_data['KPPs'],  # КПП отправителя
                   'payer_account': payer_data['Account'],  # номер счета отправителя
                   'payer_bank_bic': payer_data['BankBIC'],  # БИК банка отправителя
                   'payer_bank_name': payer_data['BankName'],  # наименование банка отправителя
                   'payer_bank_city': payer_data['BankCity'],  # город банка отправителя
                   'payer_bank_correspondent_account': payer_data['BankCorrAccount'],  # корр. счет банка отправителя
                   'payee_name': receiver_data['OrgName'],  # наименование получателя
                   'payee_inn': receiver_data['INN'],  # ИНН получателя
                   'payee_kpp': receiver_data['KPPs'],  # КПП получателя
                   'payee_account': receiver_data['Account'],  # номер счета получателя
                   'payee_bank_bic': receiver_data['BankBIC'],  # БИК банка получателя
                   'payee_bank_name': receiver_data['BankName'],  # наименование банка получателя
                   'payee_bank_city': receiver_data['BankCity'],  # город банка получателя
                   'payee_bank_correspondent_account': receiver_data['BankCorrAccount']  # корр. счет банка получателя
                   }
        # Отправим запрос на создание платёжного поручения
        resp = requests.post(f'http://{VTB_HOST}/{route}', data=payment, headers=headers)
        if resp.status_code == 200:
            # Изменим статус платёжного поручения на подтверждённый
            drft.update_with_data(draft_id, {'Confirmed': True})
        else:
            # TODO: Нужно умнее обрабатывать значения результата!!!
            # Просто залогируем угрожающее сообщение
            print('SOMETHING TERRIBLE HAPPEND, WHEN I WAS TRYING TO CREATE A DRAFT!!!')
        # В любом случае залогируем код ответа и описание результата
        print('HTTP status: {}\nVTB API response: {}'.format(resp.status_code, resp.json()))

