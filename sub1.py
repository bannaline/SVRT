from PyQt5.QtWidgets import QApplication, QDialog, QInputDialog, QMessageBox
from PyQt5 import QtCore
from data_manage import d_check, ccp_check, cp_list, locale_load
import sys
import json
import re
from cpdl import Ui_Cpdl


sub_form = Ui_Cpdl


class Sub(QDialog, sub_form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.trans = QtCore.QTranslator(self)
        self.retranslateUi(self)

        cls_ko = ['엘프', '로얄', '위치', '비숍', '네크로맨서', '드래곤', '뱀파이어', '네메시스']
        cls_ja = ["エルフ", "ロイヤル", "ウィッチ", "ビショップ", "ネクロマンサー", "ドラゴン", "ヴァンパイア", "ネメシス"]
        cls_en = ["Forest", "Sword", "Rune", "Haven", "Shadow", "Dragon", "Blood", "Portal"]
        self.clss = [cls_ko, cls_ja, cls_en]

        self.loc = locale_load()
        self.retrans_code(self.loc)

        self.radiorota.clicked.connect(self.cpdl_mod)
        self.radiounli.clicked.connect(self.cpdl_mod)

        self.cp = cp = ccp_check()
        if len(cp) == 4:
            self.checkmini.setCheckState(2)
        else:
            self.checkmini.setCheckState(0)
        cpl = cp_list()
        cp = cp[:3]
        self.combocp.addItems(cpl)
        self.combocp.setCurrentText(cp)
        self.combocp.currentIndexChanged.connect(self.cpdl_cp)
        self.checkmini.stateChanged.connect(self.cpdl_cp)
        self.pushcpa.clicked.connect(self.ncp)
        self.pushcpd.clicked.connect(self.cp_del)
        self.pushcpm.clicked.connect(self.cp_m)
        self.pushsave.clicked.connect(self.save_renew)
        self.lw = [self.listelf, self.listroyal, self.listwitch, self.listbishop, self.listnec,
                   self.listdra, self.listvamp, self.listneme]
        self.list_renew()

        pb = [self.pushelfp, self.pushroyalp, self.pushwitchp, self.pushbishopp,
              self.pushnecp, self.pushdrap, self.pushvampp, self.pushnemep]
        for i in range(len(pb)):
            pb[i].clicked.connect(lambda state, x=i: self.plus(x))

        mb = [self.pushelfm, self.pushroyalm, self.pushwitchm, self.pushbishopm,
              self.pushnecm, self.pushdram, self.pushvampm, self.pushnemem]
        for i in range(len(mb)):
            mb[i].clicked.connect(lambda state, x=i: self.minus(x))

        rb = [self.pushelfr, self.pushroyalr, self.pushwitchr, self.pushbishopr,
              self.pushnecr, self.pushdrar, self.pushvampr, self.pushnemer]
        for i in range(len(rb)):
            rb[i].clicked.connect(lambda state, x=i: self.replace(x))

    cp = ''
    cgs_check = cpm_check = False
    fdl = {}
    locales = ["ko_KR", "ja_JP", "en_US"]
    etcs = [["기타"], ["その他"], ["Others"]]
    mod_col = [["로테이션", "언리미티드"], ["ローテーション", "アンリミテッド"], ["Rotation", "Unlimited"]]

    def retrans_code(self, locale_code):
        loc_path = "./locales/cpdl_" + locale_code + ".qm"
        self.dl_path = "./resources/" + locale_code + "/decklist.json"
        with open(self.dl_path, "r", encoding='UTF-8') as dli:
            self.all_dl = json.load(dli)
        self.trans.load(loc_path)
        QApplication.instance().installTranslator(self.trans)
        self.retranslateUi(Sub)
        self.retrans_text(locale_code)

    def retrans_text(self, locale_code):
        if locale_code == "ko_KR":
            self.mods = ["로테이션", "언리미티드"]
            self.mod = self.mods[0]
            self.cls = self.clss[0]
            self.msgs = ["새로운 카드팩 추가", "추가할 카드팩 약자를 입력하세요.(ex. ROB, DOV 등)", "카드팩 이름 오류",
                         "알파벳 3글자로 입력해주세요.", "카드팩 삭제", "마지막 카드팩을 삭제합니다.", "현재 카드팩 변경",
                         "지금 선택된 카드팩을 현재 카드팩으로 설정합니다.", "주의", "덱이 없는 직업이 존재합니다.",
                         "새로운 카드팩", "이전 카드팩에서 덱 리스트를 가져오겠습니까?", "저장",
                         "변경사항이 있습니다. 저장하시겠습니까?"]
            self.msgs2 = ["{} 덱 추가", "추가할 {} 덱을 입력하세요.", "{} 덱 수정", "{}의 덱 이름을 수정합니다.", "주의",
                          "존재하지 않는 카드팩이 현재 카드팩으로 설정되어 있습니다.", "안정성을 위해 프로그램을 재시작해주십시오."]
            self.etc = ["기타"]
        elif locale_code == "ja_JP":
            self.mods = ["ローテーション", "アンリミテッド"]
            self.mod = self.mods[0]
            self.cls = self.clss[1]
            self.msgs = ["新しいカードパックを追加", "追加するカードパックの略を入力してください。(例. ROB, DOV など)",
                         "カードパックの名前エラー", "アルファベット3文字で入力してください。", "カードパックの削除",
                         "最後のカードパックを削除します。", "現在のカードパックを変更",
                         "今選択されたカードパックを、現在のカードパックに設定します。", "注意", "デッキがないクラスが存在します。",
                         "新しいカードパック", "前のカードパックからデッキリストをインポートしますか？", "保存",
                         "変更があります。保存しますか？"]
            self.msgs2 = ["{} デッキに追加", "追加する {} デッキを入力してください。", "{} デッキの修正",
                          "{}のデッキの名前を変更します。", "注意", "存在していないカードパックが現在のカードパックに設定されています。",
                          "安定性のためのプログラムを再起動してください。"]
            self.etc = ["その他"]
        else:
            self.mods = ["Rotation", "Unlimited"]
            self.mod = self.mods[0]
            self.cls = self.clss[2]
            self.msgs = ["Add new expansion", "Enter the abbreviation of the expansion to be added.(Ex. ROB, DOV, etc.)",
                         "Error - a name of the expansion", "Please enter 3 letters of the alphabet.",
                         "Delete the expansion", "Delete the last expansion.", "Change the current expansion",
                         "Set the selected expansion to the current expansion.", "Warning",
                         "There are crafts without decks.",
                         "New expansion", "Would you like to import the decklist from the last expansion", "Save",
                         "There are changes. Save?"]
            self.msgs2 = ["Add {} deck", "Please enter the {} deck you want to add.", "Rename {} deck",
                          "Rename the {} deck.", "Warning",
                          "A expansion that does not exist is set as a current expansion.",
                          "Please restart the program for stability."]
            self.etc = ["Others"]

    def ncp(self):
        text, ok = QInputDialog.getText(self, self.msgs[0], self.msgs[1])
        if ok:
            p = re.compile('^a-zA-Z')
            m = p.match(text)
            if m or len(text) != 3:
                QMessageBox.warning(self, self.msgs[2], self.msgs[3], QMessageBox.Ok, QMessageBox.Ok)
            else:
                text = text.upper()
                self.cp_add(text)

    def cp_add(self, a):
        cpl = cp_list()
        cpl.append(a)
        with open("cplist.json", "w") as file:
            file.write(json.dumps(cpl, indent='\t'))
        self.combocp.addItem(a)
        self.checkmini.setCheckState(0)
        self.combocp.setCurrentText(a)
        self.cpdl_cp()

    def cp_del(self):
        reply = QMessageBox.question(self, self.msgs[4], self.msgs[5], QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            cpl = cp_list()
            cpi = len(cpl) - 1
            self.combocp.setCurrentIndex(cpi)
            dcp = self.combocp.currentText()
            dcpm = dcp + 'm'
            self.combocp.removeItem(cpi)
            cpl.remove(dcp)
            with open("cplist.json", "w") as file:
                file.write(json.dumps(cpl, indent='\t'))
            for loc, mod_loc in zip(self.locales, self.mod_col):
                path = "./resources/" + loc + "/decklist.json"
                with open(path, "r", encoding='UTF-8') as dli:
                    all_dl = json.load(dli)
                del all_dl[mod_loc[0]][dcp]
                del all_dl[mod_loc[0]][dcpm]
                del all_dl[mod_loc[1]][dcp]
                del all_dl[mod_loc[1]][dcpm]
                with open(path, 'w', encoding='UTF-8') as file:
                    file.write(json.dumps(all_dl, ensure_ascii=False, indent='\t'))
            with open(self.dl_path, 'w', encoding='UTF-8') as file:
                file.write(json.dumps(self.all_dl, ensure_ascii=False, indent='\t'))
            self.cpdl_cp()

    def cp_m(self):
        reply = QMessageBox.question(self, self.msgs[6], self.msgs[7],
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            ccp = self.combocp.currentText()
            if self.checkmini.isChecked():
                ccp = ccp + 'm'
            for loc in self.locales:
                path = "./resources/" + loc + "/decklist.json"
                with open(path, "r", encoding='UTF-8') as dli:
                    all_dl = json.load(dli)
                all_dl['CCP'] = ccp
                with open(path, 'w', encoding='UTF-8') as file:
                    file.write(json.dumps(all_dl, ensure_ascii=False, indent='\t'))
            self.cpm_check = True

    def list_renew(self):
        error_check = False
        for i in range(len(self.lw)):
            dl = d_check(self.mod, self.cp, self.cls[i])
            if dl:
                self.lw[i].clear()
                for deck in dl:
                    self.lw[i].addItem(deck)
                self.lw[i].setCurrentRow(0)
                self.lw[i].model().rowsMoved.connect(self.dl_changes)
            else:
                self.new_cp()
        if error_check:
            QMessageBox.warning(self, self.msgs[8], self.msgs[9], QMessageBox.Ok, QMessageBox.Ok)

    def new_cp(self):
        reply = QMessageBox.question(self, self.msgs[10], self.msgs[11],
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        for loc, etc, mod_loc, cls in zip(self.locales, self.etcs, self.mod_col, self.clss):
            path = "./resources/" + loc + "/decklist.json"
            with open(path, "r", encoding='UTF-8') as dli:
                all_dl = json.load(dli)
            if reply == QMessageBox.Yes and loc == self.loc:
                if len(self.cp) == 4:
                    cp = self.cp[:3]
                else:
                    cp_index = self.combocp.currentIndex() - 1
                    cp = self.combocp.itemText(cp_index) + 'm'
                try:
                    ndl_r = all_dl[mod_loc[0]][cp]
                    ndl_u = all_dl[mod_loc[1]][cp]
                except:
                    cp = cp[:3]
                    ndl_r = all_dl[mod_loc[0]][cp]
                    ndl_u = all_dl[mod_loc[1]][cp]
            else:
                ndl_r = ndl_u = {}
                for x in cls:
                    ndl_r[x] = etc
                    ndl_u[x] = etc
            all_dl[mod_loc[0]][self.cp] = ndl_r
            all_dl[mod_loc[1]][self.cp] = ndl_u
            with open(path, 'w', encoding='UTF-8') as file:
                file.write(json.dumps(all_dl, ensure_ascii=False, indent='\t'))
        self.list_renew()

    def save_renew(self):
        if self.cgs_check:
            self.all_dl[self.mod][self.cp] = self.fdl
        with open(self.dl_path, 'w', encoding='UTF-8') as file:
            file.write(json.dumps(self.all_dl, ensure_ascii=False, indent='\t'))
        self.cgs_check = False

    def cpdl_mod(self):
        if self.cgs_check:
            reply = QMessageBox.question(self, self.msgs[12], self.msgs[13],
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            if reply == QMessageBox.Yes:
                self.save_renew()
            elif reply == QMessageBox.No:
                self.cgs_check = False
        if self.radiorota.isChecked():
            self.mod = self.mods[0]
        elif self.radiounli.isChecked():
            self.mod = self.mods[1]
        self.cpdl_cp()

    def cpdl_cp(self):
        if self.cgs_check:
            reply = QMessageBox.question(self, self.msgs[12], self.msgs[13],
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            if reply == QMessageBox.Yes:
                self.save_renew()
            elif reply == QMessageBox.No:
                self.cgs_check = False
        cp = self.combocp.currentText()
        if self.checkmini.isChecked():
            cp = cp + 'm'
        self.cp = cp
        self.list_renew()

    def plus(self, i):
        cla = self.cls[i]
        d_title = self.msgs2[0].format(cla)
        d_text = self.msgs2[1].format(cla)
        text, ok = QInputDialog.getText(self, d_title, d_text)
        if ok:
            self.lw[i].addItem(text)
            self.dl_changes()

    def minus(self, i):
        item = self.lw[i].currentRow()
        self.lw[i].takeItem(item)
        self.dl_changes()

    def replace(self, i):
        cla = self.cls[i]
        item = self.lw[i].currentItem()
        cd = item.text()
        d_title = self.msgs2[2].format(cla)
        d_text = self.msgs2[3].format(cd)
        text, ok = QInputDialog.getText(self, d_title, d_text)
        if ok:
            item.setText(text)
            self.dl_changes()

    def dl_changes(self):
        fdl = {}
        for i in range(len(self.lw)):
            list_cls = self.lw[i].count()
            deck_cls = []
            for j in range(list_cls):
                deck = self.lw[i].item(j).text()
                deck_cls.append(deck)
            fdl[self.cls[i]] = deck_cls
        self.changes_check()
        self.fdl = fdl

    def changes_check(self):
        if not self.cgs_check:
            self.cgs_check = True

    def ccp_mo_check(self):
        if self.cpm_check:
            QMessageBox.warning(self, self.msgs2[4], self.msgs2[6])
            self.cpm_check = False

    def closeEvent(self, event):
        ccp = ccp_check()
        if self.combocp.findText(ccp[:3]) == -1:
            QMessageBox.warning(self, self.msgs2[4], self.msgs2[5],
                                QMessageBox.Ok, QMessageBox.Ok)
            event.ignore()
            return
        if self.cgs_check:
            reply = QMessageBox.question(self, self.msgs2[4], self.msgs[13],
                                         QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Yes)
            if reply == QMessageBox.Yes:
                self.save_renew()
                self.ccp_mo_check()
                event.accept()
            elif reply == QMessageBox.No:
                self.ccp_mo_check()
                event.accept()
            else:
                event.ignore()
        else:
            self.ccp_mo_check()
            event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = Sub()
    myWindow.show()
    sys.exit(app.exec_())
