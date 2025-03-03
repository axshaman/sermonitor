import json
from models.models import Users, KeyWords


def get_keywords_from_database(telegram_id):
    user = Users.find_by_telegram_id(telegram_id=telegram_id)
    word_names = [i.name for i in user.word_user]
    words = {}
    c = 1
    for name in word_names:
        words[f'{c}'] = name
        c+=1
    return json.dumps(words, ensure_ascii=False,)