from threading import Thread
import telebot
import structure as struct
import index as req
import const
import admin
import texttable as table
import mongodb as backend
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

bot = const.bot
Thread1 = Thread(target=struct.take_contests)
Thread1.start()


def print_contests(chatId, prefix):
    try:
        key = InlineKeyboardMarkup()
        for contest in backend.get_contests():
            contestName = contest['name']
            id = contest['contest_id']
            button = InlineKeyboardButton(text=contestName, callback_data=prefix + 'id' + str(id))
            key.add(button)
        bot.send_message(chatId, "Выберите контест:", reply_markup=key)
    except Exception as err:
        bot.send_message(chatId, "Произошла ошибка")
        print('Произошла ошибка при выводе контестов', err)


def print_users(chatId, prefix, admin):
    try:
        key = InlineKeyboardMarkup()
        if not admin:
            users = backend.get_users({'is_participant': not admin}).sort('is_participant')
        else:
            users = backend.get_users({}).sort('is_participant')
        for user in users:
            id = user['user_id']
            button = InlineKeyboardButton(text=user['active_name'], callback_data=prefix + 'login: ' + str(id))
            key.add(button)
        bot.send_message(chatId, "Выберите пользователя:", reply_markup=key)
    except Exception as err:
        bot.send_message(chatId, "Произошла ошибка")
        print('Произошла ошибка при выводе пользователей', err)


def print_settings(chatId):
    try:
        key = InlineKeyboardMarkup()
        button = InlineKeyboardButton(text='Вкл/Выкл уведомления', callback_data='notifications')
        key.add(button)
        user = backend.get_user(chatId)
        notifications = user['notifications']
        status = 'Уведомления: '
        if notifications:
            status += '🟢'
        else:
            status += '🔴'
        bot.send_message(chatId, status, reply_markup=key)
    except Exception as err:
        bot.send_message(chatId, "Произошла ошибка")
        print('Произошла ошибка при выводе настроек пользователя', err)


def print_contest_information(chatId, contestId):
    try:
        contest = backend.get_contest_information(contestId)
        contestTop = contest['contestTop']
        rating = contest['allRating']
        top = ""
        if len(contestTop) >= 1:
            top += "Топ:\n" + "🥇 " + backend.get_user(contestTop[0][0])['name'] + " - " + str(contestTop[0][1]) \
                   + " " + struct.declension(contestTop[0][1], "задача", "задачи", "задач") + "\n"
        if len(contestTop) >= 2:
            top += "🥈 " + backend.get_user(contestTop[1][0])['name'] + " - " + str(contestTop[1][1]) \
                   + " " + struct.declension(contestTop[1][1], "задача", "задачи", "задач") + "\n"
        if len(contestTop) >= 3:
            top += "🥉 " + backend.get_user(contestTop[2][0])['name'] + " - " + str(contestTop[2][1]) \
                   + " " + struct.declension(contestTop[2][1], "задача", "задачи", "задач") + "\n"
        if len(contestTop) >= 1:
            top += "\n"

        first_submit = ""
        if 'firstSubmission' in contest:
            first_submit = "Первая успешная посылка:\n" + backend.get_user(contest['firstSubmission']['name'])['name'] + "\n"\
                           + "Время посылки: " + str(contest['firstSubmission']['time']) + " " + \
                           struct.declension(contest['firstSubmission']['time'], "минута", "минуты", "минут") + "\n\n"
        key = InlineKeyboardMarkup()
        but_1 = InlineKeyboardButton(text="Посмотреть активность",
                                     callback_data="not_admin_contest_id" + str(contestId))
        key.add(but_1)
        bot.send_message(chatId, "<b>" + contest['name'] + ":</b>\n\n" + first_submit + top +
                         "Рейтинг за тренировку:\n\n<pre>" + rating + "</pre>",
                         parse_mode="html", reply_markup=key)
    except Exception as err:
        bot.send_message(chatId, "Произошла ошибка при выводе таблицы контеста", err)


def print_user_information(chatId, user):
    try:
        userInformation = backend.get_user(user)
        userAchievements = '\n'
        if 'custom_achievements' in userInformation:
            userAchievements = ''
            for achievement in userInformation['custom_achievements']:
                userAchievements += str(achievement) + '\n'
        activity = ''
        for color in userInformation['last_activities']:
            activity += const.activity[color][0]
        bot.send_message(chatId, "<b>" + userInformation['active_name'] + ":</b>\n\n" +
                         "Div: " + str(userInformation['division']) + "\n" +
                         "Средняя активность:\n" + const.activity[userInformation['activity']] + "\nАктивность за 5 тренировок:\n" +
                        activity + '\n\n'
                         "Достижения:\n" + userInformation['achievements'] + "\n" + userAchievements + "\n" +
                         "Решено задач: " + str(userInformation['solved']) + "\n" +
                         "Не решено задач: " + str(userInformation['unsolved']) + "\n\n" +
                         "За последние 5 тренировок вы решили: \n" + str(userInformation['solvedLast']) + " " +
                         str(struct.declension(userInformation['solvedLast'], "задачу", "задачи", "задач")) + " из " +
                         str(userInformation['allLast']) + "\n",
                         parse_mode="html")
    except Exception as err:
        print('Ошибка при выводе личной информации', err)
        bot.send_message(chatId, "Произошла ошибка")


def print_all_rating(chatId):
    rating = backend.get_rating()
    rating = rating['rating']
    try:
        bot.send_message(chatId, "<b>" + "Общий рейтинг:" + "</b>\n\n<pre>" + rating + "</pre>", parse_mode="html")
    except Exception as err:
        bot.send_message(chatId, 'Произошла ошибка при выводе общего рейтинга', err)


@bot.message_handler(commands=["start"])
def start_chat(message):
    print(str(message.chat.id) + ' ' + str(message.from_user.username) + ' ' + str(
        message.from_user.first_name) + ' ' + str(message.from_user.last_name) + ': ' + str(message.text))  # логи

    backend.insert_user(message.from_user.id)  # запоминаем пользователя в бд

    menuKey = ReplyKeyboardMarkup(resize_keyboard=True)  # кнопка меню
    menuBut = KeyboardButton(text="Меню")
    menuKey.add(menuBut)

    key = InlineKeyboardMarkup() # кнопки взаимодействия
    but_1 = InlineKeyboardButton(text="Тренировки", callback_data="getcontest")
    but_2 = InlineKeyboardButton(text="Рейтинг", callback_data="getrating")
    but_3 = InlineKeyboardButton(text="Личная информация", callback_data="getuser")
    key.add(but_1, but_2)
    key.add(but_3)

    bot.send_message(message.chat.id, "Привет", reply_markup=menuKey)
    bot.send_message(message.chat.id, "Выберите:", reply_markup=key)


@bot.message_handler(content_types=["text"])
def continue_chat(message):
    backend.insert_user(message.from_user.id)  # запоминаем пользователя в бд
    print(str(message.chat.id) + ' ' + str(message.from_user.username) + ' ' + str(
        message.from_user.first_name) + ' ' + str(message.from_user.last_name) + ': ' + str(message.text))  # логи

    if backend.find_session(message.from_user.id) is not None:  # проверка сессий
        session = backend.find_session(message.from_user.id)
        backend.erase_session(message.from_user.id)
        if session['name'] == 'achievement':
            admin.new_achievement(message.text, message.from_user.id, session['args'])
        elif session['name'] == 'change_contest_activity':
            admin.change_activity(message.text, message.from_user.id, session['args'])
        elif session['name'] == 'name':
            admin.edit_name(message.text, message.from_user.id, session['args'])
        elif session['name'] == 'handle':
            admin.edit_handle(message.text, message.from_user.id, session['args'])

    elif message.text == "Меню":
        key = InlineKeyboardMarkup()  # кнопки взаимодействия
        but_1 = InlineKeyboardButton(text="Тренировки", callback_data="getcontest")
        but_2 = InlineKeyboardButton(text="Рейтинг", callback_data="getrating")
        but_3 = InlineKeyboardButton(text="Личная информация", callback_data="getuser")
        key.add(but_1, but_2)
        key.add(but_3)
        bot.send_message(message.chat.id, "Выберите:", reply_markup=key)
    elif message.text.find('/all ') != -1 and str(message.chat.id) in const.admins:  # вывод сообщения всем пользователям
        for user in backend.get_users({}):
            userId = user['user_id']
            try:
                bot.send_message(userId, message.text[message.text.find('/all ') + 5: len(message.text)])
            except Exception as err:
                print('Пользователь ' + userId + ' удалил чат', err)
    elif message.text.find('/admin') != -1:
        if str(message.chat.id) in const.admins:
            key = InlineKeyboardMarkup()  # кнопки взаимодействия
            but_1 = InlineKeyboardButton(text="Пользователи", callback_data="admin_users")
            but_2 = InlineKeyboardButton(text="Контесты", callback_data="admin_contests")
            key.add(but_1)
            key.add(but_2)
            bot.send_message(message.chat.id, "Выберите:", reply_markup=key)
        else:
            img = open('Who_are_u?.jpg', 'rb')
            bot.send_photo(message.chat.id, img)
    elif message.text.find('/settings') != -1: # настройки
        print_settings(message.chat.id)


@bot.callback_query_handler(func=lambda text: True)
def callback_text(text):
    backend.erase_session(text.from_user.id)  # удаление сессии при нажатии на кнопку
    try:
        message = text.data
        print(str(text.message.chat.id) + ' ' + str(text.from_user.username) + ' ' + str(
            text.from_user.first_name) + ' ' + str(text.from_user.last_name) + ': ' + str(message))  # логи
        if message == "getcontest":
            print_contests(text.message.chat.id, '')
        elif message == "getrating":
            print_all_rating(text.message.chat.id)
        elif message == "getuser":
            print_users(text.message.chat.id, 'info', False)
        elif message.find('infologin: ') != -1:
            print_user_information(text.message.chat.id, message[message.find('infologin: ') + 11: len(message)])
        elif message.find('admin_info_login: ') != -1:
            try:
                user_id = message[message.find('admin_info_login: ') + 18: len(message)]
                admin.print_admin_user_information(text.message.chat.id, user_id)
            except Exception as err:
                print('Не удалось вывести пользователя админу', err)
                bot.send_message(text.message.chat.id, 'Не удалось вывести пользователя')
        elif message.find('change_div ') != -1:
            admin.change_div(message, text.from_user.id)
        elif message.find('change_participant ') != -1:
            admin.change_participant(message, text.from_user.id)
        elif message.find('change_name ') != -1:
            admin.change_name(message, text.from_user.id)
        elif message.find('change_handle ') != -1:
            admin.change_handle(message, text.from_user.id)
        elif message.find('show_achievements ') != -1:
            admin.show_achievements(message, text.from_user.id)
        elif message.find('achievement: ') != -1:
            admin.edit_achievement(message, text.from_user.id)
        elif message.find('+achievement') != -1:
            admin.add_achievement(message, text.from_user.id)
        elif message.find('not_admin_contest_id') != -1:
            id = message[message.find('not_admin_contest_id') + 20: len(message)]
            admin.show_contest(id, text.message.chat.id, False)
        elif message.find('admin_contest_id') != -1:
            id = message[message.find('admin_contest_id') + 16: len(message)]
            admin.show_contest(id, text.message.chat.id, True)
        elif message.find('id') != -1:
            print_contest_information(text.message.chat.id, message[message.find('id') + 2: len(message)])
        elif message.find('notifications') != -1:
            user = backend.get_user(text.message.chat.id)
            new_notifications = not user['notifications']
            backend.update_user(text.message.chat.id, {'notifications': new_notifications})
            print_settings(text.message.chat.id)
        elif message.find('admin_users') != -1:
            print_users(text.message.chat.id, 'admin_info_', True)  # вывод пользователей для админа
        elif message.find('admin_contests') != -1:
            print_contests(text.message.chat.id, 'admin_contest_')
        elif message.find('choose_div') != -1:
            contestId = message[message.find(' ') + 1 : message.rfind(' ')]
            chatId = message[message.rfind(' ') + 1: len(message)]
            admin.choose_div(contestId, chatId)
        elif message.find('div_') != -1:
            contestId = message[message.find(' ') + 1: message.rfind(' ')]
            chatId = message[message.rfind(' ') + 1: len(message)]
            div = message[message.find('_') + 1: message.find(' ')]
            admin.edit_activity(contestId, chatId, div)
    except Exception as err:
        print("Проблемы с callback", err)


bot.polling(none_stop=True)
