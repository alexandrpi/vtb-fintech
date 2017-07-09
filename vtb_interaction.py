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
            # если токен получен, запишем его и срок истечения в БД
            token_data = {'AccessToken': resp_data['access_token'],
                          'TokenExpires': datetime.now() + timedelta(seconds=resp_data['expires_in'])}
            usr.update_with_data(user_id, token_data)
        return resp_data

    @staticmethod
    def update_user_data(user_id: int, access_token):
        route = 'accounts'
        headers = {'Authorization': f'Bearer {access_token}',
                   'Host': CLIENT_HOST}
        accs = requests.get(f'http://{VTB_HOST}/{route}', headers=headers)
        if accs.status_code == 200:
            orgs_data = accs.json()
            # Пока что будем исходить из предположения,
            # что на один телефон-аккаунт приходится одна организация
            if orgs_data and len(orgs_data) > 0:
                org_data = orgs_data[0]
                # соберем user_data
                user_data = {'Account': org_data['Acc'],
                             'INN': org_data['INN'],
                             'KPPs': [org_data['KPP']],
                             'BankName': org_data['Name_Bank'],
                             'BankBIC': org_data['BIC'],
                             'OrgName': org_data['Name_org']
                             }
                usr.update_with_data(user_id, user_data)

    @staticmethod
    def new_draft(draft_id, access_token):
        """Метод для создания нового платёжного поручения"""
        route = 'payment'
        headers = {'Authorization': f'Bearer {access_token}',
                   'Host': CLIENT_HOST}
        # Получим данные о платёжном поручении
        draft_data = drft.get({'@Draft': draft_id})[0]
        # Получим данные о плательщике и получателе платежа
        payer_data = usr.get({'@Users': draft_data['PayerID']})[0]
        reciever_data = usr.get({'@Users': draft_data['RecieverID']})[0]
        # Заполним данные для сервера
        payment = {'document_number': draft_id,  # номер документа
                   'sum': draft_data['Total'],  # сумма платежа
                   'purpose': draft_data['Reason'],  # назначение платежа
                   'payer_name': payer_data['OrgName'],  # наименование отправителя
                   'payer_inn': payer_data['INN'],  # ИНН отправителя
                   'payer_kpp': payer_data['KPP'][0],  # КПП отправителя
                   'payer_account': payer_data['Account'],  # номер счета отправителя
                   'payer_bank_bic': payer_data['BankBIC'],  # БИК банка отправителя
                   'payer_bank_name': payer_data['BankName'],  # наименование банка отправителя
                   'payer_bank_city': payer_data['BankCity'],  # город банка отправителя
                   'payer_bank_correspondent_account': payer_data['BankCorrAccount'],  # корр. счет банка отправителя
                   'payee_name': reciever_data['OrgName'],  # наименование получателя
                   'payee_inn': reciever_data['INN'],  # ИНН получателя
                   'payee_kpp': reciever_data['KPP'][0],  # КПП получателя
                   'payee_account': reciever_data['Account'],  # номер счета получателя
                   'payee_bank_bic': reciever_data['BankBIC'],  # БИК банка получателя
                   'payee_bank_name': reciever_data['BankName'],  # наименование банка получателя
                   'payee_bank_city': reciever_data['BankCity'],  # город банка получателя
                   'payee_bank_correspondent_account': reciever_data['BankCorrAccount']  # корр. счет банка получателя
                   }
        # Отправим запрос на создание платёжного поручения
        result = requests.post(f'http://{VTB_HOST}/{route}', data=payment, headers=headers)
        # TODO: Обрабатывать значения результата создания платёжного поручения
        # Изменим статус платёжного поручения на подверждённый
        drft.confirm(draft_id)

