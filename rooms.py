from constants import *
from database import ThingTime, add_new_thing, get_things_list, add_thing_flow, TimeFlow, refresh_last_time
from time_change import time_change, tts_change


def get_thing_flow(db, user_id):
    return db.session.query(TimeFlow).filter_by(user_id=user_id).first()


def change_r_p(user, room=None, passage=None):
    if not (room is None):
        user.step_room = room
    if not (passage is None):
        user.step_passage = passage


class Menu():
    def __init__(self, res, req, db, user, timeflow, new, new_user, actions_flag):
        self.res = res
        self.req = req
        self.db = db
        self.user = user
        self.new = new
        self.new_user = new_user
        self.timeflow = timeflow
        self.actions_flag = actions_flag
        self.markup = self.req["request"].get("markup")
        if self.markup:
            self.dangerous = self.markup.get("dangerous_context")
        else:
            self.dangerous = False

    def get_c_t(self):
        if self.req['request'].get("original_utterance"):
            command = self.req['request']["original_utterance"].strip().lower()
            tokens = self.req['request']['nlu']['tokens']
        else:
            command = self.req['request']["payload"]["text"]
            tokens = list(map(lambda x: x.lower(), self.req['request']["payload"]["text"].split()))
        return command, tokens

    def start(self):
        things_list = get_things_list(self.req['session']['user_id'])

        if self.timeflow:
            times = time_change(time.time() - self.timeflow.time_start)
            thing = ThingTime.query.filter_by(id=self.timeflow.thing_id).first()
            if (time.time() - self.timeflow.time_start) > 72000:
                change_r_p(self.user, room=0, passage=0)
                self.res['response']["card"] = DIALOGS_CONTENT['cards']['menu']
                self.res['response']["card"]['header']['text'] = self.res['response']['text'] = \
                    DIALOGS_CONTENT["dialogs"]["timeflow"]["20"][0]
                self.res['response']['tts'] = \
                    DIALOGS_CONTENT["dialogs"]["timeflow"]["20"][1]
                if self.actions_flag:
                    action = random.choice(DIALOGS_CONTENT["dialogs"]["timeflow"]["stop_actions"])
                    self.res['response']['text'] += action[0]
                    self.res['response']['tts'] += action[1]

                self.res['response']['buttons'] = [BUTTONS["help"], BUTTONS["can"]]
                self.db.session.delete(self.timeflow)
            else:
                if not (time.time() - self.timeflow.time_start) < 1:

                    if self.new:
                        self.res['response']['text'] = \
                            DIALOGS_CONTENT["dialogs"]["timeflow"]["start"]["new_session"][0].format(
                                thing.name.capitalize(),
                                *times)
                        self.res['response']['tts'] = \
                            DIALOGS_CONTENT["dialogs"]["timeflow"]["start"]["new_session"][1].format(thing.name,
                                                                                                     tts_change(*times))

                    else:
                        self.res['response']['text'] = \
                            DIALOGS_CONTENT["dialogs"]["timeflow"]["start"]["old_session"][0].format(
                                thing.name.capitalize(), *times)
                        self.res['response']['tts'] = \
                            DIALOGS_CONTENT["dialogs"]["timeflow"]["start"]["old_session"][1].format(thing.name,
                                                                                                     tts_change(*times))
                else:
                    start_word = random.choice(DIALOGS_CONTENT["dialogs"]["timeflow"]["start"]["start_words"])
                    self.res['response']['text'] = \
                        DIALOGS_CONTENT["dialogs"]["timeflow"]["start"]["start"][0].format(
                            thing.name.capitalize(), start_word[0])
                    self.res['response']['tts'] = \
                        DIALOGS_CONTENT["dialogs"]["timeflow"]["start"]["start"][1].format(thing.name, start_word[1])
                if self.actions_flag:
                    action = random.choice(DIALOGS_CONTENT["dialogs"]["timeflow"]["start"]["start_actions"])
                    self.res['response']['text'] += action[0]
                    self.res['response']['tts'] += action[1]
                self.res['response']['buttons'] = [BUTTONS["update"], BUTTONS["stop"]]

        else:
            if self.new:
                hello = random.choice(DIALOGS_CONTENT["dialogs"]["menu"]["start"]["hello"])
                if self.new_user:
                    change_r_p(self.user, room=0, passage=0)
                    self.res['response']["card"] = DIALOGS_CONTENT['cards']['menu']
                    self.res['response']['buttons'] = [BUTTONS["help"], BUTTONS["can"]]
                    self.res['response']['text'] = \
                        DIALOGS_CONTENT["dialogs"]["menu"]["start"]["new_user"][0]
                    self.res['response']['tts'] = \
                        DIALOGS_CONTENT["dialogs"]["menu"]["start"]["new_user"][1]

                else:
                    change_r_p(self.user, room=0, passage=0)

                    self.res['response']["card"] = DIALOGS_CONTENT['cards']['menu']
                    self.res['response']['buttons'] = [BUTTONS["help"], BUTTONS["can"]]
                    if things_list:
                        self.res['response']['text'] = \
                            DIALOGS_CONTENT["dialogs"]["menu"]["start"]["new_session"]["true_list"][0]
                        self.res['response']['tts'] = \
                            DIALOGS_CONTENT["dialogs"]["menu"]["start"]["new_session"]["true_list"][1]
                        if self.actions_flag:
                            action = random.choice(
                                DIALOGS_CONTENT["dialogs"]["menu"]["start"]["new_session"]["true_actions"])
                            self.res['response']['text'] += action[0]
                            self.res['response']['tts'] += action[1]
                    else:
                        self.res['response']['text'] = \
                            DIALOGS_CONTENT["dialogs"]["menu"]["start"]["new_session"]["empty_list"][0]
                        self.res['response']['tts'] = \
                            DIALOGS_CONTENT["dialogs"]["menu"]["start"]["new_session"]["empty_list"][1]
                        if self.actions_flag:
                            action = random.choice(
                                DIALOGS_CONTENT["dialogs"]["menu"]["start"]["new_session"]["empty_actions"])
                            self.res['response']['text'] += action[0]
                            self.res['response']['tts'] += action[1]
                self.res['response']['text'] = hello[0] + " " + self.res['response']['text']
                self.res['response']["card"]['header']['text'] = self.res['response']['text']
                self.res['response']['tts'] = hello[1] + self.res['response']['tts']

            else:
                self.res['response']["card"] = DIALOGS_CONTENT['cards']['menu']
                self.res['response']['buttons'] = [BUTTONS["help"], BUTTONS["can"]]
                if things_list:
                    if self.actions_flag:
                        action = random.choice(
                            DIALOGS_CONTENT["dialogs"]["menu"]["start"]["old_session"]["true_actions"])
                        self.res['response']["card"]['header']['text'] = self.res['response']['text'] = action[0]
                        self.res['response']['tts'] = action[1]
                    else:
                        self.res['response']["card"]['header']['text'] = " "
                        self.res['response']['text'] = "Засечь время. Добавить дело. Мои дела."
                        self.res['response']['tts'] = "Засечь время. sil <[200]> Добавить дело. sil <[200]> Мои дела."
                else:
                    self.res['response']["card"]['header']['text'] = self.res['response']['text'] = \
                        DIALOGS_CONTENT["dialogs"]["menu"]["start"]["old_session"]["empty_list"][0]
                    self.res['response']['tts'] = \
                        DIALOGS_CONTENT["dialogs"]["menu"]["start"]["old_session"]["empty_list"][1]
                    if self.actions_flag:
                        action = random.choice(
                            DIALOGS_CONTENT["dialogs"]["menu"]["start"]["old_session"]["empty_actions"])
                        self.res['response']['text'] += action[0]
                        self.res['response']['tts'] += action[1]
        self.db.session.commit()

    def tree(self):
        command, tokens = self.get_c_t()
        if self.timeflow:
            thing = ThingTime.query.filter_by(id=self.timeflow.thing_id).first()
            if (time.time() - self.timeflow.time_start) > 72000:
                self.res['response']["card"] = DIALOGS_CONTENT['cards']['menu']
                self.res['response']["card"]['header']['text'] = self.res['response']['text'] = \
                    DIALOGS_CONTENT["dialogs"]["timeflow"]["20"][0]
                self.res['response']['tts'] = DIALOGS_CONTENT["dialogs"]["timeflow"]["20"][1]

                self.res['response']['buttons'] = [BUTTONS["help"], BUTTONS["can"]]
                self.db.session.delete(self.timeflow)
            else:
                if any(word in tokens for word in HELP):
                    self.res['response']['text'] = DIALOGS_CONTENT["dialogs"]["timeflow"]["help"][0]
                    self.res['response']['tts'] = DIALOGS_CONTENT["dialogs"]["timeflow"]["help"][1]
                    self.res['response']['buttons'] = [BUTTONS["update"], BUTTONS["stop"]]
                elif any(word in tokens for word in STOP):
                    this_time = time.time()
                    thing.time = thing.time + (this_time - self.timeflow.time_start)
                    thing.last_time = this_time - self.timeflow.time_start
                    thing.res_last_time = 1
                    times = time_change(thing.last_time)
                    self.db.session.delete(self.timeflow)
                    victory = random.choice(DIALOGS_CONTENT["dialogs"]["timeflow"]["stop_victory"])
                    self.res['response']['text'] = DIALOGS_CONTENT["dialogs"]["timeflow"]["stop"][0].format(
                        thing.name.capitalize(), *times) + "\n" + victory[0]
                    self.res['response']['tts'] = DIALOGS_CONTENT["dialogs"]["timeflow"]["stop"][1].format(
                        thing.name, tts_change(*times)) + victory[1]
                    if self.actions_flag:
                        action = random.choice(DIALOGS_CONTENT["dialogs"]["timeflow"]["stop_actions"])
                        self.res['response']['text'] += action[0]
                        self.res['response']['tts'] += action[1]
                    self.res['response']['buttons'] = [BUTTONS["list"], BUTTONS["add"], BUTTONS["start"],
                                                       BUTTONS["help"], BUTTONS["can"]]
                elif any(word in tokens for word in UPDATE):
                    times = time_change(time.time() - self.timeflow.time_start)
                    self.res['response']['text'] = DIALOGS_CONTENT["dialogs"]["timeflow"]["update"][0].format(
                        thing.name.capitalize(),
                        *times)
                    self.res['response']['tts'] = DIALOGS_CONTENT["dialogs"]["timeflow"]["update"][1].format(thing.name,
                                                                                                             tts_change(
                                                                                                                 *times))
                    self.res['response']['buttons'] = [BUTTONS["update"], BUTTONS["stop"]]
                else:
                    self.res['response']['text'] = DIALOGS_CONTENT["dialogs"]["timeflow"]["help"][0]
                    self.res['response']['tts'] = DIALOGS_CONTENT["dialogs"]["timeflow"]["help"][1]
                    self.res['response']['buttons'] = [BUTTONS["update"], BUTTONS["stop"]]
        else:
            if self.new:
                change_r_p(self.user, room=0, passage=0)
                self.res['response']["card"] = DIALOGS_CONTENT['cards']['menu']
                self.res['response']["card"]['header']['text'] = self.res['response']['text'] = \
                    DIALOGS_CONTENT["dialogs"]["menu"]["start"]["old_session"][0]
                self.res['response']['tts'] = DIALOGS_CONTENT["dialogs"]["menu"]["start"]["old_session"][1]
            else:
                things_list = get_things_list(self.req['session']['user_id'])

                if any(word in tokens for word in START_TIME) and search_thing(command, things_list):
                    thing = search_thing(command, things_list)
                    self.user.thing_id = thing.id
                    add_thing_flow(self.user.id, thing.id)
                    refresh_last_time(thing, datetime.datetime.today())
                    self.go_menu()
                elif any(word in tokens for word in MENU):
                    self.go_menu()
                elif any(word in tokens for word in MANUAL):
                    self.res['response']['text'] = DIALOGS_CONTENT["dialogs"]['manual'][0]
                    self.res['response']['tts'] = DIALOGS_CONTENT["dialogs"]['manual'][1]
                    self.res['response']['buttons'] = sessionSettings[self.req['session']['user_id']]["buttons"]
                elif any(word in tokens for word in ON) and any(word in tokens for word in HINT):
                    self.user.help_actions = True
                    self.res['response']['text'] = "Подсказки включены! \n" + \
                                                   sessionSettings[self.req['session']['user_id']]["text"]
                    self.res['response']['tts'] = "Подсказки включены! sil <[400]>" + \
                                                  sessionSettings[self.req['session']['user_id']]["tts"]
                    self.res['response']['buttons'] = sessionSettings[self.req['session']['user_id']]["buttons"]
                elif any(word in tokens for word in OFF) and any(word in tokens for word in HINT):
                    self.user.help_actions = False
                    self.res['response']['text'] = "Подсказки выключены!\n" + \
                                                   sessionSettings[self.req['session']['user_id']]["text"]
                    self.res['response']['tts'] = "Подсказки выключены! sil <[400]>" + \
                                                  sessionSettings[self.req['session']['user_id']]["tts"]
                    self.res['response']['buttons'] = sessionSettings[self.req['session']['user_id']]["buttons"]
                elif any(word in tokens for word in REPEAT):
                    self.res['response']['text'] = sessionSettings[self.req['session']['user_id']]["text"]
                    self.res['response']['tts'] = sessionSettings[self.req['session']['user_id']]["tts"]
                    self.res['response']['buttons'] = sessionSettings[self.req['session']['user_id']]["buttons"]
                elif any(word in tokens for word in EXIT) and (word in tokens for word in ABILITY):
                    self.res['response']['text'] = DIALOGS_CONTENT["dialogs"]["exit"][0]
                    self.res['response']['tts'] = DIALOGS_CONTENT["dialogs"]["exit"][1]
                    self.res['response']['end_session'] = False
                elif all(word in tokens for word in ['умеешь', "что"]):
                    self.res['response']['text'] = DIALOGS_CONTENT["dialogs"]["menu"]["can"][0]
                    self.res['response']['tts'] = DIALOGS_CONTENT["dialogs"]["menu"]["can"][1]
                    self.res['response']['buttons'] = sessionSettings[str(self.user.user_id)]["buttons"]
                elif self.user.step_passage == -1:
                    if any(word in tokens for word in YES):
                        add_thing_flow(self.user.id, self.user.thing_id)
                        self.go_menu()
                    else:
                        recordtime = RecordTime(self.res, self.req, self.db, self.user, self.timeflow, False,
                                                self.actions_flag)
                        change_r_p(self.user, room=0, passage=2)
                        recordtime.start(command, tokens)
                        self.res = recordtime.get_res()
                elif self.user.step_passage == 0:
                    change_r_p(self.user, room=0)
                    if any(word in tokens for word in THING_LIST):
                        thingslist = UsersThing(self.res, self.req, self.db, self.user, self.timeflow, False,
                                                self.actions_flag)
                        change_r_p(self.user, room=0, passage=1)
                        thingslist.start(command, tokens)
                        self.res = thingslist.get_res()
                    elif any(word in tokens for word in START_TIME):
                        recordtime = RecordTime(self.res, self.req, self.db, self.user, self.timeflow, False,
                                                self.actions_flag)
                        change_r_p(self.user, room=0, passage=2)
                        recordtime.start(command, tokens)
                        self.res = recordtime.get_res()
                    elif any(word in tokens for word in CREATE):
                        creater = CreateThing(self.res, self.req, self.db, self.user, self.timeflow, False,
                                              self.dangerous, self.actions_flag)
                        change_r_p(self.user, room=0, passage=3)
                        creater.start(command, tokens)
                        self.res = creater.get_res()
                    else:
                        self.res['response']['text'] = DIALOGS_CONTENT["dialogs"]["menu"]["help"][0]
                        self.res['response']['tts'] = DIALOGS_CONTENT["dialogs"]["menu"]["help"][1]
                        self.res['response']['buttons'] = [BUTTONS["list"], BUTTONS["add"], BUTTONS["start"],
                                                           BUTTONS["help"], BUTTONS["can"]]

                elif self.user.step_passage == 1:
                    thingslist = UsersThing(self.res, self.req, self.db, self.user, self.timeflow, False,
                                            self.actions_flag)
                    thingslist.tree(command, tokens)
                    self.res = thingslist.get_res()

                elif self.user.step_passage == 2:
                    recordtime = RecordTime(self.res, self.req, self.db, self.user, self.timeflow, False,
                                            self.actions_flag)
                    recordtime.tree(command, tokens)
                    self.res = recordtime.get_res()

                elif self.user.step_passage == 3:
                    creater = CreateThing(self.res, self.req, self.db, self.user, self.timeflow, False, self.dangerous,
                                          self.actions_flag)
                    creater.tree(command, tokens)
                    self.res = creater.get_res()
                else:
                    self.res['response']["card"] = DIALOGS_CONTENT['cards']['menu']
                    self.res['response']['buttons'] = [BUTTONS['help'], BUTTONS['can']]
                    change_r_p(self.user, room=0, passage=0)
                    if things_list:
                        self.res['response']["card"]['header']['text'] = self.res['response']['text'] = \
                            DIALOGS_CONTENT["dialogs"]["menu"]["start"]["old_session"]["true_list"][0]
                        self.res['response']['tts'] = \
                            DIALOGS_CONTENT["dialogs"]["menu"]["start"]["old_session"]["true_list"][1]
                    else:
                        self.res['response']["card"]['header']['text'] = self.res['response']['text'] = \
                            DIALOGS_CONTENT["dialogs"]["menu"]["start"]["old_session"]["empty_list"][0]
                        self.res['response']['tts'] = \
                            DIALOGS_CONTENT["dialogs"]["menu"]["start"]["old_session"]["empty_list"][1]

        self.db.session.commit()

    def go_menu(self):

        self.timeflow = get_thing_flow(self.db, self.user.id)
        change_r_p(self.user, room=0, passage=0)
        menu = Menu(self.res, self.req, self.db, self.user, self.timeflow, False, False, self.actions_flag)
        menu.start()
        self.res = menu.get_res()
        return self.res

    def get_res(self):
        return self.res


class CreateThing():
    def __init__(self, res, req, db, user, timeflow, new, dangerous, actions_flag):
        self.res = res
        self.req = req
        self.db = db
        self.user = user
        self.new = new
        self.actions_flag = actions_flag
        self.timeflow = timeflow
        self.dangerous = dangerous

    def start(self, command, tokens):
        self.res['response']['buttons'] = [BUTTONS["help"]]
        if len(ThingTime.query.filter_by(user_id=self.user.user_id).all()) >= 15:
            self.res['response']['text'] = DIALOGS_CONTENT["dialogs"]["create_thing"]["2"]["start"][0]
            self.res['response']['tts'] = DIALOGS_CONTENT["dialogs"]["create_thing"]["2"]["start"][1]
            change_r_p(self.user, room=2)
            self.res['response']['buttons'].insert(0, BUTTONS["no"])
            self.res['response']['buttons'].insert(0, BUTTONS["yes"])

        else:
            self.res['response']['text'] = DIALOGS_CONTENT["dialogs"]["create_thing"]["start"][0]
            self.res['response']['tts'] = DIALOGS_CONTENT["dialogs"]["create_thing"]["start"][1]
            if self.actions_flag:
                action = random.choice(DIALOGS_CONTENT["dialogs"]["create_thing"]["actions"])
                self.res['response']['text'] += action[0]
                self.res['response']['tts'] += action[1]
            self.res['response']['buttons'].insert(0, BUTTONS["cancl"])

    def tree(self, command, tokens):
        things_list = get_things_list(self.req['session']['user_id'])
        command = command.strip().lower()
        if self.user.step_room == 0:
            if any(word in tokens for word in HELP):
                self.res['response']['text'] = DIALOGS_CONTENT["dialogs"]["create_thing"]["0"]["help"][0]
                self.res['response']['tts'] = DIALOGS_CONTENT["dialogs"]["create_thing"]["0"]["help"][1]
                self.res['response']['buttons'] = sessionSettings[self.user.user_id]['buttons']
            elif any(word in tokens for word in CANCEL_LAST_TIME):
                self.go_menu()
            elif self.dangerous:
                self.res['response']['text'] = DIALOGS_CONTENT["dialogs"]["create_thing"]["0"]["errors"]["bich"][0]
                self.res['response']['tts'] = DIALOGS_CONTENT["dialogs"]["create_thing"]["0"]["errors"]["bich"][1]
                self.res['response']['buttons'] = sessionSettings[self.user.user_id]['buttons']
                if self.actions_flag:
                    action = random.choice(DIALOGS_CONTENT["dialogs"]["create_thing"]["actions"])
                    self.res['response']['text'] += action[0]
                    self.res['response']['tts'] += action[1]
            elif any(word in tokens for word in SERVICE_WORDS):
                self.res['response']['text'] = DIALOGS_CONTENT["dialogs"]["create_thing"]["0"]["errors"]["serv"][0]
                self.res['response']['tts'] = DIALOGS_CONTENT["dialogs"]["create_thing"]["0"]["errors"]["serv"][1]
                self.res['response']['buttons'] = sessionSettings[self.user.user_id]['buttons']
                if self.actions_flag:
                    action = random.choice(DIALOGS_CONTENT["dialogs"]["create_thing"]["actions"])
                    self.res['response']['text'] += action[0]
                    self.res['response']['tts'] += action[1]
            elif ThingTime.query.filter_by(name=command).first():
                self.res['response']['text'] = DIALOGS_CONTENT["dialogs"]["create_thing"]["0"]["errors"]["repeat"][0]
                self.res['response']['tts'] = DIALOGS_CONTENT["dialogs"]["create_thing"]["0"]["errors"]["repeat"][1]
                self.res['response']['buttons'] = sessionSettings[self.user.user_id]['buttons']
                if self.actions_flag:
                    action = random.choice(DIALOGS_CONTENT["dialogs"]["create_thing"]["actions"])
                    self.res['response']['text'] += action[0]
                    self.res['response']['tts'] += action[1]
            elif all(word in command.replace(' ', '').split() for word in RUS_SYMBOLS):
                self.res['response']['text'] = DIALOGS_CONTENT["dialogs"]["create_thing"]["0"]["errors"]["rus"][0]
                self.res['response']['tts'] = DIALOGS_CONTENT["dialogs"]["create_thing"]["0"]["errors"]["rus"][1]
                self.res['response']['buttons'] = sessionSettings[self.user.user_id]['buttons']
                if self.actions_flag:
                    action = random.choice(DIALOGS_CONTENT["dialogs"]["create_thing"]["actions"])
                    self.res['response']['text'] += action[0]
                    self.res['response']['tts'] += action[1]
            elif len(command.strip().lower()) > 20:
                self.res['response']['text'] = DIALOGS_CONTENT["dialogs"]["create_thing"]["0"]["errors"]["20"][0]
                self.res['response']['tts'] = DIALOGS_CONTENT["dialogs"]["create_thing"]["0"]["errors"]["20"][1]
                self.res['response']['buttons'] = sessionSettings[self.user.user_id]['buttons']
                if self.actions_flag:
                    action = random.choice(DIALOGS_CONTENT["dialogs"]["create_thing"]["actions"])
                    self.res['response']['text'] += action[0]
                    self.res['response']['tts'] += action[1]
            elif len(command.strip().lower()) < 5:
                self.res['response']['text'] = DIALOGS_CONTENT["dialogs"]["create_thing"]["0"]["errors"]["5"][0]
                self.res['response']['tts'] = DIALOGS_CONTENT["dialogs"]["create_thing"]["0"]["errors"]["5"][1]
                self.res['response']['buttons'] = sessionSettings[self.user.user_id]['buttons']
                if self.actions_flag:
                    action = random.choice(DIALOGS_CONTENT["dialogs"]["create_thing"]["actions"])
                    self.res['response']['text'] += action[0]
                    self.res['response']['tts'] += action[1]
            else:
                thing = add_new_thing(self.req['session']['user_id'], command.lower())
                self.user.thing_id = thing.id
                change_r_p(self.user, room=1)
                self.res['response']['text'] = DIALOGS_CONTENT["dialogs"]["create_thing"]["0"]["created"][0]
                self.res['response']['tts'] = DIALOGS_CONTENT["dialogs"]["create_thing"]["0"]["created"][1]
                self.res['response']['buttons'] = [BUTTONS["yes"], BUTTONS["no"], BUTTONS["help"]]

        elif self.user.step_room == 1:
            thing = ThingTime.query.filter_by(id=self.user.thing_id).first()
            if any(word in tokens for word in HELP):
                self.res['response']['text'] = DIALOGS_CONTENT["dialogs"]["create_thing"]["1"]["help"][0]
                self.res['response']['tts'] = DIALOGS_CONTENT["dialogs"]["create_thing"]["1"]["help"][1]
                self.res['response']['buttons'] = sessionSettings[self.user.user_id]['buttons']
            elif any(word in tokens for word in YES) or any(word in tokens for word in START_TIME):
                add_thing_flow(self.user.id, thing.id)
                refresh_last_time(thing, datetime.datetime.today())
                self.go_menu()
            elif any(word in tokens for word in THING_LIST) or any(word in tokens for word in NO):
                change_r_p(self.user, room=0, passage=0)
                menu = Menu(self.res, self.req, self.db, self.user, self.timeflow, False, False, self.actions_flag)
                menu.start()
                self.res = menu.get_res()
            else:
                self.res['response']['text'] = DIALOGS_CONTENT["dialogs"]["create_thing"]["1"]["help"][0]
                self.res['response']['tts'] = DIALOGS_CONTENT["dialogs"]["create_thing"]["1"]["help"][1]
                self.res['response']['buttons'] = sessionSettings[self.user.user_id]['buttons']
        elif self.user.step_room == 2:
            if any(word in tokens for word in HELP):
                self.res['response']['text'] = DIALOGS_CONTENT["dialogs"]["create_thing"]["2"]["help"][0]
                self.res['response']['tts'] = DIALOGS_CONTENT["dialogs"]["create_thing"]["2"]["help"][1]
                self.res['response']['buttons'] = sessionSettings[self.user.user_id]['buttons']
            elif any(word in tokens for word in YES):
                change_r_p(self.user, room=3)
                str_things_list = RecordTime.get_str_things_list(things_list, 0, 15, 0)
                self.res['response']['text'] = DIALOGS_CONTENT["dialogs"]["create_thing"]["3"]["start"][0]
                self.res['response']['tts'] = DIALOGS_CONTENT["dialogs"]["create_thing"]["3"]["start"][1]
                self.res['response']['text'] += "\n" + str_things_list
                self.res['response']['tts'] += "\n" + str_things_list.replace("\n", "sil <[300]> ")
                self.res['response']['buttons'] = [BUTTONS["cancl"], BUTTONS["help"]]
            elif any(word in tokens for word in NO) or any(word in tokens for word in CANCEL_LAST_TIME):
                change_r_p(self.user, room=0, passage=0)
                menu = Menu(self.res, self.req, self.db, self.user, self.timeflow, False, False, self.actions_flag)
                menu.start()
                self.res = menu.get_res()
            else:
                self.res['response']['buttons'] = sessionSettings[self.user.user_id]['buttons']
                self.res['response']['text'] = DIALOGS_CONTENT["dialogs"]["create_thing"]["2"]["help"][0]
                self.res['response']['tts'] = DIALOGS_CONTENT["dialogs"]["create_thing"]["2"]["help"][1]
        elif self.user.step_room == 3:
            if any(word in tokens for word in CANCEL_LAST_TIME):
                change_r_p(self.user, room=0, passage=0)
                menu = Menu(self.res, self.req, self.db, self.user, self.timeflow, False, False, self.actions_flag)
                menu.start()
                self.res = menu.get_res()
            elif any(word in tokens for word in HELP):
                self.res['response']['buttons'] = [BUTTONS["cancl"], BUTTONS["help"]]
                self.res['response']['text'] = DIALOGS_CONTENT["dialogs"]["create_thing"]["3"]["help"][0]
                self.res['response']['tts'] = DIALOGS_CONTENT["dialogs"]["create_thing"]["3"]["help"][1]
            elif any(word in tokens for word in THING_LIST):
                str_things_list = RecordTime.get_str_things_list(things_list, 0, 15, 0)
                self.res['response']['text'] = str_things_list
                self.res['response']['tts'] = str_things_list.replace("\n", "sil <[300]> ")
                self.res['response']['buttons'] = [BUTTONS["cancl"], BUTTONS["help"]]
            elif any(word in command.lower().strip() for word in [x.name.lower() for x in things_list]):
                thing = RecordTime.search_thing(command, things_list)
                change_r_p(self.user, room=0)
                self.res['response']['text'] = DIALOGS_CONTENT["dialogs"]["create_thing"]["3"]["after_delete_thing"][
                    0].format(thing.name.capitalize())
                self.res['response']['tts'] = DIALOGS_CONTENT["dialogs"]["create_thing"]["3"]["after_delete_thing"][
                    1].format(thing.name)
                self.db.session.delete(thing)
                self.res['response']['buttons'] = [BUTTONS["cancl"], BUTTONS["help"]]
            else:
                self.res['response']['text'] = DIALOGS_CONTENT["dialogs"]["create_thing"]["3"]["else"][0]
                self.res['response']['tts'] = DIALOGS_CONTENT["dialogs"]["create_thing"]["3"]["else"][1]
                self.res['response']['buttons'] = [BUTTONS["cancl"], BUTTONS["help"]]

    def go_menu(self):
        self.timeflow = get_thing_flow(self.db, self.user.id)
        change_r_p(self.user, room=0, passage=0)
        menu = Menu(self.res, self.req, self.db, self.user, self.timeflow, False, False, self.actions_flag)
        menu.start()
        self.res = menu.get_res()
        return self.res

    def get_res(self):
        return self.res


class RecordTime():
    def __init__(self, res, req, db, user, timeflow, new, actions_flag):
        self.res = res
        self.req = req
        self.db = db
        self.actions_flag = actions_flag
        self.user = user
        self.new = new
        self.timeflow = timeflow

    def start(self, command, tokens):
        things_list = get_things_list(self.req['session']['user_id'])
        str_things_list = self.get_str_things_list(things_list, 0, 15, 0)

        self.res['response']['buttons'] = [BUTTONS["help"]]
        if len(things_list) == 0:
            change_r_p(self.user, room=0, passage=0)
            self.res['response']['buttons'].append(BUTTONS["add"])
            self.res['response']['text'] = DIALOGS_CONTENT["dialogs"]["timer"]["zero"][0]
            self.res['response']['tts'] = DIALOGS_CONTENT["dialogs"]["timer"]["zero"][1]
        else:
            time_text = random.choice(DIALOGS_CONTENT["dialogs"]["timer"]["start"])
            self.res['response']['text'] = time_text[0]
            self.res['response']['tts'] = time_text[1]
            self.res['response']['text'] += str_things_list
            self.res['response']['tts'] += str_things_list.replace("\n", "sil <[300]> ")
            self.res['response']['buttons'].append(BUTTONS["catalog"])
            self.res['response']['buttons'].append(BUTTONS["menu"])

    @staticmethod
    def get_str_things_list(things_list, n_1, n_2, last_n):
        str_things_list = ""
        for thing in things_list[n_1:n_2]:
            str_things_list += DIALOGS_CONTENT["dialogs"]["timer"]["thing"][0].format(thing.name.capitalize())
        return str_things_list

    def tree(self, command, tokens):
        things_list = get_things_list(self.req['session']['user_id'])
        if any(word in tokens for word in HELP):
            self.res['response']['text'] = DIALOGS_CONTENT["dialogs"]["timer"]["help"][0]
            self.res['response']['tts'] = DIALOGS_CONTENT["dialogs"]["timer"]["help"][1]
            self.res['response']['buttons'] = [BUTTONS["menu"], BUTTONS["help"]]
        elif any(word in tokens for word in THING_LIST):
            things_list = get_things_list(self.req['session']['user_id'])
            str_things_list = self.get_str_things_list(things_list, 0, 15, 0)
            self.res['response']['buttons'] = [BUTTONS["help"]]
            if len(things_list) == 0:
                change_r_p(self.user, room=0, passage=0)
                self.res['response']['buttons'].append(BUTTONS["add"])
                self.res['response']['text'] = DIALOGS_CONTENT["dialogs"]["timer"]["zero"][0]
                self.res['response']['tts'] = DIALOGS_CONTENT["dialogs"]["timer"]["zero"][1]
            else:
                self.res['response']['text'] = str_things_list
                self.res['response']['tts'] = str_things_list.replace("\n", "sil <[300]> ")
                self.res['response']['buttons'].append(BUTTONS["catalog"])
                self.res['response']['buttons'].append(BUTTONS["menu"])
        elif any(word in tokens for word in MENU):
            self.go_menu()
        elif any(word in command.lower().strip() for word in [x.name.lower() for x in things_list]):
            thing = self.search_thing(command, things_list)
            add_thing_flow(self.user.id, thing.id)
            refresh_last_time(thing, datetime.datetime.today())
            self.go_menu()
        else:
            self.res['response']['text'] = DIALOGS_CONTENT["dialogs"]["timer"]["else"][0]
            self.res['response']['tts'] = DIALOGS_CONTENT["dialogs"]["timer"]["else"][1]
            self.res['response']['buttons'] = [BUTTONS["catalog"], BUTTONS["menu"], BUTTONS["help"]]

    @staticmethod
    def search_thing(command, things_list):
        for thing in things_list:
            if command.lower().strip() == thing.name.lower().strip():
                return thing

    def get_res(self):
        return self.res

    def go_menu(self):
        self.timeflow = get_thing_flow(self.db, self.user.id)
        change_r_p(self.user, room=0, passage=0)
        menu = Menu(self.res, self.req, self.db, self.user, self.timeflow, False, False, self.actions_flag)
        menu.start()
        self.res = menu.get_res()
        return self.res


class UsersThing():
    def __init__(self, res, req, db, user, timeflow, new, actions_flag):
        self.res = res
        self.req = req
        self.db = db
        self.user = user
        self.new = new
        self.timeflow = timeflow
        self.actions_flag = actions_flag
        if "screen" in self.req["meta"]["interfaces"]:
            self.screen = True
        else:
            self.screen = False

    def start(self, command, tokens):
        things_list = get_things_list(self.req['session']['user_id'])
        self.res['response']['buttons'] = []

        if self.screen:
            self.res['response']["card"] = copy.deepcopy(DIALOGS_CONTENT['cards']['things_list'])
            self.res['response']["card"]['header']['text'] = self.res['response']['text']
            for item in things_list[:5]:
                times_all = time_change(item.time)
                self.res['response']["card"]["items"].append({
                    "title": "• " + item.name.capitalize(),
                    "description": "{}:{}:{}".format(*times_all),
                    "button": {
                        "text": item.name.capitalize(),
                        "payload": {
                            "text": item.name.capitalize()
                        }
                    }
                })
                self.res['response']['tts'] += item.name + "sil <[300]> "
            if things_list[5:]:
                self.res['response']['buttons'].append(BUTTONS["next"])
            self.res['response']['buttons'].append(BUTTONS["help"])
            if len(self.res['response']["card"]["items"]) == 0:
                del self.res['response']["card"]
                self.res['response']['buttons'].append(BUTTONS["add"])
                change_r_p(self.user, room=0, passage=0)
                self.res['response']['text'] = DIALOGS_CONTENT["dialogs"]["usersthing"]["zero"][0]
                self.res['response']['tts'] = DIALOGS_CONTENT["dialogs"]["usersthing"]["zero"][1]
            else:
                self.res['response']['buttons'].append(BUTTONS["menu"])
        else:
            if len(things_list) == 0:
                self.res['response']['buttons'].append(BUTTONS["add"])
                change_r_p(self.user, room=0, passage=0)
                self.res['response']['text'] = DIALOGS_CONTENT["dialogs"]["usersthing"]["zero"][0]
                self.res['response']['tts'] = DIALOGS_CONTENT["dialogs"]["usersthing"]["zero"][1]
            else:
                str_things_list = RecordTime.get_str_things_list(things_list, 0, 15, 0)
                self.res['response']['buttons'].append(BUTTONS["help"])
                self.res['response']['text'] = str_things_list
                self.res['response']['tts'] = str_things_list.replace("\n", "sil <[300]> ")
                self.res['response']['buttons'].append(BUTTONS["catalog"])
                self.res['response']['buttons'].append(BUTTONS["menu"])

    def get_thing_menu(self, thing):

        times_last = time_change(thing.last_time)
        times_all = time_change(thing.time)
        self.user.step_room = -1
        self.user.thing_id = thing.id
        if thing.time:
            self.res['response']['text'] = DIALOGS_CONTENT["dialogs"]["usersthing"]["list"]["thing_menu"][0].format(
                thing.name.capitalize(), *times_all, *times_last)
            self.res['response']['tts'] = DIALOGS_CONTENT["dialogs"]["usersthing"]["list"]["thing_menu"][1].format(
                thing.name, tts_change(*times_all), tts_change(*times_last))
        else:
            self.res['response']['text'] = DIALOGS_CONTENT["dialogs"]["usersthing"]["list"]["empty_thing_menu"][
                0].format(thing.name.capitalize())
            self.res['response']['tts'] = DIALOGS_CONTENT["dialogs"]["usersthing"]["list"]["empty_thing_menu"][
                1].format(thing.name.capitalize())
        if self.actions_flag:
            action = random.choice(DIALOGS_CONTENT["dialogs"]["usersthing"]["-1"]["actions"])
            self.res['response']['text'] += action[0]
            self.res['response']['tts'] += "sil <[400]>" + action[1]

        del self.res['response']['card']
        self.res['response']['buttons'] = [BUTTONS["start"]]
        self.res['response']['buttons'].append(BUTTONS["time"])
        if thing.res_last_time == 1:
            self.res['response']['buttons'].append(BUTTONS["cancel"])
        elif thing.res_last_time == 2:
            self.res['response']['buttons'].append(BUTTONS["return"])
        else:
            pass
        self.res['response']['buttons'].append(BUTTONS["delete"])
        self.res['response']['buttons'].append(BUTTONS["catalog"])
        self.res['response']['buttons'].append(BUTTONS["menu"])
        self.res['response']['buttons'].append(BUTTONS["help"])

    def tree(self, command, tokens):
        things_list = get_things_list(self.req['session']['user_id'])
        if self.user.step_room == -2:
            thing = ThingTime.query.filter_by(id=self.user.thing_id).first()
            if any(word in tokens for word in YES):
                self.res['response']['text'] = DIALOGS_CONTENT["dialogs"]["usersthing"]["-2"]["del"][0]
                self.res['response']['tts'] = DIALOGS_CONTENT["dialogs"]["usersthing"]["-2"]["del"][1]
                self.db.session.delete(thing)
                change_r_p(self.user, room=0, passage=1)
                self.start(command, tokens)
            elif any(word in tokens for word in NO):
                self.res['response']["card"] = copy.deepcopy(DIALOGS_CONTENT['cards']['things_list'])
                self.get_thing_menu(thing)
            else:
                self.res['response']['buttons'] = [BUTTONS["yes"], BUTTONS["no"]]
                self.res['response']['text'] = DIALOGS_CONTENT["dialogs"]["usersthing"]["-2"]["help"][0]
                self.res['response']['tts'] = DIALOGS_CONTENT["dialogs"]["usersthing"]["-2"]["help"][1]

        elif self.user.step_room == -1:
            thing = ThingTime.query.filter_by(id=self.user.thing_id).first()
            if any(word in tokens for word in HELP):
                self.res['response']['text'] = DIALOGS_CONTENT["dialogs"]["usersthing"]["-1"]["help"][0]
                self.res['response']['tts'] = DIALOGS_CONTENT["dialogs"]["usersthing"]["-1"]["help"][1]
                self.res['response']['buttons'] = sessionSettings[self.user.user_id]['buttons']
            elif any(word in tokens for word in START_TIME):
                add_thing_flow(self.user.id, thing.id)
                refresh_last_time(thing, datetime.datetime.today())
                self.go_menu()
            elif any(word in tokens for word in RETURN_LAST_TIME):
                if thing.res_last_time == 2:
                    thing.time = thing.time + thing.last_time
                    thing.res_last_time = 1
                    self.res['response']['text'] = DIALOGS_CONTENT["dialogs"]["usersthing"]["-1"]["suc_return"][0]
                    self.res['response']['tts'] = DIALOGS_CONTENT["dialogs"]["usersthing"]["-1"]["suc_return"][1]
                else:
                    self.res['response']['text'] = DIALOGS_CONTENT["dialogs"]["usersthing"]["-1"]["unsuc_return"][0]
                    self.res['response']['tts'] = DIALOGS_CONTENT["dialogs"]["usersthing"]["-1"]["unsuc_return"][1]
                if self.actions_flag:
                    action = random.choice(DIALOGS_CONTENT["dialogs"]["usersthing"]["-1"]["actions"])
                    self.res['response']['text'] += action[0]
                    self.res['response']['tts'] += "sil <[400]>" + action[1]
                self.res['response']['buttons'] = [BUTTONS["start"]]
                if thing.res_last_time == 1:
                    self.res['response']['buttons'].append(BUTTONS["cancel"])
                elif thing.res_last_time == 2:
                    self.res['response']['buttons'].append(BUTTONS["return"])
                else:
                    pass
                self.res['response']['buttons'].append(BUTTONS["delete"])
                self.res['response']['buttons'].append(BUTTONS["catalog"])
                self.res['response']['buttons'].append(BUTTONS["menu"])
                self.res['response']['buttons'].append(BUTTONS["help"])
            elif any(word in tokens for word in CANCEL_LAST_TIME):
                if thing.res_last_time == 0:
                    self.res['response']['text'] = DIALOGS_CONTENT["dialogs"]["usersthing"]["-1"]["none_cancel"][0]
                    self.res['response']['tts'] = DIALOGS_CONTENT["dialogs"]["usersthing"]["-1"]["none_cancel"][1]
                elif thing.res_last_time == 2:
                    self.res['response']['text'] = DIALOGS_CONTENT["dialogs"]["usersthing"]["-1"]["unsuc_cancel"][0]
                    self.res['response']['tts'] = DIALOGS_CONTENT["dialogs"]["usersthing"]["-1"]["unsuc_cancel"][1]
                else:
                    thing.time = thing.time - thing.last_time
                    thing.res_last_time = 2
                    self.res['response']['text'] = DIALOGS_CONTENT["dialogs"]["usersthing"]["-1"]["suc_cancel"][0]
                    self.res['response']['tts'] = DIALOGS_CONTENT["dialogs"]["usersthing"]["-1"]["suc_cancel"][1]
                if self.actions_flag:
                    action = random.choice(DIALOGS_CONTENT["dialogs"]["usersthing"]["-1"]["actions"])
                    self.res['response']['text'] += action[0]
                    self.res['response']['tts'] += "sil <[400]>" + action[1]
                self.res['response']['buttons'] = [BUTTONS["start"]]
                if thing.res_last_time == 1:
                    self.res['response']['buttons'].append(BUTTONS["cancel"])
                elif thing.res_last_time == 2:
                    self.res['response']['buttons'].append(BUTTONS["return"])
                else:
                    pass
                self.res['response']['buttons'].append(BUTTONS["delete"])
                self.res['response']['buttons'].append(BUTTONS["catalog"])
                self.res['response']['buttons'].append(BUTTONS["menu"])
                self.res['response']['buttons'].append(BUTTONS["help"])
            elif any(word in tokens for word in TIME):
                self.res['response']["card"] = copy.deepcopy(DIALOGS_CONTENT['cards']['things_list'])
                self.get_thing_menu(thing)
            elif any(word in tokens for word in THING_LIST):
                change_r_p(self.user, room=0, passage=1)
                self.start(command, tokens)
            elif any(word in tokens for word in DELETE):
                self.user.step_room = -2

                self.res['response']['text'] = DIALOGS_CONTENT["dialogs"]["usersthing"]["-1"]["want_del"][0].format(
                    thing.name.capitalize())
                self.res['response']['tts'] = DIALOGS_CONTENT["dialogs"]["usersthing"]["-1"]["want_del"][1].format(
                    thing.name)
                self.res['response']['buttons'] = [BUTTONS["yes"], BUTTONS["no"]]
            elif any(word in tokens for word in MENU):
                self.go_menu()
            else:
                self.res['response']['text'] = self.res['response']['text'] = \
                    DIALOGS_CONTENT["dialogs"]["usersthing"]["-1"]["help"][0]
                self.res['response']['tts'] = DIALOGS_CONTENT["dialogs"]["usersthing"]["-1"]["help"][1]
                self.res['response']['buttons'] = sessionSettings[self.user.user_id]['buttons']

        else:
            self.res['response']["card"] = copy.deepcopy(DIALOGS_CONTENT['cards']['things_list'])
            if any(word in command.lower().strip() for word in [x.name.lower() for x in things_list]):
                thing = search_thing(command, things_list)
                self.get_thing_menu(thing)
            elif any(word in tokens for word in HELP):
                del self.res['response']["card"]
                self.res['response']['text'] = DIALOGS_CONTENT["dialogs"]["usersthing"]["list"]["help"][0]
                self.res['response']['tts'] = DIALOGS_CONTENT["dialogs"]["usersthing"]["list"]["help"][1]
                self.res['response']['buttons'] = sessionSettings[self.user.user_id]['buttons']
            elif any(word in tokens for word in THING_LIST):
                things_list = get_things_list(self.req['session']['user_id'])
                if self.screen:
                    self.res['response']["card"] = copy.deepcopy(DIALOGS_CONTENT['cards']['things_list'])
                    self.res['response']['buttons'] = []
                    self.res['response']["card"]['header']['text'] = self.res['response']['text']
                    for item in things_list[self.user.step_room * 5: (self.user.step_room + 1) * 5]:
                        times_all = time_change(item.time)
                        self.res['response']["card"]["items"].append({
                            "title": "• " + item.name.capitalize(),
                            "description": "{}:{}:{}".format(*times_all),
                            "button": {
                                "text": item.name.capitalize(),
                                "payload": {
                                    "text": item.name.capitalize()
                                }
                            }
                        })
                        self.res['response']['tts'] += item.name + "sil <[300]> "
                    if things_list[5:]:
                        self.res['response']['buttons'].append(BUTTONS["next"])
                    self.res['response']['buttons'].append(BUTTONS["help"])
                    if len(self.res['response']["card"]["items"]) == 0:
                        del self.res['response']["card"]
                        self.res['response']['buttons'].append(BUTTONS["add"])
                        change_r_p(self.user, room=0, passage=0)
                        self.res['response']['text'] = DIALOGS_CONTENT["dialogs"]["usersthing"]["zero"][0]
                        self.res['response']['tts'] = DIALOGS_CONTENT["dialogs"]["usersthing"]["zero"][1]
                    else:
                        self.res['response']['buttons'].append(BUTTONS["menu"])
                else:
                    del self.res['response']["card"]
                    if len(things_list) == 0:
                        self.res['response']['buttons'].append(BUTTONS["add"])
                        change_r_p(self.user, room=0, passage=0)
                        self.res['response']['text'] = DIALOGS_CONTENT["dialogs"]["usersthing"]["zero"][0]
                        self.res['response']['tts'] = DIALOGS_CONTENT["dialogs"]["usersthing"]["zero"][1]
                    else:
                        str_things_list = RecordTime.get_str_things_list(things_list, 0, 15, 0)
                        self.res['response']['buttons'].append(BUTTONS["help"])
                        self.res['response']['text'] = str_things_list
                        self.res['response']['tts'] = str_things_list.replace("\n", "sil <[300]> ")
                        self.res['response']['buttons'].append(BUTTONS["catalog"])
                        self.res['response']['buttons'].append(BUTTONS["menu"])
            elif any(word in tokens for word in NEXT) or any(word in tokens for word in BACK):
                if any(word in tokens for word in NEXT):
                    if len(things_list) > (self.user.step_room + 1) * 5:
                        self.user.step_room += 1
                        self.res['response']["card"]['header']['text'] = self.res['response'][
                            'text'] = ""
                    else:
                        self.res['response']["card"]['header']['text'] = self.res['response'][
                            'text'] = DIALOGS_CONTENT["dialogs"]["usersthing"]["list"]["next_empty"][0]
                        self.res['response']['tts'] = DIALOGS_CONTENT["dialogs"]["usersthing"]["list"]["next_empty"][1]
                elif any(word in tokens for word in BACK):
                    if self.user.step_room - 1 >= 0:
                        self.user.step_room -= 1
                        self.res['response']["card"]['header']['text'] = self.res['response'][
                            'text'] = ""
                    else:
                        self.res['response']["card"]['header']['text'] = self.res['response'][
                            'text'] = self.res['response']['tts'] = \
                            DIALOGS_CONTENT["dialogs"]["usersthing"]["list"]["back_empty"][
                                0]
                        self.res['response']['tts'] = DIALOGS_CONTENT["dialogs"]["usersthing"]["list"]["back_empty"][1]
                if self.user.step_room == 0:
                    if self.screen:
                        for item in things_list[:5]:
                            times_all = time_change(item.time)
                            self.res['response']["card"]["items"].append({
                                "title": "• " + item.name.capitalize(),
                                "description": "{}:{}:{}".format(*times_all),
                                "button": {
                                    "text": item.name.capitalize(),
                                    "payload": {
                                        "text": item.name.capitalize()
                                    }
                                }
                            })
                            self.res['response']['tts'] += item.name + "sil <[300]>"
                        if things_list[5:]:
                            self.res['response']['buttons'].append(BUTTONS["next"])

                    else:
                        str_things_list = RecordTime.get_str_things_list(things_list, 0, 15, 0)
                        self.res['response']['buttons'] = [BUTTONS["help"]]
                        self.res['response']['text'] = str_things_list
                        self.res['response']['tts'] = str_things_list.replace("\n", "sil <[300]> ")
                        self.res['response']['buttons'].append(BUTTONS["catalog"])
                        self.res['response']['buttons'].append(BUTTONS["menu"])

                else:
                    if self.screen:
                        for item in things_list[self.user.step_room * 5: (self.user.step_room + 1) * 5]:
                            times_all = time_change(item.time)
                            self.res['response']["card"]["items"].append({
                                "title": "• " + item.name.capitalize(),
                                "description": "{}:{}:{}".format(*times_all),
                                "button": {
                                    "text": item.name.capitalize(),
                                    "payload": {
                                        "text": item.name.capitalize()
                                    }
                                }
                            })
                            self.res['response']['tts'] += item.name + " "
                        if things_list[(self.user.step_room + 1) * 5:]:
                            self.res['response']['buttons'].append(BUTTONS["next"])
                        self.res['response']['buttons'].append(BUTTONS["back"])
                    else:
                        str_things_list = RecordTime.get_str_things_list(things_list, 0, 15, 0)
                        self.res['response']['buttons'] = [BUTTONS["help"]]
                        self.res['response']['text'] = str_things_list
                        self.res['response']['tts'] = str_things_list.replace("\n", "sil <[300]> ")
                        self.res['response']['buttons'].append(BUTTONS["catalog"])
                        self.res['response']['buttons'].append(BUTTONS["menu"])
                self.res['response']['buttons'].append(BUTTONS["menu"])
                if len(things_list) == 0:
                    del self.res['response']["card"]
                    self.res['response']['text'] = DIALOGS_CONTENT["dialogs"]["usersthing"]["zero"][0]
                    self.res['response']['tts'] = DIALOGS_CONTENT["dialogs"]["usersthing"]["zero"][1]
            elif any(word in tokens for word in MENU):
                self.go_menu()
            else:
                del self.res['response']["card"]
                self.res['response']['text'] = DIALOGS_CONTENT["dialogs"]["usersthing"]["list"]["help"][0]
                self.res['response']['tts'] = DIALOGS_CONTENT["dialogs"]["usersthing"]["list"]["help"][1]
                self.res['response']['buttons'] = [BUTTONS["catalog"], BUTTONS["help"], BUTTONS["menu"]]

    def go_menu(self):
        self.timeflow = get_thing_flow(self.db, self.user.id)
        change_r_p(self.user, room=0, passage=0)
        menu = Menu(self.res, self.req, self.db, self.user, self.timeflow, False, False, self.actions_flag)
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
