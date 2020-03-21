from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
import json, logging, time, copy


def read_json():
    with open("mysite/info.json", "r", encoding='utf-8') as read_file:
        data = json.load(read_file)
    return data


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sqldatabase.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'key?'
db = SQLAlchemy(app)
info = read_json()
sessionSettings = {}

YES = ["да", "давай", "поехали", "начали", "начинаем", "гоу", "го", "конечно", "полетели", "начать", "ес"]
NO = ["нет", "не", "нит", "никак", "ноу"]
START_TIME = ["засекай", "засечь", "таймер", "поставь", "отсчёт", "отсчитывать", "отсчитай", "отсчитывай", "засеки",
              "ставь"]
THING_LIST = ["список", "списки", "лист", "дела", "каталог", "перечень", "каталоги"]
CREATE = ["создать", "создай", "сделай", "сделать", "добавить", "добавь", "каталоги", "дополни"]
MENU = ["главное", "меню", "начало"]
NEXT = ["дальше", "далее", "следующие", "следующее", "вперёд"]
BACK = ["назад", "взад", "возврат", "прежде"]
DELETE = ["удалить", "удали", "удаляй", "делитни"]
HELP = ["помоги", "хелп", "помощь", "help", "выручай", "выручи"]
RETURN_LAST_TIME = ["верни", "вернуть"]
CANCEL_LAST_TIME = ["отмени", "отменить", "отмена"]
STOP = ["стоп", "остановить", "завершить", "останови", "стопни", "stop", "завершай"]
UPDATE = ["обнови", "обновить", "сколько", "натикало"]
BUTTONS = {'yes': {
    "title": "Да",
    "hide": True
}, "no": {
    "title": "Нет",
    "hide": True
}, "menu": {
    "title": "В меню",
    "hide": True
}, "help": {
    "title": "Помощь",
    "hide": True
}, "can": {
    "title": "Что ты умеешь?",
    "hide": True
}, "next": {
    "title": "Далее",
    "hide": True
}, "back": {
    "title": "Назад",
    "hide": True
}, "return": {
    "title": "Вернуть",
    "hide": True
}, "cancel": {
    "title": "Отмена времени",
    "hide": True
}, "delete": {
    "title": "Удалить",
    "hide": True
}, "start": {
    "title": "Засечь",
    "hide": True
}, "update": {
    "title": "Обновить",
    "hide": True
}, "stop": {
    "title": "Завершить",
    "hide": True
}}
