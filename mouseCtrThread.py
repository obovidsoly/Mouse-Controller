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