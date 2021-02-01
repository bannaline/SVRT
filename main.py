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
from sub2 import Sub2
from sub3 import Sub3
# import configparser
from pyautogui import locate
import threading
import time
import win32gui
import win32ui
from ctypes import windll
from PIL import Image
import json


form_class = uic.loadUiType("main_window.ui")[0]
button_map = {}
b_text = []


class Form(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        load_data(self)
        self.table_rate()

        # CpDl 버튼
        self.actionCpDl.triggered.connect(self.cpdl)

        # Database 버튼
        self.actionDb.triggered.connect(self.dbmenu)

        # Deck Categorization 버튼
        self.actionDeckCate.triggered.connect(self.dcmenu)

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

        # 등록 버튼
        self.pushRegister.clicked.connect(self.write_btn)

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
        self.tableRecord.setColumnWidth(1, 55)
        self.tableRecord.setColumnWidth(2, 75)
        self.tableRecord.setColumnWidth(3, 77)
        self.tableRecord.setColumnWidth(4, 105)
        self.tableRecord.setColumnWidth(5, 77)
        self.tableRecord.setColumnWidth(6, 105)
        self.tableRecord.setColumnWidth(7, 51)
        self.tableRecord.setColumnWidth(8, 42)

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

        global button_map
        button_map = {}
        global b_text
        b_text = []
        labels = [self.Deck1VSCount, self.Deck1First, self.Deck1Second, self.Deck2VSCount, self.Deck2First,
                  self.Deck2Second, self.Deck3VSCount, self.Deck3First, self.Deck3Second, self.Deck4VSCount,
                  self.Deck4First, self.Deck4Second, self.Deck5VSCount, self.Deck5First, self.Deck5Second,
                  self.Deck6VSCount, self.Deck6First, self.Deck6Second, self.Deck7VSCount, self.Deck7First,
                  self.Deck7Second, self.Deck8VSCount, self.Deck8First, self.Deck8Second]
        for obj in labels:
            button_map[obj.text()] = obj
            b_text.append(obj.text())
            obj.setText('')

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
        self.status_list = [self.stelfr, self.stroyalr, self.stwitchr, self.stbishopr, self.stdragonr,
                            self.stnecror, self.stvampr, self.stnemer]
        self.status_list_u = [self.stelfu, self.stroyalu, self.stwitchu, self.stbishopu, self.stdragonu,
                              self.stnecrou, self.stvampu, self.stnemeu]
        for i in range(len(self.status_list)):
            self.status_list[i].setFont(QtGui.QFont('맑은 고딕'))
            self.status_list_u[i].setFont(QtGui.QFont('맑은 고딕'))
        self.status = False
        self.status_u = False
        self.pushrefresh.clicked.connect(self.status_check)
        self.radioautoRota.clicked.connect(self.auto_mod)
        self.radioautoUnli.clicked.connect(self.auto_mod)
        path = "./resources/"
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
        self.my_cls = self.my_cls_2 = ""
        self.oppo_cls = ""
        self.mycn = self.oppocn = 0
        self.icons = [foresticon, swordicon, runeicon, havenicon, dragonicon, shadowicon, bloodicon, portalicon]
        self.posts = [forestpost, swordpost, runepost, havenpost, dragonpost, shadowpost, bloodpost, portalpost]
        self.crafts = ["엘프", "로얄", "위치", "비숍", "드래곤", "네크로맨서", "뱀파이어", "네메시스"]
        img1 = Image.open(path + "1st.png")
        img2 = Image.open(path + "2nd.png")
        img_v = Image.open(path + "Victory.png")
        img_d = Image.open(path + "Defeat.png")
        img_t = Image.open(path + "myturn.png")
        self.miscs = [img1, img2, img_v, img_d, img_t]
        self.first = ''
        self.win = ''
        self.mullTaken = False
        self.turnSet = False
        self.oppoSet = False
        self.resultSet = False
        self.yourSet = False
        self.today = ''
        self.ccp = ccp
        self.amod = self.amod_2 = '로테이션'
        self.mydeck = self.mydeck_2 = ''
        self.opdeck = ''
        self.mydeck_card = []
        self.opdeck_card = []
        self.log = []
        self.logtime = ''
        self.timer = None
        self.timer1 = None
        self.al_timer = 5
        # self.conf = None
        self.clslist = ['forest', 'sword', 'rune', 'haven', 'dragon', 'shadow', 'blood', 'portal']
        self.cll = []
        # self.auto_img()
        if len(ccp) == 4:
            self.checkautomini.setCheckState(2)
        else:
            self.checkautomini.setCheckState(0)
        self.comboautocp.addItems(cpl)
        self.comboautocp.setCurrentText(cp)
        self.pushal.clicked.connect(self.autolog)
        self.pushal.setEnabled(False)
        self.lb_alarm.setText('새로고침을 눌러 상태를 확인해주세요.')
        self.pushstop.setEnabled(False)
        self.pushstop.clicked.connect(self.stop)
        self.cb_mydeck.currentIndexChanged.connect(self.auto_mydeck)
        self.cb_opdeck.currentIndexChanged.connect(self.auto_opdeck)
        self.cb_fix.setEnabled(False)

    mod = '로테이션'
    logcp = ccp_check()
    fs = wl = logdate = myjob = myarche = oppojob = oppoarche = deckmod = deckstartdate = deckenddate = ''
    fscheck = wlcheck = deckmodcheck = deckrmodcheck = 0
    df = df2 = df3 = df5 = df6 = all_data()
    sortlim = deckrmod = deckrstartdate = deckrenddate = deckrarche = ''
    al_work = False

    # CpDl 버튼 이벤트
    def cpdl(self):
        self.cp_dl = Sub()
        self.cp_dl.show()

    def dbmenu(self):
        self.db_menu = Sub2()
        self.db_menu.show()

    def dcmenu(self):
        self.dc_menu = Sub3()
        self.dc_menu.show()

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

    # 등록 버튼 / 아키타입 한번 더 로드할것!
    def write_btn(self):
        write_record(self, self.logcp, self.mod, self.myjob, self.myarche,
                     self.oppojob, self.oppoarche, self.fs, self.wl)
        load_data(self)
        self.table_rate()

    # 데이터 삭제 - 최신 1개만
    def erase_data(self):
        conn = sqlite3.connect('log.db')
        cursor = conn.cursor()
        result = cursor.execute("SELECT LogTime FROM log ORDER BY LogTime DESC LIMIT 1")
        edata = result.fetchall()
        cursor.execute("DELETE FROM log WHERE LogTime=?", edata[0])
        conn.commit()
        conn.close()
        load_data(self)
        self.table_rate()

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
        cur.execute("CREATE TABLE log(Date text, CardPack text, Mod TEXT, MyJob text, MyArche text, OppoJob text, OppoArche text, FirstSecond text, WinLose text, LogTime TEXT)")
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
        global button_map
        global b_text
        text = b_text
        spl = range(241, 249)
        for i in range(8):
            if len(df) > i:
                name = df.index[i]
                vs = str(df.iloc[i, 0]) + '전 ' + str(df.iloc[i, 1]) + '승 ' + str(df.iloc[i, 2]) + '패'
                button_map[text[i*3]].setText(vs)
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
                if len(first) == 0:
                    button_map[text[i*3+1]].setText('N/A')
                else:
                    wr1st = '선공 ' + str(round(len(firstwin) * 100 / len(first), 1)) + '%'
                    button_map[text[i*3+1]].setText(wr1st)
                if len(second) == 0:
                    button_map[text[i*3+2]].setText('N/A')
                else:
                    wr2nd = '후공 ' + str(round(len(secondwin) * 100 / len(second), 1)) + '%'
                    button_map[text[i*3+2]].setText(wr2nd)
            else:
                button_map[text[i*3]].setText('')
                button_map[text[i*3+1]].setText('')
                button_map[text[i*3+2]].setText('')

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
        if fwin >= 30:
            for i, rect in enumerate(rects1):
                ax.text(0.95 * rect.get_width(), rect.get_y() + rect.get_height() / 2.0, str(fwin) + '%',
                        ha='right', va='center')
        else:
            for i, rect in enumerate(rects1):
                ax.text(rect.get_width() + 2, rect.get_y() + rect.get_height() / 2.0, str(fwin) + '%',
                        ha='left', va='center')
        if swin >= 30:
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

    def status_check(self):
        self.status = self.status_u = True
        with open("classifier.json", "r", encoding='UTF-8') as clsf:
            classifier = json.load(clsf)
        mods = ['로테이션', '언리미티드']
        st_lists = [self.status_list, self.status_list_u]
        for mod, st_list in zip(mods, st_lists):
            for i in range(len(st_list)):
                if classifier[mod][self.clslist[i]]['status'] == 'comp':
                    st_list[i].setText('OK')
                    st_list[i].setStyleSheet('color: green')
                else:
                    st_list[i].setText('FAIL')
                    st_list[i].setStyleSheet('color: red')
                    if mod == '로테이션':
                        self.status = False
                    else:
                        self.status_u = False

        """
        for i in range(len(self.status_list)):
            if classifier[self.amod][self.clslist[i]]['status'] == 'comp':
                self.status_list[i].setText('OK')
                self.status_list[i].setStyleSheet('color: green')
            else:
                self.status_list[i].setText('FAIL')
                self.status_list[i].setStyleSheet('color: red')
                self.status = False
        """
        self.al_enable()

    def auto_mod(self):
        self.cb_fix.setChecked(False)
        mod = ''
        if self.radioautoRota.isChecked():
            mod = '로테이션'
        elif self.radioautoUnli.isChecked():
            mod = '언리미티드'
        self.amod = mod
        self.al_enable()

    def al_enable(self):
        if self.amod == '로테이션' and self.status:
            self.lb_alarm.setText('기록을 시작하려면 시작 버튼을 누르세요.')
            self.pushal.setEnabled(True)
            self.auto_img(self.amod)
        elif self.amod == '언리미티드' and self.status_u:
            self.lb_alarm.setText('기록을 시작하려면 시작 버튼을 누르세요.')
            self.pushal.setEnabled(True)
            self.auto_img(self.amod)
        else:
            self.lb_alarm.setText('메뉴로 들어가 덱 분류를 확인해주세요.')
            self.pushal.setEnabled(False)

    def auto_img(self, mod):
        # 카드 이미지 읽기
        if mod == '로테이션':
            path = 'rota/'
        else:
            path = 'unli/'
        cpath = './cards/' + path
        # self.conf = configparser.ConfigParser()
        # self.conf.read(cpath + 'config.ini', encoding='UTF-8')
        self.cll = []
        for cls in self.clslist:
            cnpath = cpath + cls + '/'
            cn = os.listdir(cnpath)
            clist = []
            for card_file in cn:
                card = cnpath + card_file
                name = card_file.split('.')[0]
                cimg = Image.open(card)
                clist.append((name, cimg))
            self.cll.append(clist)

    def auto_cp(self):
        ccp = self.comboautocp.currentText()
        if self.checkautomini.isChecked():
            ccp = ccp + 'm'
        self.ccp = ccp

    def autolog(self):
        self.pushal.setEnabled(False)
        self.pushstop.setEnabled(True)
        self.al_work = True
        self.lb_alarm.setText('데이터 수집 중')
        hwnd = win32gui.FindWindow(None, 'Shadowverse')
        try:
            left, top, right, bot = win32gui.GetClientRect(hwnd)
        except:
            print('창을 찾을 수 없습니다.')
            sys.exit()

        w = right - left
        h = bot - top

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
            print('창이 최소화되어있습니다.')
            sys.exit()

        win32gui.DeleteObject(saveBitMap.GetHandle())
        saveDC.DeleteDC()
        mfcDC.DeleteDC()
        win32gui.ReleaseDC(hwnd, hwndDC)

        if not self.mullTaken:
            # 선후공 체크
            if not locate(self.miscs[0], im, grayscale=True, confidence=0.90, region=(0, 0, 200, 150)) is None:
                self.first = '선공'
                self.turnSet = True
            elif not locate(self.miscs[1], im, grayscale=True, confidence=0.90, region=(0, 0, 200, 150)) is None:
                self.first = '후공'
                self.turnSet = True
            # 상대 직업 체크
            if self.turnSet:
                for icon in self.icons:
                    if not locate(icon, im, grayscale=True, confidence=0.90, region=(1000, 0, 280, 100)) is None:
                        self.oppocn = self.icons.index(icon)
                        self.oppo_cls = self.crafts[self.oppocn]
                        self.oppoSet = True
                        break
            self.mullTaken = self.turnSet and self.oppoSet
        elif self.mullTaken and not self.yourSet:
            # 내 직업 체크
            for post in self.posts:
                if not locate(post, im, grayscale=True, confidence=0.90, region=(0, 490, 220, 100)) is None:
                    self.mycn = self.posts.index(post)
                    self.my_cls = self.crafts[self.mycn]
                    self.yourSet = True
        elif self.mullTaken and self.yourSet:
            # 카드 체크
            if not locate(self.miscs[4], im, grayscale=True, confidence=0.9, region=(1110, 330, 110, 50)) is None:
                card_img = self.cll[self.mycn]
                for name, card in card_img:
                    if not locate(card, im, grayscale=True, confidence=0.63, region=(530, 140, 230, 60)) is None:
                        self.mydeck_card.append(name)
                        print(self.mydeck_card)
                        time.sleep(0.40)
            else:
                card_img = self.cll[self.oppocn]
                for name, card in card_img:
                    if not locate(card, im, grayscale=True, confidence=0.63, region=(530, 140, 230, 60)) is None:
                        self.opdeck_card.append(name)
                        print(self.opdeck_card)
                        time.sleep(0.40)
            # 승패 체크
            if not locate(self.miscs[3], im, grayscale=False, confidence=0.97, region=(150, 55, 240, 25)) is None:
                self.win = '패'
                self.resultSet = True
            elif not locate(self.miscs[2], im, grayscale=False, confidence=0.97, region=(150, 55, 240, 25)) is None:
                self.win = '승'
                self.resultSet = True
            # 결과 출력 및 초기화
            if self.resultSet:
                if self.amod == self.amod_2 and self.my_cls == self.my_cls_2 and self.cb_fix.isChecked():
                    self.mydeck = self.mydeck_2
                else:
                    self.cb_fix.setChecked(False)
                    self.mydeck = self.deck_check(self.mydeck_card, self.mycn)
                self.opdeck = self.deck_check(self.opdeck_card, self.oppocn)
                self.today = datetime.now().strftime('%Y-%m-%d')
                self.logtime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.lb_day.setText(self.today)
                self.lb_cp.setText(self.ccp)
                self.lb_mod.setText(self.amod)
                self.lb_fs.setText(self.first)
                self.lb_mycls.setText(self.my_cls)
                self.lb_opcls.setText(self.oppo_cls)
                self.lb_wl.setText(self.win)
                self.lb_logtime.setText(self.logtime)
                mydecklist = d_check(self.amod, self.ccp, self.my_cls)
                self.cb_mydeck.clear()
                self.cb_mydeck.addItems(mydecklist)
                self.cb_mydeck.setCurrentText(self.mydeck)
                opdecklist = d_check(self.amod, self.ccp, self.oppo_cls)
                self.cb_opdeck.clear()
                self.cb_opdeck.addItems(opdecklist)
                self.cb_opdeck.setCurrentText(self.opdeck)
                self.cb_fix.setEnabled(True)
                self.timer.cancel()
                self.alarm()
                return

        self.timer = threading.Timer(0.05, self.autolog)
        self.timer.start()

    def deck_check(self, card_list, cls_num):
        with open("classifier.json", "r", encoding='UTF-8') as clsf:
            classifier = json.load(clsf)
        print(card_list, cls_num)
        cls = self.clslist[cls_num]
        cd_list = classifier[self.amod][cls]
        d_type = []
        for card in card_list:
            try:
                d_type.append(cd_list[card])
            except:
                d_type.append('기타')
        print(d_type)
        i = 1
        deck = ''
        while i:
            arche = cd_list[str(i)]
            if arche == '기타' or arche in d_type:
                deck = arche
                break
            i += 1
        return deck

    def auto_mydeck(self):
        self.mydeck = self.cb_mydeck.currentText()

    def auto_opdeck(self):
        self.opdeck = self.cb_opdeck.currentText()

    def alarm(self):
        if self.al_timer == 0:
            write_record(self, self.ccp, self.amod, self.my_cls, self.mydeck, self.oppo_cls, self.opdeck,
                         self.first, self.win)
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
            self.amod_2 = self.amod
            self.my_cls_2 = self.my_cls
            self.mydeck_2 = self.mydeck
            self.first = ''
            self.win = ''
            self.mullTaken = False
            self.turnSet = False
            self.oppoSet = False
            self.resultSet = False
            self.yourSet = False
            self.my_cls = ""
            self.mydeck = ""
            self.mydeck_card = []
            self.oppo_cls = ""
            self.opdeck = ""
            self.opdeck_card = []
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
            load_data(self)
            self.table_rate()
            self.lb_alarm.setText('기록이 저장되었습니다.\n3초 후 자동시작')
            self.al_timer = 5
            self.timer = threading.Timer(3, self.autolog)
            self.timer.start()
            return
        text = '{}초 후 기록을 자동으로 저장합니다.'.format(self.al_timer)
        self.lb_alarm.setText(text)
        self.al_timer -= 1
        self.timer1 = threading.Timer(1, self.alarm)
        self.timer1.start()

    def stop(self):
        self.timer.cancel()
        self.timer1.cancel()
        self.al_work = False
        self.pushal.setEnabled(True)
        self.pushstop.setEnabled(False)
        self.lb_alarm.setText('기록 중지')

    def closeEvent(self, event):
        if self.al_work:
            self.timer.cancel()
            self.timer1.cancel()
            event.accept()
        else:
            event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = Form()
    myWindow.show()
    sys.exit(app.exec_())
