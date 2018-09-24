#!/usr/bin/python3
# -*- coding: utf-8 -*-

from typing import List, Dict, Tuple
import re

from PyQt5.QtCore import QAbstractTableModel, QModelIndex, QVariant, Qt, QTime, QTimer, pyqtSignal
from PyQt5.QtGui import QBrush


# noinspection PyPep8Naming
class TimeTableModel(QAbstractTableModel):
    FROM_TIME_KEY: str = 'from'
    TO_TIME_KEY: str = 'to'

    EMPTY_SPAN: str = '--:--'

    TIME_REFRESH_INTERVAL: int = 200

    sumChanged = pyqtSignal(QTime)

    def __init__(self):
        super(TimeTableModel, self).__init__()

        self.timeContent: List[Dict[str, str]] = list()
        self.invalidElements: List[Tuple[int, int]] = list()
        self.tooltips: Dict[Tuple[int, int], str] = dict()

        self.updateTimer = QTimer()
        self.updateTimer.setInterval(TimeTableModel.TIME_REFRESH_INTERVAL)
        self.updateTimer.timeout.connect(self.updateTime)

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.timeContent)

    def columnCount(self, parent=None, *args, **kwargs):
        return 3

    def headerData(self, section, orientation, role=None):
        if role != Qt.DisplayRole:
            return QVariant()

        if orientation == Qt.Horizontal:
            return {
                0: 'From',
                1: 'To',
                2: 'Time Span'
            }.get(section, QVariant())

        elif orientation == Qt.Vertical:
            return section + 1

    def insertRows(self, position, rows, parent=None, *args, **kwargs):
        self.beginInsertRows(QModelIndex(), position, position + rows - 1)

        for i in range(rows):
            self.timeContent.append({
                TimeTableModel.FROM_TIME_KEY: '',
                TimeTableModel.TO_TIME_KEY: ''
            })

        self.endInsertRows()

        return True

    def removeRows(self, position, rows, parent=None, *args, **kwargs):
        self.beginRemoveRows(QModelIndex(), position, position + rows - 1)

        for i in range(rows):
            del self.timeContent[position]

        self.endRemoveRows()
        return True

    def data(self, index: QModelIndex, role=None):

        if not index.isValid():
            return QVariant()

        if index.row() < 0 or index.row() > len(self.timeContent):
            return QVariant()

        pos: Tuple[int, int] = (index.row(), index.column())
        if role == Qt.DisplayRole:
            if index.column() == 0:
                return self.getFromTime(index.row())

            elif index.column() == 1:
                return self.getToTime(index.row())

            elif index.column() == 2:
                row: int = index.row()
                if (row, 0) in self.invalidElements or (row, 1) in self.invalidElements:
                    return TimeTableModel.EMPTY_SPAN

                try:
                    diff: QTime = self.calcDiff(self.getFromTime(index.row()), self.getToTime(index.row()))

                    if not diff.isValid():
                        return TimeTableModel.EMPTY_SPAN
                    else:
                        return diff.toString('hh:mm')
                except ValueError as error:
                    self.invalidElements.append((row, 0))
                    self.invalidElements.append((row, 1))
                    self.tooltips[(row, 0)] = str(error)
                    self.tooltips[(row, 1)] = str(error)

                    return TimeTableModel.EMPTY_SPAN

        elif role == Qt.BackgroundRole:
            if pos in self.invalidElements:
                return QBrush(Qt.red)
            else:
                return QBrush(Qt.white)

        elif role == Qt.ToolTipRole:
            if pos in self.tooltips:
                return self.tooltips[pos]
            else:
                return QVariant()

        return QVariant()

    def setData(self, index: QModelIndex, value: QVariant, role=None):
        if index.isValid() and role == Qt.EditRole:
            entry: Dict[str, str] = self.timeContent[index.row()]

            if index.column() not in [0, 1]:
                return False

            pos: Tuple[int, int] = (index.row(), index.column())

            inputRaw = value
            inputFormatted: str = inputRaw

            # right format continue processing
            if len(inputRaw) <= 0:
                if index.column() == 0:
                    inputFormatted = entry[TimeTableModel.FROM_TIME_KEY]
                elif index.column() == 1:
                    inputFormatted = entry[TimeTableModel.TO_TIME_KEY]

            elif re.match('[0-9]{2}:[0-9]{2}', inputRaw):
                inputFormatted = inputRaw
                if pos in self.invalidElements: self.invalidElements.remove(pos)

            elif re.match('[0-9]{1,2}[.:/,][0-9]{1,2}', inputRaw):
                inputFormatted = ':'.join([n.zfill(2) for n in re.split('[.:/,]', inputRaw)])
                if pos in self.invalidElements: self.invalidElements.remove(pos)

            elif re.match('[0-9]{1,4}', re.sub('[^0-9]', '', inputRaw)):
                inputTrimmed = re.sub('[^0-9]', '', inputRaw).zfill(4)
                inputFormatted = ':'.join([inputTrimmed[:-2], inputTrimmed[-2:]])
                if pos in self.invalidElements: self.invalidElements.remove(pos)

            elif len(inputRaw) > 0:
                self.invalidElements.append(pos)

            if index.column() == 0:
                entry[TimeTableModel.FROM_TIME_KEY] = inputFormatted
            elif index.column() == 1:
                entry[TimeTableModel.TO_TIME_KEY] = inputFormatted

            self.updateRow(pos[0])

            self.dataChanged.emit(self.createIndex(index.row(), 0), self.createIndex(index.row(), 2))

            if entry[TimeTableModel.FROM_TIME_KEY] != '' and \
                    (index.row(), 0) not in self.invalidElements:

                if entry[TimeTableModel.TO_TIME_KEY] == '' and \
                        (index.row(), 1) not in self.invalidElements:
                    self.updateTimer.start()
                else:
                    self.updateTimer.stop()

            return True

    def flags(self, index: QModelIndex):
        if not index.isValid():
            return Qt.ItemIsEnabled

        if index.column() in [0, 1]:
            return super(TimeTableModel, self).flags(index) | Qt.ItemIsEditable
        else:
            return Qt.NoItemFlags

    def updateRow(self, row: int):

        lastRow: bool = row == len(self.timeContent) - 1
        noEmptyElements: bool = len([t for t in self.timeContent[row].values() if t is None or len(t) <= 0]) <= 0
        noInvalidElements: bool = (row, 0) not in self.invalidElements and (row, 0) not in self.invalidElements

        if lastRow and noEmptyElements and noInvalidElements:
            self.insertRows(len(self.timeContent), 1)

    def getFromTime(self, row: int) -> str:
        return self.timeContent[row][TimeTableModel.FROM_TIME_KEY]

    def getToTime(self, row: int) -> str:
        return self.timeContent[row][TimeTableModel.TO_TIME_KEY]

    @staticmethod
    def calcDiff(fromTimeText: str, toTimeText: str) -> QTime:

        if len(fromTimeText) <= 0:
            return QTime()

        if len(toTimeText) <= 0:
            toTimeText = QTime.currentTime().toString("hh:mm")

        fromTime: QTime = QTime.fromString(fromTimeText, 'hh:mm')
        toTime: QTime = QTime.fromString(toTimeText, 'hh:mm')

        if fromTime >= toTime:
            raise ValueError('Begin time after end time')

        else:
            diffSecs: int = fromTime.secsTo(toTime)
            return QTime(0, 0).addSecs(diffSecs)

    def calcWorkTime(self) -> QTime:
        timeSum: QTime = QTime(0, 0)

        for row in range(len(self.timeContent)):
            try:
                rowTime: QTime = TimeTableModel.calcDiff(self.getFromTime(row), self.getToTime(row))

                if rowTime.isValid():
                    timeSum = timeSum.addSecs(QTime(0, 0).secsTo(rowTime))
            except ValueError:
                pass

        return timeSum

    def updateTime(self):
        lastRow: int = len(self.timeContent) - 1
        self.dataChanged.emit(self.createIndex(lastRow, 2), self.createIndex(lastRow, 2))
        self.sumChanged.emit(self.calcWorkTime())



