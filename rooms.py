from constants import *
from database import ThingTime, add_new_thing, get_things_list, add_thing_flow, TimeFlow
from time_change import time_change


def get_thing_flow(db, user_id):
    return db.session.query(TimeFlow).filter_by(user_id=user_id).first()


class Menu():
    def __init__(self, res, req, db, user, timeflow, new):
        self.res = res
        self.req = req
        self.db = db
        self.user = user
        self.new = new
        self.timeflow = timeflow

    def get_c_t(self):
        if self.req['request'].get("original_utterance"):
            command = self.req['request']["original_utterance"].strip().lower()
            tokens = self.req['request']['nlu']['tokens']
        else:
            command = self.req['request']["payload"]["text"]
            tokens = list(map(lambda x: x.lower(), self.req['request']["payload"]["text"].split()))
        return command, tokens

    def start(self):
        if self.timeflow:
            times = time_change(time.time() - self.timeflow.time_start)
            if self.new:
                thing = ThingTime.query.filter_by(id=self.timeflow.thing_id).first()
                self.res['response']['text'] = \
                    'Текущее задание: {}\n Времени прошло {}:{}:{}\n'.format(thing.name, *times)
            else:
                thing = ThingTime.query.filter_by(id=self.timeflow.thing_id).first()
                self.res['response']['text'] = \
                    'Текущее задание: {}\n Времени прошло {}:{}:{}\n'.format(thing.name, *times)
            self.res['response']['buttons'] = [BUTTONS["update"], BUTTONS["stop"]]

        else:
            if self.new:
                self.user.step_passage = 0
                self.user.step_room = 0
                self.db.session.commit()
                self.res['response']["card"] = info['menu']
                self.res['response']["card"]['header']['text'] = self.res['response']['text'] = 'Меню'
                self.res['response']['tts'] = 'Меню'
                self.res['response']['buttons'] = [BUTTONS["help"], BUTTONS["can"]]
            else:
                self.res['response']["card"] = info['menu']
                self.res['response']["card"]['header']['text'] = self.res['response']['text'] = 'Меню'
                self.res['response']['tts'] = 'Меню'
                self.res['response']['buttons'] = [BUTTONS["help"], BUTTONS["can"]]

    def tree(self):
        command, tokens = self.get_c_t()
        if self.timeflow:
            thing = ThingTime.query.filter_by(id=self.timeflow.thing_id).first()
            if any(word in tokens for word in HELP):
                self.res['response']['text'] = 'Помогаю'
                self.res['response']['buttons'] = [BUTTONS["update"], BUTTONS["stop"]]
            elif any(word in tokens for word in STOP):
                this_time = time.time()
                thing.time = thing.time + (this_time - self.timeflow.time_start)
                thing.last_time = this_time - self.timeflow.time_start
                thing.res_last_time = 1
                times = time_change(thing.last_time)
                self.db.session.delete(self.timeflow)
                self.db.session.commit()
                self.res['response']['text'] = "Ты выполнял дело {} на протяжении {}:{}:{} ".format(thing.name,
                                                                                                    *times)

            elif any(word in tokens for word in UPDATE):
                times = time_change(time.time() - self.timeflow.time_start)
                self.res['response']['text'] = \
                    'Текущее задание: {}\n Времени прошло {}:{}:{}\n'.format(thing.name,
                                                                             *times)
                self.res['response']['buttons'] = [BUTTONS["update"], BUTTONS["stop"]]
            else:
                self.res['response']['text'] = "пояснение"
                self.res['response']['buttons'] = [BUTTONS["update"], BUTTONS["stop"]]
        else:
            if self.new:
                self.user.step_passage = 0
                self.user.step_room = 0
                self.db.session.commit()
                self.res['response']["card"] = info['menu']
                self.res['response']["card"]['header']['text'] = self.res['response']['text'] = 'Меню'
                self.res['response']['tts'] = 'Меню'
            else:
                things_list = get_things_list(self.req['session']['user_id'])

                if any(word in tokens for word in START_TIME) and search_thing(command, things_list):
                    thing = search_thing(command, things_list)
                    self.user.step_passage = -1
                    self.user.thing_id = thing.id
                    self.db.session.commit()
                    self.res['response']['text'] = 'Хочешь чтобы я поставила таймер на действие {}?'.format(thing.name)
                elif all(word in tokens for word in ['умеешь', "что"]):
                    self.res['response'][
                        'text'] = 'Я могу помочь тебе отслеживать время которое вы тратите на какое-нибудь занятие'
                    self.res['response'][
                        'tts'] = 'Я могу помочь тебе отслеживать время которое вы тратите на какое-нибудь занятие'
                    self.res['response']['buttons'] = sessionSettings[str(self.user.user_id)]["buttons"]
                elif self.user.step_passage == -1:
                    if any(word in tokens for word in YES):
                        add_thing_flow(self.user.id, self.user.thing_id)
                        self.go_menu()
                    else:
                        recordtime = RecordTime(self.res, self.req, self.db, self.user, self.timeflow, False)
                        self.user.step_room = 0
                        self.user.step_passage = 2
                        self.db.session.commit()
                        recordtime.start(command, tokens)
                        self.res = recordtime.get_res()
                elif self.user.step_passage == 0:
                    self.user.step_room = 0
                    self.db.session.commit()
                    if any(word in tokens for word in THING_LIST):
                        thingslist = UsersThing(self.res, self.req, self.db, self.user, self.timeflow, False)
                        self.user.step_room = 0
                        self.user.step_passage = 1
                        self.db.session.commit()
                        thingslist.start(command, tokens)
                        self.res = thingslist.get_res()
                    elif any(word in tokens for word in START_TIME):
                        recordtime = RecordTime(self.res, self.req, self.db, self.user, self.timeflow, False)
                        self.user.step_room = 0
                        self.user.step_passage = 2
                        self.db.session.commit()
                        recordtime.start(command, tokens)
                        self.res = recordtime.get_res()
                    elif any(word in tokens for word in CREATE):
                        creater = CreateThing(self.res, self.req, self.db, self.user, self.timeflow, False)
                        self.user.step_room = 0
                        self.user.step_passage = 3
                        self.db.session.commit()
                        creater.start(command, tokens)
                        self.res = creater.get_res()
                    else:
                        self.res['response']["card"] = info['menu']
                        self.res['response']["card"]['header']['text'] = self.res['response']['text'] = 'Меню'
                        self.res['response']['tts'] = 'Меню'

                elif self.user.step_passage == 1:
                    thingslist = UsersThing(self.res, self.req, self.db, self.user, self.timeflow, False)
                    thingslist.tree(command, tokens)
                    self.res = thingslist.get_res()

                elif self.user.step_passage == 2:
                    recordtime = RecordTime(self.res, self.req, self.db, self.user, self.timeflow, False)
                    recordtime.tree(command, tokens)
                    self.res = recordtime.get_res()

                elif self.user.step_passage == 3:
                    creater = CreateThing(self.res, self.req, self.db, self.user, self.timeflow, False)
                    creater.tree(command, tokens)
                    self.res = creater.get_res()
                else:
                    self.res['response']["card"] = info['menu']
                    self.res['response']["card"]['header']['text'] = self.res['response']['text'] = 'Меню'
                    self.res['response']['tts'] = 'Меню'
                    self.res['response']['buttons'] = [BUTTONS['help'], BUTTONS['can']]
                    self.user.step_passage = 0
                    self.user.step_room = 0
                    self.db.session.commit()

    def go_menu(self):
        self.timeflow = get_thing_flow(self.db, self.user.id)
        self.user.step_passage = 0
        self.user.step_room = 0
        self.db.session.commit()
        menu = Menu(self.res, self.req, self.db, self.user, self.timeflow, False)
        menu.start()
        self.res = menu.get_res()
        return self.res

    def get_res(self):
        return self.res


class CreateThing():
    def __init__(self, res, req, db, user, timeflow, new):
        self.res = res
        self.req = req
        self.db = db
        self.user = user
        self.new = new
        self.timeflow = timeflow

    def start(self, command, tokens):
        self.res['response']['text'] = 'Назови название дейставия'
        self.res['response']['tts'] = 'Назови название дейставия'
        self.res['response']['buttons'] = [BUTTONS["help"]]

    def tree(self, command, tokens):
        command = command.strip().lower()
        if self.user.step_room == 0:
            if any(word in tokens for word in HELP):
                self.res['response']['text'] = "Помогаю"
                self.res['response']['buttons'] = sessionSettings[self.user.user_id]['buttons']
            # elif command.isdigit():
            #     self.res['response']['text'] = 'Назови название дейставия'
            #     self.res['response']['tts'] = 'Назови название дейставия'
            elif ThingTime.query.filter_by(name=command).first():
                self.res['response']['text'] = 'Такое занятие у вас уже есть'
                self.res['response']['tts'] = 'Такое занятие у вас уже есть'
                self.res['response']['buttons'] = sessionSettings[self.user.user_id]['buttons']
            elif not command.replace(' ', '').isalpha():
                self.res['response']['text'] = 'Занятие должно состоять из слов, без символов'
                self.res['response']['tts'] = 'Занятие должно состоять из слов, без символов'
                self.res['response']['buttons'] = sessionSettings[self.user.user_id]['buttons']
            # elif any([x for x in tokens if len(x)<4]):
            elif len(command.strip().lower()) > 20:
                self.res['response']['text'] = 'Название занятия должно состоять не более чем из 20 символов'
                self.res['response']['tts'] = 'Название занятия должно состоять не более чем из двадцати символов'
                self.res['response']['buttons'] = sessionSettings[self.user.user_id]['buttons']
            elif len(command.strip().lower()) < 5:
                self.res['response']['text'] = 'Название занятия должно состоять не менее чем из 5 символов'
                self.res['response']['tts'] = 'Название занятия должно состоять не менее чем из пяти символов'
                self.res['response']['buttons'] = sessionSettings[self.user.user_id]['buttons']
            else:
                thing = add_new_thing(self.req['session']['user_id'], command.lower())
                self.user.thing_id = thing.id
                self.user.step_room = 1
                self.db.session.commit()

                self.res['response']['text'] = 'Создала, засечь время?'
                self.res['response']['tts'] = 'Создала, засечь время?'
                self.res['response']['buttons'] = [BUTTONS["yes"], BUTTONS["no"], BUTTONS["help"]]

        elif self.user.step_room == 1:
            thing = ThingTime.query.filter_by(id=self.user.thing_id).first()
            if any(word in tokens for word in HELP):
                self.res['response']['text'] = "Помогаю"
                self.res['response']['buttons'] = sessionSettings[self.user.user_id]['buttons']
            elif any(word in tokens for word in YES) or any(word in tokens for word in START_TIME):
                add_thing_flow(self.user.id, thing.id)
                self.go_menu()
            elif any(word in tokens for word in THING_LIST) or any(word in tokens for word in NO):
                self.user.step_passage = 0
                self.user.step_room = 0
                self.db.session.commit()
                menu = Menu(self.res, self.req, self.db, self.user, self.timeflow, False)
                menu.start()
                self.res = menu.get_res()

            else:
                self.res['response']['text'] = 'Повтори'
                self.res['response']['tts'] = 'Повтори'
                self.res['response']['buttons'] = [BUTTONS["help"]]

    def go_menu(self):
        self.timeflow = get_thing_flow(self.db, self.user.id)
        self.user.step_passage = 0
        self.user.step_room = 0
        self.db.session.commit()
        menu = Menu(self.res, self.req, self.db, self.user, self.timeflow, False)
        menu.start()
        self.res = menu.get_res()
        return self.res

    def get_res(self):
        return self.res


class RecordTime():
    def __init__(self, res, req, db, user, timeflow, new):
        self.res = res
        self.req = req
        self.db = db
        self.user = user
        self.new = new
        self.timeflow = timeflow

    def start(self, command, tokens):
        things_list = get_things_list(self.req['session']['user_id'])
        str_things_list = self.get_str_things_list(things_list, 0, 15, 0)
        self.res['response']['buttons'] = []
        if things_list[15:]:
            self.res['response']['buttons'].append(BUTTONS["next"])
        self.res['response']['buttons'].append(BUTTONS["menu"])
        self.res['response']['text'] = str_things_list
        self.res['response']['tts'] = str_things_list

        if len(things_list) == 0:
            self.res['response']['text'] = "Шеф, похоже здесь пусто"
            self.res['response']['tts'] = "Шеф, похоже здесь пусто"
        self.res['response']['buttons'].append(BUTTONS["menu"])

    def get_str_things_list(self, things_list, n_1, n_2, last_n):
        str_things_list = ""
        for num, thing in enumerate(things_list[n_1:n_2]):
            str_things_list += "{}. {}\n".format(last_n + num + 1, thing.name.capitalize())
        return str_things_list

    def tree(self, command, tokens):
        things_list = get_things_list(self.req['session']['user_id'])
        if any(word in tokens for word in HELP):
            self.res['response']['text'] = "Помогаю"
            self.res['response']['buttons'] = [BUTTONS["menu"], BUTTONS["help"]]
        elif any(word in tokens for word in BACK) or any(word in tokens for word in NEXT):
            if any(word in tokens for word in NEXT):
                if len(things_list) >= (self.user.step_room + 1) * 15:
                    self.user.step_room += 1

                else:
                    pass
            elif any(word in tokens for word in BACK):
                if self.user.step_room - 1 >= 0:
                    self.user.step_room -= 1

                else:
                    pass

            self.db.session.commit()

            if self.user.step_room == 0:
                str_things_list = self.get_str_things_list(things_list, 0, 15, 0)
                self.res['response']['text'] = str_things_list
                if things_list[15:]:
                    self.res['response']['buttons'].append(BUTTONS["next"])

            else:
                str_things_list = self.get_str_things_list(things_list, self.user.step_room * 15,
                                                           (self.user.step_room + 1) * 15,
                                                           (self.user.step_room) * 15)
                self.res['response']['text'] = str_things_list
                if things_list[(self.user.step_room + 1) * 15:]:
                    self.res['response']['buttons'].append(BUTTONS["next"])
                self.res['response']['buttons'].append(BUTTONS["back"])
            self.res['response']['buttons'].append(BUTTONS["menu"])
            self.res['response']['buttons'].append(BUTTONS["help"])
            if len(things_list) == 0:
                self.res['response']['text'] = "Здесь ничего нет"
        elif any(word in tokens for word in MENU):
            self.go_menu()
        elif any(word in command.lower().strip() for word in [x.name.lower() for x in things_list]):
            thing = self.search_thing(command, things_list)
            add_thing_flow(self.user.id, thing.id)
            self.go_menu()
        else:
            self.res['response']['text'] = 'Повтори'
            self.res['response']['tts'] = 'Повтори'
            self.res['response']['buttons'] = [BUTTONS["menu"], BUTTONS["help"]]

    def search_thing(self, command, things_list):
        for thing in things_list:
            if command.lower().strip() == thing.name.lower().strip():
                return thing

    def get_res(self):
        return self.res

    def go_menu(self):
        self.timeflow = get_thing_flow(self.db, self.user.id)
        self.user.step_passage = 0
        self.user.step_room = 0
        self.db.session.commit()
        menu = Menu(self.res, self.req, self.db, self.user, self.timeflow, False)
        menu.start()
        self.res = menu.get_res()
        return self.res


class UsersThing():
    def __init__(self, res, req, db, user, timeflow, new):
        self.res = res
        self.req = req
        self.db = db
        self.user = user
        self.new = new
        self.timeflow = timeflow

    def start(self, command, tokens):
        things_list = get_things_list(self.req['session']['user_id'])
        self.res['response']['text'] = 'Страница 1'
        self.res['response']['tts'] = 'Страница 1'
        self.res['response']['buttons'] = []
        self.res['response']["card"] = copy.deepcopy(info['things_list'])
        self.res['response']["card"]['header']['text'] = self.res['response']['text']

        for item in things_list[:5]:
            self.res['response']["card"]["items"].append({
                "title": "• " + item.name.capitalize(),
                "button": {
                    "text": item.name,
                    "payload": {
                        "text": item.name
                    }
                }
            })
        if things_list[5:]:
            self.res['response']['buttons'].append(BUTTONS["next"])
        self.res['response']['buttons'].append(BUTTONS["menu"])
        self.res['response']['buttons'].append(BUTTONS["help"])
        if len(self.res['response']["card"]["items"]) == 0:
            del self.res['response']["card"]
            self.res['response']['text'] = 'Здесь пусто'

    def tree(self, command, tokens):
        things_list = get_things_list(self.req['session']['user_id'])
        if self.user.step_room == -2:
            thing = ThingTime.query.filter_by(id=self.user.thing_id).first()
            if any(word in tokens for word in YES):
                self.res['response']['text'] = "Занятие успешно удалено!"
                self.db.session.delete(thing)
                self.user.step_passage = 1
                self.user.step_room = 0
                self.start(command, tokens)
                self.db.session.commit()
            else:
                pass
        elif self.user.step_room == -1:
            thing = ThingTime.query.filter_by(id=self.user.thing_id).first()
            if any(word in tokens for word in HELP):
                self.res['response']['text'] = "Помогаю"
                self.res['response']['buttons'] = sessionSettings[self.user.user_id]['buttons']
            elif any(word in tokens for word in START_TIME):
                add_thing_flow(self.user.id, thing.id)
                self.go_menu()
            elif any(word in tokens for word in RETURN_LAST_TIME):
                if thing.res_last_time == 2:
                    thing.time = thing.time + thing.last_time
                    thing.res_last_time = 1
                    self.res['response']['text'] = "Сделано"
                else:
                    self.res['response']['text'] = "нечего возвращать"
                self.res['response']['buttons'] = sessionSettings[self.user.user_id]['buttons']
            elif any(word in tokens for word in CANCEL_LAST_TIME):

                if thing.res_last_time == 0:
                    self.res['response']['text'] = "Вы ещё не засекали время"
                elif thing.res_last_time == 2:
                    self.res['response']['text'] = "Уже отменила последнее время"
                else:
                    thing.time = thing.time - thing.last_time
                    thing.res_last_time = 2
                    self.res['response']['text'] = "Сделано"
                self.res['response']['buttons'] = sessionSettings[self.user.user_id]['buttons']
            elif any(word in tokens for word in THING_LIST):
                self.user.step_passage = 1
                self.user.step_room = 0
                self.start(command, tokens)
            elif any(word in tokens for word in DELETE):
                self.user.step_room = -2

                self.res['response']['text'] = "Вы точно хотите удалить занятие {}?".format(thing.name)
                self.res['response']['buttons'] = [BUTTONS["yes"], BUTTONS["no"]]
            elif any(word in tokens for word in MENU):
                self.go_menu()
            else:
                self.res['response']['text'] = "не поняв"
                self.res['response']['buttons'] = sessionSettings[self.user.user_id]['buttons']
            self.db.session.commit()
        else:
            self.res['response']["card"] = copy.deepcopy(info['things_list'])
            if any(word in command.lower().strip() for word in [x.name.lower() for x in things_list]):
                thing = search_thing(command, things_list)
                times_last = time_change(thing.last_time)
                times_all = time_change(thing.time)
                self.user.step_room = -1
                self.user.thing_id = thing.id
                self.db.session.commit()
                self.res['response']['text'] = '{}\nВремя {}:{}:{} \nПоследний раз {}:{}:{}'.format(thing.name,
                                                                                                    *times_all,
                                                                                                    *times_last)
                self.res['response']['tts'] = '{}\nВремя {}:{}:{} \nПоследний раз {}:{}:{}'.format(thing.name,
                                                                                                   *times_all,
                                                                                                   *times_last)
                del self.res['response']['card']
                self.res['response']['buttons'] = [BUTTONS["start"]]
                if thing.res_last_time == 1:
                    self.res['response']['buttons'].append(BUTTONS["cancel"])
                elif thing.res_last_time == 2:
                    self.res['response']['buttons'].append(BUTTONS["return"])
                else:
                    pass
                self.res['response']['buttons'].append(BUTTONS["delete"])
                self.res['response']['buttons'].append(BUTTONS["menu"])
            elif any(word in tokens for word in HELP):
                self.res['response']['text'] = "Помогаю"
            elif any(word in tokens for word in NEXT) or any(word in tokens for word in BACK):
                if any(word in tokens for word in NEXT):
                    if len(things_list) > (self.user.step_room + 1) * 5:
                        self.user.step_room += 1
                        self.res['response']["card"]['header']['text'] = self.res['response'][
                            'text'] = "Страница {}".format(
                            self.user.step_room + 1)
                    else:
                        self.res['response']["card"]['header']['text'] = self.res['response'][
                            'text'] = "Дальше ничего нет."
                elif any(word in tokens for word in BACK):
                    if self.user.step_room - 1 >= 0:
                        self.user.step_room -= 1
                        self.res['response']["card"]['header']['text'] = self.res['response'][
                            'text'] = "Страница {}".format(
                            self.user.step_room + 1)
                    else:
                        self.res['response']["card"]['header']['text'] = self.res['response'][
                            'text'] = "Позади пустота."
                self.db.session.commit()

                if self.user.step_room == 0:
                    for item in things_list[:5]:
                        self.res['response']["card"]["items"].append({
                            "title": "• " + item.name.capitalize(),
                            "button": {
                                "text": item.name,
                                "payload": {
                                    "text": item.name
                                }
                            }
                        })

                    if things_list[5:]:
                        self.res['response']['buttons'].append(BUTTONS["next"])
                else:
                    for item in things_list[self.user.step_room * 5: (self.user.step_room + 1) * 5]:
                        self.res['response']["card"]["items"].append({
                            "title": "• " + item.name.capitalize(),
                            "button": {
                                "text": item.name,
                                "payload": {
                                    "text": item.name
                                }
                            }
                        })
                    if things_list[(self.user.step_room + 1) * 5:]:
                        self.res['response']['buttons'].append(BUTTONS["next"])
                    self.res['response']['buttons'].append(BUTTONS["back"])
                self.res['response']['buttons'].append(BUTTONS["menu"])
                if len(things_list) == 0:
                    del self.res['response']["card"]
                    self.res['response']['text'] = 'Здесь пусто'
            elif any(word in tokens for word in MENU):
                self.go_menu()
            else:
                self.res['response']['text'] = "Повтори"
                self.res['response']['buttons'] = sessionSettings[self.user.user_id]['buttons']

    def go_menu(self):
        self.timeflow = get_thing_flow(self.db, self.user.id)
        self.user.step_passage = 0
        self.user.step_room = 0
        self.db.session.commit()
        menu = Menu(self.res, self.req, self.db, self.user, self.timeflow, False)
        menu.start()
        self.res = menu.get_res()
        return self.res

    def get_res(self):
        return self.res


def search_thing(command, things_list):
    for thing in things_list:
        if thing.name.lower().strip() in command.lower().strip():
            return thing
    return False
