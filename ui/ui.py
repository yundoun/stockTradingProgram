# Ui 파일

from kiwoom.kiwoom import *

import sys   # 파이썬 시스템에 필요한 라이브러리
from PyQt5.QtWidgets import *


class Ui_class():
    def __init__(self):
        print("Ui_class 입니다.")

        self.app = QApplication(sys.argv)       # ui를 실행하기 위해서 필요한 변수 함수 초기화

        self.kiwoom = Kiwoom()   # 키움 실행

        self.app.exec()  # 이벤트 루프 실행  / 프로그램 종료 안되게