from db_worker import Users as usr


def main(event, context):
    usr.new({'TelegramID': 1, 'PhoneNumber': '2', 'VTBClient': False})
    usr.new({'TelegramID': 2, 'PhoneNumber': '3', 'VTBClient': True})
    print(usr.get({'TelegramID': 2}))
    usr.update_with_data(3, {'CLIENT_ID': 983745, 'PhoneNumber': '09385'})
