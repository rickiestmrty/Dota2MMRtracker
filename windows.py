import sys
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QWidget, QStackedWidget, QDesktopWidget, QGraphicsScene, QMessageBox
from PyQt5 import QtCore
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import glob
from datetime import date


class User():
    solo = 30
    party = 20

    def __init__(self,username,exist=False):
        self.filepath = "./users/"+username+".txt"
        self.matches = {}
        self.reset()
        if exist:
            self.get_existing_info()
            
    def reset(self):
        self.winrate = 0
        self.total_games = 0
        self.total_wins = 0
        self.total_wins_solo = 0
        self.total_wins_party = 0
        self.total_lose = 0
        self.total_lose_solo = 0
        self.total_lose_party = 0

    def get_existing_info(self):
        with open(self.filepath) as file:
            lines = file.readlines()
            lines = [line.rstrip() for line in lines]
        self.start_date = lines[0][12:]
        self.start_mmr = int(lines[1][11:])
        self.mmr_curr = int(lines[2][10:])
        self.mmr_goal = int(lines[3][10:])

        n = 4
        while n < len(lines):
            match = lines[n].split(";")
            match = list(map(int, match))
            day = match[0]
            win_solo = match[1]
            lose_solo = match[2]
            win_party = match[3]
            lose_party = match[4]
            self.matches[day] = [win_solo,lose_solo,win_party,lose_party]
            n += 1
            self.calculate()
        

    def add_match(self,day,result):
        if result == "winsolo":
            n = 0
        elif result == "losesolo":
            n = 1
        elif result == "winparty":
            n = 2
        elif result == "loseparty":
            n = 3
        try:
            self.matches[day][n] += 1
        except:
            self.matches[day] = [0,0,0,0]
            self.matches[day][n] += 1
        self.calculate()
    
    def progress_calculation(self):
        gain = self.mmr_curr - self.start_mmr
        difference = self.mmr_goal - self.start_mmr
        self.progress = (gain/difference)*100
    
    def calculate(self):
        self.reset()
        for key in self.matches:
            self.total_wins_solo += self.matches[key][0]
            self.total_lose_solo += self.matches[key][1]
            self.total_wins_party += self.matches[key][2]
            self.total_lose_party += self.matches[key][3]
        self.total_wins = self.total_wins_solo + self.total_wins_party
        self.total_lose = self.total_lose_solo + self.total_lose_party

        self.total_games = self.total_wins + self.total_lose
        self.winrate = round(((self.total_wins / self.total_games) * 100),2)
        gain_solo = (self.total_wins_solo - self.total_lose_solo)*self.solo
        gain_party = (self.total_wins_party - self.total_lose_party)*self.party
        self.mmr_curr = self.start_mmr + gain_party + gain_solo
    
    def show_graph(self):
        days = [0]
        gains = [0]
        mmr = []
        for key in self.matches:
            solo = (self.matches[key][0] - self.matches[key][1]) * self.solo
            party = (self.matches[key][2] - self.matches[key][3]) * self.party
            days.append(key)
            gains.append(solo+party)
        prev_mmr = self.start_mmr
        for idx,gain in enumerate(gains):
            if idx > 0:
                prev_mmr = mmr[idx-1]
            new_mmr = gain + prev_mmr
            mmr.append(new_mmr)

        return days, mmr

    def save(self):
        new_data = "start_date: "+str(self.start_date)+"\nstart_mmr: "+str(self.start_mmr)+"\n"
        new_data += "curr_mmr: "+str(self.mmr_curr)+"\ngoal_mmr: "+str(self.mmr_goal)
        for key in self.matches:
            new_data += "\n"+ str(key) + ""
            for value in self.matches[key]:
                new_data += ";"+str(value)

            with open(self.filepath,'w+') as myfile:
                myfile.seek(0)
                myfile.write(new_data)
                myfile.truncate()

class Graph_Window(QDialog):
    def __init__(self,widget):
        super(Graph_Window, self).__init__()
        loadUi("plot_widget.ui",self)
        self.widget = widget
        self.btn_back_2.clicked.connect(self.back)
        self.get_data()

    def get_data(self):
        days, gain = user.show_graph()
        self.plot(days,gain)
    
    def plot(self, days, gain):
        self.graphWidget.setXRange(0, max(user.matches))
        self.graphWidget.setMouseEnabled(x=False, y=False)
        self.graphWidget.plot(days, gain)

    def back(self):
        self.graphWidget.clear()
        self.widget.setCurrentIndex(3)

class Main_Window(QDialog):
    def __init__(self,widget):
        super(Main_Window, self).__init__()
        loadUi("main_window.ui",self)
        self.widget = widget
        self.btn_start.clicked.connect(self.gotologin)
        
    def gotologin(self):
        self.widget.setCurrentIndex(1)

class Login_Window(QDialog):
    def __init__(self,widget,user_window,app):
        super(Login_Window, self).__init__()
        loadUi("login_signup.ui",self)
        self.widget = widget
        self.btn_start_2.clicked.connect(self.gotosetup)
        self.btn_back_1.clicked.connect(self.home_button)
        self.user_name_input.installEventFilter(self)
        app.focusChanged.connect(self.focus_changed)
        self.user_window = user_window
        self.get_users()

    def get_users(self):
        lst = glob.glob("./users/*.txt")
        self.users = []
        for filename in lst:
            user = filename.split("\\")[1]
            idx = user.index(".")
            user = user[:idx]
            self.users.append(user)

    def focus_changed(self):
        if self.visibleRegion().isEmpty():
            self.user_name_input.clear()
            self.get_users()

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.KeyPress and obj is self.user_name_input:
            if event.key() == QtCore.Qt.Key_Return and self.user_name_input.hasFocus():
                self.gotosetup()
        return super().eventFilter(obj, event)
    
    def gotosetup(self):
        username = self.user_name_input.toPlainText()
        if username == "":
            QMessageBox.about(self, "Invalid Input", "Please enter a username that exists or a new username with at least 1 character.")
        else:
            if self.user_window.x == 1:
                self.user_window.x = 0
                self.widget.removeWidget(self.user_window.graph_window)
            global user
            if username in self.users:
                user = User(username,True)
                self.widget.setCurrentIndex(3)
                self.user_window.update_display()
            else:
                user = User(username)
                self.widget.setCurrentIndex(2)
        
    def home_button(self):
        self.widget.setCurrentIndex(0)
            

class New_User_Window(QDialog):
    def __init__(self,widget,user_window):
        super(New_User_Window, self).__init__()
        loadUi("new_user.ui",self)
        self.widget = widget
        global g_user_window
        g_user_window = user_window
        self.btn_start_3.clicked.connect(self.new_user)
        self.btn_back_2.clicked.connect(self.back_button)

    def new_user(self):
        now = date.today()
        user.start_mmr = self.mmr_current.value()
        user.mmr_curr = self.mmr_current.value()
        user.mmr_goal = self.mmr_goal.value()
        if user.mmr_curr < user.mmr_goal:
            user.start_date = now.strftime("%m/%d/%Y")
            g_user_window.update_display()
            self.widget.setCurrentIndex(3)
    
    def back_button(self):
        self.widget.setCurrentIndex(1)
        

class User_Window(QDialog):
    def __init__(self,widget):
        super(User_Window, self).__init__()
        loadUi("user_status_window.ui",self)
        self.widget = widget
        self.btn_add_new_match.clicked.connect(self.new_match)
        self.btn_save.clicked.connect(self.save_data)
        self.btn_home.clicked.connect(self.home_button)
        self.btn_graph.clicked.connect(self.display_graph)
        self.x = 0

    def update_display(self):
        user.progress_calculation()
        self.lbl_start_date.setText(user.start_date)
        self.lbl_winrate.setText(str(user.winrate)+"%")
        self.lbl_totalgames.setText(str(user.total_games))
        self.lbl_start_mmr.setText(str(user.start_mmr))
        self.lbl_curr_mmr.setText(str(user.mmr_curr))
        self.lbl_goal_mmr.setText(str(user.mmr_goal))
        self.progressBar.setValue(user.progress)
    
    def new_match(self):
        self.widget.setCurrentIndex(4)

    def save_data(self):
        user.save()
    
    def home_button(self):
        self.widget.setCurrentIndex(0)

    def display_graph(self):
        if self.x == 0:
            self.graph_window = Graph_Window(self.widget)
            self.widget.addWidget(self.graph_window)
            self.x = 1
        if self.x == 1:
            self.graph_window.get_data()
        self.widget.setCurrentIndex(5)

class New_Match(QDialog):
    def __init__(self,widget):
        super(New_Match, self).__init__()
        loadUi("new_match.ui",self)
        self.widget = widget
        self.btn_start_2.clicked.connect(self.add_match)
        self.btn_back_3.clicked.connect(self.back_button)


    def add_match(self):
        day = self.new_day.value()
        if self.radio1_win.isChecked():
            result = "win"
        else:
            result = "lose"

        if self.radio2_solo.isChecked():
            result += "solo"
        else:
            result += "party"
        user.add_match(day,result)
        g_user_window.update_display()
        self.widget.setCurrentIndex(3)
    
    def back_button(self):
        self.widget.setCurrentIndex(3)