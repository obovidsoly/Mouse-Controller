import sys
from PyQt5.QtWidgets import QApplication
from myApp import MyApp

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())