from vtb_interaction import VTBProfile as vtbp


def main(event, context):
    user_id = event['state']
    auth_code = event['code']
    if vtbp.tokenize(auth_code, user_id):
        # Публикация события успешного получения токена
        pass
