# 키움 증권

from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from config.errorCode import *

class Kiwoom(QAxWidget):
    def __init__(self):
        super().__init__()
        print("kiwoom 클래스 입니다.")

        #초기값
        ################ eventloop 모음###################
        self.login_event_loop = None
        ##################################################

        # 변수 모음
        #################################
        self.account_num = None
        ####################




        self.get_ocx_instance()
        self.event_slots()

        self.signal_login_commConnect()
        self.get_account_info()


    def get_ocx_instance(self):
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")               # 응용프로그램 제어


    def event_slots(self):        # 이벤트 모아두는 slot
        self.OnEventConnect.connect(self.login_slot)


    def login_slot(self, errCode):   #  성공이면 인자값 ErrCode가 0
        print(errCode)
        print(errors(errCode))
        print("로그인 성공")

        self.login_event_loop.exit()  # 로그인이 완료 되면 다음 코드 실행되게 탈출
        print("로그인 이후 코드 실행")

    def signal_login_commConnect(self):     # 로그인 시도하는 함수
        self.dynamicCall("CommConnect()")    # PyQt5에서 제공하는 함수 / 데이터 전송 하는 역할

        self.login_event_loop = QEventLoop()    # 이벤트 루프 클래스
        self.login_event_loop.exec_()   #  다음 코드 실행 안되게 막기

    def get_account_info(self):     # 로그인한 정보에서 계좌번호 가져오기
        account_list = self.dynamicCall("GetLoginInfo(String)", "ACCNO")   #koa 스튜디오 함수  / ACC nomber => 계좌번호 가져오기

        self.account_num = account_list.split(';')[0]
        print("나의 계좌번호는 %s " % self.account_num)


























