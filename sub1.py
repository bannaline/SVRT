from PyQt5.QtWidgets import QApplication, QDialog, QInputDialog, QMessageBox
from PyQt5 import uic
from data_manage import d_check, ccp_check, cp_list
import sys
import json
import re


sub_form = uic.loadUiType("cpdl.ui")[0]
cls = ['엘프', '로얄', '위치', '비숍', '네크로맨서', '드래곤', '뱀파이어', '네메시스']
lw = []
pb = []


class Sub(QDialog, sub_form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.radiorota.clicked.connect(self.cpdl_mod)
        self.radiounli.clicked.connect(self.cpdl_mod)
        self.mod = '로테이션'
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
        global cls
        global lw
        lw = [self.listelf, self.listroyal, self.listwitch, self.listbishop, self.listnec,
              self.listdra, self.listvamp, self.listneme]
        self.list_renew()

        global pb
        pb = [self.pushelfp, self.pushroyalp, self.pushwitchp, self.pushbishopp,
              self.pushnecp, self.pushdrap, self.pushvampp, self.pushnemep]
        for i in range(len(pb)):
            pb[i].setText('추가')
            pb[i].clicked.connect(lambda state, x=i: self.plus(x))

        mb = [self.pushelfm, self.pushroyalm, self.pushwitchm, self.pushbishopm,
              self.pushnecm, self.pushdram, self.pushvampm, self.pushnemem]
        for i in range(len(mb)):
            mb[i].setText('삭제')
            mb[i].clicked.connect(lambda state, x=i: self.minus(x))

        rb = [self.pushelfr, self.pushroyalr, self.pushwitchr, self.pushbishopr,
              self.pushnecr, self.pushdrar, self.pushvampr, self.pushnemer]
        for i in range(len(rb)):
            rb[i].setText('수정')
            rb[i].clicked.connect(lambda state, x=i: self.replace(x))

    mod = cp = ''
    cgs_check = False
    cls = ['엘프', '로얄', '위치', '비숍', '네크로맨서', '드래곤', '뱀파이어', '네메시스']
    with open("decklist.json", "r", encoding='UTF-8') as dli:
        all_dl = json.load(dli)
    fdl = {}

    def ncp(self):
        d_title = '새로운 카드팩 추가'
        d_text = '추가할 카드팩 약자를 입력하세요.(ex. ROB, FOH 등)'
        text, ok = QInputDialog.getText(self, d_title, d_text)
        if ok:
            p = re.compile('^a-zA-Z')
            m = p.match(text)
            if m or len(text) != 3:
                QMessageBox.warning(self, '카드팩 이름 오류', '알파벳 3글자로 입력해주세요.', QMessageBox.Ok, QMessageBox.Ok)
            else:
                text = text.upper()
                self.cp_add(text)

    def cp_add(self, a):
        cpl = cp_list()
        cpl.append(a)
        with open("cplist.json", "w") as file:
            file.write(json.dumps(cpl, indent='\t'))
        self.combocp.addItem(a)
        self.combocp.setCurrentText(a)
        self.checkmini.setCheckState(0)
        self.cpdl_cp()

    def cp_del(self):
        reply = QMessageBox.question(self, '카드팩 삭제', '마지막 카드팩을 삭제합니다.',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
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
            del self.all_dl[self.mod][dcp]
            del self.all_dl[self.mod][dcpm]
            with open('decklist.json', 'w', encoding='UTF-8') as file:
                file.write(json.dumps(self.all_dl, ensure_ascii=False, indent='\t'))
            self.cpdl_cp()

    def cp_m(self):
        reply = QMessageBox.question(self, '현재 카드팩 변경', '지금 선택된 카드팩을 현재 카드팩으로 설정합니다.',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            ccp = self.combocp.currentText()
            if self.checkmini.isChecked():
                ccp = ccp + 'm'
            self.all_dl['CCP'] = ccp
            with open('decklist.json', 'w', encoding='UTF-8') as file:
                file.write(json.dumps(self.all_dl, ensure_ascii=False, indent='\t'))
            clsf_init = {
                "로테이션": {
                    "sword": {"status": "init"},
                    "rune": {"status": "init"},
                    "forest": {"status": "init"},
                    "haven": {"status": "init"},
                    "dragon": {"status": "init"},
                    "shadow": {"status": "init"},
                    "blood": {"status": "init"},
                    "portal": {"status": "init"},
                },
                "언리미티드": {
                    "sword": {"status": "init"},
                    "rune": {"status": "init"},
                    "forest": {"status": "init"},
                    "haven": {"status": "init"},
                    "dragon": {"status": "init"},
                    "shadow": {"status": "init"},
                    "blood": {"status": "init"},
                    "portal": {"status": "init"},
                }
            }
            with open('classifier.json', 'w', encoding='UTF-8') as file:
                file.write(json.dumps(clsf_init, ensure_ascii=False, indent='\t'))

    def list_renew(self):
        global lw
        error_check = False
        for i in range(len(lw)):
            dl = d_check(self.mod, self.cp, cls[i])
            if dl:
                lw[i].clear()
                for deck in dl:
                    lw[i].addItem(deck)
                lw[i].setCurrentRow(0)
                lw[i].model().rowsMoved.connect(self.dl_changes)
            else:
                self.new_cp()
        if error_check:
            QMessageBox.warning(self, '주의', '덱이 없는 직업이 존재합니다.', QMessageBox.Ok, QMessageBox.Ok)

    def new_cp(self):
        ndl = {'엘프': ['기타'], '로얄': ['기타'], '위치': ['기타'], '비숍': ['기타'],
               '드래곤': ['기타'], '네크로맨서': ['기타'], '뱀파이어': ['기타'], '네메시스': ['기타']}
        self.all_dl['로테이션'][self.cp] = ndl
        self.all_dl['언리미티드'][self.cp] = ndl
        with open('decklist.json', 'w', encoding='UTF-8') as file:
            file.write(json.dumps(self.all_dl, ensure_ascii=False, indent='\t'))
        self.list_renew()

    def save_renew(self):
        if self.cgs_check:
            self.all_dl[self.mod][self.cp] = self.fdl
        with open('decklist.json', 'w', encoding='UTF-8') as file:
            file.write(json.dumps(self.all_dl, ensure_ascii=False, indent='\t'))
        self.cgs_check = False

    def cpdl_mod(self):
        if self.cgs_check:
            reply = QMessageBox.question(self, '저장', '변경사항이 있습니다. 저장하시겠습니까?',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            if reply == QMessageBox.Yes:
                self.save_renew()
            elif reply == QMessageBox.No:
                self.cgs_check = False
        if self.radiorota.isChecked():
            self.mod = '로테이션'
        elif self.radiounli.isChecked():
            self.mod = '언리미티드'
        self.cpdl_cp()

    def cpdl_cp(self):
        if self.cgs_check:
            reply = QMessageBox.question(self, '저장', '변경사항이 있습니다. 저장하시겠습니까?',
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
        global lw
        cla = self.cls[i]
        d_title = '{} 덱 추가'.format(cla)
        d_text = '추가할 {} 덱을 입력하세요.'.format(cla)
        text, ok = QInputDialog.getText(self, d_title, d_text)
        if ok:
            lw[i].addItem(text)
            self.dl_changes()

    def minus(self, i):
        global lw
        item = lw[i].currentRow()
        lw[i].takeItem(item)
        self.dl_changes()

    def replace(self, i):
        global lw
        cla = self.cls[i]
        item = lw[i].currentItem()
        cd = item.text()
        d_title = '{} 덱 수정'.format(cla)
        d_text = '{}의 덱 이름을 수정합니다.'.format(cd)
        text, ok = QInputDialog.getText(self, d_title, d_text)
        if ok:
            item.setText(text)
            self.dl_changes()

    def dl_changes(self):
        fdl = {}
        global cls
        global lw
        for i in range(len(lw)):
            list_cls = lw[i].count()
            deck_cls = []
            for j in range(list_cls):
                deck = lw[i].item(j).text()
                deck_cls.append(deck)
            fdl[cls[i]] = deck_cls
        self.changes_check()
        self.fdl = fdl

    def changes_check(self):
        if self.cgs_check:
            pass
        else:
            self.cgs_check = True

    def closeEvent(self, event):
        ccp = ccp_check()
        if self.combocp.findText(ccp[:3]) == -1:
            QMessageBox.warning(self, '주의', '존재하지 않는 카드팩이 현재 카드팩으로 설정되어 있습니다.',
                                QMessageBox.Ok, QMessageBox.Ok)
            event.ignore()
            return
        if self.cgs_check:
            reply = QMessageBox.question(self, '주의', '변경사항이 있습니다. 저장하시겠습니까?',
                                         QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Yes)
            if reply == QMessageBox.Yes:
                self.save_renew()
                event.accept()
            elif reply == QMessageBox.No:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = Sub()
    myWindow.show()
    sys.exit(app.exec_())
