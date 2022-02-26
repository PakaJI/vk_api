import vk_api
import random
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from pymongo import MongoClient
from configvk import vkapi_my, tasks, commands_meny, db_connect

session = vk_api.VkApi(token=vkapi_my)

cluster = MongoClient(db_connect)
db = cluster["ecodb"]
collection = db["vkcolldb"]

# def ready(user_id):
#     keyboard = VkKeyboard()
#     keyboard.add_button("Старт", VkKeyboardColor.POSITIVE)
#     post = {
#             "user_id": user_id,
#             "message": "Привет!!",
#             "keyboard": keyboard,
#             "random_id": 0
#         }
#     session.method("messages.send", post)


def send_message(user_id, message, keyboard=None):
    post = {
        "user_id": user_id,
        "message": message,
        "random_id": 0
    }

    if keyboard is not None:
        post["keyboard"] = keyboard.get_keyboard()
    else:
        post = post

    session.method("messages.send", post)


def main_meny():
    keyboard = VkKeyboard()
    keyboard.add_button("Профиль", VkKeyboardColor.POSITIVE)
    keyboard.add_button("Профтест", VkKeyboardColor.NEGATIVE)
    keyboard.add_line()
    keyboard.add_openlink_button("Вступить", r"http://sfu-prof.com/home/vstupit-v-ppos-sfu")
    keyboard.add_button("Помощь", VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_openlink_button("Сайт ППОС СФУ", r"http://sfu-prof.com/")
    send_message(user_id, "Главное меню открыто", keyboard)


def help_meny():
    keyboard = VkKeyboard()
    keyboard.add_button("Социальная стипендия")
    keyboard.add_button("Повышенная стипендия")
    keyboard.add_line()
    keyboard.add_button("Материальная помощь")
    keyboard.add_button("Получения талона на кашу")
    keyboard.add_line()
    keyboard.add_button("Главное меню", VkKeyboardColor.POSITIVE)
    send_message(user_id, "Меню с помощью открыта", keyboard)


def game_meny():
    keyboard = VkKeyboard()
    keyboard.add_button("4")
    keyboard.add_button("6")
    keyboard.add_button("8")
    keyboard.add_button("10")
    keyboard.add_line()
    keyboard.add_button("Главное меню", VkKeyboardColor.POSITIVE)
    send_message(user_id, "Выберите кол-во вопросов:", keyboard)


def game_pro(user_id, chis):
    keyboard = VkKeyboard()
    keyboard.add_button("1")
    keyboard.add_button("2")
    keyboard.add_button("3")
    keyboard.add_button("4")
    keyboard.add_line()
    keyboard.add_button("Главное меню", VkKeyboardColor.POSITIVE)
    send_message(user_id, "Профтест:", keyboard)

    game_tasks = []
    x = 0
    while x != chis:
        random1 = random.randint(0, len(tasks) - 1)
        random_task = tasks[random1]
        if random_task not in game_tasks:
            game_tasks.append(random_task)
            x += 1
    a = True
    profiki = 0
    true = 0
    for x in range(0, len(game_tasks)):
        if a:
            send_message(user_id, f"{game_tasks[x][0]}\n")
            for event in VkLongPoll(session).listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    text = event.text.lower()
                    if text == "главное меню":
                        a = False
                        break
                    try:
                        if int(text) == game_tasks[x][1]:
                            send_message(user_id, f"Верно!\n")
                            profiki += 2
                            true += 1
                            break
                        elif int(text) != game_tasks[x][1]:
                            send_message(user_id, f"Неверно\nПравильный ответ находится под номером {game_tasks[x][1]}\n")
                            profiki -= 1
                            break
                        else:
                            a = False
                            break
                    except:
                        a = False
                        break
        else:
            break
    collection.update_one({"_id": user_id}, {"$inc": {"balance": profiki}})
    send_message(user_id, f"Вы ответили верно на {true} из {chis} вопросов!\nПолучено {profiki} профбаллов")


def social_meny():
    keyboard = VkKeyboard()
    keyboard.add_button("Кто может получить", VkKeyboardColor.POSITIVE)
    keyboard.add_line()
    keyboard.add_button("Алгоритм получения", VkKeyboardColor.SECONDARY)
    keyboard.add_line()
    keyboard.add_button("Размер", VkKeyboardColor.PRIMARY)
    keyboard.add_button("ПГСС", VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button("Главное меню", VkKeyboardColor.POSITIVE)
    send_message(user_id, "Меню социальной стипендии открыто", keyboard)


for event in VkLongPoll(session).listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        text = event.text.lower()
        user_id = event.user_id
        print(f"Ооо, сообщение от {user_id}: {text}!")

        # if __name__ == "__main__":
        #     print("ready...")
        #     ready(user_id)

        data1 = {
            "_id": user_id,
            "balance": 0
        }

        if collection.count_documents({"_id": user_id}) == 0:
            collection.insert_one(data1)
            print(f"Пользователь с айди {user_id} добавлен в базу данных")
        else:
            print(f"Пользователь с айди {user_id} уже есть в базе данных")

        if text == "старт":

            if collection.count_documents({"_id": user_id}) == 0:
                collection.insert_one(data1)
                print(f"Пользователь с айди {user_id} добавлен в базу данных")
            else:
                print(f"Пользователь с айди {user_id} уже есть в базе данных")

            main_meny()

        glmen = ["главное меню", "m", "меню"]
        if text in glmen:
            main_meny()

        if text == "профиль":
            balans_member = collection.find_one({'_id': user_id})['balance']
            if 1 < balans_member < 5:
                balans_member = str(balans_member) + " профбалла 😸"
            elif balans_member == 1:
                balans_member = str(balans_member) + " профбалл 😸"
            elif balans_member >= 5:
                balans_member = str(balans_member) + " профбаллов 😸"
            else:
                balans_member = "0 профбаллов 😸"
            send_message(user_id, f"Профиль участника @id{user_id}\n\nБаланс: {balans_member}")

        if text == "профтест":
            game_meny()
            for event in VkLongPoll(session).listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    text = event.text.lower()
                    if text == "4":
                        game_pro(user_id, 4)
                    elif text == "6":
                        game_pro(user_id, 6)
                    elif text == "8":
                        game_pro(user_id, 8)
                    elif text == "10":
                        game_pro(user_id, 10)
                    else:
                        main_meny()
                        break

        if text == "помощь":
            help_meny()

        if text == "социальная стипендия":
            social_meny()
            for event in VkLongPoll(session).listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    text = event.text.lower()
                    if text == "главное меню":
                        break
                    if text == "кто может получить":
                        send_message(user_id, "Федеральный закон № 273, статья 36:\nГосударственная социальная стипендия назначается студентам, являющимся:\n- детьми-сиротами и детьми, оставшимися без попечения родителей, лицами из числа детей-сирот и детей, оставшихся без попечения родителей;\n- лицами, потерявшими в период обучения обоих родителей или единственного родителя;\n- детьми-инвалидами, инвалидами I и II групп, инвалидами с детства;\n- студентам, подвергшимся воздействию радиации вследствие катастрофы на Чернобыльской АЭС и иных радиационных катастроф, вследствие ядерных испытаний на Семипалатинском полигоне;\n- студентам, являющимся инвалидами вследствие военной травмы или заболевания, полученных в период прохождения военной службы, и ветеранами боевых действий;\n- также студентам из числа граждан, проходивших в течение не менее трех лет военную службу по контракту;\n- получившим государственную социальную помощь.")
                    else:
                        break

        if text == "t":
            send_message(664915953, "I'm working...")

        # if text not in commands_meny:
        #     send_message(user_id, "Команда не распознана!\nПопробуйте написать 'меню' для открытия главного меню")

# collection.update_one({"_id": user_id}, {"$inc": {"balance": int(summa)}})
