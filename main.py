from windows import *
import os

newpath = "./users"
if not os.path.exists(newpath):
    os.makedirs(newpath)

# main
app = QApplication(sys.argv)
widget = QStackedWidget()

main_window = Main_Window(widget)
user_window = User_Window(widget)
new_user_window = New_User_Window(widget,user_window)
login_window = Login_Window(widget,user_window,app)
new_match = New_Match(widget)

widget.addWidget(main_window)
widget.addWidget(login_window)
widget.addWidget(new_user_window)
widget.addWidget(user_window)
widget.addWidget(new_match)

widget.setFixedHeight(371)
widget.setFixedWidth(571)
widget.show()
try:
    sys.exit(app.exec_())
except:
    pass