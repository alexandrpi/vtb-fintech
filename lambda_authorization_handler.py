from vtb_interaction import VTBProfile as vtbp


def entry(event, context):
    user_id = event['state']
    auth_code = event['code']
    # TODO: Публикация события успешного получения токена
    return vtbp.tokenize(auth_code, user_id)
