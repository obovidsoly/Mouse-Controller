﻿## Mouse Controller
 
 ![image](https://user-images.githubusercontent.com/44926279/216830171-7ef78694-734e-4333-a63b-d0918c4522a8.png)

### 실행
실행 버튼을 누르기 전 카메라에 대한 권한을 허용해 주세요. 버튼을 누르면  카메라가 켜지고 영상을 인식하기 시작합니다. 손으로 마우스를 제어할 수 있습니다. 이때 카메라가 충분히 인식 가능한 거리와 위치에 손이 있어야 마우스를 제어할 수 있습니다.

### 중지
중지 버튼을 누르면 카메라와 마우스 컨트롤 기능이 중지됩니다.

### 마우스 커서 움직이기
카메라가 보이는 영역 안에서 주먹 쥔 손을 움직이면 마우스 커서가 따라옵니다. 손등을 보인 상태로 움직이면 인식률이 떨어질 수 있습니다. 주먹 쥔 손을 손바닥 방향으로 비출 수록 인식률이 좋아집니다.

### 마우스 좌클릭 이벤트
주먹을 쥔 상태에서 검지만 곧게 펴면 마우스 좌클릭 이벤트가 발생합니다. 좌클릭 이벤트를 다시 발생 시키려면 손을 움켜쥐고 다시 검지만 곧게 펴 줍니다.

### 마우스 우클릭 이벤트
주먹을 쥔 상태에서 검지와 중지만 곧게 펴면 마우스 우클릭 이벤트가 발생합니다. 우클릭 이벤트를 다시 발생 시키려면 손을 움켜쥐고 다시 검지와 중지만 곧게 펴 줍니다. 

### 카메라 화면 보이기
박스를 체크하고 실행 버튼을 누르면 카메라 캡쳐 영상을 보여주면서 마우스 제어가 실행됩니다. 영상을 클릭하고 esc를 눌러도 실행이 중지됩니다. 손이 인식되면 손의 골격을 영상에 표시합니다. 체크를 해제하면 영상이 보이지 않은 상태로 제어가 실행됩니다. 단, 실행 중에는 체크박스의 상태를 변경할 수 없습니다.

### library
pyautogui==0.9.53<br/>
pyqt==5.9.2<br/>
mediapipe==0.8.10<br/>
