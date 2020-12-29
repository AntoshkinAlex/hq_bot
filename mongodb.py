from pymongo import MongoClient
from const import MONGODB, MONGODB_LINK

mdb = MongoClient(MONGODB_LINK)[MONGODB]  # переменная для работы с монго


def get_user(user_id):
    user_id = str(user_id)
    try:
        for user in mdb.users.find({"user_id": user_id}):
            return user
    except Exception as err:
        print("Ошибка при взятии пользователя из базы данных", err)


def insert_user(user_id):
    user_id = str(user_id)
    handle = ""
    is_participant = False
    division = 1
    old_user = get_user(user_id)
    name = user_id
    active_name = name
    notifications = True
    if old_user is not None:
        if 'division' in old_user:
            division = old_user['division']
        if 'is_participant' in old_user:
            is_participant = old_user['is_participant']
        if 'name' in old_user:
            name = old_user['name']
            active_name = name
        if 'active_name' in old_user:
            active_name = old_user['active_name']
        if 'notifications' in old_user:
            notifications = old_user['notifications']
        if 'handle' in old_user:
            handle = old_user['handle']

    user = {
        "user_id": user_id,
        "handle": handle,
        "is_participant": is_participant,
        "division": division,
        "name": name,
        "active_name": active_name,
        "notifications": notifications
    }
    try:
        mdb.users.update_one({"user_id": user_id}, {'$set': user}, upsert=True)
    except Exception as err:
        print("Ошибка при добавлении пользователя в базу данных", err)
    return user


def update_user(user_id, keys):
    user_id = str(user_id)
    try:
        mdb.users.update_one({"user_id": user_id}, {'$set': keys}, upsert=True)
    except Exception as err:
        print("Ошибка при обновлении пользователя в базе данных", err)


def get_users(params):
    try:
        return mdb.users.find(params)
    except Exception as err:
        print("Ошибка при взятии пользователей из базы данных", err)


def update_contest(contest_id, keys):
    contest_id = str(contest_id)
    try:
        mdb.contests.update_one({"contest_id": contest_id}, {'$set': keys}, upsert=True)
    except Exception as err:
        print("Ошибка при обновлении контеста в базе данных", err)


def get_contests():
    return mdb.contests.find({'finished': True}).sort("contest_id")


def get_contest_information(contest_id):
    contest_id = str(contest_id)
    for contest in mdb.contests.find({"contest_id": contest_id}):
        return contest


def update_rating(rating):
    try:
        mdb.rating.update_one({}, {'$set': rating}, upsert=True)
    except Exception as err:
        print("Ошибка при обновлении рейтинга в базе данных", err)


def get_rating():
    for rating in mdb.rating.find():
        return rating


def insert_session(chat_id, name, args):
    chat_id = str(chat_id)
    session = {
        "chat_id": chat_id,
        "name": name,
        "args": args
    }
    try:
        mdb.sessions.update_one({"chat_id": chat_id}, {'$set': session}, upsert=True)
    except Exception as err:
        print("Ошибка при обновлении сессии", err)


def find_session(chat_id):
    chat_id = str(chat_id)
    for session in mdb.sessions.find({"chat_id": chat_id}):
        return session


def erase_session(chat_id):
    chat_id = str(chat_id)
    mdb.sessions.delete_many({"chat_id": chat_id})


def add_weather(date):
    mdb.weather.delete_many({})
    mdb.weather.insert({"date": date})


def find_weather(date):
    for day in mdb.weather.find({"date": date}):
        return day
