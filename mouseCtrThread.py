import pyautogui as gui     # pip install pyautogui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QThread,pyqtSignal
import cv2
import mediapipe as mp

#마우스를 제어하는 스레드 클래스
class MouseCtrThread(QThread):
    cam_not_ready=pyqtSignal()  #카메라 접근 권한이 없을 경우 윈도우로 보낼 시그널

    def __init__(self, parent=None,display=False):
        super().__init__(parent)
        self.working=False
        self.display=display

    def run(self):
        #영상캡쳐를 실행, 카메라 접근이 불가능하면
        #메인 윈도우로 시그널을 보낸다
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            self.cam_not_ready.emit()
            return

        mp_drawing = mp.solutions.drawing_utils
        mp_drawing_styles = mp.solutions.drawing_styles
        mp_hands = mp.solutions.hands

        with mp_hands.Hands(
            model_complexity=0,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5) as hands:
            
            hand_prev = [None, None]
            hand_now = [None, None]
            gui.PAUSE = 0.001
            gui.FAILSAFE=False
            click_flag = True
            right_click_flag = True
            screen = gui.size()
            self.working=True

            pointer = [0]*2
            position = gui.position()
            pointer[0] = position[0]
            pointer[1] = position[1]

            if self.display:
                cv2.namedWindow("camera")
                cv2.moveWindow("camera",round(screen[0]/2)-400,round(screen[1]/2)-300)

            while self.working:
                success, image = cap.read()
                if not success:
                    print("Ignoring empty camera frame.")
                    continue

                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                results = hands.process(image)

                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                image = cv2.resize(image, (800, 600))

                if results.multi_hand_landmarks:
                    hand_landmarks = results.multi_hand_landmarks[0]

                    hand_now[0] = 1-hand_landmarks.landmark[17].x
                    hand_now[1] = hand_landmarks.landmark[17].y
                    hand_now[0]=round(hand_now[0],3)
                    hand_now[1]=round(hand_now[1],3)

                    if hand_now[0]<0:
                        hand_now[0]=0
                    if hand_now[1]<0:
                        hand_now[1]=0
                    
                    #주먹을 쥐었을 때 마우스를 제어
                    if self.is_rock(hand_landmarks) is True:
                        if hand_prev[0] is not None:
                            x_dis = (hand_now[0]-hand_prev[0])*screen[0]*1
                            y_dis = (hand_now[1]-hand_prev[1])*screen[1]*1

                            gui.moveTo(pointer[0]+x_dis, pointer[1]+y_dis)
                            pointer[0] +=x_dis
                            pointer[1] +=y_dis

                    hand_prev[0] = hand_now[0]
                    hand_prev[1] = hand_now[1]

                    #검지 손가락을 폈을 때 마우스 좌클릭 이벤트를 발생 시킨다.
                    if self.is_click(hand_landmarks):
                        if click_flag:
                            gui.click(button='left')
                            click_flag = False
                    else:
                        click_flag = True

                    #검지와 중지 손가락을 폈을 때 마우스 우클릭 이벤트를 발생시킨다.
                    if self.is_right_click(hand_landmarks):
                        if right_click_flag:
                            gui.click(button='right')
                            right_click_flag = False
                    else:
                        right_click_flag = True

                    #영상에 손 모양의 골격을 표시
                    mp_drawing.draw_landmarks(
                        image,
                        hand_landmarks,
                        mp_hands.HAND_CONNECTIONS,
                        mp_drawing_styles.get_default_hand_landmarks_style(),
                        mp_drawing_styles.get_default_hand_connections_style())
                
                #박스가 체크된 상태일 때 영상을 보여줌
                if self.display:
                    cv2.imshow("camera", cv2.flip(image, 1))
                    if cv2.waitKey(5) & 0xFF == 27:
                        self.working=False

        cv2.destroyAllWindows()
        cap.release()

    #주먹 쥔 손 모양을 인식하는 메소드
    def is_rock(self,hand_landmarks):
        tip_y_pos = []
        mcp_y_pos = []

        for i in range(8, 21, 4):
            tip_y_pos.append(hand_landmarks.landmark[i].y)

        for i in range(5, 18, 4):
            mcp_y_pos.append(hand_landmarks.landmark[i].y)

        for i in range(4):
            if(tip_y_pos[i]-mcp_y_pos[i] <= 0):
                return False

        return True

    #검지만 곧게 편 상태인지 분별하는 메소드
    def is_click(self,hand_landmarks):
        index_y_pos = []
        tip_y_pos = []
        mcp_y_pos = []

        for i in range(5, 9):
            index_y_pos.append(hand_landmarks.landmark[i].y)

        for i in range(12, 21, 4):
            tip_y_pos.append(hand_landmarks.landmark[i].y)

        for i in range(9, 18, 4):
            mcp_y_pos.append(hand_landmarks.landmark[i].y)

        for i in range(len(index_y_pos)-1):
            if index_y_pos[i] <= index_y_pos[i+1]:
                return False

        for i in range(3):
            if tip_y_pos[i] <= mcp_y_pos[i]:
                return False

        return True

    #검지와 중지만 곧게 편 상태인지 인식하는 메소드
    def is_right_click(self,hand_landmarks):
        index_y_pos = []
        middle_y_pos = []
        tip_y_pos = []
        mcp_y_pos = []

        for i in range(5, 9):
            index_y_pos.append(hand_landmarks.landmark[i].y)
            middle_y_pos.append(hand_landmarks.landmark[i+4].y)

        for i in range(16, 21, 4):
            tip_y_pos.append(hand_landmarks.landmark[i].y)

        for i in range(13, 18, 4):
            mcp_y_pos.append(hand_landmarks.landmark[i].y)

        for i in range(len(index_y_pos)-1):
            if index_y_pos[i] <= index_y_pos[i+1] or middle_y_pos[i] <= middle_y_pos[i+1]:
                return False

        for i in range(2):
            if tip_y_pos[i] <= mcp_y_pos[i]:
                return False

        return True

    #working 변수를 False로 설정하면 run메소드 내의 while문을
    #빠져나오면서 마우스 제어 쓰레드가 종료된다.
    def stop(self):
        self.working=False

    def is_working(self):
        return self.working

    def toggle_display(self):
        if self.display:
            self.display=False
        else:
            self.display=True



#사용 설명 내용이 있는 윈도우
""" class Manual(QMainWindow):
    def __init__(self,parent):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Manual")
        self.setFixedSize(900,675)
        vlayout=QVBoxLayout()

        content=("<p style='font-size: 17px'>"
                +"<b>실행</b><br>"
                +"실행 버튼을 누르기 전 카메라에 대한 권한을 허용해 주세요. "
                +"버튼을 누르면  카메라가 켜지고 영상을 인식하기 시작합니다. "
                +"손으로 마우스를 제어할 수 있습니다. "
                +"이때 카메라가 충분히 인식 가능한 거리와 위치에 손이 있어야 마우스를 제어할 수 있습니다.<br><br>"
                +"<b>중지</b><br>"
                +"중지 버튼을 누르면 카메라와 마우스 컨트롤 기능이 중지됩니다.<br><br>"
                +"<b>마우스 커서 움직이기</b><br>"
                +"카메라가 보이는 영역 안에서 주먹 쥔 손을 움직이면 마우스 커서가 따라옵니다. "
                +"손등을 보인 상태로 움직이면 인식률이 떨어질 수 있습니다. "
                +"주먹 쥔 손을 손바닥 방향으로 비출 수록 인식률이 좋아집니다.<br><br>"
                +"<b>마우스 좌클릭 이벤트</b><br>"
                +"주먹을 쥔 상태에서 검지만 곧게 펴면 마우스 좌클릭 이벤트가 발생합니다. "
                +"좌클릭 이벤트를 다시 발생 시키려면 손을 움켜쥐고 다시 검지만 곧게 펴 줍니다.<br><br>"
                +"<b>마우스 우클릭 이벤트</b><br>"
                +"주먹을 쥔 상태에서 검지와 중지만 곧게 펴면 마우스 우클릭 이벤트가 발생합니다. "
                +"우클릭 이벤트를 다시 발생 시키려면 손을 움켜쥐고 다시 검지와 중지만 곧게 펴 줍니다.<br><br>"
                +"<b>카메라 화면 보이기</b><br>"
                +"박스를 체크하고 실행 버튼을 누르면 카메라 캡쳐 영상을 보여주면서 마우스 제어가 실행됩니다. "
                +"영상을 클릭하고 esc를 눌러도 실행이 중지됩니다. "
                +"손이 인식되면 손의 골격을 영상에 표시합니다. "
                +"체크를 해제하면 영상이 보이지 않은 상태로 제어가 실행됩니다. "
                +"단, 실행 중에는 체크박스의 상태를 변경할 수 없습니다.<br><br>"
                +"<b>제작 과정 중 직면한 문제 해결 방법들</b><br>"
                +"실행 버튼을 누르면 카메라는 영상을 인식합니다. 이 상태에서 중지 버튼을 누르면 함수 실행 중에 사용자가 또 다른 함수를 "
                +"호출하게 됩니다. 결국 충돌이 일어나서 프로그램이 강제 종료되는 문제가 발생했는데 이것을 "
                +"멀티 쓰레딩으로 해결했습니다.<br>"
                +"또한 카메라에 대한 접근 권한이 없다면 프로그램은 실행되지 않습니다. "
                +"이런 경고 메시지를 출력하는 기능을 구현하려면 쓰레드 객체와 윈도우 객체가 "
                +"통신할 수 있어야 하는데 이것을 쓰레드의 시그널 객체에 윈도우 객체의 메소드를 연결해 해결했습니다."
                )
        label=QLabel(content)
        label.setWordWrap(True)

        vlayout.addWidget(label)
        widget=QWidget()
        widget.setLayout(vlayout)
        self.setCentralWidget(widget)
 """