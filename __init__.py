# 실행 용도 파일

from ui.ui import *  # 클래스 다 가져 올려면 * 사용  / 사용 중일 때 활성화 됨


class Main():
    def __init__(self):
        print("실행할 메인 클래스")

        Ui_class()



if __name__== "__main__":
    Main()
    # 실행 파일 명시하기 위해 사용