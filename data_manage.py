from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox
from PyQt5 import QtCore
import sqlite3
import pandas as pd
import json
from datetime import datetime


# 데이터 로드
def load_data(self):
    conn = sqlite3.connect('log.db')
    cursor = conn.cursor()
    result = cursor.execute("SELECT Date, CardPack, Mod, MyJob, MyArche, OppoJob, OppoArche, FirstSecond, WinLose, Turn FROM log ORDER BY LogTime DESC LIMIT 10")
    rows = result.fetchall()
    row_cnt_query = cursor.execute("SELECT * FROM log")
    row_cnt = row_cnt_query.fetchall()
    sb_msg = '{0}개 기록 검색됨'.format(len(row_cnt))
    if len(row_cnt) < 10:
        self.tableRecord.setRowCount(len(row_cnt))
    for i, row in enumerate(rows):
        for j, data in enumerate(row):
            if i == 0:
                last_record(self, j, data)
            item = QTableWidgetItem()
            item.setText(str(data))
            item.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
            self.tableRecord.setItem(i, j, item)
    conn.close()
    self.statusBar().showMessage(sb_msg)


def last_record(self, j, data):
    data = str(data)
    if j == 2:
        if data == "로테이션":
            self.radioRecRota.setChecked(True)
        elif data == "언리미티드":
            self.radioRecUnli.setChecked(True)
        self.rad_mod()

    if j == 3:
        mycls = ['로얄', '위치', '엘프', '비숍', '드래곤', '네크로맨서', '뱀파이어', '네메시스']
        mycls_btn = [self.radioRoyalMy, self.radioWitchMy, self.radioElfMy, self.radioBishopMy,
                     self.radioDragonMy, self.radioNecroMy, self.radioVampMy, self.radioNemeMy]
        num = mycls.index(data)
        mycls_btn[num].setChecked(True)
        self.radio_myjob()

    if j == 4:
        self.comboArcheMy.setCurrentText(data)
        self.cb_my_arche()

    if j == 5:
        oppocls = ['로얄', '위치', '엘프', '비숍', '드래곤', '네크로맨서', '뱀파이어', '네메시스']
        oppocls_btn = [self.radioRoyalOppo, self.radioWitchOppo, self.radioElfOppo, self.radioBishopOppo,
                       self.radioDragonOppo, self.radioNecroOppo, self.radioVampOppo, self.radioNemeOppo]
        num = oppocls.index(data)
        oppocls_btn[num].setChecked(True)
        self.radio_oppojob()

    if j == 6:
        self.comboArcheOppo.setCurrentText(data)
        self.cb_oppo_arche()

    if j == 7:
        if data == '선공':
            self.radioFirst.setChecked(True)
        elif data == '후공':
            self.radioSecond.setChecked(True)
        self.rad_fs()

    if j == 8:
        if data == '승':
            self.radioWin.setChecked(True)
        elif data == '패':
            self.radioLose.setChecked(True)
        self.rad_wl()

    if j == 9:
        self.comboTurn.setCurrentText(data)
        self.cb_turn()


def write_record(self, a, b, c, d, e, f, g, h, i, j):
    # a is cardpack, b is mod, c is myjob, d is myarche, e is oppojob, f is oppoarche, g is first, h is win, i is type
    date = datetime.today().strftime("%Y-%m-%d")
    logtime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if c == '':
        QMessageBox.about(self, '주의', '내 덱을 선택해주세요.')
        return
    elif e == '':
        QMessageBox.about(self, '주의', '상대 덱을 선택해주세요.')
        return
    record = [date, a, b, c, d, e, f, g, h, logtime, i, j]
    conn = sqlite3.connect('log.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO log VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", record)
    conn.commit()
    conn.close()


# 전체 로그데이터
def all_data():
    conn = sqlite3.connect('log.db')
    df = pd.read_sql("SELECT * FROM log", conn)  # 전체 데이터
    conn.close()
    return df


def cp_list():
    with open("cplist.json", "r") as cpl:
        cp = json.load(cpl)
    return cp


def ccp_check():
    with open("decklist.json", "r", encoding='UTF-8') as dli:
        all_dl = json.load(dli)
    ccp = all_dl["CCP"]
    return ccp


def d_check(a, b, c):
    # a is mod, b is card pack, c is class
    with open("decklist.json", "r", encoding='UTF-8') as dli:
        all_dl = json.load(dli)
    try:
        dl = all_dl[a][b][c]
    except KeyError:
        dl = None
    return dl

