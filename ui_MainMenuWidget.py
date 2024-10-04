# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'MainMenuWidget.ui'
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
from PySide6.QtWidgets import (QApplication, QGridLayout, QLabel, QPushButton,
    QSizePolicy, QSpacerItem, QWidget)

class Ui_MainMenuWidget(object):
    def setupUi(self, MainMenuWidget):
        if not MainMenuWidget.objectName():
            MainMenuWidget.setObjectName(u"MainMenuWidget")
        MainMenuWidget.resize(442, 305)
        self.gridLayout = QGridLayout(MainMenuWidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.pushButton = QPushButton(MainMenuWidget)
        self.pushButton.setObjectName(u"pushButton")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton.sizePolicy().hasHeightForWidth())
        self.pushButton.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.pushButton, 1, 1, 1, 1)

        self.verticalSpacer_2 = QSpacerItem(20, 250, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer_2, 3, 1, 1, 1)

        self.pushButton_2 = QPushButton(MainMenuWidget)
        self.pushButton_2.setObjectName(u"pushButton_2")

        self.gridLayout.addWidget(self.pushButton_2, 2, 1, 1, 1)

        self.label = QLabel(MainMenuWidget)
        self.label.setObjectName(u"label")
        font = QFont()
        font.setPointSize(14)
        self.label.setFont(font)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout.addWidget(self.label, 0, 1, 1, 1)

        self.horizontalSpacer = QSpacerItem(136, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer, 1, 0, 1, 1)

        self.horizontalSpacer_2 = QSpacerItem(136, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer_2, 1, 2, 1, 1)

        self.gridLayout.setColumnStretch(0, 1)
        self.gridLayout.setColumnStretch(1, 1)
        self.gridLayout.setColumnStretch(2, 1)

        self.retranslateUi(MainMenuWidget)

        QMetaObject.connectSlotsByName(MainMenuWidget)
    # setupUi

    def retranslateUi(self, MainMenuWidget):
        MainMenuWidget.setWindowTitle(QCoreApplication.translate("MainMenuWidget", u"Form", None))
        self.pushButton.setText(QCoreApplication.translate("MainMenuWidget", u"Overview", None))
        self.pushButton_2.setText(QCoreApplication.translate("MainMenuWidget", u"Create tally", None))
        self.label.setText(QCoreApplication.translate("MainMenuWidget", u"Main menu", None))
    # retranslateUi

