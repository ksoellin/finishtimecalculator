#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys

from PyQt5.QtCore import QTime
from PyQt5.QtWidgets import QApplication, QMainWindow, QHeaderView

from TimeTableModel import TimeTableModel

from ui_mainwindow import Ui_MainWindow


# noinspection PyPep8Naming
class Example(QMainWindow):
    
    def __init__(self):
        super(Example, self).__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.time = TimeTableModel()
        self.time.insertRows(0, 1)
        self.time.sumChanged.connect(self.updateTime)

        self.ui.manTimeTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ui.manTimeTable.setModel(self.time)

        self.show()

    def updateTime(self, newTime: QTime):
        self.ui.workSoFar.setText(newTime.toString('hh:mm'))


if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
