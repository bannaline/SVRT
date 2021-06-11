import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QTableWidgetItem, qApp, QMessageBox
from PyQt5 import QtCore, QtGui, uic
import sqlite3
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc, style
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import pandas as pd
from datetime import datetime
from data_manage import load_data, all_data, cp_list, d_check, ccp_check, write_record
import os
from sub1 import Sub
from pyautogui import locate
import threading
import win32gui
import win32ui
from ctypes import windll
from PIL import Image
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QObject
from logger import logger


form_class = uic.loadUiType("main_window.ui")[0]


class Form(QMainWindow, form_class):
    def __init__(self):
        logger.info("초기화시작")
        super().__init__()
        self.setupUi(self)

        # CpDl 버튼
        self.actionCpDl.triggered.connect(self.cpdl)

        # Exit 버튼
        self.actionExit.triggered.connect(qApp.quit)

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
        self.ccp = ccp
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
        self.tableRecord.setColumnWidth(1, 53)
        self.tableRecord.setColumnWidth(2, 75)
        self.tableRecord.setColumnWidth(3, 77)
        self.tableRecord.setColumnWidth(4, 105)
        self.tableRecord.setColumnWidth(5, 77)
        self.tableRecord.setColumnWidth(6, 105)
        self.tableRecord.setColumnWidth(7, 50)
        self.tableRecord.setColumnWidth(8, 40)
        self.tableRecord.setColumnWidth(9, 27)

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
        self.tableDeckR1.setColumnWidth(0, 98)
        self.tableDeckR1.setColumnWidth(1, 30)
        self.tableDeckR1.setColumnWidth(2, 30)
        self.tableDeckR1.setColumnWidth(3, 30)
        self.tableDeckR1.setColumnWidth(4, 48)
        self.tableDeckR1.setColumnWidth(5, 48)
        self.tableDeckR1.setColumnWidth(6, 48)
        self.tableDeckR2.setColumnWidth(0, 98)
        self.tableDeckR2.setColumnWidth(1, 30)
        self.tableDeckR2.setColumnWidth(2, 30)
        self.tableDeckR2.setColumnWidth(3, 30)
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
        self.font_name = font_manager.FontProperties(fname="c:/Windows/Fonts/malgun.ttf").get_name()
        rc('font', family=self.font_name)
        font_manager.FontProperties().set_size('xx-small')
        style.use('ggplot')

        # 자동 기록 탭
        self.tabWidget.tabBarClicked.connect(self.status_check)
        self.status_list = [self.stelfr, self.stroyalr, self.stwitchr, self.stbishopr, self.stdragonr,
                            self.stnecror, self.stvampr, self.stnemer]
        self.status_list_u = [self.stelfu, self.stroyalu, self.stwitchu, self.stbishopu, self.stdragonu,
                              self.stnecrou, self.stvampu, self.stnemeu]
        for i in range(len(self.status_list)):
            self.status_list[i].setFont(QtGui.QFont('맑은 고딕'))
            self.status_list_u[i].setFont(QtGui.QFont('맑은 고딕'))
        self.pushrefresh.clicked.connect(self.status_refresh)
        self.radioautoRota.clicked.connect(self.auto_mod)
        self.radioautoUnli.clicked.connect(self.auto_mod)

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
        self.timer = threading.Timer(1, self.autolog)
        self.timer1 = threading.Timer(1, self.alarm)

        logger.info("초기화끝")

        if os.path.isfile('log.db'):
            load_data(self)
        else:
            self.init_data()
        self.table_rate()

        logger.info("테이블 불러오기 완료")

    mod = '로테이션'
    logcp = ccp_check()
    fs = wl = logdate = myjob = myarche = oppojob = oppoarche = deckmod = deckstartdate = deckenddate = ''
    fscheck = wlcheck = deckmodcheck = deckrmodcheck = 0
    turn = 1
    df = df2 = df3 = df5 = df6 = pd.DataFrame([])
    sortlim = deckrmod = deckrstartdate = deckrenddate = deckrarche = ''
    al_work = modi = status = status_u = stat_c = False
    my_cls = my_cls_2 = oppo_cls = first = win = today = amod = amod_2 = atype = mydeck = mydeck_2 = opdeck = logtime = ""
    mycn = oppocn = aturn = img_size = current_size = 0
    crafts = ["엘프", "로얄", "위치", "비숍", "드래곤", "네크로맨서", "뱀파이어", "네메시스"]
    mulligan = fsdecision = oppocls_al = wldecision = mycls_al = preview = False
    log = []
    al_timer = 7
    clslist = ['forest', 'sword', 'rune', 'haven', 'dragon', 'shadow', 'blood', 'portal']
    cll = []
    icons = []
    posts = []
    miscs = []
    regions = []
    names = []

    # CpDl 버튼 이벤트
    def cpdl(self):
        self.cp_dl = Sub()
        self.cp_dl.show()

    # 모드 버튼 이벤트
    def rad_mod(self):
        mod = ''
        if self.radioRecRota.isChecked():
            mod = '로테이션'
        elif self.radioRecUnli.isChecked():
            mod = '언리미티드'
        self.mod = mod
        self.radio_myjob()
        self.radio_oppojob()

    # 선후공 버튼 이벤트
    def rad_fs(self):
        fs = ''
        if self.radioFirst.isChecked():
            fs = '선공'
        elif self.radioSecond.isChecked():
            fs = '후공'
        self.fs = fs
        if self.fscheck == 0:
            self.radioWin.setEnabled(True)
            self.radioLose.setEnabled(True)
            self.fscheck = 1

    # 승패 버튼 이벤트
    def rad_wl(self):
        wl = ''
        if self.radioWin.isChecked():
            wl = '승'
        elif self.radioLose.isChecked():
            wl = '패'
        self.wl = wl
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
        if self.radioRoyalMy.isChecked():
            myjob = '로얄'
        elif self.radioWitchMy.isChecked():
            myjob = '위치'
        elif self.radioElfMy.isChecked():
            myjob = '엘프'
        elif self.radioBishopMy.isChecked():
            myjob = '비숍'
        elif self.radioDragonMy.isChecked():
            myjob = '드래곤'
        elif self.radioNecroMy.isChecked():
            myjob = '네크로맨서'
        elif self.radioVampMy.isChecked():
            myjob = '뱀파이어'
        elif self.radioNemeMy.isChecked():
            myjob = '네메시스'
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
        if self.radioRoyalOppo.isChecked():
            oppojob = '로얄'
        elif self.radioWitchOppo.isChecked():
            oppojob = '위치'
        elif self.radioElfOppo.isChecked():
            oppojob = '엘프'
        elif self.radioBishopOppo.isChecked():
            oppojob = '비숍'
        elif self.radioDragonOppo.isChecked():
            oppojob = '드래곤'
        elif self.radioNecroOppo.isChecked():
            oppojob = '네크로맨서'
        elif self.radioVampOppo.isChecked():
            oppojob = '뱀파이어'
        elif self.radioNemeOppo.isChecked():
            oppojob = '네메시스'
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
                     self.oppojob, self.oppoarche, self.fs, self.wl, '랭크전', self.turn)
        load_data(self)
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
        load_data(self)
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
            ret = msgbox.question(self, '경고', '정말 기록을 초기화하겠습니까?')
            if ret == QMessageBox.Yes:
                os.remove('log.db')
            elif ret == QMessageBox.No:
                return
        conn = sqlite3.connect('log.db')
        cur = conn.cursor()
        cur.execute("CREATE TABLE log(Date text, CardPack text, Mod TEXT, MyJob text, MyArche text, OppoJob text, OppoArche text, FirstSecond text, WinLose text, LogTime TEXT, Type text, Turn int)")
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
        df1 = df[df['Mod'].isin(['로테이션'])]
        vscount = len(df1)
        rota = []
        if vscount == 0:
            rota = ['', '', '', '', '', '', '', '', '', '', '', '']
        else:
            rota.append(str(vscount))
            win = df1[df1['WinLose'].isin(['승'])]
            rota.append(str(len(win)))
            lose = df1[df1['WinLose'].isin(['패'])]
            rota.append(str(len(lose)))
            wr = round(len(win) / vscount * 100, 1)
            wr = str(wr) + '%'
            rota.append(wr)
            first = df1[df1['FirstSecond'].isin(['선공'])]
            if len(first) == 0:
                rota.extend(['N/A', 'N/A', 'N/A', 'N/A'])
            else:
                rota.append(str(len(first)))
                fwin = first[first['WinLose'].isin(['승'])]
                rota.append(str(len(fwin)))
                flose = first[first['WinLose'].isin(['패'])]
                rota.append(str(len(flose)))
                fwr = round(len(fwin) / len(first) * 100, 1)
                fwr = str(fwr) + '%'
                rota.append(fwr)
            second = df1[df1['FirstSecond'].isin(['후공'])]
            if len(second) == 0:
                rota.extend(['N/A', 'N/A', 'N/A', 'N/A'])
            else:
                rota.append(str(len(second)))
                swin = second[second['WinLose'].isin(['승'])]
                rota.append(str(len(swin)))
                slose = second[second['WinLose'].isin(['패'])]
                rota.append(str(len(slose)))
                swr = round(len(swin) / len(second) * 100, 1)
                swr = str(swr) + '%'
                rota.append(swr)
        df1 = df[df['Mod'].isin(['언리미티드'])]
        vscount = len(df1)
        unli = []
        if vscount == 0:
            unli = ['', '', '', '', '', '', '', '', '', '', '', '']
        else:
            unli.append(str(vscount))
            win = df1[df1['WinLose'].isin(['승'])]
            unli.append(str(len(win)))
            lose = df1[df1['WinLose'].isin(['패'])]
            unli.append(str(len(lose)))
            wr = round(len(win) / vscount * 100, 1)
            wr = str(wr) + '%'
            unli.append(wr)
            first = df1[df1['FirstSecond'].isin(['선공'])]
            if len(first) == 0:
                unli.extend(['N/A', 'N/A', 'N/A', 'N/A'])
            else:
                unli.append(str(len(first)))
                fwin = first[first['WinLose'].isin(['승'])]
                unli.append(str(len(fwin)))
                flose = first[first['WinLose'].isin(['패'])]
                unli.append(str(len(flose)))
                fwr = round(len(fwin) / len(first) * 100, 1)
                fwr = str(fwr) + '%'
                unli.append(fwr)
            second = df1[df1['FirstSecond'].isin(['후공'])]
            if len(second) == 0:
                unli.extend(['N/A', 'N/A', 'N/A', 'N/A'])
            else:
                unli.append(str(len(second)))
                swin = second[second['WinLose'].isin(['승'])]
                unli.append(str(len(swin)))
                slose = second[second['WinLose'].isin(['패'])]
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
            self.deckmod = '로테이션'
            self.groupDeckRecord.setTitle('기간 내 로테이션 전적')
        elif self.radioDeckUnli.isChecked():
            self.deckmod = '언리미티드'
            self.groupDeckRecord.setTitle('기간 내 언리미티드 전적')
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
        if self.deckmod == '로테이션':
            df3 = df2[df2['Mod'].isin(['로테이션'])]
        elif self.deckmod == '언리미티드':
            df3 = df2[df2['Mod'].isin(['언리미티드'])]
        self.df2 = df3
        self.deckrecordupdate()
        df4 = df3.drop_duplicates(['MyArche'])
        lists = list(set(df4['MyArche']))
        rec = {}

        for deck in lists:
            record = []
            vs = df3[df3['MyArche'].isin([deck])]
            win = vs[vs['WinLose'].isin(['승'])]
            lose = vs[vs['WinLose'].isin(['패'])]
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
            self.DeckVS.setText('전적없음')
            self.DeckWin.setText('N/A')
            self.DeckLose.setText('N/A')
            self.DeckWinRate.setText('N/A')
            return
        win = df[df['WinLose'].isin(['승'])]
        lose = df[df['WinLose'].isin(['패'])]
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
                vs = str(df.iloc[i, 0]) + '전 ' + str(df.iloc[i, 1]) + '승 ' + str(df.iloc[i, 2]) + '패'
                self.labels[i*4].setText(vs)
                colors = ['lightskyblue', 'red']
                labels = ['승', '패']
                ratio = [df.iloc[i, 1], df.iloc[i, 2]]
                d1 = self.figure1.add_subplot(spl[i])
                d1.pie(ratio, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
                d1.set_title(name, fontdict={'fontsize': 11}, pad=40)
                df1 = self.df2
                df1 = df1[df1['MyArche'].isin([name])]
                first = df1[df1['FirstSecond'].isin(['선공'])]
                firstwin = first[first['WinLose'].isin(['승'])]
                second = df1[df1['FirstSecond'].isin(['후공'])]
                secondwin = second[second['WinLose'].isin(['승'])]
                turn = round(df1['Turn'].mean(skipna=True), 2)
                if len(first) == 0:
                    self.labels[i*4+1].setText('N/A')
                else:
                    wr1st = '선공 ' + str(round(len(firstwin) * 100 / len(first), 1)) + '%'
                    self.labels[i*4+1].setText(wr1st)
                if len(second) == 0:
                    self.labels[i*4+2].setText('N/A')
                else:
                    wr2nd = '후공 ' + str(round(len(secondwin) * 100 / len(second), 1)) + '%'
                    self.labels[i*4+2].setText(wr2nd)
                if str(type(turn)) == "<class 'float'>":
                    self.labels[i * 4 + 3].setText('턴 정보 없음')
                else:
                    self.labels[i*4+3].setText('평균 ' + str(turn) + '턴')
                self.deck_btns[i].setEnabled(True)
            else:
                self.labels[i*4].setText('')
                self.labels[i*4+1].setText('')
                self.labels[i*4+2].setText('')
                self.labels[i*4+3].setText('')
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
            self.deckrmod = '로테이션'
        elif self.radioDeckRUnli.isChecked():
            self.deckrmod = '언리미티드'
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
        if self.deckrmod == '로테이션':
            df3 = df2[df2['Mod'].isin(['로테이션'])]
        elif self.deckrmod == '언리미티드':
            df3 = df2[df2['Mod'].isin(['언리미티드'])]
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
        self.DeckRVS.setText('전적없음')
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
            self.DeckVS.setText('전적없음')
            self.DeckWin.setText('N/A')
            self.DeckLose.setText('N/A')
            self.DeckWinRate.setText('N/A')
            return
        win = df[df['WinLose'].isin(['승'])]
        lose = df[df['WinLose'].isin(['패'])]
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
        df1 = df[df['FirstSecond'].isin(['선공'])]
        df1_1 = df1[df1['WinLose'].isin(['승'])]
        df2 = df[df['FirstSecond'].isin(['후공'])]
        df2_1 = df2[df2['WinLose'].isin(['승'])]
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
        rects1 = ax.barh(2, fwin, align='center', color='lightskyblue', height=0.5, label='선공')
        rects2 = ax.barh(1, swin, align='center', color='xkcd:pistachio', height=0.5, label='후공')
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
        cls = ['엘프', '로얄', '위치', '비숍']
        # 직업별 색상 [메인RGB, 서브RGB]
        cls_cl = {"엘프": [207, 247, 99, 176, 239, 12], "로얄": [253, 251, 140, 197, 191, 3],
                  "위치": [158, 168, 240, 92, 109, 231], "비숍": [255, 255, 255, 190, 190, 190]}
        for i in range(4):
            df = self.df6
            df1 = df[df['OppoJob'].isin([cls[i]])]
            vsc = len(df1)
            if vsc == 0:
                rec = ['VS'+cls[i], '0', '0', '0', 'N/A', 'N/A', 'N/A']
            else:
                win = len(df1[df1['WinLose'].isin(['승'])])
                lose = len(df1[df1['WinLose'].isin(['패'])])
                winrate = str(round(win * 100 / vsc, 1)) + '%'
                df2 = df1[df1['FirstSecond'].isin(['선공'])]
                df2_1 = df2[df2['WinLose'].isin(['승'])]
                df3 = df1[df1['FirstSecond'].isin(['후공'])]
                df3_1 = df3[df3['WinLose'].isin(['승'])]
                if len(df2) == 0:
                    fwin = 'N/A'
                else:
                    fwin = str(round(len(df2_1) * 100 / len(df2), 1)) + '%'
                if len(df3) == 0:
                    swin = 'N/A'
                else:
                    swin = str(round(len(df3_1) * 100 / len(df3), 1)) + '%'
                rec = ['VS'+cls[i], str(vsc), str(win), str(lose), winrate, fwin, swin]
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
                    win = len(df1[df1['WinLose'].isin(['승'])])
                    lose = len(df1[df1['WinLose'].isin(['패'])])
                    winrate = str(round(win * 100 / vsc, 1)) + '%'
                    df2 = df1[df1['FirstSecond'].isin(['선공'])]
                    df2_1 = df2[df2['WinLose'].isin(['승'])]
                    df3 = df1[df1['FirstSecond'].isin(['후공'])]
                    df3_1 = df3[df3['WinLose'].isin(['승'])]
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
        cls = ['네크로맨서', '드래곤', '뱀파이어', '네메시스']
        # 직업별 색상 [메인RGB, 서브RGB]
        cls_cl = {"네크로맨서": [242, 178, 255, 226, 89, 255], "드래곤": [255, 232, 99, 249, 211, 0],
                  "뱀파이어": [255, 125, 177, 255, 40, 126], "네메시스": [215, 255, 255, 155, 255, 255]}
        for i in range(4):
            df = self.df6
            df1 = df[df['OppoJob'].isin([cls[i]])]
            vsc = len(df1)
            if vsc == 0:
                rec = ['VS'+cls[i], '0', '0', '0', 'N/A', 'N/A', 'N/A']
            else:
                win = len(df1[df1['WinLose'].isin(['승'])])
                lose = len(df1[df1['WinLose'].isin(['패'])])
                winrate = str(round(win * 100 / vsc, 1)) + '%'
                df2 = df1[df1['FirstSecond'].isin(['선공'])]
                df2_1 = df2[df2['WinLose'].isin(['승'])]
                df3 = df1[df1['FirstSecond'].isin(['후공'])]
                df3_1 = df3[df3['WinLose'].isin(['승'])]
                if len(df2) == 0:
                    fwin = 'N/A'
                else:
                    fwin = str(round(len(df2_1) * 100 / len(df2), 1)) + '%'
                if len(df3) == 0:
                    swin = 'N/A'
                else:
                    swin = str(round(len(df3_1) * 100 / len(df3), 1)) + '%'
                rec = ['VS'+cls[i], str(vsc), str(win), str(lose), winrate, fwin, swin]
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
                    win = len(df1[df1['WinLose'].isin(['승'])])
                    lose = len(df1[df1['WinLose'].isin(['패'])])
                    winrate = str(round(win * 100 / vsc, 1)) + '%'
                    df2 = df1[df1['FirstSecond'].isin(['선공'])]
                    df2_1 = df2[df2['WinLose'].isin(['승'])]
                    df3 = df1[df1['FirstSecond'].isin(['후공'])]
                    df3_1 = df3[df3['WinLose'].isin(['승'])]
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
            num = len(d_check("로테이션", self.ccp, cls))
            lb.setText(str(num) + "개")
            if num == 0:
                self.status = False
        for cls, lb in zip(self.crafts, self.status_list_u):
            num = len(d_check("언리미티드", self.ccp, cls))
            lb.setText(str(num) + "개")
            if num == 0:
                self.status = False
        self.stat_c = True
        self.al_enable()

    def auto_mod(self):
        mod = ''
        if self.radioautoRota.isChecked():
            mod = '로테이션'
        elif self.radioautoUnli.isChecked():
            mod = '언리미티드'
        self.amod = mod

    def al_enable(self):
        if self.status and self.status_u:
            self.lb_alarm.setText('기록을 시작하려면 시작 버튼을 누르세요.')
            self.pushal.setEnabled(True)
        else:
            self.lb_alarm.setText('메뉴로 들어가 덱을 확인해주세요.')
            self.pushal.setEnabled(False)

    """
    def auto_cp(self):
        ccp = self.comboautocp.currentText()
        if self.checkautomini.isChecked():
            ccp = ccp + 'm'
        self.ccp = ccp
    """

    def autologstart(self):
        logger.info("자동기록 시작")
        self.pushal.setEnabled(False)
        self.pushstop.setEnabled(True)
        self.al_work = True
        self.toggle_watchdog()
        self.autolog()

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
                # Log.e(self.tag, 'directory path error! :', e.__class__.__name__)
                return

    def auto_load_img(self, number):
        logger.info(str(number) + " 이미지 불러오기 시작")
        path = "./resources/" + str(number) + "/"
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
        if number == 1280:
            self.regions = [(615, 30, 665, 75), (0, 0, 200, 150), (1000, 0, 280, 100),
                            (0, 490, 220, 100), (150, 55, 240, 25)]
        elif number == 1600:
            self.regions = [(770, 40, 60, 55), (15, 10, 120, 95), (1355, 18, 45, 45),
                            (30, 625, 220, 100), (170, 65, 310, 30)]
        else:
            self.regions = [(925, 48, 70, 70), (20, 13, 145, 110), (1630, 23, 50, 50),
                            (40, 760, 255, 110), (210, 85, 360, 30)]
        self.img_size = number
        logger.info("이미지 불러오기 끝")

    def autolog(self):
        # if self.al_work:
        self.lb_alarm.setText('데이터 수집 중')

        # self.al_work = True

        hwnd = win32gui.FindWindow(None, 'Shadowverse')
        try:
            left, top, right, bot = win32gui.GetClientRect(hwnd)
        except:
            ans = QMessageBox.warning(self, '주의', '창을 찾을 수 없습니다.', QMessageBox.Ok, QMessageBox.Ok)
            self.stop()
            logger.warning("창 못찾음")
            return
        w = right - left
        h = bot - top

        if not self.atype == "랭크전":
            self.timer = threading.Timer(0.5, self.autolog)
            self.timer.start()
            return

        hwndDC = win32gui.GetWindowDC(hwnd)
        mfcDC  = win32ui.CreateDCFromHandle(hwndDC)
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
            QMessageBox.warning(self, '주의', '창이 최소화되어 있습니다.', QMessageBox.Ok, QMessageBox.Ok)
            self.stop()
            logger.warning("창 최소화됨")
            return

        window_size = [(1280, 720), (1600, 900), (1920, 1080)]
        size_check = False
        for i in range(3):
            if im.size[0] == window_size[i][0] and im.size[1] == window_size[i][1]:
                size_check = True
                self.current_size = im.size[0]
                break

        if size_check:
            if not self.current_size == self.img_size:
                self.auto_load_img(self.current_size)
        else:
            warning = QMessageBox.warning(self, '주의', '해상도가 맞지 않습니다.\n지원하는 해상도\n1280x720, 1600x900, 1920x1080',
                                          QMessageBox.Cancel | QMessageBox.Ok, QMessageBox.Ok)
            if warning == QMessageBox.Cancel:
                self.stop()
                return
            else:
                self.autolog()
                return

        win32gui.DeleteObject(saveBitMap.GetHandle())
        saveDC.DeleteDC()
        mfcDC.DeleteDC()
        win32gui.ReleaseDC(hwnd, hwndDC)

        if not locate(self.miscs[4], im, grayscale=True, confidence=0.90, region=self.regions[0]) is None:
            self.amod = "로테이션"
            self.radioautoRota.setChecked(True)
        elif not locate(self.miscs[5], im, grayscale=True, confidence=0.90, region=self.regions[0]) is None:
            self.amod = "언리미티드"
            self.radioautoUnli.setChecked(True)

        if not self.mulligan:
            # 선후공 체크
            if not locate(self.miscs[0], im, grayscale=True, confidence=0.90, region=self.regions[1]) is None:
                self.first = '선공'
                self.fsdecision = True
            elif not locate(self.miscs[1], im, grayscale=True, confidence=0.90, region=self.regions[1]) is None:
                self.first = '후공'
                self.fsdecision = True
            # 상대 직업 체크
            if self.fsdecision:
                for icon in self.icons:
                    if not locate(icon, im, grayscale=True, confidence=0.90, region=self.regions[2]) is None:
                        self.oppocn = self.icons.index(icon)
                        self.oppo_cls = self.crafts[self.oppocn]
                        self.oppocls_al = True
                        break
            self.mulligan = self.fsdecision and self.oppocls_al
        elif self.mulligan and not self.mycls_al:
            # 내 직업 체크
            for post in self.posts:
                if not locate(post, im, grayscale=True, confidence=0.90, region=self.regions[3]) is None:
                    self.mycn = self.posts.index(post)
                    self.my_cls = self.crafts[self.mycn]
                    self.mycls_al = True
        elif self.mulligan and self.mycls_al:
            if not self.preview:
                if self.amod == self.amod_2 and self.my_cls == self.my_cls_2 and self.cb_fix.isChecked():
                    self.mydeck = self.mydeck_2
                else:
                    self.mydeck = "기타"
                self.opdeck = "기타"
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
                self.cb_mydeck.setCurrentText(self.mydeck)
                opdecklist = d_check(self.amod, self.ccp, self.oppo_cls)
                self.cb_opdeck.clear()
                self.cb_opdeck.addItems(opdecklist)
                self.cb_opdeck.setCurrentText(self.opdeck)
                self.preview = True

            # 승패 체크
            if not locate(self.miscs[3], im, grayscale=False, confidence=0.97, region=self.regions[4]) is None:
                self.win = '패'
                self.wldecision = True
            elif not locate(self.miscs[2], im, grayscale=False, confidence=0.97, region=self.regions[4]) is None:
                self.win = '승'
                self.wldecision = True
            # 결과 출력 및 초기화
            if self.wldecision:
                self.logtime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.lb_wl.setText(self.win)
                self.lb_logtime.setText(self.logtime)
                self.lb_turn.setText(str(self.aturn))
                self.timer.cancel()
                self.alarm()
                return

        if self.al_work:
            self.timer = threading.Timer(0.5, self.autolog)
            self.timer.start()

    @pyqtSlot(str, str)
    def signal_m(self, clf, text):
        if clf == "mod":
            self.atype = text
            logger.info(text + " 매칭 중")
        elif clf == "turn":
            self.aturn = int(text.split('n')[1])
            logger.info(text + " 종료")

    def auto_mydeck(self):
        self.mydeck = self.cb_mydeck.currentText()

    def auto_opdeck(self):
        self.opdeck = self.cb_opdeck.currentText()

    def alarm(self):
        if self.al_timer == 7:
            logger.info("매치 종료")
        if self.al_timer == 0:
            write_record(self, self.ccp, self.amod, self.my_cls, self.mydeck, self.oppo_cls, self.opdeck,
                         self.first, self.win, self.atype, self.aturn)
            logger.info("기록 저장")
            self.lb_day2.setText(self.today)
            self.lb_cp2.setText(self.ccp)
            self.lb_mod2.setText(self.amod)
            self.lb_fs2.setText(self.first)
            self.lb_mycls2.setText(self.my_cls)
            self.lb_mydeck2.setText(self.mydeck)
            self.lb_opcls2.setText(self.oppo_cls)
            self.lb_opdeck2.setText(self.opdeck)
            self.lb_wl2.setText(self.win)
            self.lb_logtime2.setText(self.logtime)
            self.lb_turn2.setText(str(self.aturn))
            self.amod_2 = self.amod
            self.my_cls_2 = self.my_cls
            self.mydeck_2 = self.mydeck
            self.auto_init()
            load_data(self)
            self.table_rate()
            self.lb_alarm.setText('기록이 저장되었습니다.\n1초 후 자동시작')
            self.al_timer = 7
            self.timer = threading.Timer(1, self.autolog)
            self.timer.start()
            return
        text = '{}초 후 기록을 자동으로 저장합니다.'.format(self.al_timer)
        self.lb_alarm.setText(text)
        self.al_timer -= 1
        self.timer1 = threading.Timer(1, self.alarm)
        self.timer1.start()

    def auto_init(self):
        self.first = ''
        self.win = ''
        self.mulligan = False
        self.fsdecision = False
        self.oppocls_al = False
        self.wldecision = False
        self.mycls_al = False
        self.my_cls = ""
        self.mydeck = ""
        self.oppo_cls = ""
        self.opdeck = ""
        self.amod = ""
        self.aturn = 0
        self.preview = False
        self.lb_day.setText('')
        self.lb_cp.setText('')
        self.lb_mod.setText('')
        self.lb_fs.setText('')
        self.lb_mycls.setText('')
        self.cb_mydeck.clear()
        self.lb_opcls.setText('')
        self.cb_opdeck.clear()
        self.lb_wl.setText('')
        self.lb_logtime.setText('')
        self.lb_turn.setText('')
        logger.info("라벨 초기화")

    def stop(self):
        self.timer.cancel()
        self.timer1.cancel()
        self.auto_init()
        if self.is_watchdog:
            self.toggle_watchdog()
        self.al_work = False
        self.pushal.setEnabled(True)
        self.pushstop.setEnabled(False)
        self.lb_alarm.setText('기록 중지')
        logger.info("기록 중지")

    def closeEvent(self, event):
        if self.al_work:
            self.timer.cancel()
            self.timer1.cancel()
            event.accept()
        else:
            event.accept()


class Target:
    import getpass
    username = getpass.getuser()
    watchDir = 'C:/Users/' + username + '/AppData/LocalLow/Cygames/Shadowverse'
    #watchDir에 감시하려는 디렉토리를 명시한다.

    def __init__(self):
        self.observer = None   #observer객체를 만듦
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

    def on_modified(self, event): #파일, 디렉터리가 수정되면 실행
        try:
            with open(event.src_path, 'r', encoding='UTF-8') as log:
                lines = log.read().splitlines()
                if len(lines) > 12:
                    logs = lines[-12:-1]
                else:
                    logs = lines
            for i in range(len(logs)):
                if "Matching_ConnectAPI" in logs[i]:
                    mod = ""
                    if "FreeBattle" in logs[i]:
                        mod = "일반전"
                    elif "RankBattle" in logs[i]:
                        mod = "랭크전"
                    elif "Colosseum" in logs[i]:
                        mod = "그랑프리"
                    else:
                        print(logs[i])
                    self._emitter.signal1.emit("mod", mod)
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