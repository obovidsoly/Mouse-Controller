from PyQt5.QtWidgets import *
from mouseCtrThread import MouseCtrThread
import pyautogui as gui     # pip install pyautogui
from PyQt5.QtCore import Qt


#실행하자마자 보이는 메인 윈도우
class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.mouse_ctr=MouseCtrThread(self,display=False)   #마우스 컨트롤 스레드
        self.check_cam=QCheckBox()                          #카메라 화면 체크박스

        self.mouse_ctr.cam_not_ready.connect(self.cam_mbox) #cam_not_ready 시그널을 cam_mbox 메소드에 연결
        
        self.check_cam.setText("카메라 화면 보이기")
        self.check_cam.setChecked(False)
        self.check_cam.clicked.connect(self.toggle_display) #체크박스를 toggle_display 메소드에 연결

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Mouse controller')
        self.setFixedSize(450,150)
        screen=gui.size()
        self.move(screen[0]/2-self.width()/2,screen[1]/2-self.height()/2)   #윈도우가 화면 중앙에 위치하도록 조정

        hlayout=QHBoxLayout()
        vlayout=QVBoxLayout()
        
        btn_exe = QPushButton("실행")
        btn_exe.setFixedSize(100,50)
        btn_exe.clicked.connect(self.btn_exe_clicked)           #실행 버튼을 btn_exe_clicked 메소드에 연결

        btn_stop=QPushButton("중지")
        btn_stop.setFixedSize(100,50)
        btn_stop.clicked.connect(self.btn_stop_clicked)         #실행 버튼을 btn_stop_clicked 메소드에 연결

        """ btn_manual=QPushButton("사용법")
        btn_manual.setFixedSize(100,50)
        btn_manual.clicked.connect(self.btn_manual_clicked) """     #실행 버튼을 btn_manual_clicked 메소드에 연결

        hlayout.addStretch(1)
        hlayout.addWidget(btn_exe)
        hlayout.addStretch(1)
        hlayout.addWidget(btn_stop)
        hlayout.addStretch(1)
        #hlayout.addWidget(btn_manual)
        hlayout.addStretch(1)

        vlayout.addStretch(1)
        vlayout.addLayout(hlayout)
        vlayout.addStretch(1)
        vlayout.addWidget(self.check_cam)
        vlayout.setAlignment(self.check_cam,Qt.AlignCenter)
        vlayout.addStretch(1)

        widget=QWidget()
        widget.setLayout(vlayout)
        self.setCentralWidget(widget)
        self.show()

    def btn_exe_clicked(self):
        #스레드가 실행 중이지 않으면 실행하고
        #실행 중이면 경고 메시지를 출력
        if not self.mouse_ctr.is_working():
            self.mouse_ctr.start()
        else:
            mbox=QMessageBox(self)
            mbox.setWindowTitle("Executing...")
            mbox.setIcon(QMessageBox.Information)
            mbox.setText("이미 실행 중 입니다.")
            mbox.setStandardButtons(QMessageBox.Ok)
            mbox.setDefaultButton(QMessageBox.Ok)
            mbox.show()

    def btn_stop_clicked(self):
        self.mouse_ctr.stop()

    """ def btn_manual_clicked(self):
        manual=Manual(self)
        screen=gui.size()

        manual.move(screen[0]/2-manual.width()/2,screen[1]/2-manual.height()/2)
        manual.show() """

    #카메라 접근 권한이 없을 경우 경고 메시지창 출력
    def cam_mbox(self):
        mbox=QMessageBox(self)
        mbox.setWindowTitle("Cam")
        mbox.setIcon(QMessageBox.Information)
        mbox.setText("카메라를 사용할 수 없습니다.")
        mbox.setStandardButtons(QMessageBox.Ok)
        mbox.setDefaultButton(QMessageBox.Ok)
        mbox.show()

    def toggle_display(self):
        if not self.mouse_ctr.is_working():
            self.mouse_ctr.toggle_display()
        else:
            self.check_cam.toggle()