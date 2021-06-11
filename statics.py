from PyQt5.QtWidgets import QWidget, QApplication, QTableWidgetItem
from PyQt5 import uic, QtCore
import sys
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc, style
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import pandas as pd

form = uic.loadUiType("statics.ui")[0]


class Static(QWidget, form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.my_deck = ""
        self.my_deck_lists = []
        self.cbMydeck.currentIndexChanged.connect(self.my_deck_update)
        self.oppo_cls = "모든 직업"
        self.oppo_deck_lists = []
        oppo_cls_lists = ["모든 직업", "엘프", "로얄", "위치", "비숍", "드래곤", "네크로맨서", "뱀파이어", "네메시스"]
        self.cbOppocls.addItems(oppo_cls_lists)
        self.cbOppocls.setCurrentIndex(0)
        self.cbOppocls.currentIndexChanged.connect(self.oppo_cls_update)
        self.cbOppodeck.setEnabled(False)
        self.cbOppodeck.currentIndexChanged.connect(self.oppo_deck_update)
        self.df = pd.DataFrame([])
        self.tablesta.setColumnWidth(2, 51)

        self.figure1 = plt.figure(3, constrained_layout=True)
        self.canvas1 = FigureCanvas(self.figure1)
        self.staticLayout.addWidget(self.canvas1)
        self.font_name = font_manager.FontProperties(fname="c:/Windows/Fonts/malgun.ttf").get_name()
        rc('font', family=self.font_name)
        font_manager.FontProperties().set_size('xx-small')
        style.use('ggplot')

        self.lb_result.setText("")

    oppo_deck = ""
    df2 = df3 = df_final = pd.DataFrame([])
    odu = True
    cls_list = ['엘프', '로얄', '위치', '비숍', '드래곤', '네크로맨서', '뱀파이어', '네메시스']

    def reload(self):
        self.oppo_cls = "모든 직업"
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
        if not self.oppo_cls == "모든 직업":
            self.cbOppodeck.setEnabled(True)
            df1 = self.df2
            df2 = df1[df1['OppoJob'].isin([self.oppo_cls])]
            self.df_final = df2
            df3 = df2.drop_duplicates(['OppoArche'])
            lists = sorted(list(set(df3['OppoArche'])))
            self.oppo_deck_lists = ["모든 덱"] + lists
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
            self.lb_result.setText("전적 없음")
            self.figure1.clear()
            self.canvas1.draw()
        else:
            self.lb_result.setText("")
            df = self.df_final
            dfw = df[df['WinLose'].isin(['승'])]
            dfw1 = dfw[dfw['FirstSecond'].isin(['선공'])]
            dfl = df[df['WinLose'].isin(['패'])]
            dfl1 = dfl[dfl['FirstSecond'].isin(['선공'])]
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
        if self.oppo_cls == "모든 직업":
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
            axes[0].set_title("상대 직업 분포", fontdict={'fontsize': 11}, pad=10)
        elif self.oppo_deck == "모든 덱":
            for deck in self.oppo_deck_lists:
                df1 = df[df['OppoArche'].isin([deck])]
                if len(df1) != 0:
                    ratio.append(len(df1))
                    labels.append(deck)
                    explode.append(0.1)
            axes[0].pie(ratio, labels=labels, autopct='%1.1f%%', startangle=90, explode=explode,
                        textprops={'fontsize': 9})
            axes[0].set_title("상대 덱 분포", fontdict={'fontsize': 11}, pad=10)
        else:
            axes[0].pie([100], labels=[self.oppo_deck], autopct='%1.1f%%', startangle=90,
                        textprops={'fontsize': 9})
            axes[0].set_title("상대 덱 분포", fontdict={'fontsize': 11}, pad=10)

        dfwt = dfw["Turn"]
        dflt = dfl["Turn"]
        turn_w = []
        turn_l = []
        labels_t = []
        turn_w.append(len(dfwt[dfwt <= 3]))
        turn_l.append(len(dflt[dflt <= 3]))
        labels_t.append('-3')
        for i in range(4, 12):
            turn_w.append(len(dfwt[dfwt == i]))
            turn_l.append(len(dflt[dflt == i]))
            labels_t.append(str(i))
        turn_w.append(len(dfwt[dfwt >= 12]))
        turn_l.append(len(dflt[dflt >= 12]))
        labels_t.append('12+')

        import numpy
        x = numpy.arange(len(labels_t))
        win = axes[1].bar(x - 0.2, turn_w, label='승', width=0.4, color='lightskyblue')
        lose = axes[1].bar(x + 0.2, turn_l, label='패', width=0.4, color='red')
        axes[1].set_xticks(x)
        axes[1].set_xticklabels(labels_t)
        axes[1].legend(fontsize=7, loc='upper left')
        axes[1].set_xlabel("턴", fontsize=9)
        axes[1].set_ylabel("횟수", fontsize=9)
        axes[1].set_ylim(0, max(turn_w + turn_l + [5]) + 1)
        axes[1].set_title("종료 턴 분포", fontdict={'fontsize': 11}, pad=10)

        import mplcursors

        def cursor1_annotations(sel):
            x, y, width, height = sel.artist[sel.target.index].get_bbox().bounds
            sel.annotation.set_text('{}턴: {}승'.format(labels_t[sel.target.index], int(sel.target[1])))
            sel.annotation.get_bbox_patch().set(fc="powderblue", alpha=0.9)
            sel.annotation.xy = (x + width / 2, y + height)
            for s in crs2.selections:
                crs2.remove_selection(s)

        def cursor2_annotations(sel):
            x, y, width, height = sel.artist[sel.target.index].get_bbox().bounds
            sel.annotation.set_text('{}턴: {}패'.format(labels_t[sel.target.index], int(sel.target[1])))
            sel.annotation.get_bbox_patch().set(fc="lightsalmon", alpha=0.9)
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
