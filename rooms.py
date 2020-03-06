from constants import info
from database import ThingTime, add_new_thing, get_things_list


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
            pass

        else:
            if self.new:
                self.user.step_passage = 0
                self.user.step_room = 0
                self.db.session.commit()
                self.res['response']["card"] = info['menu']
                self.res['response']['text'] = 'Меню'
                self.res['response']['tts'] = 'Меню'
            else:
                self.res['response']["card"] = info['menu']
                self.res['response']['text'] = 'Меню'
                self.res['response']['tts'] = 'Меню'

    def tree(self):
        if self.timeflow:
            self.res['response']['buttons'] = []
            self.res['response']['text'] = 'q'
            self.res['response']['tts'] = 'q'
        else:
            if self.new:
                self.user.step_passage = 0
                self.user.step_room = 0
                self.db.session.commit()
            else:
                command, tokens = self.get_c_t()

                if self.user.step_passage == 0:
                    self.user.step_room = 0
                    self.db.session.commit()
                    if any(word in tokens for word in ['мои', 'действия', 'список']):
                        thingslist = UsersThing(self.res, self.req, self.db, self.user, self.timeflow, False)
                        self.user.step_room = 0
                        self.user.step_passage = 1
                        self.db.session.commit()
                        thingslist.start(command, tokens)
                        self.res = thingslist.get_res()
                    elif any(word in tokens for word in ['засечь', 'таймер', 'поставить']):
                        recordtime = RecordTime(self.res, self.req, self.db, self.user, self.timeflow, False)
                        self.user.step_room = 0
                        self.user.step_passage = 2
                        self.db.session.commit()
                        recordtime.start(command, tokens)
                        self.res = recordtime.get_res()
                    elif any(word in tokens for word in ['добавить']):
                        creater = CreateThing(self.res, self.req, self.db, self.user, self.timeflow, False)
                        self.user.step_room = 0
                        self.user.step_passage = 3
                        self.db.session.commit()
                        creater.start(command, tokens)
                        self.res = creater.get_res()
                    else:
                        self.res['response']['buttons'] = []
                        self.res['response']['text'] = ''
                        self.res['response']['tts'] = ''

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
                    self.user.step_passage = 0
                    self.user.step_room = 0
                    self.db.session.commit()

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
        self.res['response']['buttons'] = []
        self.res['response']['text'] = 'Назови название дейставия'
        self.res['response']['tts'] = 'Назови название дейставия'

    def tree(self, command, tokens):
        if self.user.step_room == 0:
            if command.isdigit():
                self.res['response']['text'] = 'Назови название дейставия'
                self.res['response']['tts'] = 'Назови название дейставия'
            elif ThingTime.query.filter_by(name=command).first():
                self.res['response']['text'] = 'Такое занятие у вас уже есть'
                self.res['response']['tts'] = 'Такое занятие у вас уже есть'
            else:
                add_new_thing(self.req['session']['user_id'], command)
                self.res['response']['text'] = 'Создала, засечь время?'
                self.res['response']['tts'] = 'Создала, засечь время?'
                self.user.step_room = 1
                self.db.session.commit()
        elif self.user.step_room == 1:
            if any(word in tokens for word in ['таймер', 'засечь', 'да']):
                pass
            elif any(word in tokens for word in ['не', 'нет', 'список']):
                self.user.step_passage = 0
                self.user.step_room = 0
                self.db.session.commit()
                menu = Menu(self.res, self.req, self.db, self.user, self.timeflow, False)
                menu.start()
                self.res = menu.get_res()
            else:
                self.res['response']['text'] = 'Повтори'
                self.res['response']['tts'] = 'Повтори'

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
        self.res['response']['buttons'] = []
        self.res['response']['text'] = ''
        self.res['response']['tts'] = ''

    def tree(self, command, tokens):
        if self.user.step_room == 0:
            if any(word in tokens for word in ['засечь', 'таймер', 'поставить']):
                pass
        if self.user.step_room == 1:
            pass

    def get_res(self):
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
        self.res['response']['text'] = 'Список'
        self.res['response']['tts'] = 'Список'
        self.res['response']["card"] = info['things_list'].copy()
        self.res['response']["card"]['header']['text'] = self.res['response']['text']

        for item in things_list[:4]:
            self.res['response']["card"]["items"].append({
                "title": item.name,
                "button": {
                    "text": item.name,
                    "payload": {
                        "text": item.name
                    }
                }
            })
        if things_list[4:]:
            self.res['response']["card"]["items"].append({
                "title": "Далее",
                "button": {
                    "text": "Далее",
                    "payload": {
                        "text": "Далее"
                    }
                }
            })
        self.user.step_room = 1
        self.db.session.commit()

    def tree(self, command, tokens):
        if any(word in tokens for word in ['далее', 'назад']):
            things_list = get_things_list(self.req['session']['user_id'])
            if any(word in tokens for word in ['далее']):
                self.user.step_room += 1
            elif any(word in tokens for word in ['назад']):
                self.user.step_room -= 1
            self.db.session.commit()
            self.res['response']["card"] = info['things_list'].copy()
            if self.user.step_room == 0:
                for item in things_list[:4][0: self.user.step_room * 3]:
                    self.res['response']["card"]["items"].append({
                        "image_id": "",
                        "title": item.name,
                        "button": {
                            "text": item.name,
                            "payload": {
                                "text": item.name
                            }
                        }
                    })
                if things_list[4:]:
                    self.res['response']["card"]["items"].append({
                        "title": "Далее",
                        "button": {
                            "text": "Далее",
                            "payload": {
                                "text": "Далее"
                            }
                        }
                    })
            elif self.user.step_room == 1:
                for item in things_list[4:][0: self.user.step_room * 3]:
                    self.res['response']["card"]["items"].append({

                        "title": item.name,
                        "button": {
                            "text": item.name,
                            "payload": {
                                "text": item.name
                            }
                        }
                    })
                if things_list[4:][self.user.step_room * 3:]:
                    self.res['response']["card"]["items"].append({
                        "title": "Далее",
                        "button": {
                            "text": "Далее",
                            "payload": {
                                "text": "Далее"
                            }
                        }
                    })
                self.res['response']["card"]["items"].append({
                    "title": "Назад",
                    "button": {
                        "text": "Назад",
                        "payload": {
                            "text": "Назад"
                        }
                    }
                })

            else:
                for item in things_list[4:][self.user.step_room * 3: self.user.step_room + 1 * 3]:
                    self.res['response']["card"]["items"].append({
                        "image_id": "",
                        "title": item.name,
                        "button": {
                            "text": item.name,
                            "payload": {
                                "text": item.name
                            }
                        }
                    })
                if things_list[4:][self.user.step_room + 1 * 3:]:
                    self.res['response']["card"]["items"].append({

                        "title": "Далее",
                        "button": {
                            "text": "Далее",
                            "payload": {
                                "text": "Далее"
                            }
                        }
                    })
                self.res['response']["card"]["items"].append({

                    "title": "Назад",
                    "button": {
                        "text": "Назад",
                        "payload": {
                            "text": "Назад"
                        }
                    }
                })
            self.res['response']['text'] = "Список"

        elif any(word in tokens for word in []):
            pass
        else:
            pass

    def get_res(self):
        return self.res
