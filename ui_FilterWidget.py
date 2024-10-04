# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'FilterWidget.ui'
##
## Created by: Qt User Interface Compiler version 6.7.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QSizePolicy, QWidget)

class Ui_FilterWidget(object):
    def setupUi(self, FilterWidget):
        if not FilterWidget.objectName():
            FilterWidget.setObjectName(u"FilterWidget")
        FilterWidget.resize(400, 34)
        self.horizontalLayout = QHBoxLayout(FilterWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.label_2 = QLabel(FilterWidget)
        self.label_2.setObjectName(u"label_2")
        font = QFont()
        font.setBold(False)
        self.label_2.setFont(font)

        self.horizontalLayout.addWidget(self.label_2)

        self.lineEdit = QLineEdit(FilterWidget)
        self.lineEdit.setObjectName(u"lineEdit")

        self.horizontalLayout.addWidget(self.lineEdit)

        self.pushButton_3 = QPushButton(FilterWidget)
        self.pushButton_3.setObjectName(u"pushButton_3")

        self.horizontalLayout.addWidget(self.pushButton_3)


        self.retranslateUi(FilterWidget)

        QMetaObject.connectSlotsByName(FilterWidget)
    # setupUi

    def retranslateUi(self, FilterWidget):
        FilterWidget.setWindowTitle(QCoreApplication.translate("FilterWidget", u"Form", None))
        self.label_2.setText(QCoreApplication.translate("FilterWidget", u"Filter", None))
        self.lineEdit.setInputMask("")
        self.lineEdit.setPlaceholderText(QCoreApplication.translate("FilterWidget", u"filter expression", None))
        self.pushButton_3.setText(QCoreApplication.translate("FilterWidget", u"Apply", None))
    # retranslateUi

