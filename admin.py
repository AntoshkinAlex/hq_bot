from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import const
import mongodb as backend
import texttable as table

bot = const.bot

########################################################################################################################


def print_admin_user_information(chatId, user):
    try:
        user_id = user
        userInformation = backend.get_user(user_id)
        userAchievements = '\n'
        if 'custom_achievements' in userInformation:
            userAchievements = ''
            for achievement in userInformation['custom_achievements']:
                userAchievements += str(achievement) + '\n'
        key = InlineKeyboardMarkup()
        but_1 = InlineKeyboardButton(text="Дивизион", callback_data="change_div " + user_id)
        but_2 = InlineKeyboardButton(text="Участник",
                                     callback_data="change_participant " + user_id)
        but_3 = InlineKeyboardButton(text="Имя", callback_data="change_name " + user_id)
        but_4 = InlineKeyboardButton(text="Достижения", callback_data="show_achievements " + user_id)
        but_5 = InlineKeyboardButton(text="Хэндл", callback_data="change_handle " + user_id)
        key.add(but_1, but_2, but_3, but_4, but_5)
        is_participant = "Да"
        if not userInformation['is_participant']:
            is_participant = "Нет"
        mes = "<b>" + userInformation['active_name'] + ":</b>\n\n" + "Дивизион:\n" + str(userInformation['division']) + "\n\n"
        mes += "Handle: " + userInformation['handle'] + "\n"
        if 'achievements' in userInformation:
            mes += "Достижения:\n" + userInformation['achievements'] + "\n" + userAchievements + "\n"
        mes += "Является участником контестов: " + is_participant + "\n"
        bot.send_message(chatId, mes, parse_mode="html", reply_markup=key)
    except Exception as err:
        print('Ошибка при выводе личной информации админу', err)
        bot.send_message(chatId, "Произошла ошибка")


########################################################################################################################


def change_participant(message, chat_id):
    try:
        user_id = message[message.find('change_participant ') + 19: len(message)]
        user = backend.get_user(user_id)
        newparticipant = True
        if user['is_participant']:
            newparticipant = False
        backend.update_user(user_id, {'is_participant': newparticipant})
        print_admin_user_information(chat_id, user_id)
    except Exception as err:
        print('Не удалось поменять состояние участника контеста', err)
        bot.send_message(chat_id, 'Не удалось поменять состояние участника контеста')


########################################################################################################################


def show_achievements(message, chat_id):
    try:
        user_id = message[message.find('show_achievements ') + 18: len(message)]
        user = backend.get_user(user_id)
        custom_achievements = []
        if 'custom_achievements' in user:
            custom_achievements = user['custom_achievements']

        key = InlineKeyboardMarkup()
        for (index, achievement) in enumerate(custom_achievements):
            button = InlineKeyboardButton(text=achievement,
                                          callback_data='achievement: ' + str(index) + ' ' + str(user_id))
            key.add(button)
        button = InlineKeyboardButton(text='Добавить достижение', callback_data='+achievement ' + str(user_id))
        key.add(button)
        bot.send_message(chat_id,
                         'Нажмите на достижение, чтобы удалить его, или нажмите на кнопку ДОБАВИТЬ, чтобы добавить новое',
                         reply_markup=key)
    except Exception as err:
        print('Не удалось поменять достижения участника', err)
        bot.send_message(chat_id, 'Не удалось поменять достижения участника')


def edit_achievement(message, chat_id):
    try:
        number = int(message[message.find('achievement: ') + 13: message.rfind(' ')])
        user_id = str(message[message.rfind(' ') + 1: len(message)])
        user = backend.get_user(user_id)
        custom_achievements = []
        if 'custom_achievements' in user:
            custom_achievements = user['custom_achievements']
        del custom_achievements[number]
        backend.update_user(user_id, {'custom_achievements': custom_achievements})
        print_admin_user_information(chat_id, user_id)
    except Exception as err:
        print('Не удалось изменить достижения участника', err)
        bot.send_message(chat_id, 'Не удалось изменить достижения участника')


def add_achievement(message, chat_id):
    try:
        user_id = message[message.find(' ') + 1: len(message)]
        backend.insert_session(chat_id, 'achievement', {'user_id': user_id})
        bot.send_message(chat_id, 'Напишите достижение участника')
    except Exception as err:
        print('Не удалось добавить достижение участнику', err)
        bot.send_message(chat_id, 'Не удалось добавить достижение участнику')


def new_achievement(message, chat_id, args):
    try:
        backend.erase_session(chat_id)
        user_id = args['user_id']
        user = backend.get_user(user_id)
        custom_achievements = []
        if 'custom_achievements' in user:
            custom_achievements = user['custom_achievements']
        custom_achievements.append(message)
        backend.update_user(user_id, {'custom_achievements': custom_achievements})
        print_admin_user_information(chat_id, user_id)
    except Exception as err:
        print('Не удалось добавить новое достижение участнику', err)
        bot.send_message(chat_id, 'Не удалось добавить новое достижение участнику')


########################################################################################################################


def show_contest(contestId, chat_id, admin):
    try:
        contest = backend.get_contest_information(contestId)
        if not 'activity' in contest:
            activity = [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]]
            backend.update_contest(contest['id'], {'activity': activity})
        else:
            activity = contest['activity']
        contestInformation = "<b>" + contest['name'] + ":</b>\n\n"
        for num in range(3):
            contestInformation += 'Div. ' + str((num + 1)) + ':\n'
            for (index, color) in enumerate(const.activity):
                contestInformation += str(color[0]) + ': ' + str(activity[num][index]) + '\n'
            contestInformation += '\n'

        rating = contest['allActivity']
        if admin:
            key = InlineKeyboardMarkup()
            but_1 = InlineKeyboardButton(text="Изменить активность",
                                         callback_data="choose_div " + str(contestId) + ' ' + str(chat_id))
            key.add(but_1)
            bot.send_message(chat_id, contestInformation + 'Активность за контест:\n\n<pre>' + rating + '</pre>', parse_mode="html", reply_markup=key)
        else:
            bot.send_message(chat_id, contestInformation + 'Активность за контест:\n\n<pre>' + rating + '</pre>',
                             parse_mode="html")
    except Exception as err:
        print('Не удалось показать информацию о контесте', err)
        bot.send_message(chat_id, 'Не удалось показать информацию о контесте')


########################################################################################################################


def choose_div(contestId, chat_id):
    try:
        key = InlineKeyboardMarkup()
        but_1 = InlineKeyboardButton(text="Div 1",
                                     callback_data="div_1 " + contestId + ' ' + chat_id)
        but_2 = InlineKeyboardButton(text="Div 2",
                                     callback_data="div_2 " + contestId + ' ' + chat_id)
        but_3 = InlineKeyboardButton(text="Div 3",
                                     callback_data="div_3 " + contestId + ' ' + chat_id)
        key.add(but_1, but_2, but_3)
        bot.send_message(chat_id, "Выберите дивизион", reply_markup=key)
    except Exception as err:
        print('Не удалось выбрать дивизион', err)
        bot.send_message(chat_id, 'Не удалось выбрать дивизион')


def edit_activity(contestId, chat_id, div):
    try:
        bot.send_message(chat_id, "Напишите через пробел количество задач, которые надо решить для дивизиона " + str(div) + ", в следующем порядке 🟠 🟡 🟢 🟣")
        backend.insert_session(chat_id, 'change_contest_activity', {'contest_id': contestId, 'div': div})
    except Exception as err:
        print('Не удалось добавить сессию для изменения активности', err)
        bot.send_message(chat_id, 'Не удалось добавить сессию для изменения активности')


def change_activity(mes, chat_id, args):
    try:
        activity = [0, 0, 0, 0, 0]
        mes += ' '
        pos = 1
        while mes.find(' ') != -1:
            s = mes[0 : mes.find(' ')]
            activity[pos] = int(s)
            pos += 1
            mes = mes[mes.find(' ') + 1: len(mes)]
        new_activity = backend.get_contest_information(args['contest_id'])['activity']
        new_activity[int(args['div']) - 1] = activity
        backend.update_contest(args['contest_id'], {'activity': new_activity})
        show_contest(args['contest_id'], chat_id, True)
    except Exception as err:
        print('Не удалось поменять активность', err)
        bot.send_message(chat_id, 'Не удалось поменять активность')


########################################################################################################################


def change_name(message, chat_id):
    try:
        user_id = message[message.find('change_name ') + 12: len(message)]
        backend.insert_session(chat_id, 'name', {'user_id': user_id})
        bot.send_message(chat_id, 'Напишите через пробел имя и фамилию')
    except Exception as err:
        print('Произошла ошибка при выводе сообщения об изменении имени', err)
        bot.send_message(chat_id, 'Произошла ошибка при выводе сообщения об изменении имени')


def edit_name(message, chat_id, args):
    try:
        user_id = args['user_id']
        name = message
        backend.update_user(user_id, {'name': name, 'active_name': name})
        print_admin_user_information(chat_id, user_id)
    except Exception as err:
        print('Произошла ошибка при изменении имени', err)
        bot.send_message(chat_id, 'Произошла ошибка при изменении имени')


########################################################################################################################


def change_div(message, chat_id):
    try:
        user_id = message[message.find('change_div ') + 11: len(message)]
        user = backend.get_user(user_id)
        newdiv = user['division'] + 1
        if newdiv == 4:
            newdiv = 1
        backend.update_user(user_id, {'division': newdiv})
        print_admin_user_information(chat_id, user_id)
    except Exception as err:
        print('Не удалось сменить дивизион пользователя', err)
        bot.send_message(chat_id, 'Не удалось сменить дивизион пользователя')


########################################################################################################################


def change_handle(message, chat_id):
    try:
        user_id = message[message.find('change_handle ') + 14: len(message)]
        backend.insert_session(chat_id, 'handle', {'user_id': user_id})
        bot.send_message(chat_id, 'Напишите новый handle пользователя')
    except Exception as err:
        print('Произошла ошибка при выводе сообщения об изменении handle', err)
        bot.send_message(chat_id, 'Произошла ошибка при выводе сообщения об изменении handle')


def edit_handle(message, chat_id, args):
    try:
        user_id = args['user_id']
        handle = message
        backend.update_user(user_id, {'handle': handle})
        print_admin_user_information(chat_id, user_id)
    except Exception as err:
        print('Произошла ошибка при изменении имени', err)
        bot.send_message(chat_id, 'Произошла ошибка при изменении имени')


########################################################################################################################