from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
import json, logging, time, copy, random
import datetime


def read_json():
    with open("mysite/info.json", "r", encoding='utf-8') as read_file:
        data = json.load(read_file)
    return data


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sqldatabase.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'key?'
db = SQLAlchemy(app)
sessionSettings = {}
SERVICE_WORDS = ["удалить", "инструкция", "навык", "подсказка", "время", "помощь", "нет", "да", 'включить', 'выключи',
                 "дальше", "дела", "засекай", "засечь", "таймер", "далее", "назад", "время", "меню", "добавить",
                 "дело", "каталог", "список"]
RUS_SYMBOLS = ["а", "о", "у", "ы", "э", "я", "е", "ё", "ю", "и", "б", "в", "г", "д", "й", "ж", "з", "к", "л", "м", "н",
               "п", "р", "с", "т", "ф", "х", "ц", "ч", "ш", "щ", "ъ", "ь", " "]
YES = ["да", "давай", "поехали", "начали", "начинаем", "гоу", "го", "конечно", "полетели", "начать", "ес"]
NO = ["нет", "не", "нит", "никак", "ноу"]
START_TIME = ["засекай", "засечь", "таймер", "поставь", "отсчёт", "отсчитывать", "отсчитай", "отсчитывай", "засеки",
              "ставь"]
ON = ['включить', "включи", "включай", "врубай", "включаем", "врубаем"]
OFF = ['выключи', "выключить", "выключай", "офай", "отключить", "отключи", "выключим", "отключим", "выключаем"]
THING_LIST = ["список", "списки", "лист", "дела", "каталог", "перечень", "каталоги"]
CREATE = ["создать", "создай", "сделай", "сделать", "добавить", "добавь", "каталоги", "дополни", "добавим", "дополним",
          "создадим", "сделаем"]
MENU = ["главное", "меню"]
MANUAL = ["инструкция", "мануал"]
NEXT = ["дальше", "далее", "следующие", "следующее", "вперёд"]
BACK = ["назад", "взад", "возврат", "прежде"]
REPEAT = ["повтори", "повторить", "повтор", "рипит"]
DELETE = ["удалить", "удали", "удаляй", "делитни"]
HELP = ["помоги", "хелп", "помощь", "help", "выручай", "выручи"]
RETURN_LAST_TIME = ["верни", "вернуть", "восстановить"]
CANCEL_LAST_TIME = ["отмени", "отменить", "отмена"]
STOP = ["стоп", "остановить", "завершить", "останови", "стопни", "stop", "завершай"]
UPDATE = ["обнови", "обновить", "сколько", "натикало"]
EXIT = ['выйти', "выход", "закрыть", "выйди", "закрой", "покинь"]
ABILITY = ["навык", "навыка", "диалог", "диалога"]
HINT = ["подсказка", "подсказки", "подсказочки"]
TIME = ["время", "времечко", "тайм"]
BUTTONS = {'add': {
    "title": "Добавить дело",
    "hide": True
}, 'yes': {
    "title": "Да",
    "hide": True
}, "no": {
    "title": "Нет",
    "hide": True
}, "menu": {
    "title": "Меню",
    "hide": True},
    "help": {
        "title": "Помощь",
        "hide": True},
    "can": {
        "title": "Что ты умеешь?",
        "hide": True
    }, "next": {
        "title": "Далее",
        "hide": True
    }, "back": {
        "title": "Назад",
        "hide": True
    }, "return": {
        "title": "Вернуть последнее",
        "hide": True
    }, "cancel": {
        "title": "Отменить последнее",
        "hide": True
    }, "cancl": {
        "title": "Отмена",
        "hide": True
    }, "delete": {
        "title": "Удалить",
        "hide": True
    }, "start": {
        "title": "Засечь время",
        "hide": True
    }, "update": {
        "title": "Обновить",
        "hide": True
    }, "stop": {
        "title": "Завершить",
        "hide": True
    }, "list": {
        "title": "Мои дела",
        "hide": True
    }, "catalog": {
        "title": "Список",
        "hide": True
    }, "time": {
        "title": "Время",
        "hide": True
    }}

DIALOGS_CONTENT = {
    "cards": {"menu": {
        "type": "ItemsList",
        "header": {
            "text": "{}"
        },
        "items": [
            {
                "image_id": "1030494/7f818b6889258a59263f",
                "title": "Засечь время",
                "button": {
                    "text": "Засечь время",
                    "payload": {
                        "text": "Засечь время"
                    }
                }
            },
            {
                "image_id": "1656841/eefa52cc6c452acf2b88",
                "title": "Добавить дело",
                "button": {
                    "text": "Добавить дело",
                    "payload": {
                        "text": "Добавить дело"
                    }
                }
            },
            {
                "image_id": "1656841/ae28273912889feeb9fb",
                "title": "Мои дела",
                "button": {
                    "text": "Мои дела",
                    "payload": {
                        "text": "Мои дела"
                    }
                }
            }
        ]
    },
        "things_list": {
            "type": "ItemsList",
            "header": {
                "text": "{}"
            },
            "items": [
            ]

        }},

    "dialogs": {
        "exit": ["До свидания!", "До свидания!"],
        "manual": ['Для начала вам нужно создать дело. Выбирайте название с умом, например: "Игра на гитаре",'
                   ' "Прогулка в парке", "Упражнение планка".\n'
                   ' Для того чтобы начать отсчёт, перейдите в раздел "Засечь время" и выберите из'
                   ' списка дело, которое хотите засечь. Можно воспользоваться командой'
                   ' "Засечь (название дела)".\nЧтобы я повторила предыдущую фразу, скажите "Повторить".\n'
                   'В разделе "Мои дела" вы можете посмотреть список ваших дел и перейти к'
                   ' параметрам дела. Там вы сможете узнать сколько времени было потрачено. Также вам доступны такие'
                   ' функции как "Засечь время", "Отменить последнее время", "Восстановить последнее время",'
                   ' "Удалить дело", "Сколько времени", "Список дел", "Меню".\nПодсказки можно отключить командой'
                   ' "Выключить подсказки".\nВ любой непонятной ситуации кричите "Помощь"!\nПриятного пользования!',

                   'Для начала вам нужно создать дело. Выбирайте название с умом, например: "Игра на гитаре",'
                   ' sil <[200]> "Прогулка в парке", sil <[200]> "Упражнение планка".\n Для того чтобы начать отсчёт,'
                   ' перейдите в раздел "Засечь время" и выберите из списка дело, которое хотите засечь.'
                   ' Можно воспользоваться командой "Засечь sil <[200]> название дела".\nЧтобы я повторила'
                   ' предыдущую фразу, скажите "Повторить".\nВ разделе "Мои дела" вы можете посмотреть список'
                   ' ваших дел и перейти к параметрам дела. Там вы сможете узнать сколько времени было потрачено.'
                   ' Также вам доступны такие функции как "Засечь время", sil <[200]>  "Отменить последнее время",'
                   ' sil <[200]> "Восстановить последнее время", sil <[200]> "Удалить дело", sil <[200]>'
                   ' "Сколько времени", sil <[200]> "Список дел", sil <[200]> "Меню". Стоит уделить'
                   ' внимание подсказкам. Подсказки можно отключить командой "Выключить подсказки".\nВ любой'
                   ' непонятной ситуации кричите "Помощь"!\nПриятного пользования!'],
        "create_thing":
            {"start": ['Скажите название вашего дела.',
                       'Скажите название вашего дела.'],
             "actions": [[' Чтобы отменить создание дела, воспользуйтесь командой "Отмена".',
                          'Чтобы отменить создание дела, воспользуйтесь командой "Отмена".'],
                         [' Если захотите отменить создание дела - скажите "Отмена".',
                          'Если захотите отменить создание дела - скажите "Отмена".']],
             "0": {
                 "help": [
                     'Название вашего дела должно состоять из русских букв, не содержать служебных слов, не должно быть'
                     ' короче пяти символов и длиннее двадцати символов.',
                     'Название вашего дела должно состоять из русских букв, не содержать служебных слов, не должно быть'
                     ' короче пяти символов и длиннее двадцати символов.', ],
                 "errors": {"serv": ['Название не должно содержать служебные слова, такие как: "дела","засечь" и т.д.',
                                     'Название не должно содержать служебные слова, такие как "дела","засечь" и т.д.'],
                            "rus": ['Дело должно состоять только из русских букв и пробелов.',
                                    'Дело должно состоять только из русских букв и пробелов.'],
                            "20": ['Название дела должно состоять не более чем из 20 символов.',
                                   'Название дела должно состоять не более чем из 20 символов.'],
                            "5": ['Название дела должно состоять не менее чем из 5 символов.',
                                  'Название дела должно состоять не менее чем из 5 символов.'],
                            "repeat": ['Такое дело у вас уже есть.',
                                       'Такое дело у вас уже есть.'],
                            "bich": ['В названии присутствует ненормативная лексика. Пожалуйста переформулируйте.',
                                     'В названии присутствует ненормативная лексика. Пожалуйста переформулируйте.']
                            },
                 "created": ['Дело сохранено! Засечь время?', 'Дело сохранено. Засечь время?']
             },
             "1": {
                 "help": [
                     'Скажите "Да", чтобы я засекла время, или "Нет", чтобы перейти в главное меню.',
                     'Скажите "Да", чтобы я засекла время, sil <[300]> или "Нет", чтобы перейти в главное меню.'],
             },
             "2": {"start": [
                 'Упс. У вас уже максимально количество дел. Мне удалить существующее дело, чтобы освободить место?',
                 'Упс. У вас уже максимально количество дел. Мне удалить существующее дело, чтобы освободить место?'],
                 "help": ['Скажите "Да" если хотите удалить какое-нибудь дело. Если не хотите, скажите "Нет"',
                          'Скажите "Д+а." если хотите удалить какое-нибудь дело. Если не хотите, скажите "Нет"']},
             "3": {"start": [
                 'Выберите дело, которое нужно удалить. ',
                 'Выберите дело, которое нужно удалить. '],
                 "after_delete_thing": [
                     'Занятие под названием "{}" удалено. Скажите название вашего нового дела, и я его добавлю. ',
                     'Занятие под названием "{}" удалено. Скажите название вашего нового дела, и я его добавлю. '],
                 "help": [
                     'Скажите "Отмена", чтобы отменить удаление. Скажите "Список", чтобы услышать список. ',
                     'Скажите "Отмена", чтобы отменить удаление. Скажите "Список", чтобы услышать список.'],
                 "else": ['Такого дела не нашла. Попытайтесь снова. Также вам доступны команды "Отмена" и "Список".',
                          'Такого дела не нашла. Попытайтесь снова. Также вам доступны команды "Отмена"'
                          ' sil <[300]> и sil <[300]>"Список".']},
             },
        "timeflow":
            {
                "start":
                    {"new_session": ['Текущее задание: "{}"\nВремени прошло: {}:{}:{} ',
                                     'Текущее задание: {}\n Времени прошло: {}\n'],
                     "old_session": ['Текущее задание: "{}"\nВремени прошло: {}:{}:{} ',
                                     'Текущее задание: {}\n Времени прошло: {}\n'],
                     "start": ['Текущее задание: "{}"\n {}',
                               'Текущее задание: {}\n {}'],
                     "start_words": [['Отсчёт пошёл!', 'Отсчёт пошёл!'], ['Поехали!', 'Поехали!'],
                                     ['Начинаем!', 'Начинаем!']],
                     "start_actions": [[' Чтобы узнать сколько прошло времени, скажите "Обновить".'
                                        ' Когда завершите своё дело, произнесите "Завершить".',
                                        'Чтобы узнать сколько прошло времени, скажите "Обновить".'
                                        ' Когда завершите своё дело, произнесите "Завершить"'],
                                       ['', 'Обновить. sil <[300]> Завершить.']]
                     },
                "help": [
                    'Скажите "Обновить", чтобы узнать сколько времени прошло. Когда завершите своё дело, произнесите'
                    ' "Завершить", чтобы остановить отсчёт и записать результат. Другие команды запрещены во время'
                    ' выполнения текущего дела.',
                    'Скажите "Обновить", чтобы узнать сколько времени прошло. Когда завершите своё дело произнесите'
                    ' "Завершить", чтобы остановить отсчёт и записать результат. Другие команды запрещены во время'
                    ' выполнения текущего дела.'],
                "20": ['Вы провели больше 20 часов выполняя своё дело, что-то мне не верится. Я сбросила таймер.',
                       'Вы провели больше двадцати часов выполняя своё дело, что-то мне не верится. Я сбросила таймер.'
                       'Засечь время. Добавить дело. Мои дела.'],
                "stop": ['Вы выполняли дело "{}" на протяжении {}:{}:{}. ',
                         "Вы выполняли дело {} на протяжении {}."],
                "update": ['Текущее задание: "{}"\nВремени прошло {}:{}:{} ',
                           'Текущее задание: {}\n Времени прошло {} \n'],
                "stop_victory": [['Хорошая работа! ', 'Хорошая работа!'],
                                 ['Отличная работа! Надеюсь, вы с пользой провели время! ',
                                  'Отличная работа! Надеюсь, вы с пользой провели время!'],
                                 ['Отлично! Вы на верном пути! ', 'Отлично! Вы на верном пути!'],
                                 ['Круто! ', 'Круто!']],
                "stop_actions": [[" Что желаете сделать дальше? Открыть список дел? Может быть, добавить дело?",
                                  "Что желаете сделать дальше? Открыть список дел? Может быть,sil <[300]>"
                                  "  добавить дело?"],
                                 [" Какие дальше планы? Открыть список дел? Добавить дело?",
                                  "Какие дальше планы? Открыть список дел? Добавить дело?"]],
            },
        "menu":
            {"start":
                 {'hello': [['Привет!', 'Привет!'], ['Приветствую!', 'Приветствую!'],
                            ['Здравствуйте!', 'Здравствуйте!'], ['Приветствую вас!', 'Приветствую вас!']],
                  "new_session": {"empty_list": ['Похоже у вас пустой список занятий.',
                                                 'Похоже у вас пустой список занятий.'],
                                  "empty_actions": [[' Скажите "Добавить дело".', 'Скажите "Добавить дело".'],
                                                    [' Давайте создадим дело командой "Добавить дело".',
                                                     'Давайте создадим дело командой "Добавить дело".']],
                                  "true_list": [
                                      '',
                                      ''],
                                  "true_actions": [[
                                      " Чего желаете? Может быть, засечь время, открыть список занятий"
                                      " или добавить занятие?",
                                      'Чего желаете? Может быть, засечь время, открыть список занятий'
                                      ' или добавить занятие?'],
                                      [" Давайте откроем список дел или засечём время, или добавим дело?",
                                       "Давайте откроем список дел sil <[300]> или засечём время, или добавим дело?"]]},

                  "new_user": [
                      'Этот навык может помочь вам контролировать время, которое вы тратите на свои занятия.',
                      'Этот навык может помочь вам контролировать время, которое вы тратите на свои занятия.'
                      'Давайте добавим занятие. Произнесите "Добавить дело".'],
                  "old_session": {"empty_list": ['Похоже у вас пустой список занятий.',
                                                 'Похоже у вас пустой список занятий.'],
                                  "empty_actions": [[' Скажите "Добавить дело".', 'Скажите "Добавить дело".'],
                                                    [' Давайте создадим дело командой "Добавить дело".',
                                                     'Давайте создадим дело командой "Добавить дело".']],
                                  "true_actions": [[
                                      " Чего желаете? Может быть, засечь время, открыть список занятий"
                                      " или добавить занятие?",
                                      ' Чего желаете? Может быть, засечь время, открыть список занятий'
                                      ' sil <[200]>  или добавить занятие?'],
                                      [" Давайте откроем список дел или засечём время, или добавим дело?",
                                       "Давайте откроем список дел или засечём время, sil <[200]> или добавим дело?"],
                                      [' Что вам нужно? Список дел, добавить дело или засечь время?',
                                       'Что вам нужно? Список дел, добавить дело sil <[200]> или засечь время?']]
                                  }

                  },
             "can": ['Я могу помочь вам отслеживать время которое вы тратите на какое-нибудь занятие.',
                     'Я могу помочь вам отслеживать время которое вы тратите на какое-нибудь занятие.'],
             "start_timer": ['Хотите чтобы я поставила таймер на действие {}?',
                             'Хотите чтобы я поставила таймер на действие {}?'],
             "help": ['Выберите что вам нужно: засечь время, добавить дело или открыть список ваших дел.'
                      ' Если вы хотите прослушать полную инструкцию, скажите "Инструкция".',
                      'Выберите что вам нужно: засечь время, добавить дело или открыть список ваших дел.'
                      ' Если вы хотите прослушать полную инструкцию, скажите "Инструкция".']
             },
        "timer": {
            "start": [['Какое дело выбираете?\n', 'Какое дело выбираете? sil <[300]>'],
                      ['Вот список дел:\n', 'Вот список дел sil <[300]>'],
                      ['', ''], ['Диктую список дел.\n', 'Диктую список дел. sil <[300]>']],
            "zero": ['Ваш список дел пуст. Чтобы добавить дело, скажите "Добавить дело".',
                     'Ваш список дел пуст. Чтобы добавить дело, скажите "Добавить дело".'],
            "thing": ["{}\n", "{}\n"],
            "help": ['Скажите "Меню", чтобы перейти в главное меню. Скажите "Список", чтобы услышать список. ',
                     'Скажите "Меню", чтобы перейти в главное меню. Скажите "Список", чтобы услышать список. '],
            "else": ['Такого дела не обнаружилось. Повторите. ',
                     'Такого дела не обнаружилось. Повторите. ']
        },
        "usersthing": {
            "zero": ['Ваш список дел пуст. Чтобы добавить дело, скажите "Добавить дело".',
                     'Ваш список дел пуст. Чтобы добавить дело, скажите "Добавить дело".'],
            'start': ["", ""],
            '-1': {"help": [
                'Вы находитесь в параметрах вашего дела. Здесь вы можете узнать проведённое за этим делом время'
                ' с помощью команды "Время". Скажите "Засечь время", для того чтобы начать отсчёт. Чтобы отменить или'
                ' восстановить последнее время, воспользуйтесь командами "Отменить последнее" или "Вернуть последнее",'
                ' соответственно. Если вы захотите удалить дело, скажите "Удалить". Также вы можете попасть в меню или'
                ' открыть список дел. Командами "Меню" или "Список".',
                'Вы находитесь в параметрах вашего дела. Здесь вы можете узнать проведённое за этим делом время'
                ' с помощью команды "Время". Скажите "Засечь время", для того чтобы начать отсчёт. Чтобы отменить или'
                ' восстановить последнее время, воспользуйтесь командами "Отменить последнее" или "Вернуть последнее",'
                ' соответственно. Если вы захотите удалить дело, скажите "Удалить". Также вы можете попасть в меню sil'
                ' <[300]> или открыть список дел. Командами "Меню" sil <[300]> или "Список".'],
                "suc_return": [
                    "Ваш последний прогресс успешно восстановлен.",
                    "Ваш последний прогресс успешно восстановлен."],
                "unsuc_return": ["Вы ещё не засекали время.",
                                 "Вы ещё не засекали время."],
                "suc_cancel": ['Отменила последнее время. Вы можете восстановить его командой "Вернуть последнее".',
                               'Отменила последнее время. Вы можете восстановить его командой "Вернуть последнее".'],
                "none_cancel": ["Вы ещё не засекали время. ",
                                "Вы ещё не засекали время. "],
                "unsuc_cancel": ["Уже отменила последнее время. ",
                                 "Уже отменила последнее время. "],
                "want_del": ['Вы точно хотите удалить занятие "{}"?', "Вы точно хотите удалить занятие {}?"],
                "actions": [[" Засечь время? Перейти в список или в меню?",
                             "Засечь время? Перейти в список sil <[250]> или в меню?"],
                            [" Может быть, поставить таймер? Хочешь увидеть список дел? Перейти в меню?",
                             "Может быть, поставить таймер? Хочешь увидеть список дел? Перейти в меню?", ]]

            },
            '-2': {"help": ["Если требуется удалить скажите да, иначе скажите нет!",
                            "Если требуется удалить скажите да, иначе скажите нет!"],
                   "del": ["Занятие успешно удалено!",
                           "Занятие успешно удалено!"]},
            "list": {"help": [
                'Скажите название вашего дела, чтобы открыть его параметры. Чтобы послушать список снова, скажите'
                ' "Список". Произнесите "Меню", для того чтобы перейти в главное меню.',
                'Скажите название вашего дела, чтобы открыть его параметры. Чтобы послушать список снова, скажите'
                ' "Список". Произнесите "Меню", для того чтобы перейти в главное меню.'],
                "next_empty": ['На этом ваш список заканчивается.', 'На этом ваш список заканчивается.'],
                "back_empty": ['Позади ничего нет.', 'Позади ничего нет.'],
                "thing_menu": ['{}\n Вы занимались этим делом {}:{}:{} \nПоследний раз вы занимались {}:{}:{}',
                               '{}\n Вы занимались этим делом {} \nПоследний раз вы занимались {}'],
                "empty_thing_menu": ['{}\nВы ещё не занимались этим делом.',
                                     '{} sil <[300]> Вы ещё не занимались этим делом.'],
            }
        }}}
