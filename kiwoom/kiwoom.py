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
        self.detail_account_info_eventLoop = QEventLoop()  # 키움 서버에 요청 / 예수금, 계좌평가 잔고내역 요청
        ##################################################

        ##### 스크린 번호 모음
        self.screen_my_info = "2000"
        self.screen_calculation_stock = "4000"


        # 변수 모음
        #################################
        self.account_num = None
        self.account_stock_dict = {}   # 보유 종목이 담겨 있는 딕셔너리
        self.not_account_stock_dict = {}  # 미체결 종목이 담겨 있는 딕셔너리
        ####################

        # 계좌관련변수
        self.use_money=0
        self.use_money_percent = 0.5
        ###############






        self.get_ocx_instance()
        self.event_slots()

        self.signal_login_commConnect()
        self.get_account_info()
        self.detail_account_info()  # 예수금 요청
        self.detail_account_myStock()  # 계좌평가잔고내역 요청
        self.not_concluded_account()  # 미체결 요청

        self.calculator_fnc()   # 종목 분석용, 임시용으로 실행



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





    def detail_account_info(self):    #키움 서버에 요청 1
        print("예수금 요청")

        self.dynamicCall("SetInputValue(String, String)", "계좌번호", self.account_num)
        self.dynamicCall("SetInputValue(String, String)", "비밀번호", "0000")
        self.dynamicCall("SetInputValue(String, String)", "비밀번호입력매체구분", "00")
        self.dynamicCall("SetInputValue(String, String)", "조회구분", "2")
        self.dynamicCall("CommRqData(String, String, int, String)", "예수금상세현황요청","opw00001", 0,"screen_my_info")
                                                        # ("내가 지은 요청이름", "TR번호", "preNext", "화면번호")

        self.detail_account_info_eventLoop = QEventLoop()  # 요청 후 이벤트 루프 실행
        self.detail_account_info_eventLoop.exec_()  # 인스턴스화


    def detail_account_myStock(self, sPrevNext="0"):  # 키움 서버에 요청 2
        print("계좌평가잔고내역 요청")

        self.dynamicCall("SetInputValue(String, String)", "계좌번호", self.account_num)
        self.dynamicCall("SetInputValue(String, String)", "비밀번호", "0000")
        self.dynamicCall("SetInputValue(String, String)", "비밀번호입력매체구분", "00")
        self.dynamicCall("SetInputValue(String, String)", "조회구분", "2")
        self.dynamicCall("CommRqData(String, String, int, String)", "계좌평가잔고내역요청", "opw00018", sPrevNext, self.screen_my_info)
                                                            # ("내가 지은 요청이름", "TR번호", "preNext", "화면번호")

        self.detail_account_info_eventLoop.exec_()

    def not_concluded_account(self, sPrevNext = "0"):
        print("미체결 요청")
        self.dynamicCall("SetInputValue(QString, QString)", "계좌번호", self.account_num)
        self.dynamicCall("SetInputValue(QString, QString)", "전체종목구분", "1")
        self.dynamicCall("SetInputValue(QString, QString)", "매매구분", "0")

        # 이거 빼도 될려나 ?
        self.dynamicCall("SetInputValue(QString, QString)", "종목코드", "0")
        self.dynamicCall("SetInputValue(QString, QString)", "체결구분", "1")
        self.dynamicCall("CommRqData(String, String, int, String)", "미체결요청", "opt10075", sPrevNext, self.screen_my_info)


        self.detail_account_info_eventLoop.exec_()
        # 이벤트 루프를 실행 시켜야 요청이 끝날 때 까지 블락 기능 활성화 / 다음 코드 안넘어가게



    # 보유 종목이 20개 넘을 경우 sPrevNext = 2로 출력됨
    def trData_slot(self, sScrNo ,sRQName, sTrCode, sRecordName, sPrevNext ):  # 데이터 처리화면 출력
        '''
        TR요청을 받는 구역이다 / 슬롯
        :param sScrNo: 스크린번호
        :param sRQName: 내가 요청했을 때 지은 이름
        :param sTrCode:  요청 id, tr코드
        :param sRecordName: 사용 안함
        :param sPrevNext: 다음 페이지가 있는지 확인
        :return:
        '''

        if sRQName == "예수금상세현황요청":   # tr데이터 요청값 필터링하여 출력 / 요청 값은 "예수금상세현황요청"
            deposit = self.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, 0, "예수금")
            orderAmount = self.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, 0, "주문가능금액")
            withdraw = self.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, 0, "출금가능금액")
            minOrder = self.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, 0, "최소주문가능금액")

            # OnReceiveTRData() 이벤트가 발생될때 수신한 데이터를 얻어오는 함수
            # 이 함수는 OnReceiveTrData()이벤트가 발생될때 그 안에서 사용해야 합니다.


            self.use_money = int(deposit) * self.use_money_percent   # 예수금의 50퍼센트 사용
            self.use_money = self.use_money / 4  # 예수금 50퍼센트를 다시 4등분 해서 사용


            print("예수금                 : %s 원" % int(deposit))
            print("주문가능금액            : %s 원" % int(orderAmount))
            print("출금가능금액            : %s 원" % int(withdraw))
            print("최소주문가능금액         : %s 원" % int(minOrder))

            self.detail_account_info_eventLoop.exit()
            # 출력 다 하고 루프 탈출 => 다음 코드 실행

        if sRQName == "계좌평가잔고내역요청":
            totalPurchase = self.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, 0, "총매입금액")
            totalReturn = self.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, 0, "총수익률(%)")

            print("총매입금액    : %s 원" % int(totalPurchase))
            print("총수익률      : %s %%" % float(totalReturn))

            # 보유 계좌 종목 가져 오기
            # getRepeatCnt == 멀티 데이터 조회 용도
            rows = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)  # 보유 종목의 개수 가져 오기
            cnt = 0
            for i in range(rows): # 보유 종목의 개수 만큼 반복
                code = self.dynamicCall("GetCommData(QString, QString, int, QString", sTrCode, sRQName, i,"종목번호")
                code = code.strip()[1:]   # 종목코드 맨 앞자리 알파벳 제거


                code_name = self.dynamicCall("GetCommData(QString, QString, int, QString", sTrCode, sRQName, i, "종목명")
                stock_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString", sTrCode, sRQName, i, "보유수량")
                purchase_price  = self.dynamicCall("GetCommData(QString, QString, int, QString", sTrCode, sRQName, i, "매입가")
                learn_rate = self.dynamicCall("GetCommData(QString, QString, int, QString", sTrCode, sRQName,i,"수익률(%)")
                current_price = self.dynamicCall("GetCommData(QString, QString, int, QString", sTrCode, sRQName,i,"현재가")
                purchase_amount  = self.dynamicCall("GetCommData(QString, QString, int, QString", sTrCode, sRQName,i,"매입금액")
                possible_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString", sTrCode, sRQName,i,"매매가능수량")

                if code in self.account_stock_dict:  #
                    pass
                else:
                    self.account_stock_dict.update({code: {}})



                # 출력 포맷팅 / 양 쪽 공백 제거
                code_name = code_name.strip()
                stock_quantity = int(stock_quantity.strip())
                purchase_price = int(purchase_price.strip())
                learn_rate = float(learn_rate.strip())  # 수익률은 퍼센트로 출력
                current_price = int(current_price.strip())
                purchase_amount = int(purchase_amount.strip())
                possible_quantity = int(possible_quantity.strip())

                self.account_stock_dict[code].update({"종목명":code_name})
                self.account_stock_dict[code].update({"보유수량":stock_quantity})
                self.account_stock_dict[code].update({"매입가":purchase_price})
                self.account_stock_dict[code].update({"수익률(%)":learn_rate})
                self.account_stock_dict[code].update({"현재가": current_price})
                self.account_stock_dict[code].update({"매입금액":purchase_amount})
                self.account_stock_dict[code].update({"매매가능수량": possible_quantity})

                cnt +=1

                print("{}".format(self.account_stock_dict[code]))

            print("현재 보유 종목 개수", cnt)

            # 종목 내역 20개 초과시 다음 페이지 넘어 가기
            if sPrevNext == "2":
                self.detail_account_myStock(sPrevNext="2")
            # 아닐 경우 루프 탈출
            else:
                self.detail_account_info_eventLoop.exit()



        elif sRQName == "미체결요청":
            rows = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)

            if rows == 0:
                print("미체결된 종목이 존재하지 않습니다.")

            for i in range(rows):
                code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목코드")
                code_nm = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목명")
                order_number = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문번호")
                order_status = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문상태") # 접수, 확인, 체결
                order_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문수량")
                order_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문가격")
                order_divide = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문구분") # 매도, 매수, 정정, 취소
                not_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "미체결수량")
                ok_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "체결량")


                code = code.strip()
                code_nm = code_nm.strip()
                order_number = int(order_number.strip)()
                order_status = order_status.strip()
                order_quantity = int(order_quantity.strip())
                order_price = int(order_price.strip())
                order_divide = order_divide.strip().lstrip('+').lstrip('-')
                not_quantity = int(not_quantity.strip())
                ok_quantity = int(ok_quantity.strip())

                if order_number in self.not_account_stock_dict:
                    pass

                else:
                    self.not_account_stock_dict[order_number] = {}


                self.not_account_stock_dict[order_number].update({"종목코드": code})
                self.not_account_stock_dict[order_number].update({"종목명": code_nm})
                self.not_account_stock_dict[order_number].update({"주문번호": order_number})
                self.not_account_stock_dict[order_number].update({"주문상태": order_status})
                self.not_account_stock_dict[order_number].update({"주문수량": order_quantity})
                self.not_account_stock_dict[order_number].update({"주문가격": order_price})
                self.not_account_stock_dict[order_number].update({"주문구분": order_divide})
                self.not_account_stock_dict[order_number].update({"미체결수량": not_quantity})
                self.not_account_stock_dict[order_number].update({"체결량": ok_quantity})


                print("미체결 종목  : %s" % self.not_account_stock_dict[order_number])

            self.detail_account_info_eventLoop.exit()

        elif "주식일봉차트조회" == sRQName:
            print("일봉데이터 요청")



    def get_code_list_by_market(self, market_code):
        '''
        종목 코드들 반환
        :param self:
        :param market_code:
        :return:
        '''
        code_list = self.dynamicCall("GetCodeListByMarket(QString)", market_code)
        code_list = code_list.split(";")[:-1] # 마지막껀 삭제
        # 종목코드 11111;11111;11111;1111; 이런식으로 나옴 그래서-> ["1111111", "111111",111111"] 자르기
        return code_list

    # tr요청을 빠르게 할경우 끊김 그래서 3.6초 정도 딜레이가 있어야함
    def calculator_fnc(self):
        '''
        종목 분석 실행용 함수
        :return:
        '''
        code_list = self.get_code_list_by_market("10")
        print("코스닥 종목 총 개수 : %s" % len(code_list))

        # 스크린 번호 요청을 하면 그룹이 만들어지고 그 스크린번호가 쌓이면 안되니까 끊어줬다
        # 스크린 번호도 200개 까지 밖에 못만드니까 끊어주는 것이 좋다
        for idx, code in enumerate(code_list): # enumerate ==> 인덱스랑 데이터값 같이 줌
            self.dynamicCall("DisconnectRealData(QString)", self.screen_calculation_stock)
            print("%s / %s : KOSDAQ Stock code : %s is updating..." % (idx+1, len(code_list), code))
            self.day_kiwoom_db(code=code)

    def day_kiwoom_db(self, code=None, date = None, sPrevNext ="0"):
        '''
        일봉데이터TR 받아오기
        (스크린번호 요청)
        :param self: 
        :param code: 
        :param date: 
        :param sPrevNext: 
        :return: 
        '''
        self.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        self.dynamicCall("SetInputValue(QString, QString)", "수정주가구분","1")
        # 수정주가구분 : 주가의 최종적인 수정 가격이 반영된 형태  ex) 액면분할
        # 0: 반영되기 전 1: 반영된 후

        if date != None:  # 오늘 날짜로 할 경우 데이터 입력 안해도 됨
            self.dynamicCall("SetInputValue(QString, QString", "기준일자", date)

        self.dynamicCall("CommRqData(QString, QString, int, QString)", "주식일봉차트조회", "opt10081", sPrevNext, self.screen_calculation_stock)
        # Tr 서버로 전송 - Transaction


























