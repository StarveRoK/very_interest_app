import os
import time

os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.factory import Factory
from kivy.clock import Clock
from config import host, user, port, password, db_name

from lang.ru_RU import *
import pymysql

Window.clearcolor = (.13, .82, .83, 1)
global SIZE_X
SIZE_X = Window.size[0]
global Size_Y
SIZE_Y = Window.size[1]

def connect_to_mysql(id, nickname, passwordd, api, name, birth, sex, email, action):
    arguments ={"id": id, "nickname": str(nickname), "passwordd": passwordd, "api":api,"name":name,
                "birth":birth, "sex":sex, "email": email, "action":action}
    def connect():
        while True:
            try:
                connection = pymysql.connect(host=host,port=port,user=user,password=password,
                                             database=db_name,cursorclass=pymysql.cursors.DictCursor)
                return connection
            except Exception as ex:
                print(ex)

    connection = connect()
    while True:
        try:
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO `database_example` (id, nickname, password, api, name, birth, sex, " \
                                "email, action) VALUES ('%(id)s', '%(nickname)s', '%(passwordd)s', '%(api)s', " \
                                "'%(name)s', '%(birth)s', '%(sex)s', '%(email)s', '%(action)s');" % arguments)
                connection.commit()
                connection.close()
                break
        except Exception as ex:
            print(ex)

    while True:
        connection = connect()
        with connection.cursor() as cursor:
            try:
                cursor.execute("SELECT * FROM `database_example` WHERE nickname = '%(nickname)s' "
                               "and action = 'Done';" % arguments)
                answer = cursor.fetchone()
                if answer != None:
                    cursor.execute("DELETE FROM `database_example` WHERE nickname = '%(nickname)s' "
                                   "and action = 'Done';" % arguments)
                    connection.commit()
                    return answer
                else:
                    time.sleep(1)
            finally:
                connection.close()

class FirstScreen(Screen):
    def exit(self):
        raise SystemExit(1)
    pass

class RegisterScreen(Screen):
    def check_reg(self):
        answer = connect_to_mysql("null", self._nickname.text, self._password.text, self._check_password.text,
                                  'null','null','null','null','Reg')
        if answer.get('api') != None:
            account = answer.values()
            with open("accountinfo.txt", 'w') as file:
                for info in account:
                    if info == None or info == "Done":
                        break
                    file.write(info + '\n')
            self.manager.current = 'menu'
            self.manager.transition.direction = 'up'
        else:
            answer = (answer.get("id")).split("_")
            if answer[0] == "0":
                self._nickname.text = ''
                self._nickname.hint_text = bad_nickname_
            if answer[1] == "0":
                self._password.text = ''
                self._password.hint_text = bad_password_
            if answer[2] == "0":
                self._check_password.text = ''
                self._password.text = ''
                self._check_password.hint_text = bad_reset_password_
            if answer[3] == "0":
                self._nickname.text = ''
                self._nickname.hint_text = nick_already_taken_

class LoginScreen(Screen):
    def check_login(self):
        answer = connect_to_mysql("null", self._nickname.text, self._password.text, 'null',
                                  'null', 'null', 'null', 'null', 'Log')
        if answer.get("id") != "no":
            answerr = answer.values()
            self._nickname.text = ''
            self._password.text = ''
            with open("accountinfo.txt", 'w') as file:
                for info in answerr:
                    if info == None:
                        break
                    file.write(info + '\n')
            self.manager.current = 'menu'
            self.manager.transition.direction = 'left'
        else:
            self._nickname.text = ''
            self._password.text = ''
            self._nickname.hint_text = bad_nickname_
            self._password.hint_text = bad_password_

class MenuScreen(Screen):
    size_x = SIZE_X
    def exit(self):
        with open("accountinfo.txt", 'w') as file:
            file.write('')
    def account_info(self):
        self.manager.current = 'account'
        self.manager.transition.direction = 'left'
    def acc_info(self):
        def do_it(self):
            Factory.InfoPopup().open()
        with open("accountinfo.txt", 'r') as file:
            if len(file.readlines()) <= 4:
                Clock.schedule_once(do_it, 2)
    def add_info(self):
        with open("user.txt", 'r') as file:
            if file.readline() == '':
                self.manager.transition.direction = 'left'
                self.manager.current = 'add_first_info'
            else:
                self.manager.transition.direction = 'left'
                self.manager.current = 'add_info'

class AccountScreen(Screen):
    def account(self):
        with open("accountinfo.txt", 'r') as file:
            self._id.text = file.readline().replace('\n','')
            self._nickname.text = file.readline().replace('\n','')
            self._password.text = file.readline().replace('\n','')

class AddInformation(Screen):
    pass

class AddFirstInformation(Screen):
    def first_popup(self):
        Factory.FirstAddInfoPopup().open()
    pass

class MyApp(App):
    def build(self):
        sm = ScreenManager()
        with open("accountinfo.txt", 'r') as file:
            if file.readline() == '':
                sm.add_widget(FirstScreen(name="firstMenu"))
                sm.add_widget(MenuScreen(name="menu"))
            else:
                sm.add_widget(MenuScreen(name="menu"))
                sm.add_widget(FirstScreen(name="firstMenu"))
        sm.add_widget(RegisterScreen(name="registerMenu"))
        sm.add_widget(LoginScreen(name="loginMenu"))
        sm.add_widget(AccountScreen(name="account"))
        sm.add_widget(AddInformation(name="add_info"))
        sm.add_widget(AddFirstInformation(name="add_first_info"))
        return sm

if __name__ == "__main__":
    MyApp().run()
