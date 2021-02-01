from PyQt5.QtWidgets import QDialog, QMessageBox, QApplication, QTableWidgetItem, QComboBox
from PyQt5 import uic, QtCore, QtGui
import pandas as pd
import sqlite3
import sys
from img_crop import img_scrap
import json
import os
from data_manage import d_check
import threading

sub_form = uic.loadUiType("dc.ui")[0]
DATABASE_PATH = 'database/card_database.db'


class Sub3(QDialog, sub_form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.card_name.returnPressed.connect(self.cardname)
        self.pushname.setDefault(False)
        self.pushname.setAutoDefault(False)
        self.pushname.clicked.connect(self.name_clear)
        self.pushcreating.setDefault(False)
        self.pushcreating.setAutoDefault(False)
        self.pushcreating.clicked.connect(self.creating)
        self.table.cellClicked.connect(self.table_clicked)
        self.cls_list = [self.pushneutral, self.pushelf, self.pushroyal, self.pushwitch, self.pushdragon,
                         self.pushnecro, self.pushvamp, self.pushbishop, self.pushneme]
        for i in range(len(self.cls_list)):
            self.cls_list[i].setDefault(False)
            self.cls_list[i].setAutoDefault(False)
            self.cls_list[i].clicked.connect(lambda state, x=i: self.cls_num(x))

        self.cost_list = [self.pushcost0, self.pushcost1, self.pushcost2, self.pushcost3, self.pushcost4,
                          self.pushcost5, self.pushcost6, self.pushcost7, self.pushcost8, self.pushcost9,
                          self.pushcost10]
        for i in range(len(self.cost_list)):
            self.cost_list[i].setDefault(False)
            self.cost_list[i].setAutoDefault(False)
            self.cost_list[i].clicked.connect(lambda state, x=i: self.cost_num(x))

        self.type_list = [self.pushfollower, self.pushspell, self.pushamulet]
        for i in range(len(self.type_list)):
            self.type_list[i].setDefault(False)
            self.type_list[i].setAutoDefault(False)
            self.type_list[i].clicked.connect(lambda state, x=i: self.type_num(x))

        self.rarity_list = [self.pushbronze, self.pushsilver, self.pushgold, self.pushlegend]
        for i in range(len(self.rarity_list)):
            self.rarity_list[i].setDefault(False)
            self.rarity_list[i].setAutoDefault(False)
            self.rarity_list[i].clicked.connect(lambda state, x=i: self.rarity_num(x))

        self.cls_list_c = [self.pushelfc, self.pushroyalc, self.pushwitchc, self.pushbishopc,
                           self.pushdragonc, self.pushnecroc, self.pushvampc,  self.pushnemec]
        for i in range(len(self.cls_list_c)):
            self.cls_list_c[i].setDefault(False)
            self.cls_list_c[i].setAutoDefault(False)
            self.cls_list_c[i].clicked.connect(lambda state, x=i: self.cls_num_c(x))

        self.lb_list = [self.lb_elf, self.lb_royal, self.lb_witch, self.lb_bishop,
                        self.lb_dragon, self.lb_necro, self.lb_vamp, self.lb_neme]
        self.lb_list_2 = [self.lb_elf_2, self.lb_royal_2, self.lb_witch_2, self.lb_bishop_2,
                          self.lb_dragon_2, self.lb_necro_2, self.lb_vamp_2, self.lb_neme_2]
        for i in range(len(self.lb_list)):
            self.lb_list[i].setFont(QtGui.QFont('맑은 고딕'))
            self.lb_list_2[i].setFont(QtGui.QFont('맑은 고딕'))

        self.rd_rota.clicked.connect(self.mod_change)
        self.rd_unli.clicked.connect(self.mod_change)

        self.cls = ['forest', 'sword', 'rune', 'haven', 'dragon', 'shadow', 'blood', 'portal']
        self.cls_h = ['엘프', '로얄', '위치', '비숍', '드래곤', '네크로맨서', '뱀파이어', '네메시스']

        self.loadc()

        self.listprior.model().rowsMoved.connect(self.prior_change)

        self.pushsavec.clicked.connect(self.save_clsf)

        # 테이블 초기 폭 설정
        self.table.setColumnWidth(0, 40)
        self.table.setColumnWidth(1, 50)
        self.table.setColumnWidth(2, 50)
        self.table.setColumnWidth(3, 170)
        self.table.setColumnWidth(4, 21)
        self.table.setColumnWidth(5, 21)

        self.tablec.setColumnWidth(0, 180)
        self.tablec.setColumnWidth(1, 110)

    conn = sqlite3.connect(DATABASE_PATH)
    df = pd.read_sql("SELECT * FROM cards", conn)  # 전체 데이터
    conn.close()
    df1 = df
    name = ''
    clan = clan_c = 9
    cost = 11
    type = 5
    rarity = 5
    row = 'not'
    clsf = all_dl = ''
    mod = '로테이션'
    modified = False

    def specified(self):
        df = self.df
        df1 = df[df['card_name'].str.contains(self.name)]  # 카드 이름 필터
        # 클래스 필터
        if self.clan < 9:
            df1 = df1[df1['clan'].isin([self.clan])]
        # 코스트 필터
        if self.cost < 10:
            df1 = df1[df1['cost'].isin([self.cost])]
        elif self.cost == 10:
            df1 = df1[df1['cost'] >= 10]
        # 타입 필터
        if self.type == 1:
            df1 = df1[df1['char_type'].isin([self.type])]
        elif self.type == 2:
            df1 = df1[df1['char_type'] == 4]
        elif self.type == 3:
            df1 = df1[(df1['char_type'] == 2) | (df1['char_type'] == 3)]
        # 레어도 필터
        if self.rarity < 5:
            df1 = df1[df1['rarity'].isin([self.rarity])]
        self.row = 'not'
        self.table_show(df1)

    def table_show(self, df):
        df = df.loc[:, ['cost', 'char_type', 'rarity', 'card_name', 'atk', 'life']]
        self.table.setRowCount(len(df))
        type_change = {1: '추종자', 2: '마법진', 3: '마법진', 4: '주문'}
        for i, a in type_change.items():
            df.loc[df['char_type'] == i, 'char_type'] = a
        rarity_change = {1: '브론즈', 2: '실버', 3: '골드', 4: '레전드'}
        for i, a in rarity_change.items():
            df.loc[df['rarity'] == i, 'rarity'] = a

        for i in range(len(df)):
            for j in range(6):
                item = QTableWidgetItem()
                data = str(df.iloc[i, j])
                item.setText(data)
                item.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
                self.table.setItem(i, j, item)

    def table_clicked(self):
        self.row = self.table.currentRow()

    def cardname(self):
        self.name = self.card_name.text()
        self.specified()

    def name_clear(self):
        self.card_name.clear()
        self.cardname()

    def cls_num(self, num):
        for i in range(len(self.cls_list)):
            if i == num and not self.cls_list[i].isChecked():
                self.cls_list[i].setStyleSheet('background:rgb(120, 120, 120)')
                self.cls_list[i].setChecked(False)
                self.clan = 9
            elif i == num and self.cls_list[i].isChecked():
                self.cls_list[i].setStyleSheet('background:rgb(210, 210, 210)')
                self.cls_list[i].setChecked(True)
                self.clan = i
            else:
                self.cls_list[i].setStyleSheet('background:rgb(120, 120, 120)')
                self.cls_list[i].setChecked(False)
        self.specified()

    def cost_num(self, num):
        for i in range(len(self.cost_list)):
            if i == num and not self.cost_list[i].isChecked():
                self.cost_list[i].setStyleSheet('background:rgb(120, 120, 120)')
                self.cost_list[i].setChecked(False)
                self.cost = 11
            elif i == num and self.cost_list[i].isChecked():
                self.cost_list[i].setStyleSheet('background:rgb(210, 210, 210)')
                self.cost_list[i].setChecked(True)
                self.cost = i
            else:
                self.cost_list[i].setStyleSheet('background:rgb(120, 120, 120)')
                self.cost_list[i].setChecked(False)
        self.specified()

    def type_num(self, num):
        for i in range(len(self.type_list)):
            if i == num and not self.type_list[i].isChecked():
                self.type_list[i].setStyleSheet('background:rgb(120, 120, 120)')
                self.type_list[i].setChecked(False)
                self.type = 5
            elif i == num and self.type_list[i].isChecked():
                self.type_list[i].setStyleSheet('background:rgb(210, 210, 210)')
                self.type_list[i].setChecked(True)
                self.type = i + 1
            else:
                self.type_list[i].setStyleSheet('background:rgb(120, 120, 120)')
                self.type_list[i].setChecked(False)
        self.specified()
        
    def rarity_num(self, num):
        for i in range(len(self.rarity_list)):
            if i == num and not self.rarity_list[i].isChecked():
                self.rarity_list[i].setStyleSheet('background:rgb(120, 120, 120)')
                self.rarity_list[i].setChecked(False)
                self.rarity = 5
            elif i == num and self.rarity_list[i].isChecked():
                self.rarity_list[i].setStyleSheet('background:rgb(210, 210, 210)')
                self.rarity_list[i].setChecked(True)
                self.rarity = i + 1
            else:
                self.rarity_list[i].setStyleSheet('background:rgb(120, 120, 120)')
                self.rarity_list[i].setChecked(False)
        self.specified()

    def creating(self):
        if self.row == 'not':
            QMessageBox.warning(self, '주의', '카드를 선택해주세요.', QMessageBox.Ok, QMessageBox.Ok)
            return
        name = self.table.item(self.row, 3).text()
        df = self.df
        card_ids = df.loc[df['card_name'] == name, 'card_id']
        try:
            card_id = card_ids.iloc[0]
        except:
            card_id = card_ids
        card_id = int(card_id)
        scrap = threading.Thread(target=img_scrap, args=(card_id, name))
        scrap.start()
        # img_scrap(card_id, name)

    def cls_num_c(self, num):
        if self.modified:
            reply = QMessageBox.question(self, '저장', '변경사항이 있습니다. 저장하시겠습니까?',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            if reply == QMessageBox.Yes:
                self.save_clsf()
            elif reply == QMessageBox.No:
                self.modified = False
        for i in range(len(self.cls_list_c)):
            if i == num and not self.cls_list_c[i].isChecked():
                self.cls_list_c[i].setStyleSheet('background:rgb(120, 120, 120)')
                self.cls_list_c[i].setChecked(False)
                self.clan_c = 9
            elif i == num and self.cls_list_c[i].isChecked():
                self.cls_list_c[i].setStyleSheet('background:rgb(210, 210, 210)')
                self.cls_list_c[i].setChecked(True)
                self.clan_c = i
            else:
                self.cls_list_c[i].setStyleSheet('background:rgb(120, 120, 120)')
                self.cls_list_c[i].setChecked(False)
        self.clsf_dp()

    def clsf_dp(self):
        self.listprior.clear()
        self.tablec.setRowCount(0)
        if self.clan_c != 9:
            if self.mod == '로테이션':
                path = 'rota/'
            else:
                path = 'unli/'
            cpath = './cards/' + path + self.cls[self.clan_c] + '/'
            card_list_ex = os.listdir(cpath)
            card_list = []
            for card in card_list_ex:
                card_list.append(card.split('.')[0])
            self.table_dp(card_list)

    def table_dp(self, card_list):
        row = 0
        dl = d_check(self.mod, 'ETA', self.cls_h[self.clan_c])
        dl_copy = dl[:]
        for i in range(len(dl)):
            try:
                deck = self.clsf[self.mod][self.cls[self.clan_c]][str(i+1)]
            except:
                deck = dl_copy[0]
            self.listprior.addItem(deck)
            dl_copy.remove(deck)
        for card in card_list:
            self.tablec.insertRow(row)
            item = QTableWidgetItem()
            item.setText(card)
            item.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
            self.tablec.setItem(row, 0, item)
            cb_widget = QComboBox()
            cb_widget.addItems(dl)
            try:
                deck = self.clsf[self.mod][self.cls[self.clan_c]][card]
            except:
                deck = '기타'
            cb_widget.setCurrentText(deck)
            self.tablec.setCellWidget(row, 1, cb_widget)
            cb_widget.currentIndexChanged.connect(self.deck_change)
            row += 1
            if self.clsf[self.mod][self.cls[self.clan_c]]['status'] == 'init':
                self.prior_change()
                self.deck_change()

    def prior_change(self):
        self.modified = True
        num_list = self.listprior.count()
        deck_list = {}
        for i in range(num_list):
            deck = self.listprior.item(i).text()
            deck_list[str(i+1)] = deck
        self.clsf[self.mod][self.cls[self.clan_c]].update(deck_list)

    def deck_change(self):
        self.modified = True
        card_num = self.tablec.rowCount()
        card_list = {}
        row = 0
        for i in range(card_num):
            card = self.tablec.item(row, 0).text()
            deck = self.tablec.cellWidget(row, 1).currentText()
            card_list[card] = deck
            row += 1
        self.clsf[self.mod][self.cls[self.clan_c]].update(card_list)

    def mod_change(self):
        if self.rd_rota.isChecked():
            self.mod = '로테이션'
        else:
            self.mod = '언리미티드'
        self.clsf_dp()

    def loadc(self):
        with open("classifier.json", "r", encoding='UTF-8') as clsft:
            self.clsf = json.load(clsft)
        for i in range(len(self.lb_list)):
            self.status_check(i)

    def status_check(self, i):
        mods = ['로테이션', '언리미티드']
        lb_lists = [self.lb_list, self.lb_list_2]
        for mod, lb_list in zip(mods, lb_lists):
            if self.clsf[mod][self.cls[i]]['status'] == 'init':
                lb_list[i].setText('초기상태')
                lb_list[i].setStyleSheet('color: red')
            elif self.clsf[mod][self.cls[i]]['status'] == 'adj':
                lb_list[i].setText('조정필요')
                lb_list[i].setStyleSheet('color: red')
            else:
                lb_list[i].setText('조정완료')
                lb_list[i].setStyleSheet('color: green')

        """
        if self.clsf[self.mod][self.cls[i]]['status'] == 'init':
            self.lb_list[i].setText('초기상태')
            self.lb_list[i].setStyleSheet('color: red')
        elif self.clsf[self.mod][self.cls[i]]['status'] == 'adj':
            self.lb_list[i].setText('조정필요')
            self.lb_list[i].setStyleSheet('color: red')
        else:
            self.lb_list[i].setText('조정완료')
            self.lb_list[i].setStyleSheet('color: green')
        """

    def save_clsf(self):
        self.clsf[self.mod][self.cls[self.clan_c]]['status'] = 'comp'
        with open('classifier.json', 'w', encoding='UTF-8') as file:
            file.write(json.dumps(self.clsf, ensure_ascii=False, indent='\t'))
        self.modified = False
        self.loadc()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = Sub3()
    myWindow.show()
    sys.exit(app.exec_())
