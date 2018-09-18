#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import re

from PyQt5.QtCore import QTimer, QTime, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QHeaderView
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from ui_mainwindow import Ui_MainWindow


# noinspection PyPep8Naming
class Example(QMainWindow):
    
    def __init__(self):
        super(Example, self).__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.time = QStandardItemModel()
        self.appendRow(self.time)
        self.time.setHeaderData(0, Qt.Horizontal, "From")
        self.time.setHeaderData(1, Qt.Horizontal, "To")
        self.time.setHeaderData(2, Qt.Horizontal, "Span")

        self.time.itemChanged.connect(self.timeChange)

        self.ui.manTimeTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ui.manTimeTable.setModel(self.time)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(100)

        self.show()

    def update(self):
        self.ui.workSoFar.setText(QTime.currentTime().toString("hh:mm"))

    def timeChange(self, changed: QStandardItem):
        if changed.column() > 1:
            return

        inputRaw = changed.text()

        # right format continue processing
        if re.match('[0-9]{2}:[0-9]{2}', inputRaw):
            changed.setBackground(Qt.white)
            self.updateTimeCalc(changed.row())

        elif re.match('[0-9]{1,2}[.:/,][0-9]{1,2}', inputRaw):
            changed.setBackground(Qt.white)
            changed.setText(':'.join([n.zfill(2) for n in re.split('[.:/,]', inputRaw)]))

        elif re.match('[0-9]{1,4}', re.sub('[^0-9]', '', inputRaw)):
            inputTrimmed = re.sub('[^0-9]', '', inputRaw).zfill(4)
            changed.setText(':'.join([inputTrimmed[:-2], inputTrimmed[-2:]]))

        else:
            changed.setBackground(Qt.red)

    def updateTimeCalc(self, row: int):
        fromTimeItem: QStandardItem = self.time.item(row, 0)
        toTimeItem: QStandardItem = self.time.item(row, 1)
        diffTimeItem: QStandardItem = self.time.item(row, 2)

        if fromTimeItem.text() and toTimeItem.text():
            fromTime = QTime.fromString(fromTimeItem.text(), 'hh:mm')
            toTime = QTime.fromString(toTimeItem.text(), 'hh:mm')

            if fromTime >= toTime:
                fromTimeItem.setBackground(Qt.red)
                toTimeItem.setBackground(Qt.red)
                fromTimeItem.setToolTip("Begin time after end time")
                toTimeItem.setToolTip("Begin time after end time")
                return

            diffSecs: int = fromTime.secsTo(toTime)
            diffTime: QTime = QTime(0, 0).addSecs(diffSecs)
            diffTimeItem.setText(diffTime.toString('hh:mm'))

            if row + 1 >= self.time.rowCount():
                self.appendRow(self.time)

    def appendRow(self, model: QStandardItemModel):
        fromItem = QStandardItem("00:00")
        toItem = QStandardItem("")
        sumItem = QStandardItem("")
        sumItem.setEditable(False)
        model.appendRow([fromItem, toItem, sumItem])


if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
