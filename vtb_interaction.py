import requests
from db_worker import Users as usr, Drafts as drft

VTB_HOST = 'http://82.202.199.51/{route}'


class VTB:
    @staticmethod
    def update_user_data(user_id: int, token):
        route = 'accounts'
        headers = {'Authorization': 'Bearer ' + token}
        accs = requests.get(VTB_HOST.format(route=route), headers=headers)
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
    def new_draft(draft_id, token):
        """Метод для создания нового платёжного поручения"""
        route = 'payment'
        headers = {'Authorization': 'Bearer ' + token}
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
                   'payer_kpp': payer_data['KPP'],  # КПП отправителя
                   'payer_account': payer_data['Account'],  # номер счета отправителя
                   'payer_bank_bic': payer_data['BankBIC'],  # БИК банка отправителя
                   'payer_bank_name': payer_data['BankName'],  # наименование банка отправителя
                   'payer_bank_city': payer_data['BankCity'],  # город банка отправителя
                   'payer_bank_correspondent_account': payer_data['BankCorrAccount'],  # корр. счет банка отправителя
                   'payee_name': reciever_data['OrgName'],  # наименование получателя
                   'payee_inn': reciever_data['INN'],  # ИНН получателя
                   'payee_kpp': reciever_data['KPP'],  # КПП получателя
                   'payee_account': reciever_data['Account'],  # номер счета получателя
                   'payee_bank_bic': reciever_data['BankBIC'],  # БИК банка получателя
                   'payee_bank_name': reciever_data['BankName'],  # наименование банка получателя
                   'payee_bank_city': reciever_data['BankCity'],  # город банка получателя
                   'payee_bank_correspondent_account': reciever_data['BankCorrAccount']  # корр. счет банка получателя
                   }
        # Отправим запрос на создание платёжного поручения
        result = requests.post(VTB_HOST.format(route=route), data=payment, headers=headers)
        # TODO: Обрабатывать значения результата создания платёжного поручения
        # Изменим статус платёжного поручения на подверждённый
        drft.confirm(draft_id)
