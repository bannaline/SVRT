from PyQt5.QtWidgets import QWidget, QApplication, QTableWidgetItem
from PyQt5 import QtCore
import sys
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc, style
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import pandas as pd
from statics_ts import Ui_Form
import configparser


form = Ui_Form


class Static(QWidget, form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.trans = QtCore.QTranslator(self)
        self.retranslateUi(self)

        config = configparser.ConfigParser()
        config.read("config.ini")
        self.loc = config["locale"]["locale"]

        self.retrans_code(self.loc)

        self.cbMydeck.currentIndexChanged.connect(self.my_deck_update)
        self.cbOppocls.addItems(self.oppo_cls_lists)
        self.cbOppocls.setCurrentIndex(0)
        self.cbOppocls.currentIndexChanged.connect(self.oppo_cls_update)
        self.cbOppodeck.setEnabled(False)
        self.cbOppodeck.currentIndexChanged.connect(self.oppo_deck_update)
        self.df = pd.DataFrame([])
        self.tablesta.setColumnWidth(2, 51)

        self.figure1 = plt.figure(3, constrained_layout=True)
        self.canvas1 = FigureCanvas(self.figure1)
        self.staticLayout.addWidget(self.canvas1)
        fname = ""
        if self.loc == "ko_KR" or self.loc == "en_US":
            fname = "c:/Windows/Fonts/malgun.ttf"
        elif self.loc == "ja_JP":
            fname = "c:/Windows/Fonts/meiryo.ttc"
        self.font_name = font_manager.FontProperties(fname=fname).get_name()
        rc('font', family=self.font_name)
        font_manager.FontProperties().set_size('xx-small')
        style.use('ggplot')

        self.lb_result.setText("")

    my_deck = oppo_deck = ""
    my_deck_lists = []
    oppo_deck_lists = []
    df2 = df3 = df_final = pd.DataFrame([])
    odu = True
    cls_list = ["엘프", "로얄", "위치", "비숍", "드래곤", "네크로맨서", "뱀파이어", "네메시스"]
    win_lose = ["승", "패"]
    fir_sec = ["선공", "후공"]

    def retrans_code(self, locale_code):
        loc_path = "./locales/statics_" + locale_code + ".qm"
        self.trans.load(loc_path)
        QApplication.instance().installTranslator(self.trans)
        self.retranslateUi(Static)
        self.retrans_text(locale_code)

    def retrans_text(self, locale_code):
        if locale_code == "ko_KR":
            self.oppo_cls_lists = ["모든 직업", "엘프", "로얄", "위치", "비숍", "드래곤", "네크로맨서", "뱀파이어", "네메시스"]
            self.oppo_cls = self.oppo_cls_lists[0]
            self.cls_list = ["엘프", "로얄", "위치", "비숍", "드래곤", "네크로맨서", "뱀파이어", "네메시스"]
            self.win_lose = ["승", "패"]
            self.fir_sec = ["선공", "후공"]
            self.msgs = ["모든 덱", "전적 없음", "상대 직업 분포", "상대 덱 분포", "턴", "횟수", "종료 턴 분포", "{}턴: {}승",
                         "{}턴: {}패"]
        elif locale_code == "ja_JP":
            self.oppo_cls_lists = ["すべてのクラス", "エルフ", "ロイヤル", "ウィッチ", "ビショップ", "ドラゴン", "ネクロマンサー",
                                   "ヴァンパイア", "ネメシス"]
            self.oppo_cls = self.oppo_cls_lists[0]
            self.cls_list = ["エルフ", "ロイヤル", "ウィッチ", "ビショップ", "ドラゴン", "ネクロマンサー", "ヴァンパイア", "ネメシス"]
            self.win_lose = ["勝", "敗"]
            self.fir_sec = ["先攻", "後攻"]
            self.msgs = ["すべてのデッキ", "記録なし", "相手のクラスの分布", "相手のデッキの分布", "ターン", "回数", "終了ターンの分布",
                         "{}ターン: {}勝", "{}ターン: {}敗"]
        else:
            self.oppo_cls_lists = ["All crafts", "Forest", "Sword", "Rune", "Haven", "Dragon", "Shadow", "Blood",
                                   "Portal"]
            self.oppo_cls = self.oppo_cls_lists[0]
            self.cls_list = ["Forest", "Sword", "Rune", "Haven", "Dragon", "Shadow", "Blood", "Portal"]
            self.win_lose = ["Win", "Lose"]
            self.fir_sec = ["1st", "2nd"]
            self.msgs = ["All decks", "No record", "Opponent's craft distribution", "Opponent's deck distribution",
                         "Turn", "number of times", "End turn distribution", "Turn {}: {} Wins", "Turn {}: {} Loses"]

    def reload(self):
        self.oppo_cls = self.oppo_cls_lists[0]
        self.cbOppocls.setCurrentIndex(0)
        self.cbOppodeck.clear()
        self.cbOppodeck.setEnabled(False)
        self.oppo_deck = ""
        df1 = self.df
        self.df2 = df1[df1['MyArche'].isin([self.my_deck])]
        self.oppo_cls_update()

    def my_deck_init(self):
        deck = self.my_deck
        self.cbMydeck.clear()
        self.cbMydeck.addItems(self.my_deck_lists)
        self.cbMydeck.setCurrentText(deck)

    def my_deck_update(self):
        self.my_deck = self.cbMydeck.currentText()
        self.reload()

    def oppo_cls_update(self):
        self.oppo_cls = self.cbOppocls.currentText()
        if not self.oppo_cls == self.oppo_cls_lists[0]:
            self.cbOppodeck.setEnabled(True)
            df1 = self.df2
            df2 = df1[df1['OppoJob'].isin([self.oppo_cls])]
            self.df_final = df2
            df3 = df2.drop_duplicates(['OppoArche'])
            lists = sorted(list(set(df3['OppoArche'])))
            self.oppo_deck_lists = [self.msgs[0]] + lists
            self.odu = False
            self.cbOppodeck.clear()
            self.odu = False
            self.cbOppodeck.addItems(self.oppo_deck_lists)
            self.cbOppodeck.setCurrentIndex(0)
            self.table_update()
        else:
            self.cbOppodeck.setEnabled(False)
            self.cbOppodeck.clear()
            self.df_final = self.df2
            self.table_update()

    def oppo_deck_update(self):
        self.oppo_deck = self.cbOppodeck.currentText()
        if self.odu:
            df1 = self.df2
            df2 = df1[df1['OppoArche'].isin([self.oppo_deck])]
            self.df_final = df2
            self.table_update()
        else:
            self.odu = True

    def table_update(self):
        if len(self.df_final) == 0:
            for i in range(3):
                for j in range(3):
                    item = QTableWidgetItem()
                    item.setText("")
                    item.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
                    self.tablesta.setItem(i, j, item)
            self.lb_result.setText(self.msgs[1])
            self.figure1.clear()
            self.canvas1.draw()
        else:
            self.lb_result.setText("")
            df = self.df_final
            dfw = df[df['WinLose'].isin([self.win_lose[0]])]
            dfw1 = dfw[dfw['FirstSecond'].isin([self.fir_sec[0]])]
            dfl = df[df['WinLose'].isin([self.win_lose[1]])]
            dfl1 = dfl[dfl['FirstSecond'].isin([self.fir_sec[0]])]
            fw = len(dfw1)
            fl = len(dfl1)
            if fw+fl == 0:
                fwr = "N/A"
            else:
                fwr = str(round(fw*100/(fw+fl), 1)) + '%'
            sw = len(dfw) - len(dfw1)
            sl = len(dfl) - len(dfl1)
            if sw+sl == 0:
                swr = "N/A"
            else:
                swr = str(round(sw * 100 / (sw + sl), 1)) + '%'
            aw = len(dfw)
            al = len(dfl)
            awr = str(round(aw * 100 / (aw + al), 1)) + '%'
            table = [[fw, fl, fwr], [sw, sl, swr], [aw, al, awr]]

            for i, data_line in enumerate(table):
                for j, data in enumerate(data_line):
                    item = QTableWidgetItem()
                    item.setText(str(data))
                    item.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
                    self.tablesta.setItem(i, j, item)
            self.figure1.clear()
            self.graph(dfw, dfl)

    def graph(self, dfw, dfl):
        axes = self.figure1.subplots(1, 2)
        ratio = []
        labels = []
        explode = []
        colors = []
        df = self.df_final
        if self.oppo_cls == self.oppo_cls_lists[0]:
            cls_colors = ['limegreen', 'gold', 'royalblue', 'whitesmoke',
                          'darkorange', 'darkorchid', 'crimson', 'lightskyblue']
            for cls, color in zip(self.cls_list, cls_colors):
                df1 = df[df['OppoJob'].isin([cls])]
                if len(df1) != 0:
                    ratio.append(len(df1))
                    labels.append(cls)
                    explode.append(0.1)
                    colors.append(color)
            axes[0].pie(ratio, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90, explode=explode,
                        textprops={'fontsize': 9})
            axes[0].set_title(self.msgs[2], fontdict={'fontsize': 11}, pad=10)
        elif self.oppo_deck == self.msgs[0]:
            for deck in self.oppo_deck_lists:
                df1 = df[df['OppoArche'].isin([deck])]
                if len(df1) != 0:
                    ratio.append(len(df1))
                    labels.append(deck)
                    explode.append(0.1)
            axes[0].pie(ratio, labels=labels, autopct='%1.1f%%', startangle=90, explode=explode,
                        textprops={'fontsize': 9})
            axes[0].set_title(self.msgs[3], fontdict={'fontsize': 11}, pad=10)
        else:
            axes[0].pie([100], labels=[self.oppo_deck], autopct='%1.1f%%', startangle=90,
                        textprops={'fontsize': 9})
            axes[0].set_title(self.msgs[3], fontdict={'fontsize': 11}, pad=10)

        dfwt = dfw["Turn"]
        dflt = dfl["Turn"]
        turn_w = []
        turn_l = []
        labels_t = []
        turn_w.append(len(dfwt[dfwt <= 3]))
        turn_l.append(len(dflt[dflt <= 3]))
        labels_t.append('3-')
        for i in range(4, 12):
            turn_w.append(len(dfwt[dfwt == i]))
            turn_l.append(len(dflt[dflt == i]))
            labels_t.append(str(i))
        turn_w.append(len(dfwt[dfwt >= 12]))
        turn_l.append(len(dflt[dflt >= 12]))
        labels_t.append('12+')

        import numpy
        turn_x = numpy.arange(len(labels_t))
        win = axes[1].bar(turn_x - 0.2, turn_w, label=self.win_lose[0], width=0.4, color='red')
        lose = axes[1].bar(turn_x + 0.2, turn_l, label=self.win_lose[1], width=0.4, color='lightskyblue')
        axes[1].set_xticks(turn_x)
        axes[1].set_xticklabels(labels_t)
        axes[1].legend(fontsize=7, loc='upper left')
        axes[1].set_xlabel(self.msgs[4], fontsize=9)
        axes[1].set_ylabel(self.msgs[5], fontsize=9)
        axes[1].set_ylim(0, max(turn_w + turn_l + [5]) + 1)
        axes[1].set_title(self.msgs[6], fontdict={'fontsize': 11}, pad=10)

        import mplcursors

        def cursor1_annotations(sel):
            x, y, width, height = sel.artist[sel.target.index].get_bbox().bounds
            sel.annotation.set_text(self.msgs[7].format(labels_t[sel.target.index], int(sel.target[1])))
            sel.annotation.get_bbox_patch().set(fc="lightsalmon", alpha=0.9)
            sel.annotation.xy = (x + width / 2, y + height)
            for s in crs2.selections:
                crs2.remove_selection(s)

        def cursor2_annotations(sel):
            x, y, width, height = sel.artist[sel.target.index].get_bbox().bounds
            sel.annotation.set_text(self.msgs[8].format(labels_t[sel.target.index], int(sel.target[1])))
            sel.annotation.get_bbox_patch().set(fc="powderblue", alpha=0.9)
            sel.annotation.xy = (x + width / 2, y + height)
            for s in crs1.selections:
                crs1.remove_selection(s)

        crs1 = mplcursors.cursor(win, hover=2)
        crs1.connect("add", cursor1_annotations)
        crs2 = mplcursors.cursor(lose, hover=2)
        crs2.connect("add", cursor2_annotations)
        self.canvas1.draw()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = Static()
    myWindow.show()
    sys.exit(app.exec_())
