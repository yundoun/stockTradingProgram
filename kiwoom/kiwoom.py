# 키움 증권
import os

from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from config.errorCode import *
from PyQt5.QtTest import *
from config.kiwoonType import *

global dailyChart_SUM
dailyChart_SUM = 0
# 각 종목별 일봉데이터개수 총합

class Kiwoom(QAxWidget):
    def __init__(self):
        super().__init__()
        print("kiwoom 클래스 입니다.")

        self.realType = RealType()

        #초기값
        ################ eventloop 모음###################
        self.login_event_loop = None
        self.detail_account_info_eventLoop = QEventLoop()  # 키움 서버에 요청 / 예수금, 계좌평가 잔고내역 요청
        self.calculator_event_loop= QEventLoop()
        ##################################################

        ##### 스크린 번호 모음
        self.screen_my_info = "2000"
        self.screen_calculation_stock = "4000"
        self.screen_number_sock = "5000" # 종목별로 할당할 스크린 번호
        self.screen_number_trading = "6000" # 주문별 할당할 스크린 번호
        self.screen_start_stop_real = "1000"

        # 변수 모음
        #################################
        self.account_num = None
        self.account_stock_dict = {}   # 보유 종목이 담겨 있는 딕셔너리
        self.not_account_stock_dict = {}  # 미체결 종목이 담겨 있는 딕셔너리
        self.portfolio_stock_dict = {}
        self.jango_dict = {}
        ####################

        # 계좌관련변수
        self.use_money=0
        self.use_money_percent = 0.5
        ###############
        # 종목 분석용 전역변수
        self.calcul_data = []
        #########################

        self.get_ocx_instance()
        self.event_slots()

        ########## 실시간 데이터############################
        self.real_event_slots()


        self.signal_login_commConnect()
        self.get_account_info()
        self.detail_account_info()  # 예수금 요청
        self.detail_account_myStock()  # 계좌평가잔고내역 요청
        self.not_concluded_account()  # 미체결 요청

        #self.calculator_fnc()   # 종목 분석용, 임시용으로 실행
        self.read_code() # 저장된 종목들 불러오기
        self.screen_number_setting() # 스크린번호 할당

        # 실시간 데이터 수신 : 장 시작 시간, 장 종료 시각 등
        self.dynamicCall("SetRealReg(QString, QString, QString, QString)", self.screen_start_stop_real, '', self.realType.REALTYPE['장시작시간']['장운영구분'],"0")

        for code in self.portfolio_stock_dict.keys():
            screen_num = self.portfolio_stock_dict[code]['스크린번호']
            fids = self.realType.REALTYPE['주식체결']['체결시간']
            self.dynamicCall("SetRealReg(QString, QString, QString, QString)", screen_num, code, fids, "1")
            print("실시간 등록 코드 : %s, 스크린번호 : %s, fid번호 %s" % (code, screen_num,fids))
            # 실시간 등록 : SetRealReg
    def get_ocx_instance(self):
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")               # 응용프로그램 제어


    def event_slots(self):        # 이벤트 모아두는 slot
        self.OnEventConnect.connect(self.login_slot)
        self.OnReceiveTrData.connect(self.trData_slot)
        # TR요청을 받는 slot


    def real_event_slots(self):
        self.OnReceiveRealData.connect(self.realdata_slot)


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
            # 종목 코드를 알아야겠지?

            code = self.dynamicCall("GetCommData(QString, QString, int, QString",sTrCode, sRQName, 0, "종목코드")
            code = code.strip()
            print("%s 일봉데이터 요청" % code)

            cnt = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)
            print("현재 %s일의 일봉데이터를 가져왔습니다." % cnt)
            # GetRepaetCnt 는 차트 확대하는 버튼이랑 같다고 보면됨(?)

            # 한 번 조회하면 600일치까지의 일봉데이터를 받을 수 있다.
            # 시간이 많이 걸리기 때문에 원하는 종목만 선택해서 하는 것이 좋다.
            for i in range(cnt):
                data = []
                # data = self.dynamicCall("GetCommData(QString, QString)", sTrCode, sRQName)
                # [['', '현재가', '거래량', '거래대금', '날짜', '시가', '고가', '저가', '']]

                current_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "현재가")
                value = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "거래량")
                trading_value = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "거래대금")
                date = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "일자")
                start_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "시가")
                high_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "고가")
                low_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "저가")

                data.append("")
                data.append(current_price.strip())
                data.append(value.strip())
                data.append(trading_value.strip())
                data.append(date.strip())
                data.append(start_price.strip())
                data.append(high_price.strip())
                data.append(low_price.strip())
                data.append("")

                self.calcul_data.append(data.copy())
                # calcul_data : for문을 돌려서 나온 데이터를 전역변수 리스트에 저장

            print(len(self.calcul_data))

            global dailyChart_SUM
            dailyChart_SUM += cnt

            if sPrevNext == "2":
                self.day_kiwoom_db(code=code, sPrevNext=sPrevNext)
            else:
                print("종목코드 %s의 일봉데이터의 총 개수는 %s개 입니다." % (code, dailyChart_SUM))
                dailyChart_SUM = 0

                print("총 수 %s" % len(self.calcul_data))

                pass_success = False

                # 1. 120일 이평선을 그릴만큼 데이터가 있는지 체크
                if self.calcul_data == None or len(self.calcul_data) < 120:
                    pass_success = False

                else:
                    #120일 이상이 될 경우
                    total_price = 0
                    for value in self.calcul_data[:120]: # 오늘부터 120일전까지
                        total_price += int(value[1]) # 120일 간 종가를 모두 더한 것

                    moving_average_price = total_price / 120
                    # 120 이동평균선 평균의 가격
                    # 120 이동평균선 생성됨 ##########

                    # 2. 그린밸의 매수신호 적용
                    # 오늘의 주가가 120 이평선에 걸쳐있는 것을 확인
                    bottom_stock_price = False
                    check_price = None
                    if int(self.calcul_data[0][7]) <= moving_average_price and moving_average_price <= int(self.calcul_data[0][6]):
                        # 오늘 일자의 저가가 120 이동평균선보다 낮아야 하고, 오늘의 고가가 120 이동평균선보다 높아야 한다.
                        print("오늘의 주가가 120 이평선에 걸쳐있는 것을 확인")
                        bottom_stock_price = True
                        check_price = int(self.calcul_data[0][6])
                        # 현재의 고가가 과거 데이터의 저가보다 높아야 하기때문에 변수에 미리 저장

                        # 과거 일봉들이 120일 이평선보다 밑에 있는지 확인, 그리고
                        # 그렇게 확인을 하다가 일봉이 120일 이평선보다 위에 있으면 계산 진행

                    prev_price = None
                    # 과거의 일봉 저가를 나타냄

                    if bottom_stock_price == True:
                        moving_average_price_prev = 0
                        # 일수에 맞춰서 120이평선을 다시 계산해줘야 하기 때문
                        price_top_moving = False

                        idx =1
                        while True:
                            if len(self.calcul_data[idx:]) < 120:  # 120일치가 있는지 계속 확인
                                print("120일치가 없음 !!")
                                break

                            total_price = 0
                            for value in self.calcul_data[idx:120+idx]:
                                total_price += int(value[1])
                            moving_average_price_prev = total_price / 120

                            if moving_average_price_prev <= int(self.calcul_data[idx][6]) and idx<= 20:
                                # 20일전에 고가가 이동평균선위에 있을 경우 끊는다
                                # 이건 그냥 임의로 설정한거임
                                print("20일 동안 주가가 120일 이평선과 같거나 위에 있으면 통과 X")
                                price_top_moving = False
                                break

                            elif int(self.calcul_data[idx][7])  > moving_average_price_prev and idx >20:
                                # 저가가 이평선보다 위에 있고 20일보다 크면은
                                print("120일 이평선 위에 있는 일봉 확인됨")
                                price_top_moving = True
                                prev_price = int(self.calcul_data[idx][7])
                                break

                            idx += 1

                        # 해당 부분 이평선이 가장 최근 일자의 이평선 가격보다 낮은지 확인
                        if price_top_moving == True:
                            if moving_average_price > moving_average_price_prev and check_price > prev_price:
                                print("포착된 이평선이 가격이 오늘자(최근일자) 이평선 가격보다 낮은 것 확인됨")
                                print("포착된 부분의 일봉 저가가 오늘자 일봉의 고가보다 낮은지 확인됨")
                                pass_success = True


                if pass_success == True:
                    print("조건부 통과됨")
                    code_nm = self.dynamicCall("GetMasterCodeName(QString)", code)

                    f = open("files/condition_stock.txt", "a", encoding="utf8")
                    f.write("%s\t%s\t%s\n" % (code, code_nm, str(self.calcul_data[0][1])))
                    f.close()

                elif pass_success == False:
                     print("조건부 통과 못함")


                self.calcul_data.clear()
                self.calculator_event_loop.exit()





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

    def day_kiwoom_db(self, code=None, date=None, sPrevNext ="0"):
        '''
        일봉데이터TR 받아오기
        (스크린번호 요청)
        :param self: 
        :param code: 
        :param date: 
        :param sPrevNext: 
        :return: 
        '''

        # 프로세스 과정이 멈추면 안된다. 이벤트 루프 자체가 살아있어야함
        # 이 이벤트에 대한 네트워크적 프로세스를 하위 코드가 실행되기까지 딜레이를 준다.
        QTest.qWait(3600)

        self.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        self.dynamicCall("SetInputValue(QString, QString)", "수정주가구분","1")
        # 수정주가구분 : 주가의 최종적인 수정 가격이 반영된 형태  ex) 액면분할
        # 0: 반영되기 전 1: 반영된 후

        if date != None:  # 오늘 날짜로 할 경우 데이터 입력 안해도 됨
            self.dynamicCall("SetInputValue(QString, QString", "기준일자", date)

        self.dynamicCall("CommRqData(QString, QString, int, QString)", "주식일봉차트조회", "opt10081", sPrevNext, self.screen_calculation_stock)
        # Tr 서버로 전송 - Transaction

        self.calculator_event_loop.exec_()
        # 한 종목씩 완료하고 넘어가게 이벤트 루프 달아주기


    def read_code(self):
        if os.path.exists("files/condition_stock.txt"): # 운영체제의 경로에 이러한 파일이 존재하느냐 확인, 있으면 True
            f = open("files/condition_stock.txt", "r", encoding="utf8") # 파일열기

            lines = f.readlines()
            idx = 0
            for line in lines:
                if line != "":
                    ls = lines[idx].split("\t")


                    stock_code = ls[0]
                    stock_name = ls[1]
                    stock_price = int(ls[2].split("\n")[0])
                    stock_price = abs(stock_price)

                    self.portfolio_stock_dict.update({stock_code:{"종목명":stock_name, "현재가":stock_price}})
                    # ex) {"2090923":{"종목명","삼성", "현재가",:100000}
                    idx += 1
            f.close()

            print("그린밸의 1 매수법칙에 부합하는 종목은 다음과 같습니다.")
            print("=============================================")
            for key, value in self.portfolio_stock_dict.items():
                print(key, value)
            print("=============================================")

    def screen_number_setting(self):

        screen_overwrite = []

        # 계좌평가잔고내역에 있는 종목들
        for code in self.account_stock_dict.keys():
            if code not in screen_overwrite:
                screen_overwrite.append(code)

        # 미체결에 있는 종목들
        for order_number in self.not_account_stock_dict.keys():
            code = self.not_account_stock_dict[order_number]['종목코드']

            if code not in screen_overwrite:
                screen_overwrite.append(code)

        # 포트폴리오에 담겨 있는 종목들
        for code in self.portfolio_stock_dict.keys():
            if code not in screen_overwrite:
                screen_overwrite.append(code)

        # 스크린번호 할당
        # 스크린번호 한번에 요청 100개, 200개 까지 밖에 못만듬
        cnt = 0
        for code in screen_overwrite:
            temp_screen = int(self.screen_number_sock)
            trading_screen = int(self.screen_number_trading)

            if (cnt % 50) == 0:
                temp_screen += 1
                self.screen_number_sock = str(temp_screen)

            if (cnt % 50) == 0:
                trading_screen += 1
                self.screen_number_trading = str(trading_screen)

            if code in self.portfolio_stock_dict.keys():
                self.portfolio_stock_dict[code].update({"스크린번호" : str(self.screen_number_sock)})
                self.portfolio_stock_dict[code].update({"주문용스크린번호": str(self.screen_number_trading)})

            elif code not in self.portfolio_stock_dict:
                self.portfolio_stock_dict.update({code: {"스크린번호": str(self.screen_number_sock), "주문용스크린번호": str(self.screen_number_trading)}})


            cnt += 1

        for key, value in self.portfolio_stock_dict.items():
            print(key, value)

    def realdata_slot(self, sCode, sRealType, sRealData):
        '''

        :param sCode: 종목코드
        :param sRealType: 실시간 타입
        :param sRealData: 실시간 데이터
        :return:
        '''
        if sRealType == "장시작시간":
            fid = self.realType.REALTYPE[sRealType]['장운영구분']
            value = self.dynamicCall("GetCommRealData(QString, int)", sCode, fid)

            if value == '0':
                print("장 시작 전 입니다.")
            elif value == '3':
                print("장 시작했습니다.")
            elif value == "2":
                print("장 종료, 동시 호가로 넘어감")
            elif value == "4":
                print("장이 종료 되었습니다.")
        elif sRealType == "주식체결":
            print(sCode)

            # 체결시간 얻어오기
            a = self.dynamicCall("GetCommRealDate(QString, int)", sCode, self.realType.REALTYPE[sRealType]['체결시간'])
            # HHMMSS

            b = self.dynamicCall("GetCommRealDate(QString, int)", sCode, self.realType.REALTYPE[sRealType]['현재가'])
            b = abs(int(b)) # +(-) 2500 음봉일 경우 마이너스로 나옴 # 주문시 가격은 양수로만 사용할거기 때문에

            c = self.dynamicCall("GetCommRealDate(QString, int)", sCode, self.realType.REALTYPE[sRealType]['전일대비'])
            c = abs(int(c)) # 출력 : +(-) 50

            d = self.dynamicCall("GetCommRealDate(QString, int)", sCode, self.realType.REALTYPE[sRealType]['등락율'])
            d = float(d) # 소수점 사용하기 위해

            e = self.dynamicCall("GetCommRealDate(QString, int)", sCode, self.realType.REALTYPE[sRealType]['(최우선)매도호가'])
            e = abs(int(e))

            f = self.dynamicCall("GetCommRealDate(QString, int)", sCode, self.realType.REALTYPE[sRealType]['(최우선)매수호가'])
            f = abs(int(f))

            g = self.dynamicCall("GetCommRealDate(QString, int)", sCode, self.realType.REALTYPE[sRealType]['거래량'])
            g = abs(int(g)) # 틱봉의 거래량

            h = self.dynamicCall("GetCommRealDate(QString, int)", sCode, self.realType.REALTYPE[sRealType]['누적거래량'])
            h = abs(int(h))

            i = self.dynamicCall("GetCommRealDate(QString, int)", sCode, self.realType.REALTYPE[sRealType]['고가'])
            i = abs(int(i))

            j = self.dynamicCall("GetCommRealDate(QString, int)", sCode, self.realType.REALTYPE[sRealType]['시가'])
            j = abs(int(j))

            k = self.dynamicCall("GetCommRealDate(QString, int)", sCode, self.realType.REALTYPE[sRealType]['현재가'])
            k = abs(int(k))

            if sCode not in self.portfolio_stock_dict:
                self.portfolio_stock_dict.update({sCode:{}})

            self.portfolio_stock_dict[sCode].update({"체결시간": a})
            self.portfolio_stock_dict[sCode].update({"현재가": b})
            self.portfolio_stock_dict[sCode].update({"전일대비": c})
            self.portfolio_stock_dict[sCode].update({"등락율": d})
            self.portfolio_stock_dict[sCode].update({"(최우선)매도호가": e})
            self.portfolio_stock_dict[sCode].update({"(최우선)매수호가": f})
            self.portfolio_stock_dict[sCode].update({"거래량": g})
            self.portfolio_stock_dict[sCode].update({"누적거래량": h})
            self.portfolio_stock_dict[sCode].update({"고가": i})
            self.portfolio_stock_dict[sCode].update({"시가": j})
            self.portfolio_stock_dict[sCode].update({"저가": k})

            print(self.portfolio_stock_dict[sCode])

            # 매수 결정 조건문
            # 계좌잔고평가내역에 있고 (이전에 미리 매수한 종목) and 오늘 산거에서 없어야함
            if sCode in self.account_stock_dict.keys() and sCode not in self.jango_dict.key():
                print("%s %s" % ("신규 매도를 한다", sCode))

            # 오늘 산 잔고에 있을 경우
            elif sCode in self.jango_dict.keys():
                print("%s %s" % ("신규 매도를 한다2", sCode))

            # 등락율이 2.0% 이상이고 오늘 산 잔고에 없을 경우
            elif d > 2.0 and sCode not in self.jango_dict: #등락율
                print("%s %s" % ("신규매수를 한다", sCode))

            not_meme_list = list(self.not_account_stock_dict) # 새로운 주소 copy
            
            # 업데이트된 데이터가 늘어나면 에러나기 때문에 복사해서 사용
            for order_num in not_meme_list:
                code = self.not_account_stock_dict[order_num]["종목코드"]
                meme_price = self.not_account_stock_dict[order_num]["주문가격"]
                not_quantity = self.not_account_stock_dict[order_num]["미체결수량"]
                meme_gubun = self.not_account_stock_dict[order_num]["매도수구분"]
                
                # 매수일때, 미체결양이 0보다 크고, 현재가가 주문 넣은 것보다 커지면 취소
                if meme_gubun == "매수" and not_quantity > 0 and e > meme_price: # e=현재가
                    print("%s %s" % ("매수 취소한다", sCode))
                    
                # 미체결이 0일 경우
                elif not_quantity == 0:
                    del self.not_account_stock_dict[order_num]  # 모두 매수에 성공했을경우 리스트에서 삭제














