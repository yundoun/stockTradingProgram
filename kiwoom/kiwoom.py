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
        self.detail_account_info()  # 예수금 가져오기


    def get_ocx_instance(self):
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")               # 응용프로그램 제어


    def event_slots(self):        # 이벤트 모아두는 slot
        self.OnEventConnect.connect(self.login_slot)
        self.OnReceiveTrData.connect(self.trData_slot)
        # TR요청을 받는 slot


    def signal_login_commConnect(self):     # 로그인 시도하는 함수
        self.dynamicCall("CommConnect()")    # PyQt5에서 제공하는 함수 / 데이터 전송 하는 역할

        self.login_event_loop = QEventLoop()    # 이벤트 루프 클래스


        self.login_event_loop.exec_()   #  다음 코드 실행 안되게기



    def login_slot(self, errCode):   #  성공이면 인자값 ErrCode가 0
        print(errCode)
        print(errors(errCode))
        print("로그인 성공")

        self.login_event_loop.exit()  # 로그인이 완료 되면 다음 코드 실행되게 탈출
        print("로그인 이후 코드 실행")



    def get_account_info(self):     # 로그인한 정보에서 계좌번호 가져오기
        account_list = self.dynamicCall("GetLoginInfo(String)", "ACCNO")   #koa 스튜디오 함수  / ACC nomber => 계좌번호 가져오기

        self.account_num = account_list.split(';')[0]
        print("나의 계좌번호는 %s " % self.account_num)

    def detail_account_info(self):
        print("예수금을 요청하는 부분")

        self.dynamicCall("SetInputValue(String, String)", "계좌번호", self.account_num)
        self.dynamicCall("SetInputValue(String, String)", "비밀번호", "0000")
        self.dynamicCall("SetInputValue(String, String)", "비밀번호입력매체구분", "00")
        self.dynamicCall("SetInputValue(String, String)", "조회구분", "2")
        self.dynamicCall("CommRqData(String, String, int, String)", "예수금상세현황요청","opw00001", 0,"2000")

                                                        # ("내가 지은 요청이름", "TR번호", "preNext", "화면번호")



    def trData_slot(self, sScrNo ,sRQName, sTrCode, sRecordName, sPrevNext ):
        '''
        TR요청을 받는 구역이다 / 슬롯
        :param sScrNo: 스크린번호
        :param sRQName: 내가 요청했을 때 지은 이름
        :param sTrCode:  요청 id, tr코드
        :param sRecordName: 사용 안함
        :param sPrevNext: 다음 페이지가 있는지 확인
        :return:
        '''

        if sRQName == "예수금상세현황요청":
            deposit = self.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, 0, "예수금")
            orderAmount = self.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, 0, "주문가능금액")
            withdraw = self.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, 0, "출금가능금액")

            # OnReceiveTRData() 이벤트가 발생될때 수신한 데이터를 얻어오는 함수
            # 이 함수는 OnReceiveTrData()이벤트가 발생될때 그 안에서 사용해야 합니다.

            print("예수금 : %s" % deposit)
            print("주문가능금액 : %s" % orderAmount)
            print("출금가능금액 : %s" % withdraw)





















