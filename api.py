import json, datetime
from flask_restful import Resource
from flask import request
from models.models import Users, KeyWords
from models.models import db
from xmlproxy import get_urls
from pdf_loader import pdf_report
from services import get_keywords_from_database
now = datetime.date.today()


class UserRegister(Resource):

    """Принимает данные нового пользователя с телеграм бота и добавляет в базу данных"""
    def post(self):
        data = request.get_json()
        print(data)
        try:
            user = Users(**data)
            user.save_to_db()
            return {'status': 'ok'}, 200
        except:
            return {'status': 'fail'}, 400


class CheckUser(Resource):

    """Проверяет есть ли пользователь в базе данных"""
    def post(self):
        telegram_id = request.get_json()['telegram_id']
        user = Users.find_by_telegram_id(telegram_id)
        if user:
            message = {'user': 'authorized'}
            return message
        else:
            message = {'user': 'unauthorized'}
            return message


class CheckKeyWords(Resource):

    """Принимает ключевые слова для поиска, проверяет есть ли они в базе данных и связывает их с пользователем """
    def post(self):
        try:
            data = request.get_json()
            key_words = data['key_words']
            telegram_id = data['telegram_id']
        except KeyError:
            return {'status': 'data is out'}, 401
        try:
            user = Users.find_by_telegram_id(telegram_id=telegram_id)
            if not user:
                return {'status': 'user does not exist'}, 501
            words = key_words.lower().split(',')
            for name in words:
                word = KeyWords(name=name)
                user.word_user.append(word)
                user.save_to_db()
            return {'status':'done'}, 200
        except:
            return {'status': 'fail'}, 402

    """Делает запрос с параметрами на яндекс и возвращает пдф с отчетом"""
    def get(self):
        try:
            data = request.get_json()
            print(f'{data} data')
            key_words = data['key_words']
            telegram_id = data['telegram_id']
        except KeyError:
            return {'status': 'data is out'}, 401
        user = Users.find_by_telegram_id(telegram_id=telegram_id)
        if not user:
            return {'status': 'user does not exist'}, 400
        user_patronymic = user.patronymic
        words = key_words.lower().split(',')
        object = []
        # for word in words:
        query=f'{user_name} {user_surname} {user_patronymic} {user_city} {words[-1]}'

        try:  
            result = get_urls(query=query)
        except Exception:
            print('nooo')
            return {'status': 'Error'}, 400

        result = get_urls(query=query)

        try:
            js = json.loads(result)['yandexsearch']['response']["results"]["grouping"]["group"]
        except:
            return False
        c=1
        for i in js:
            elem = {}
            url = i["doc"]["url"]
            if "passages" in i["doc"].keys():
                keys = i["doc"]["passages"]['passage']
                try:
                    name = keys["hlword"]
                    snippet = keys["#text"]
                except:
                    name = keys[0]["hlword"]
                    snippet = keys[0]["#text"]
            elif "headline" in i["doc"].keys():                     
                keys = i["doc"]["headline"]
                if type(keys) == dict:
                    name = keys["hlword"]
                    snippet = keys["#text"]
                elif type(keys) == str:
                    name = words[-1]
                    snippet = keys
            elem['id'] = c
            elem['url'] = url
            elem['snippet'] = snippet
            elem['name'] = name
            object.append(elem)
            c+=1
        name=f'{user_name} {user_patronymic} {user_surname} от {now}'

        print(object)
        
        try:
            with open('src/', f'{name}.json', 'w', encoding='utf-8') as f:
                json.dump(object, f, sort_keys=True, indent=4, ensure_ascii=False)
        except:
            print(34334)
            return False
        try:
            pdf_report(object, name=f'{user_name} {user_patronymic} {user_surname} от {now}')
        except Exception:
            print(56565)
            return False
        return {'status':'done'}, 200
 


    def delete(self):
        try:
            data = request.get_json()
            telegram_id = data['telegram_id']
        except KeyError:
            return {'status': 'data is out'}, 401
        user = Users.find_by_telegram_id(telegram_id=telegram_id)
        words = [i for i in user.word_user]
        if words:
            for word in words:
                user.word_user.remove(word)
                user.save_to_db()
        return {'status':'done'}, 200

class Result(Resource):

    """Возвращает пользователю все ключевые слова по которым он делал запрос"""
    def get(self):
        data = request.get_json()
        telegram_id = data['telegram_id']
        kwords = get_keywords_from_database(telegram_id)
        return kwords

        
class UserData(Resource):

    def get(self):
        data = request.get_json()
        print(data)
        telegram_id = data['telegram_id']
        user = Users.find_by_telegram_id(telegram_id=telegram_id)
        if not user:
            print(user)
            return {'status': 'user does not exist'}, 500
        user_name = user.name
        user_surname = user.surname
        user_patronymic = user.patronymic
        data = {
            'name': user_name,
            'surname': user_surname,
            'patronymic': user_patronymic,
        }
        return json.dumps(data), 200
