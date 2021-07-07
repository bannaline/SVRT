import sys
import os
from PyQt5.QtWidgets import QMainWindow, QApplication, QTableWidgetItem, qApp, QMessageBox
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QObject, QThread
import sqlite3
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc, style
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import pandas as pd
from datetime import datetime
from data_manage import load_data, all_data, cp_list, d_check, ccp_check, write_record
from sub1 import Sub
from pyautogui import locate
import threading
import win32gui
import win32ui
from ctypes import windll
from PIL import Image
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from logger import logger
from main_window_ts1 import Ui_MainWindow
import configparser

# form_class = uic.loadUiType("./main_window.ui")[0]
form_class = Ui_MainWindow


class Form(QMainWindow, form_class):
    def __init__(self):
        logger.info("초기화시작")
        super(Form, self).__init__()
        self.setupUi(self)

        self.trans = QtCore.QTranslator(self)
        self.retranslateUi(self)

        # CpDl 버튼
        self.actionCpDl.triggered.connect(self.cpdl)

        # Exit 버튼
        self.actionExit.triggered.connect(qApp.quit)

        # 언어 버튼
        self.actionKorean.triggered.connect(lambda: self.retrans_code("ko_KR"))
        self.actionEnglish.triggered.connect(lambda: self.retrans_code("en_US"))
        self.actionJapanese.triggered.connect(lambda: self.retrans_code("ja_JP"))

        # 로캘 초기화
        config = configparser.ConfigParser()
        config.read("config.ini")
        loc = config["locale"]["locale"]
        if loc == "None":
            import locale
            loc = locale.getdefaultlocale()[0]
        if loc == "ko_KR" or loc == "ja_JP":
            pass
        else:
            loc = "en_US"
        self.loc = loc
        self.retrans_code(loc)

        # 날짜 위젯 현재 날짜로 초기화
        self.dateEdit.setDate(datetime.today())
        self.dateDeckStart.setDate(datetime.today())
        self.dateDeckEnd.setDate(datetime.today())
        self.dateDeckRStart.setDate(datetime.today())
        self.dateDeckREnd.setDate(datetime.today())

        # 초기 등록, 삭제 버튼 사용불가
        self.pushRegister.setEnabled(False)

        # 초기 승패 버튼 사용불가
        self.radioWin.setEnabled(False)
        self.radioLose.setEnabled(False)

        # 모드 버튼
        self.radioRecRota.clicked.connect(self.rad_mod)
        self.radioRecUnli.clicked.connect(self.rad_mod)

        # 선후공 버튼
        self.radioFirst.clicked.connect(self.rad_fs)
        self.radioSecond.clicked.connect(self.rad_fs)

        # 승패 버튼
        self.radioWin.clicked.connect(self.rad_wl)
        self.radioLose.clicked.connect(self.rad_wl)

        # 날짜 버튼
        self.dateEdit.dateChanged.connect(self.date_update)

        # 카드팩 버튼
        ccp = ccp_check()
        self.ccp = self.logcp = ccp
        if len(ccp) == 4:
            self.checkmini.setCheckState(2)
        else:
            self.checkmini.setCheckState(0)
        cpl = cp_list()
        cp = ccp[:3]
        self.comboCPlist.addItems(cpl)
        self.comboCPlist.setCurrentText(cp)

        # 내 직업 버튼
        self.radioRoyalMy.clicked.connect(self.radio_myjob)
        self.radioWitchMy.clicked.connect(self.radio_myjob)
        self.radioElfMy.clicked.connect(self.radio_myjob)
        self.radioBishopMy.clicked.connect(self.radio_myjob)
        self.radioDragonMy.clicked.connect(self.radio_myjob)
        self.radioNecroMy.clicked.connect(self.radio_myjob)
        self.radioVampMy.clicked.connect(self.radio_myjob)
        self.radioNemeMy.clicked.connect(self.radio_myjob)

        # 내 아키타입 버튼
        self.comboArcheMy.currentIndexChanged.connect(self.cb_my_arche)

        # 상대 직업 버튼
        self.radioRoyalOppo.clicked.connect(self.radio_oppojob)
        self.radioWitchOppo.clicked.connect(self.radio_oppojob)
        self.radioElfOppo.clicked.connect(self.radio_oppojob)
        self.radioBishopOppo.clicked.connect(self.radio_oppojob)
        self.radioDragonOppo.clicked.connect(self.radio_oppojob)
        self.radioNecroOppo.clicked.connect(self.radio_oppojob)
        self.radioVampOppo.clicked.connect(self.radio_oppojob)
        self.radioNemeOppo.clicked.connect(self.radio_oppojob)

        # 상대 아키타입 버튼
        self.comboArcheOppo.currentIndexChanged.connect(self.cb_oppo_arche)

        # 턴 버튼
        self.comboTurn.clear()
        turn_list = list(map(str, list(range(1, 41))))
        self.comboTurn.addItems(turn_list)
        self.comboTurn.currentIndexChanged.connect(self.cb_turn)

        # 등록 버튼
        self.pushRegister.clicked.connect(self.write_btn)

        # 수정 버튼
        self.pushModify.clicked.connect(self.modify_data)

        # 삭제 버튼
        self.pushErase.clicked.connect(self.erase_data)

        # 초기화 버튼
        self.pushInitailize.clicked.connect(self.init_data)

        # 전적 기간 버튼
        self.radioRecordAll.clicked.connect(self.table_rate)
        self.radioRecordNow.setText(ccp_check())
        self.radioRecordNow.clicked.connect(self.table_rate)
        self.radioToday.clicked.connect(self.table_rate)
        self.tablerate.setSpan(0, 0, 1, 4)
        self.tablerate.setSpan(0, 4, 1, 4)
        self.tablerate.setSpan(0, 8, 1, 4)

        # 초기 덱별 승률 탭 버튼 사용불가
        self.radioDeckAll.setEnabled(False)
        self.radioDeckPeriod.setEnabled(False)
        self.radioDeckCP.setEnabled(False)
        self.checkdmini.setEnabled(False)
        self.radioDeckRate.setEnabled(False)
        self.radioDeckVS.setEnabled(False)

        # 초기 덱별 전적 탭 버튼 사용불가
        self.radioDeckRPeriod.setEnabled(False)
        self.radioDeckRCP.setEnabled(False)
        self.checkdrmini.setEnabled(False)
        self.pushRLoad.setEnabled(False)

        # 기록테이블 초기 폭 설정
        self.tableRecord.setColumnWidth(0, 80)
        self.tableRecord.setColumnWidth(1, 68)
        self.tableRecord.setColumnWidth(2, 90)
        self.tableRecord.setColumnWidth(3, 85)
        self.tableRecord.setColumnWidth(4, 120)
        self.tableRecord.setColumnWidth(5, 85)
        self.tableRecord.setColumnWidth(6, 120)
        self.tableRecord.setColumnWidth(7, 60)
        self.tableRecord.setColumnWidth(8, 40)
        self.tableRecord.setColumnWidth(9, 41)

        # 덱별 승률 모드 버튼
        self.radioDeckRota.clicked.connect(self.deckmodbtn)
        self.radioDeckUnli.clicked.connect(self.deckmodbtn)

        # 덱별 승률 기간 버튼
        self.radioDeckAll.clicked.connect(self.deckperiod)
        self.radioDeckPeriod.clicked.connect(self.deckperiod)
        self.radioDeckCP.clicked.connect(self.deckperiod)
        if len(ccp) == 4:
            self.checkdmini.setCheckState(2)
        else:
            self.checkdmini.setCheckState(0)
        self.combodcp.addItems(cpl)
        self.combodcp.setCurrentText(cp)
        self.combodcp.currentIndexChanged.connect(self.deckperiod)
        self.checkdmini.stateChanged.connect(self.deckperiod)

        # 덱별 승률 날짜 버튼
        self.dateDeckStart.dateChanged.connect(self.deckdateupdate)
        self.dateDeckEnd.dateChanged.connect(self.deckdateupdate)

        # 덱별 승률 정렬 버튼
        self.radioDeckVS.clicked.connect(self.sortdeck)
        self.radioDeckRate.clicked.connect(self.sortdeck)

        # 덱별 승률 스핀박스
        self.spinBox.valueChanged.connect(self.sortlimupdate)

        self.labels = [self.Deck1VSCount, self.Deck1First, self.Deck1Second, self.Deck1Turn,
                       self.Deck2VSCount, self.Deck2First, self.Deck2Second, self.Deck2Turn,
                       self.Deck3VSCount, self.Deck3First, self.Deck3Second, self.Deck3Turn,
                       self.Deck4VSCount, self.Deck4First, self.Deck4Second, self.Deck4Turn,
                       self.Deck5VSCount, self.Deck5First, self.Deck5Second, self.Deck5Turn,
                       self.Deck6VSCount, self.Deck6First, self.Deck6Second, self.Deck6Turn,
                       self.Deck7VSCount, self.Deck7First, self.Deck7Second, self.Deck7Turn,
                       self.Deck8VSCount, self.Deck8First, self.Deck8Second, self.Deck8Turn]

        for label in self.labels:
            label.setText("")

        self.deck_btns = [self.pushdeck1, self.pushdeck2, self.pushdeck3, self.pushdeck4,
                          self.pushdeck5, self.pushdeck6, self.pushdeck7, self.pushdeck8]
        for i in range(len(self.deck_btns)):
            self.deck_btns[i].setText("")
            self.deck_btns[i].setEnabled(False)
            self.deck_btns[i].clicked.connect(self.deck_static)

        # 덱별 전적 모드 버튼
        self.radioDeckRRota.clicked.connect(self.deckrmodbtn)
        self.radioDeckRUnli.clicked.connect(self.deckrmodbtn)

        # 덱별 전적 기간 버튼
        self.radioDeckRPeriod.clicked.connect(self.deckrperiod)
        self.radioDeckRCP.clicked.connect(self.deckrperiod)
        if len(ccp) == 4:
            self.checkdrmini.setCheckState(2)
        else:
            self.checkdrmini.setCheckState(0)
        self.combodrcp.addItems(cpl)
        self.combodrcp.setCurrentText(cp)
        self.combodrcp.currentIndexChanged.connect(self.deckrperiod)
        self.checkdrmini.clicked.connect(self.deckrperiod)

        # 덱별 전적 날짜 버튼
        self.dateDeckRStart.dateChanged.connect(self.deckr_date_update)
        self.dateDeckREnd.dateChanged.connect(self.deckr_date_update)

        # 덱별 전적 아키타입 버튼
        self.comboDeckR.currentIndexChanged.connect(self.cb_rec_arche)

        # 덱별 전적 로드 버튼
        self.pushRLoad.clicked.connect(self.deckrrecordupdate)

        # 덱별 전적 테이블 폭 설정
        self.tableDeckR1.setColumnWidth(0, 115)
        self.tableDeckR1.setColumnWidth(1, 50)
        self.tableDeckR1.setColumnWidth(2, 40)
        self.tableDeckR1.setColumnWidth(3, 40)
        self.tableDeckR1.setColumnWidth(4, 48)
        self.tableDeckR1.setColumnWidth(5, 48)
        self.tableDeckR1.setColumnWidth(6, 48)
        self.tableDeckR2.setColumnWidth(0, 115)
        self.tableDeckR2.setColumnWidth(1, 50)
        self.tableDeckR2.setColumnWidth(2, 40)
        self.tableDeckR2.setColumnWidth(3, 40)
        self.tableDeckR2.setColumnWidth(4, 48)
        self.tableDeckR2.setColumnWidth(5, 48)
        self.tableDeckR2.setColumnWidth(6, 48)

        # 그래프
        self.figure1 = plt.figure(1)
        self.canvas1 = FigureCanvas(self.figure1)
        self.DeckLayout1.addWidget(self.canvas1)
        self.figure2 = plt.figure(2)
        self.canvas2 = FigureCanvas(self.figure2)
        self.DeckRLayout1.addWidget(self.canvas2)
        fname = ""
        if self.loc == "ko_KR" or self.loc == "en_US":
            fname = "c:/Windows/Fonts/malgun.ttf"
        elif self.loc == "ja_JP":
            fname = "c:/Windows/Fonts/meiryo.ttc"
        self.font_name = font_manager.FontProperties(fname=fname).get_name()
        rc('font', family=self.font_name)
        font_manager.FontProperties().set_size('xx-small')
        style.use('ggplot')

        # 자동 기록 탭
        self.tabWidget.tabBarClicked.connect(self.status_check)
        self.status_list = [self.stelfr, self.stroyalr, self.stwitchr, self.stbishopr, self.stdragonr,
                            self.stnecror, self.stvampr, self.stnemer]
        self.status_list_u = [self.stelfu, self.stroyalu, self.stwitchu, self.stbishopu, self.stdragonu,
                              self.stnecrou, self.stvampu, self.stnemeu]
        self.pushrefresh.clicked.connect(self.status_refresh)

        if len(ccp) == 4:
            self.checkautomini.setCheckState(2)
        else:
            self.checkautomini.setCheckState(0)
        self.comboautocp.addItems(cpl)
        self.comboautocp.setCurrentText(cp)
        self.pushal.clicked.connect(self.autologstart)
        self.pushal.setEnabled(False)
        self.lb_alarm.setText('새로고침을 눌러 상태를 확인해주세요.')
        self.pushstop.setEnabled(False)
        self.pushstop.clicked.connect(self.stop)
        self.cb_mydeck.currentIndexChanged.connect(self.auto_mydeck)
        self.cb_opdeck.currentIndexChanged.connect(self.auto_opdeck)
        self.is_watchdog = False
        self.watch = Target()
        self.watch.modsignal.signal1.connect(self.signal_m)
        self.thread1 = Worker()
        self.thread1.not_found.connect(self.not_found)
        self.thread1.minimize.connect(self.minimized)
        self.thread1.req_resizing.connect(self.req_resize)
        self.thread1.auto_mod.connect(self.auto_mod)
        self.thread1.first.connect(self.auto_first)
        self.thread1.oppo_craft.connect(self.auto_oppo_craft)
        self.thread1.my_craft.connect(self.auto_my_craft)
        self.thread1.auto_preview.connect(self.auto_preview)
        self.thread1.auto_win.connect(self.auto_win)
        self.thread1.auto_result.connect(self.auto_result)
        self.timer1 = threading.Timer(1, self.alarm)

        logger.info("초기화끝")

        if os.path.isfile('log.db'):
            load_data(self, self.loc)
        else:
            self.init_data()
        self.table_rate()

        logger.info("테이블 불러오기 완료")

    fs = wl = logdate = myjob = myarche = oppojob = oppoarche = deckmod = deckstartdate = deckenddate = ""
    fscheck = wlcheck = deckmodcheck = deckrmodcheck = 0
    turn = 1
    sortlim = 10
    df = df2 = df3 = df5 = df6 = pd.DataFrame([])
    deckrmod = deckrstartdate = deckrenddate = deckrarche = ""
    al_work = modi = status = status_u = stat_c = retrans = in_match = False
    my_cls = my_cls_2 = oppo_cls = first = win = today = ""
    amod = amod_2 = atype = mydeck = mydeck_2 = opdeck = logtime = ""
    mycn = oppocn = aturn = img_size = current_size = 0
    log = []
    al_timer = 5
    cll = []
    icons = []
    posts = []
    miscs = []
    regions = []
    names = []
    win_style = "background-color:rgba(255,0,0,20)"
    lose_style = "background-color:rgba(0,0,255,20)"
    init_style = "background-color:rgba(0,0,0,0)"
    ok_style = "background-color:rgba(0,255,0,20)"

    # CpDl 버튼 이벤트
    def cpdl(self):
        self.cp_dl = Sub()
        self.cp_dl.show()

    def retrans_code(self, locale_code):
        config = configparser.ConfigParser()
        config.read("config.ini")
        if self.retrans or config["locale"]["locale"] == "None":
            QApplication.instance().removeTranslator(self.trans)
            config["locale"]["locale"] = locale_code
            with open('config.ini', 'w') as configfile:
                config.write(configfile)
        loc_path = "./locales/base_" + locale_code + ".qm"
        self.trans.load(loc_path)
        QApplication.instance().installTranslator(self.trans)
        self.retranslateUi(Form)
        self.retrans_text(locale_code)
        if self.retrans:
            QMessageBox.warning(self, self.msgs[6], self.msgs[10])
        self.retrans = True

    def retrans_text(self, locale_code):
        if locale_code == "ko_KR":
            self.mod = "로테이션"
            self.crafts = ["엘프", "로얄", "위치", "비숍", "드래곤", "네크로맨서", "뱀파이어", "네메시스"]
            self.mods = ["로테이션", "언리미티드"]
            self.win_lose = ["승", "패"]
            self.fir_sec = ["선공", "후공"]
            self.types = ["일반전", "랭킹전", "그랑프리", "기타", "친선전"]
            self.msgs = ["경고", "정말 기록을 초기화하겠습니까?", "기간 내 로테이션 전적", "기간 내 언리미티드 전적", "전적없음",
                         "전", "주의", "창을 찾을 수 없어 자동기록이 중지되었습니다.", "창이 최소화되어 자동기록이 중지되었습니다.",
                         "해상도 조정 필요. (가로해상도: 1280, 1600, 1920)", "안정성을 위해 프로그램을 재시작해주십시오."]
            self.lb_msgs = ["턴 정보 없음", "평균", "턴", "개", "기록을 시작하려면 시작 버튼을 누르세요.",
                            "메뉴로 들어가 덱을 확인해주세요.", "데이터 수집 중", "기타", " ※ {} 외는 저장되지 않습니다.",
                            "{}초 후 기록을 자동으로 저장합니다.", "기록 중지", "{}은 기록되지 않습니다. {}초 후 데이터 수집을 재개"]
        elif locale_code == "ja_JP":
            self.mod = "ローテーション"
            self.crafts = ["エルフ", "ロイヤル", "ウィッチ", "ビショップ", "ドラゴン", "ネクロマンサー", "ヴァンパイア", "ネメシス"]
            self.mods = ["ローテーション", "アンリミテッド"]
            self.win_lose = ["勝", "敗"]
            self.fir_sec = ["先攻", "後攻"]
            self.types = ["フリーマッチ", "ランクマッチ", "グランプリ", "その他", "ルームマッチ"]
            self.msgs = ["警告", "本当に記録を初期化しますか？", "期間内ローテーションのレコード", "期間内アンリミテッドのレコード",
                         "記録なし", "試合", "注意", "ウィンドウを見つけることができないため、自動記録が停止されました。",
                         "ウィンドウが最小化されて、自動記録が停止されました。", "解像度の調整が必要です。 (横解像度: 1280, 1600, 1920)",
                         "安定性のためのプログラムを再起動してください。"]
            self.lb_msgs = ["ターン情報なし", "平均", "ターン", "個", "記録を開始するには、スタートボタンを押してください。",
                            "メニューに入りデッキを確認してください。", "データ収集中", "その他",
                            " ※ {}以外は保存されません。", "{}秒後に記録を自動的に保存します。", "記録停止",
                            "{}は記録されません。{}秒後にデータ収集を再開"]
        else:
            self.mod = "Rotation"
            self.crafts = ["Forest", "Sword", "Rune", "Haven", "Dragon", "Shadow", "Blood", "Portal"]
            self.mods = ["Rotation", "Unlimited"]
            self.win_lose = ["Win", "Lose"]
            self.fir_sec = ["1st", "2nd"]
            self.types = ["FreeMatch", "RankMatch", "Colosseum", "Others", "RoomMatch"]
            self.msgs = ["Alert", "Are you sure you want to reset the records?", "Rotation records in the period",
                         "Unlimited records in the period", "No record", "Match", "Warning",
                         "Autologging has stopped because the window could not be found.",
                         "Autologging has stopped because the window was minimized.",
                         "Need to adjust resolution. (horizontal resolution: 1280, 1600, 1920)",
                         "Please restart the program for stability."]
            self.lb_msgs = ["No information", "Average", "Turn", "Decks", "Press the Start button to start recording.",
                            "Please go to the menu and check your deck.", "Collecting data", "Others",
                            " ※ Anything other than {} is not saved.",
                            "Automatically save the recording after {} seconds.", "Stop recording",
                            "{} is not recorded. Restart data collection after {} seconds"]
        self.loc = locale_code

    # 모드 버튼 이벤트
    def rad_mod(self):
        if self.radioRecRota.isChecked():
            self.mod = self.mods[0]
        elif self.radioRecUnli.isChecked():
            self.mod = self.mods[1]
        self.radio_myjob()
        self.radio_oppojob()

    # 선후공 버튼 이벤트
    def rad_fs(self):
        if self.radioFirst.isChecked():
            self.fs = self.fir_sec[0]
        elif self.radioSecond.isChecked():
            self.fs = self.fir_sec[1]
        if self.fscheck == 0:
            self.radioWin.setEnabled(True)
            self.radioLose.setEnabled(True)
            self.fscheck = 1

    # 승패 버튼 이벤트
    def rad_wl(self):
        if self.radioWin.isChecked():
            self.wl = self.win_lose[0]
        elif self.radioLose.isChecked():
            self.wl = self.win_lose[1]
        if self.wlcheck == 0:
            self.pushRegister.setEnabled(True)
            self.wlcheck = 1

    # 날짜 버튼 이벤트
    def date_update(self):
        temp_date = self.dateEdit.date()
        self.logdate = temp_date.toPyDate()

    # 카드팩 버튼 이벤트
    def rad_rec_cp(self):
        logcp = self.comboCPlist.currentText()
        if self.checkmini.isChecked():
            logcp = logcp + 'm'
        self.logcp = logcp

    # 내 직업
    def radio_myjob(self):
        if self.radioElfMy.isChecked():
            myjob = self.crafts[0]
        elif self.radioRoyalMy.isChecked():
            myjob = self.crafts[1]
        elif self.radioWitchMy.isChecked():
            myjob = self.crafts[2]
        elif self.radioBishopMy.isChecked():
            myjob = self.crafts[3]
        elif self.radioDragonMy.isChecked():
            myjob = self.crafts[4]
        elif self.radioNecroMy.isChecked():
            myjob = self.crafts[5]
        elif self.radioVampMy.isChecked():
            myjob = self.crafts[6]
        elif self.radioNemeMy.isChecked():
            myjob = self.crafts[7]
        else:
            return

        self.myjob = myjob
        archelist = d_check(self.mod, self.logcp, myjob)

        self.comboArcheMy.clear()
        self.comboArcheMy.addItems(archelist)
        self.cb_my_arche()

    # 내 아키타입
    def cb_my_arche(self):
        self.myarche = self.comboArcheMy.currentText()

    # 상대 직업
    def radio_oppojob(self):
        if self.radioElfOppo.isChecked():
            oppojob = self.crafts[0]
        elif self.radioRoyalOppo.isChecked():
            oppojob = self.crafts[1]
        elif self.radioWitchOppo.isChecked():
            oppojob = self.crafts[2]
        elif self.radioBishopOppo.isChecked():
            oppojob = self.crafts[3]
        elif self.radioDragonOppo.isChecked():
            oppojob = self.crafts[4]
        elif self.radioNecroOppo.isChecked():
            oppojob = self.crafts[5]
        elif self.radioVampOppo.isChecked():
            oppojob = self.crafts[6]
        elif self.radioNemeOppo.isChecked():
            oppojob = self.crafts[7]
        else:
            return

        self.oppojob = oppojob
        archelist = d_check(self.mod, self.logcp, oppojob)

        self.comboArcheOppo.clear()
        self.comboArcheOppo.addItems(archelist)
        self.cb_oppo_arche()

    # 상대 아키타입
    def cb_oppo_arche(self):
        self.oppoarche = self.comboArcheOppo.currentText()

    # 종료 턴
    def cb_turn(self):
        self.turn = int(self.comboTurn.currentText())

    # 등록 버튼 / 아키타입 한번 더 로드할것!
    def write_btn(self):
        write_record(self, self.logcp, self.mod, self.myjob, self.myarche,
                     self.oppojob, self.oppoarche, self.fs, self.wl, self.types[1], self.turn)
        load_data(self, self.loc)
        self.table_rate()

    # 데이터 삭제 - 최신 1개만
    def erase_data(self):
        conn = sqlite3.connect('log.db')
        cursor = conn.cursor()
        if not self.modi:
            result = cursor.execute("SELECT LogTime FROM log ORDER BY LogTime DESC LIMIT 1")
            edata = result.fetchall()
            cursor.execute("DELETE FROM log WHERE LogTime=?", edata[0])
        elif self.modi:
            result = cursor.execute("SELECT LogTime FROM log ORDER BY LogTime DESC LIMIT 2")
            edata = result.fetchall()
            cursor.execute("DELETE FROM log WHERE LogTime=?", edata[1])
        conn.commit()
        conn.close()
        load_data(self, self.loc)
        self.table_rate()

    # 데이터 수정
    def modify_data(self):
        self.write_btn()
        self.modi = True
        self.erase_data()
        self.modi = False

    # 초기화
    def init_data(self):
        if os.path.isfile('log.db'):
            msgbox = QMessageBox
            ret = msgbox.question(self, self.msgs[0], self.msgs[1])
            if ret == QMessageBox.Yes:
                os.remove('log.db')
            elif ret == QMessageBox.No:
                return
        conn = sqlite3.connect('log.db')
        cur = conn.cursor()
        cur.execute(
            "CREATE TABLE log(Date text, CardPack text, Mod TEXT, MyJob text, MyArche text, OppoJob text, OppoArche text, FirstSecond text, WinLose text, LogTime TEXT, Type text, Turn int)")
        conn.commit()
        conn.close()
        self.tableRecord.setRowCount(0)

    def table_rate(self):
        df = all_data()
        today = datetime.today().strftime("%Y-%m-%d")
        if self.radioRecordAll.isChecked():
            pass
        elif self.radioRecordNow.isChecked():
            cp = ccp_check()
            df = df[df['CardPack'].isin([cp])]
        elif self.radioToday.isChecked():
            df = df[df['Date'].isin([today])]
        df1 = df[df['Mod'].isin([self.mods[0]])]
        vscount = len(df1)
        rota = []
        if vscount == 0:
            rota = ['', '', '', '', '', '', '', '', '', '', '', '']
        else:
            rota.append(str(vscount))
            win = df1[df1['WinLose'].isin([self.win_lose[0]])]
            rota.append(str(len(win)))
            lose = df1[df1['WinLose'].isin([self.win_lose[1]])]
            rota.append(str(len(lose)))
            wr = round(len(win) / vscount * 100, 1)
            wr = str(wr) + '%'
            rota.append(wr)
            first = df1[df1['FirstSecond'].isin([self.fir_sec[0]])]
            if len(first) == 0:
                rota.extend(['N/A', 'N/A', 'N/A', 'N/A'])
            else:
                rota.append(str(len(first)))
                fwin = first[first['WinLose'].isin([self.win_lose[0]])]
                rota.append(str(len(fwin)))
                flose = first[first['WinLose'].isin([self.win_lose[1]])]
                rota.append(str(len(flose)))
                fwr = round(len(fwin) / len(first) * 100, 1)
                fwr = str(fwr) + '%'
                rota.append(fwr)
            second = df1[df1['FirstSecond'].isin([self.fir_sec[1]])]
            if len(second) == 0:
                rota.extend(['N/A', 'N/A', 'N/A', 'N/A'])
            else:
                rota.append(str(len(second)))
                swin = second[second['WinLose'].isin([self.win_lose[0]])]
                rota.append(str(len(swin)))
                slose = second[second['WinLose'].isin([self.win_lose[1]])]
                rota.append(str(len(slose)))
                swr = round(len(swin) / len(second) * 100, 1)
                swr = str(swr) + '%'
                rota.append(swr)
        df1 = df[df['Mod'].isin([self.mods[1]])]
        vscount = len(df1)
        unli = []
        if vscount == 0:
            unli = ['', '', '', '', '', '', '', '', '', '', '', '']
        else:
            unli.append(str(vscount))
            win = df1[df1['WinLose'].isin([self.win_lose[0]])]
            unli.append(str(len(win)))
            lose = df1[df1['WinLose'].isin([self.win_lose[1]])]
            unli.append(str(len(lose)))
            wr = round(len(win) / vscount * 100, 1)
            wr = str(wr) + '%'
            unli.append(wr)
            first = df1[df1['FirstSecond'].isin([self.fir_sec[0]])]
            if len(first) == 0:
                unli.extend(['N/A', 'N/A', 'N/A', 'N/A'])
            else:
                unli.append(str(len(first)))
                fwin = first[first['WinLose'].isin([self.win_lose[0]])]
                unli.append(str(len(fwin)))
                flose = first[first['WinLose'].isin([self.win_lose[1]])]
                unli.append(str(len(flose)))
                fwr = round(len(fwin) / len(first) * 100, 1)
                fwr = str(fwr) + '%'
                unli.append(fwr)
            second = df1[df1['FirstSecond'].isin([self.fir_sec[1]])]
            if len(second) == 0:
                unli.extend(['N/A', 'N/A', 'N/A', 'N/A'])
            else:
                unli.append(str(len(second)))
                swin = second[second['WinLose'].isin([self.win_lose[0]])]
                unli.append(str(len(swin)))
                slose = second[second['WinLose'].isin([self.win_lose[1]])]
                unli.append(str(len(slose)))
                swr = round(len(swin) / len(second) * 100, 1)
                swr = str(swr) + '%'
                unli.append(swr)

        j = 0
        for data in rota:
            item = QTableWidgetItem()
            item.setText(str(data))
            item.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
            self.tablerate.setItem(2, j, item)
            j = j + 1
        j = 0
        for data in unli:
            item = QTableWidgetItem()
            item.setText(str(data))
            item.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
            self.tablerate.setItem(3, j, item)
            j = j + 1

    # 모드버튼 in 덱별 승률
    def deckmodbtn(self):
        if self.radioDeckRota.isChecked():
            self.deckmod = self.mods[0]
            self.groupDeckRecord.setTitle(self.msgs[2])
        elif self.radioDeckUnli.isChecked():
            self.deckmod = self.mods[1]
            self.groupDeckRecord.setTitle(self.msgs[3])
        if self.deckmodcheck == 0:
            self.radioDeckAll.setEnabled(True)
            self.radioDeckPeriod.setEnabled(True)
            self.radioDeckCP.setEnabled(True)
            self.checkdmini.setEnabled(True)
            self.radioDeckRate.setEnabled(True)
            self.radioDeckVS.setEnabled(True)
            self.deckmodcheck = 1
        self.deckperiod()

    # 기간버튼 in 덱별 승률
    def deckperiod(self):
        df1 = all_data()
        df2 = df1
        df3 = df1
        if self.radioDeckAll.isChecked():
            df2 = df1
        elif self.radioDeckPeriod.isChecked():
            self.deckdateupdate()
            df2 = df1[(df1['Date'] >= self.deckstartdate) & (df1['Date'] <= self.deckenddate)]
        elif self.radioDeckCP.isChecked():
            cp = self.combodcp.currentText()
            if self.checkdmini.isChecked():
                cp = cp + 'm'
            df2 = df1[df1['CardPack'].isin([cp])]
        if self.deckmod == self.mods[0]:
            df3 = df2[df2['Mod'].isin([self.mods[0]])]
        elif self.deckmod == self.mods[1]:
            df3 = df2[df2['Mod'].isin([self.mods[1]])]
        self.df2 = df3
        self.deckrecordupdate()
        df4 = df3.drop_duplicates(['MyArche'])
        lists = list(set(df4['MyArche']))
        rec = {}

        for deck in lists:
            record = []
            vs = df3[df3['MyArche'].isin([deck])]
            win = vs[vs['WinLose'].isin([self.win_lose[0]])]
            lose = vs[vs['WinLose'].isin([self.win_lose[1]])]
            record.append(len(vs))
            record.append(len(win))
            record.append(len(lose))
            record.append(round(len(win) * 100 / len(vs), 1))
            rec[deck] = record
        self.df3 = pd.DataFrame.from_dict(rec, orient='index', columns=['VS', 'Win', 'Lose', 'WinRate'])
        self.sortdeck()

    def deckrecordupdate(self):
        df = self.df2
        if len(df) == 0:
            self.DeckVS.setText(self.msgs[4])
            self.DeckWin.setText('N/A')
            self.DeckLose.setText('N/A')
            self.DeckWinRate.setText('N/A')
            return
        win = df[df['WinLose'].isin([self.win_lose[0]])]
        lose = df[df['WinLose'].isin([self.win_lose[1]])]
        winrate = str(round(len(win) * 100 / len(df), 1)) + '%'
        self.DeckVS.setText(str(len(df)))
        self.DeckWin.setText(str(len(win)))
        self.DeckLose.setText(str(len(lose)))
        self.DeckWinRate.setText(winrate)

    def sortlimupdate(self):
        self.sortlim = self.spinBox.value()

    # 날짜변경 in 덱별 승률
    def deckdateupdate(self):
        temp_date = self.dateDeckStart.date()
        self.deckstartdate = str(temp_date.toPyDate())
        temp_date1 = self.dateDeckEnd.date()
        self.deckenddate = str(temp_date1.toPyDate())

    def sortdeck(self):
        df = ''
        if self.radioDeckRate.isChecked():
            df = self.df3.sort_values(['WinRate'], ascending=[False])
            df = df.loc[df['VS'] >= self.sortlim, :]
        elif self.radioDeckVS.isChecked():
            df = self.df3.sort_values(['VS'], ascending=[False])
        self.figure1.clear()
        self.deck(df)
        self.figure1.tight_layout()
        self.canvas1.draw()
        self.figure1.clear()

    def deck(self, df):
        spl = range(241, 249)
        self.names = []
        for k in range(len(df)):
            self.names.append(df.index[k])
        for i in range(8):
            if len(df) > i:
                name = self.names[i]
                vs = str(df.iloc[i, 0]) + self.msgs[5] + ' ' + str(df.iloc[i, 1]) + self.win_lose[0] + ' ' + str(
                    df.iloc[i, 2]) + self.win_lose[1]
                self.labels[i * 4].setText(vs)
                colors = ['red', 'lightskyblue']
                labels = [self.win_lose[0], self.win_lose[1]]
                ratio = [df.iloc[i, 1], df.iloc[i, 2]]
                d1 = self.figure1.add_subplot(spl[i])
                d1.pie(ratio, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
                d1.set_title(name, fontdict={'fontsize': 11}, pad=40)
                df1 = self.df2
                df1 = df1[df1['MyArche'].isin([name])]
                first = df1[df1['FirstSecond'].isin([self.fir_sec[0]])]
                firstwin = first[first['WinLose'].isin([self.win_lose[0]])]
                second = df1[df1['FirstSecond'].isin([self.fir_sec[1]])]
                secondwin = second[second['WinLose'].isin([self.win_lose[0]])]
                turn = round(df1['Turn'].mean(skipna=True), 2)
                if len(first) == 0:
                    self.labels[i * 4 + 1].setText('N/A')
                else:
                    wr1st = self.fir_sec[0] + ' ' + str(round(len(firstwin) * 100 / len(first), 1)) + '%'
                    self.labels[i * 4 + 1].setText(wr1st)
                if len(second) == 0:
                    self.labels[i * 4 + 2].setText('N/A')
                else:
                    wr2nd = self.fir_sec[1] + ' ' + str(round(len(secondwin) * 100 / len(second), 1)) + '%'
                    self.labels[i * 4 + 2].setText(wr2nd)
                if str(type(turn)) == "<class 'float'>":
                    self.labels[i * 4 + 3].setText(self.lb_msgs[0])
                else:
                    self.labels[i * 4 + 3].setText(self.lb_msgs[1] + ' ' + str(turn) + self.lb_msgs[2])
                self.deck_btns[i].setEnabled(True)
            else:
                self.labels[i * 4].setText('')
                self.labels[i * 4 + 1].setText('')
                self.labels[i * 4 + 2].setText('')
                self.labels[i * 4 + 3].setText('')
                self.deck_btns[i].setEnabled(False)

    # 덱 상세
    def deck_static(self):
        from statics import Static
        self.static = Static()
        self.static.my_deck = self.names[self.deck_btns.index(self.sender())]
        self.static.my_deck_lists = self.names
        self.static.df = self.df2
        self.static.my_deck_init()
        self.static.show()

    # 모드 버튼 in 덱별 전적
    def deckrmodbtn(self):
        if self.radioDeckRRota.isChecked():
            self.deckrmod = self.mods[0]
        elif self.radioDeckRUnli.isChecked():
            self.deckrmod = self.mods[1]
        if self.deckrmodcheck == 0:
            self.radioDeckRPeriod.setEnabled(True)
            self.radioDeckRCP.setEnabled(True)
            self.checkdrmini.setEnabled(True)
            self.pushRLoad.setEnabled(True)
            self.deckrmodcheck = 1
        self.deckrperiod()

    # 기간버튼 in 직업별
    def deckrperiod(self):
        df1 = all_data()
        df2 = df1
        df3 = df1
        if self.radioDeckRPeriod.isChecked():
            self.deckr_date_update()
            df2 = df1[(df1['Date'] >= self.deckrstartdate) & (df1['Date'] <= self.deckrenddate)]
        elif self.radioDeckRCP.isChecked():
            cp = self.combodrcp.currentText()
            if self.checkdrmini.isChecked():
                cp = cp + 'm'
            df2 = df1[df1['CardPack'].isin([cp])]
        if self.deckrmod == self.mods[0]:
            df3 = df2[df2['Mod'].isin([self.mods[0]])]
        elif self.deckrmod == self.mods[1]:
            df3 = df2[df2['Mod'].isin([self.mods[1]])]
        self.df5 = df3
        df4 = df3.drop_duplicates(['MyArche'])
        lists = list(set(df4['MyArche']))
        lt = [[x, x[-2:]] for x in lists]
        lt.sort(key=lambda deck: deck[1])
        lists = [x[0] for x in lt]
        self.comboDeckR.clear()
        self.comboDeckR.addItems(lists)
        self.cb_rec_arche()

    # 날짜변경 in 덱별 전적
    def deckr_date_update(self):
        temp_date = self.dateDeckRStart.date()
        self.deckrstartdate = str(temp_date.toPyDate())
        temp_date1 = self.dateDeckREnd.date()
        self.deckrenddate = str(temp_date1.toPyDate())

    # 덱별 전적 아키타입
    def cb_rec_arche(self):
        self.deckrarche = self.comboDeckR.currentText()
        self.DeckRVS.setText(self.msgs[4])
        self.DeckRWin.setText('N/A')
        self.DeckRLose.setText('N/A')
        self.DeckRWinRate.setText('N/A')
        self.tableDeckR1.setRowCount(0)
        self.tableDeckR2.setRowCount(0)
        self.figure2.clear()
        self.canvas2.draw()

    def deckrrecordupdate(self):
        df = self.df5
        df = df[df['MyArche'].isin([self.deckrarche])]
        self.df6 = df
        if len(df) == 0:
            self.DeckVS.setText(self.msgs[4])
            self.DeckWin.setText('N/A')
            self.DeckLose.setText('N/A')
            self.DeckWinRate.setText('N/A')
            return
        win = df[df['WinLose'].isin([self.win_lose[0]])]
        lose = df[df['WinLose'].isin([self.win_lose[1]])]
        winrate = str(round(len(win) * 100 / len(df), 1)) + '%'
        self.DeckRVS.setText(str(len(df)))
        self.DeckRWin.setText(str(len(win)))
        self.DeckRLose.setText(str(len(lose)))
        self.DeckRWinRate.setText(winrate)
        self.recload()

    def recload(self):
        self.tableDeckR1.setRowCount(0)
        self.tableDeckR2.setRowCount(0)
        self.fsgraph()
        self.deckr1()
        self.deckr2()

    # 선후공 승률 막대 그래프 in 덱별 전적
    def fsgraph(self):
        df = self.df6
        df1 = df[df['FirstSecond'].isin([self.fir_sec[0]])]
        df1_1 = df1[df1['WinLose'].isin([self.win_lose[0]])]
        df2 = df[df['FirstSecond'].isin([self.fir_sec[1]])]
        df2_1 = df2[df2['WinLose'].isin([self.win_lose[0]])]
        if len(df1) == 0:
            fwin = 0
        else:
            fwin = round(len(df1_1) * 100 / len(df1), 1)
        if len(df2) == 0:
            swin = 0
        else:
            swin = round(len(df2_1) * 100 / len(df2), 1)
        self.figure2.clear()
        ax = self.figure2.add_subplot(111)
        rects1 = ax.barh(2, fwin, align='center', color='lightskyblue', height=0.5, label=self.fir_sec[0])
        rects2 = ax.barh(1, swin, align='center', color='xkcd:pistachio', height=0.5, label=self.fir_sec[1])
        ax.set_xlim([0, 100])
        ax.set_yticks([])
        if fwin >= 40:
            for i, rect in enumerate(rects1):
                ax.text(0.95 * rect.get_width(), rect.get_y() + rect.get_height() / 2.0, str(fwin) + '%',
                        ha='right', va='center')
        else:
            for i, rect in enumerate(rects1):
                ax.text(rect.get_width() + 2, rect.get_y() + rect.get_height() / 2.0, str(fwin) + '%',
                        ha='left', va='center')
        if swin >= 40:
            for i, rect in enumerate(rects2):
                ax.text(0.95 * rect.get_width(), rect.get_y() + rect.get_height() / 2.0, str(swin) + '%',
                        ha='right', va='center')
        else:
            for i, rect in enumerate(rects2):
                ax.text(rect.get_width() + 2, rect.get_y() + rect.get_height() / 2.0, str(swin) + '%',
                        ha='left', va='center')
        self.canvas2.draw()
        self.figure2.clear()

    def deckr1(self):
        cls = self.crafts[:4]
        # 직업별 색상 [메인RGB, 서브RGB]
        cls_cl = {cls[0]: [207, 247, 99, 176, 239, 12], cls[1]: [253, 251, 140, 197, 191, 3],
                  cls[2]: [158, 168, 240, 92, 109, 231], cls[3]: [255, 255, 255, 190, 190, 190]}
        for i in range(4):
            df = self.df6
            df1 = df[df['OppoJob'].isin([cls[i]])]
            vsc = len(df1)
            if vsc == 0:
                rec = ['VS ' + cls[i], '0', '0', '0', 'N/A', 'N/A', 'N/A']
            else:
                win = len(df1[df1['WinLose'].isin([self.win_lose[0]])])
                lose = len(df1[df1['WinLose'].isin([self.win_lose[1]])])
                winrate = str(round(win * 100 / vsc, 1)) + '%'
                df2 = df1[df1['FirstSecond'].isin([self.fir_sec[0]])]
                df2_1 = df2[df2['WinLose'].isin([self.win_lose[0]])]
                df3 = df1[df1['FirstSecond'].isin([self.fir_sec[1]])]
                df3_1 = df3[df3['WinLose'].isin([self.win_lose[0]])]
                if len(df2) == 0:
                    fwin = 'N/A'
                else:
                    fwin = str(round(len(df2_1) * 100 / len(df2), 1)) + '%'
                if len(df3) == 0:
                    swin = 'N/A'
                else:
                    swin = str(round(len(df3_1) * 100 / len(df3), 1)) + '%'
                rec = ['VS ' + cls[i], str(vsc), str(win), str(lose), winrate, fwin, swin]
            rowcount = self.tableDeckR1.rowCount()
            self.tableDeckR1.insertRow(rowcount)
            for j, text in enumerate(rec):
                item = QTableWidgetItem()
                item.setText(text)
                item.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
                item.setBackground(QtGui.QColor(cls_cl[cls[i]][0], cls_cl[cls[i]][1], cls_cl[cls[i]][2]))
                self.tableDeckR1.setItem(rowcount, j, item)
            if vsc == 0:
                pass
            else:
                df4 = df1.drop_duplicates(['OppoArche'])
                lists = list(set(df4['OppoArche']))
                for arche in lists:
                    df1 = df[df['OppoArche'].isin([arche])]
                    vsc = len(df1)
                    win = len(df1[df1['WinLose'].isin([self.win_lose[0]])])
                    lose = len(df1[df1['WinLose'].isin([self.win_lose[1]])])
                    winrate = str(round(win * 100 / vsc, 1)) + '%'
                    df2 = df1[df1['FirstSecond'].isin([self.fir_sec[0]])]
                    df2_1 = df2[df2['WinLose'].isin([self.win_lose[0]])]
                    df3 = df1[df1['FirstSecond'].isin([self.fir_sec[1]])]
                    df3_1 = df3[df3['WinLose'].isin([self.win_lose[0]])]
                    if len(df2) == 0:
                        fwin = 'N/A'
                    else:
                        fwin = str(round(len(df2_1) * 100 / len(df2), 1)) + '%'
                    if len(df3) == 0:
                        swin = 'N/A'
                    else:
                        swin = str(round(len(df3_1) * 100 / len(df3), 1)) + '%'
                    rec = [arche, str(vsc), str(win), str(lose), winrate, fwin, swin]
                    rowcount = self.tableDeckR1.rowCount()
                    self.tableDeckR1.insertRow(rowcount)
                    for j, text in enumerate(rec):
                        item = QTableWidgetItem()
                        item.setText(text)
                        item.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
                        item.setBackground(QtGui.QColor(cls_cl[cls[i]][3], cls_cl[cls[i]][4], cls_cl[cls[i]][5]))
                        self.tableDeckR1.setItem(rowcount, j, item)

    def deckr2(self):
        cls = self.crafts[4:]
        # 직업별 색상 [메인RGB, 서브RGB]
        cls_cl = {cls[0]: [255, 232, 99, 249, 211, 0], cls[1]: [242, 178, 255, 226, 89, 255],
                  cls[2]: [255, 125, 177, 255, 40, 126], cls[3]: [215, 255, 255, 155, 255, 255]}
        for i in range(4):
            df = self.df6
            df1 = df[df['OppoJob'].isin([cls[i]])]
            vsc = len(df1)
            if vsc == 0:
                rec = ['VS ' + cls[i], '0', '0', '0', 'N/A', 'N/A', 'N/A']
            else:
                win = len(df1[df1['WinLose'].isin([self.win_lose[0]])])
                lose = len(df1[df1['WinLose'].isin([self.win_lose[1]])])
                winrate = str(round(win * 100 / vsc, 1)) + '%'
                df2 = df1[df1['FirstSecond'].isin([self.fir_sec[0]])]
                df2_1 = df2[df2['WinLose'].isin([self.win_lose[0]])]
                df3 = df1[df1['FirstSecond'].isin([self.fir_sec[1]])]
                df3_1 = df3[df3['WinLose'].isin([self.win_lose[0]])]
                if len(df2) == 0:
                    fwin = 'N/A'
                else:
                    fwin = str(round(len(df2_1) * 100 / len(df2), 1)) + '%'
                if len(df3) == 0:
                    swin = 'N/A'
                else:
                    swin = str(round(len(df3_1) * 100 / len(df3), 1)) + '%'
                rec = ['VS ' + cls[i], str(vsc), str(win), str(lose), winrate, fwin, swin]
            rowcount = self.tableDeckR2.rowCount()
            self.tableDeckR2.insertRow(rowcount)
            for j, text in enumerate(rec):
                item = QTableWidgetItem()
                item.setText(text)
                item.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
                item.setBackground(QtGui.QColor(cls_cl[cls[i]][0], cls_cl[cls[i]][1], cls_cl[cls[i]][2]))
                self.tableDeckR2.setItem(rowcount, j, item)
            if vsc == 0:
                pass
            else:
                df4 = df1.drop_duplicates(['OppoArche'])
                lists = list(set(df4['OppoArche']))
                for arche in lists:
                    df1 = df[df['OppoArche'].isin([arche])]
                    vsc = len(df1)
                    win = len(df1[df1['WinLose'].isin([self.win_lose[0]])])
                    lose = len(df1[df1['WinLose'].isin([self.win_lose[1]])])
                    winrate = str(round(win * 100 / vsc, 1)) + '%'
                    df2 = df1[df1['FirstSecond'].isin([self.fir_sec[0]])]
                    df2_1 = df2[df2['WinLose'].isin([self.win_lose[0]])]
                    df3 = df1[df1['FirstSecond'].isin([self.fir_sec[1]])]
                    df3_1 = df3[df3['WinLose'].isin([self.win_lose[0]])]
                    if len(df2) == 0:
                        fwin = 'N/A'
                    else:
                        fwin = str(round(len(df2_1) * 100 / len(df2), 1)) + '%'
                    if len(df3) == 0:
                        swin = 'N/A'
                    else:
                        swin = str(round(len(df3_1) * 100 / len(df3), 1)) + '%'
                    rec = [arche, str(vsc), str(win), str(lose), winrate, fwin, swin]
                    rowcount = self.tableDeckR2.rowCount()
                    self.tableDeckR2.insertRow(rowcount)
                    for j, text in enumerate(rec):
                        item = QTableWidgetItem()
                        item.setText(text)
                        item.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
                        item.setBackground(QtGui.QColor(cls_cl[cls[i]][3], cls_cl[cls[i]][4], cls_cl[cls[i]][5]))
                        self.tableDeckR2.setItem(rowcount, j, item)

    def status_refresh(self):
        self.stat_c = False
        self.status_check()

    def status_check(self):
        if self.stat_c:
            return
        self.status = self.status_u = True
        for cls, lb in zip(self.crafts, self.status_list):
            num = len(d_check(self.mods[0], self.ccp, cls))
            lb.setText(str(num) + self.lb_msgs[3])
            if num == 0:
                self.status = False
        for cls, lb in zip(self.crafts, self.status_list_u):
            num = len(d_check(self.mods[1], self.ccp, cls))
            lb.setText(str(num) + self.lb_msgs[3])
            if num == 0:
                self.status = False
        self.stat_c = True
        self.al_enable()

    def al_enable(self):
        if self.status and self.status_u:
            self.lb_alarm.setText(self.lb_msgs[4])
            self.pushal.setEnabled(True)
        else:
            self.lb_alarm.setText(self.lb_msgs[5])
            self.pushal.setEnabled(False)

    def autologstart(self):
        logger.info("자동기록 시작")
        self.pushal.setEnabled(False)
        self.pushstop.setEnabled(True)
        self.al_work = True
        self.toggle_watchdog()
        self.autolog()
        self.thread1.working = True
        self.thread1.start()

    def toggle_watchdog(self):
        if self.is_watchdog:
            # streaming off
            self.watch.watchdog_off()
            self.is_watchdog = False
        else:
            try:
                # setup
                self.watch.set_observer()

                # streaming on
                self.watch.watchdog_on()
                self.is_watchdog = True
            except Exception as e:
                logger.warning("디렉토리 오류")
                return

    def autolog(self):
        self.lb_alarm.setText(self.lb_msgs[6])
        self.lb_alarm.setStyleSheet(self.ok_style)

    @pyqtSlot()
    def not_found(self):
        self.lb_alarm.setText(self.msgs[7])
        self.lb_alarm.setStyleSheet("background-color:rgba(255,131,0,50)")
        self.pushal.setEnabled(True)
        self.pushstop.setEnabled(False)
        logger.warning("창 못찾음")

    @pyqtSlot()
    def minimized(self):
        self.lb_alarm.setText(self.msgs[8])
        self.lb_alarm.setStyleSheet("background-color:rgba(255,131,0,50)")
        self.pushal.setEnabled(True)
        self.pushstop.setEnabled(False)
        logger.warning("창 최소화됨")

    @pyqtSlot()
    def req_resize(self):
        self.lb_alarm.setText(self.msgs[9])
        self.lb_alarm.setStyleSheet("background-color:rgba(255,131,0,50)")

    @pyqtSlot(int)
    def auto_mod(self, num):
        self.amod = self.mods[num]

    @pyqtSlot(int)
    def auto_first(self, num):
        self.first = self.fir_sec[num]

    @pyqtSlot(int)
    def auto_oppo_craft(self, num):
        self.oppo_cls = self.crafts[num]

    @pyqtSlot(int)
    def auto_my_craft(self, num):
        self.my_cls = self.crafts[num]

    @pyqtSlot()
    def auto_preview(self):
        text = self.lb_msgs[6] + "(" + self.atype + ")"
        if self.atype != self.types[1]:
            text = text + self.lb_msgs[8].format(self.types[1])
        self.lb_alarm.setText(text)
        if (self.atype in self.types[3:]) or (self.atype == self.types[2] and self.amod == ""):
            return
        self.today = datetime.now().strftime('%Y-%m-%d')
        self.lb_day.setText(self.today)
        self.lb_cp.setText(self.ccp)
        self.lb_mod.setText(self.amod)
        self.lb_fs.setText(self.first)
        self.lb_mycls.setText(self.my_cls)
        self.lb_opcls.setText(self.oppo_cls)
        mydecklist = d_check(self.amod, self.ccp, self.my_cls)
        self.cb_mydeck.clear()
        self.cb_mydeck.addItems(mydecklist)
        if self.amod == self.amod_2 and self.my_cls == self.my_cls_2 and self.cb_fix.isChecked():
            self.mydeck = self.mydeck_2
        else:
            self.mydeck = self.lb_msgs[7]
        self.cb_mydeck.setCurrentText(self.mydeck)
        opdecklist = d_check(self.amod, self.ccp, self.oppo_cls)
        self.cb_opdeck.clear()
        self.cb_opdeck.addItems(opdecklist)
        self.opdeck = self.lb_msgs[7]
        self.cb_opdeck.setCurrentText(self.opdeck)

    @pyqtSlot(int)
    def auto_win(self, num):
        self.win = self.win_lose[num]

    @pyqtSlot()
    def auto_result(self):
        if self.atype in self.types[3:]:
            pass
        else:
            self.logtime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.lb_wl.setText(self.win)
            self.lb_wl_style(self.lb_wl, self.win)
            self.lb_logtime.setText(self.logtime)
            self.lb_turn.setText(str(self.aturn))
        self.alarm()

    @pyqtSlot(str, str)
    def signal_m(self, clf, text):
        if clf == "type":
            self.atype = self.types[int(text)]
            logger.info(self.atype + " 매칭 중")
            if not self.in_match:
                self.in_match = True
        elif clf == "turn":
            self.aturn = int(text.split('n')[1])
            logger.info(text + " 종료")
            if self.in_match:
                self.in_match = False
                if self.atype == self.types[4]:
                    self.auto_result()

    def lb_wl_style(self, label, wl):
        if wl == self.win_lose[0]:
            label.setStyleSheet(self.win_style)
        else:
            label.setStyleSheet(self.lose_style)

    def auto_mydeck(self):
        self.mydeck = self.cb_mydeck.currentText()

    def auto_opdeck(self):
        self.opdeck = self.cb_opdeck.currentText()

    def alarm(self):
        if self.al_timer == 5:
            logger.info("매치 종료")
        if self.al_timer == 0:
            if self.atype == self.types[1]:
                write_record(self, self.ccp, self.amod, self.my_cls, self.mydeck, self.oppo_cls, self.opdeck,
                             self.first, self.win, self.atype, self.aturn)
                logger.info("기록 저장")
            if self.atype != self.types[3]:
                self.lb_day2.setText(self.today)
                self.lb_cp2.setText(self.ccp)
                self.lb_mod2.setText(self.amod)
                self.lb_fs2.setText(self.first)
                self.lb_mycls2.setText(self.my_cls)
                self.lb_mydeck2.setText(self.mydeck)
                self.lb_opcls2.setText(self.oppo_cls)
                self.lb_opdeck2.setText(self.opdeck)
                self.lb_wl2.setText(self.win)
                self.lb_wl_style(self.lb_wl2, self.win)
                self.lb_logtime2.setText(self.logtime)
                self.lb_turn2.setText(str(self.aturn))
                self.amod_2 = self.amod
                self.my_cls_2 = self.my_cls
                self.mydeck_2 = self.mydeck
            self.auto_init()
            load_data(self, self.loc)
            self.table_rate()
            self.al_timer = 5
            self.autolog()
            return
        if self.atype == self.types[1]:
            text = self.lb_msgs[9].format(self.al_timer)
        else:
            text = self.lb_msgs[11].format(self.atype, self.al_timer)
        self.lb_alarm.setText(text)
        self.al_timer -= 1
        self.timer1 = threading.Timer(1, self.alarm)
        self.timer1.start()

    def auto_init(self):
        self.first = ""
        self.win = ""
        self.my_cls = ""
        self.mydeck = ""
        self.oppo_cls = ""
        self.opdeck = ""
        self.amod = ""
        self.atype = ""
        self.aturn = 0
        self.lb_day.setText("")
        self.lb_cp.setText("")
        self.lb_mod.setText("")
        self.lb_fs.setText("")
        self.lb_mycls.setText("")
        self.cb_mydeck.clear()
        self.lb_opcls.setText("")
        self.cb_opdeck.clear()
        self.lb_wl.setText("")
        self.lb_wl.setStyleSheet(self.init_style)
        self.lb_logtime.setText("")
        self.lb_turn.setText("")
        logger.info("라벨 초기화")

    def stop(self):
        self.atype = ""
        self.timer1.cancel()
        self.auto_init()
        if self.is_watchdog:
            self.toggle_watchdog()
        self.al_work = False
        self.thread1.working = False
        self.thread1.wait()
        self.pushal.setEnabled(True)
        self.pushstop.setEnabled(False)
        self.lb_alarm.setText(self.lb_msgs[10])
        self.lb_alarm.setStyleSheet(self.init_style)
        logger.info("기록 중지")

    def closeEvent(self, event):
        if self.al_work:
            self.timer1.cancel()
            self.thread1.stop()
            event.accept()
        else:
            event.accept()


class Worker(QThread):
    def __init__(self):
        super().__init__()
        self.working = True

    not_found = pyqtSignal()
    minimize = pyqtSignal()
    req_resizing = pyqtSignal()
    auto_mod = pyqtSignal(int)
    first = pyqtSignal(int)
    oppo_craft = pyqtSignal(int)
    my_craft = pyqtSignal(int)
    auto_preview = pyqtSignal()
    auto_win = pyqtSignal(int)
    auto_result = pyqtSignal()
    current_size = img_size = 0
    mulligan = fsdecision = oppocls_al = mycls_al = preview = wldecision = False

    def auto_load_img(self, size):
        config = configparser.ConfigParser()
        config.read("config.ini")
        self.loc = config["locale"]["locale"]
        logger.info(str(size[0]) + " 이미지 불러오기 시작")
        path = "./resources/" + self.loc + "/" + str(size[0]) + "/"
        bloodicon = Image.open(path + "BloodIcon.png")
        bloodpost = Image.open(path + "BloodPost.png")
        dragonicon = Image.open(path + "DragonIcon.png")
        dragonpost = Image.open(path + "DragonPost.png")
        foresticon = Image.open(path + "ForestIcon.png")
        forestpost = Image.open(path + "ForestPost.png")
        havenicon = Image.open(path + "HavenIcon.png")
        havenpost = Image.open(path + "HavenPost.png")
        portalicon = Image.open(path + "PortalIcon.png")
        portalpost = Image.open(path + "PortalPost.png")
        runeicon = Image.open(path + "RuneIcon.png")
        runepost = Image.open(path + "RunePost.png")
        shadowicon = Image.open(path + "ShadowIcon.png")
        shadowpost = Image.open(path + "ShadowPost.png")
        swordicon = Image.open(path + "SwordIcon.png")
        swordpost = Image.open(path + "SwordPost.png")
        self.icons = [foresticon, swordicon, runeicon, havenicon, dragonicon, shadowicon, bloodicon, portalicon]
        self.posts = [forestpost, swordpost, runepost, havenpost, dragonpost, shadowpost, bloodpost, portalpost]
        img1 = Image.open(path + "1st.png")
        img2 = Image.open(path + "2nd.png")
        img_v = Image.open(path + "Victory.png")
        img_d = Image.open(path + "Defeat.png")
        img_r = Image.open(path + "rota.png")
        img_u = Image.open(path + "unli.png")
        self.miscs = [img1, img2, img_v, img_d, img_r, img_u]
        # [0]: 로테/언리, [1]: 선공/후공, [2]: 상대 직업, [3]: 내 직업, [4]: 승/패
        if size[0] == 1280:
            self.regions = [(615, int((size[1] - 720) / 2) + 20, 55, 75), (0, 0, 200, 150), (1000, 0, 280, 45),
                            (0, size[1] - 230, 220, 100), (150, int((size[1] - 720) / 2) + 45, 240, 35)]
        elif size[0] == 1600:
            self.regions = [(770, int((size[1] - 900) / 2) + 30, 60, 75), (15, 10, 120, 95), (1355, 18, 45, 45),
                            (30, size[1] - 275, 220, 100), (170, int((size[1] - 900) / 2) + 55, 310, 40)]
        else:
            self.regions = [(925, int((size[1] - 1080) / 2) + 40, 70, 80), (20, 13, 145, 110), (1630, 23, 50, 50),
                            (40, size[1] - 320, 255, 110), (210, int((size[1] - 1080) / 2) + 75, 360, 50)]
        self.img_size = size
        logger.info("이미지 불러오기 끝")

    def run(self):
        while self.working:
            hwnd = win32gui.FindWindow(None, 'Shadowverse')
            try:
                left, top, right, bot = win32gui.GetClientRect(hwnd)
            except:
                self.not_found.emit()
                break
            w = right - left
            h = bot - top

            hwndDC = win32gui.GetWindowDC(hwnd)
            mfcDC = win32ui.CreateDCFromHandle(hwndDC)
            saveDC = mfcDC.CreateCompatibleDC()

            saveBitMap = win32ui.CreateBitmap()
            saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)

            saveDC.SelectObject(saveBitMap)

            result = windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 1)

            bmpinfo = saveBitMap.GetInfo()
            bmpstr = saveBitMap.GetBitmapBits(True)

            try:
                im = Image.frombuffer('RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmpstr, 'raw', 'BGRX', 0, 1)
            except ValueError:
                self.minimize.emit()
                break

            win32gui.DeleteObject(saveBitMap.GetHandle())
            saveDC.DeleteDC()
            mfcDC.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwndDC)

            window_size = [1280, 1600, 1920]
            size_check = False
            for i in range(3):
                if im.size[0] == window_size[i]:
                    size_check = True
                    self.current_size = im.size
                    break

            if size_check:
                if not self.current_size == self.img_size:
                    self.auto_load_img(self.current_size)
                    logger.info("(%s) %s * %s 리소스 불러오기 끝", self.loc, self.current_size[0], self.current_size[1])
            else:
                self.req_resizing.emit()
                self.sleep(1)
                continue

            if not locate(self.miscs[4], im, grayscale=True, confidence=0.85, region=self.regions[0]) is None:
                self.auto_mod.emit(0)
            elif not locate(self.miscs[5], im, grayscale=True, confidence=0.75, region=self.regions[0]) is None:
                self.auto_mod.emit(1)

            if not self.mulligan:
                # 선후공 체크
                if not locate(self.miscs[0], im, grayscale=True, confidence=0.90, region=self.regions[1]) is None:
                    self.first.emit(0)
                    self.fsdecision = True
                    logger.info("선공")
                elif not locate(self.miscs[1], im, grayscale=True, confidence=0.90, region=self.regions[1]) is None:
                    self.first.emit(1)
                    self.fsdecision = True
                    logger.info("후공")
                # 상대 직업 체크
                if self.fsdecision:
                    for icon in self.icons:
                        if not locate(icon, im, grayscale=True, confidence=0.90, region=self.regions[2]) is None:
                            self.oppo_craft.emit(self.icons.index(icon))
                            self.oppocls_al = True
                            logger.info("상대 직업 체크")
                            break
                self.mulligan = self.fsdecision and self.oppocls_al
            elif self.mulligan and not self.mycls_al:
                # 내 직업 체크
                for post in self.posts:
                    if not locate(post, im, grayscale=True, confidence=0.90, region=self.regions[3]) is None:
                        self.my_craft.emit(self.posts.index(post))
                        self.mycls_al = True
                        logger.info("내 직업 체크")
            elif self.mulligan and self.mycls_al:
                if not self.preview:
                    self.auto_preview.emit()
                    self.preview = True
                    logger.info("프리뷰")

                # 승패 체크
                if not locate(self.miscs[2], im, grayscale=False, confidence=0.97, region=self.regions[4]) is None:
                    self.auto_win.emit(0)
                    self.wldecision = True
                    logger.info("패")
                    self.msleep(100)
                elif not locate(self.miscs[3], im, grayscale=False, confidence=0.97, region=self.regions[4]) is None:
                    self.auto_win.emit(1)
                    self.wldecision = True
                    logger.info("승")
                    self.msleep(100)
                # 결과 출력 및 초기화
                if self.wldecision:
                    self.auto_result.emit()
                    self.sleep(4)
                    self.mulligan = self.fsdecision = self.oppocls_al = False
                    self.mycls_al = self.preview = self.wldecision = False
                self.sleep(1)

    def stop(self):
        self.working = False
        self.quit()
        self.wait(1000)


class Target:
    import getpass
    username = getpass.getuser()
    watchDir = 'C:/Users/' + username + '/AppData/LocalLow/Cygames/Shadowverse'

    def __init__(self):
        self.observer = None
        self.is_watchdog = False
        self.modsignal = ModSignal()

    def set_observer(self):
        self.observer = Observer()
        event_handler = Handler(emitter=self.modsignal)
        self.observer.schedule(event_handler, self.watchDir, recursive=False)

    def watchdog_on(self):
        if not self.observer:
            self.set_observer()
        self.observer.start()
        self.is_watchdog = True

    def watchdog_off(self):
        self.observer.stop()
        self.observer = None
        self.is_watchdog = False

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.watchdog_off()


class Handler(FileSystemEventHandler):

    def __init__(self, *args, emitter=None, **kwargs):
        super(Handler, self).__init__(*args, **kwargs)
        self._emitter = emitter

    def on_modified(self, event):
        try:
            with open(event.src_path, 'r', encoding='UTF-8') as log:
                lines = log.read().splitlines()
                if len(lines) > 12:
                    logs = lines[-12:-1]
                else:
                    logs = lines
            for i in range(len(logs)):
                if "Matching_ConnectAPI" in logs[i]:
                    if "FreeBattle" in logs[i]:
                        type = "0"
                    elif "RankBattle" in logs[i]:
                        type = "1"
                    elif "Colosseum" in logs[i]:
                        type = "2"
                    elif "RoomBattle" in logs[i]:
                        type = "4"
                    else:
                        type = "3"
                    self._emitter.signal1.emit("type", type)
                elif "FinishTask" in logs[i]:
                    turn = lines[1].split()
                    self._emitter.signal1.emit("turn", turn[0])
        except:
            pass


class ModSignal(QObject):
    signal1 = pyqtSignal(str, str)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = Form()
    myWindow.show()
    sys.exit(app.exec_())
