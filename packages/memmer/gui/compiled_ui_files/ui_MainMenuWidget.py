# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'MainMenuWidget.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
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
        self.overview_button = QPushButton(MainMenuWidget)
        self.overview_button.setObjectName(u"overview_button")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.overview_button.sizePolicy().hasHeightForWidth())
        self.overview_button.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.overview_button, 1, 1, 1, 1)

        self.horizontalSpacer_2 = QSpacerItem(136, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer_2, 1, 2, 1, 1)

        self.title_label = QLabel(MainMenuWidget)
        self.title_label.setObjectName(u"title_label")
        font = QFont()
        font.setPointSize(14)
        self.title_label.setFont(font)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout.addWidget(self.title_label, 0, 1, 1, 1)

        self.disconnect_button = QPushButton(MainMenuWidget)
        self.disconnect_button.setObjectName(u"disconnect_button")

        self.gridLayout.addWidget(self.disconnect_button, 5, 1, 1, 1)

        self.tally_button = QPushButton(MainMenuWidget)
        self.tally_button.setObjectName(u"tally_button")

        self.gridLayout.addWidget(self.tally_button, 2, 1, 1, 1)

        self.verticalSpacer_2 = QSpacerItem(20, 250, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer_2, 3, 1, 1, 1)

        self.horizontalSpacer = QSpacerItem(136, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer, 1, 0, 1, 1)

        self.commit_button = QPushButton(MainMenuWidget)
        self.commit_button.setObjectName(u"commit_button")

        self.gridLayout.addWidget(self.commit_button, 4, 1, 1, 1)

        self.gridLayout.setColumnStretch(0, 1)
        self.gridLayout.setColumnStretch(1, 1)
        self.gridLayout.setColumnStretch(2, 1)

        self.retranslateUi(MainMenuWidget)
    # setupUi

    def retranslateUi(self, MainMenuWidget):
        MainMenuWidget.setWindowTitle(QCoreApplication.translate("MainMenuWidget", u"Form", None))
        self.overview_button.setText(QCoreApplication.translate("MainMenuWidget", u"Overview", None))
        self.title_label.setText(QCoreApplication.translate("MainMenuWidget", u"Main menu", None))
        self.disconnect_button.setText(QCoreApplication.translate("MainMenuWidget", u"Disconnect", None))
        self.tally_button.setText(QCoreApplication.translate("MainMenuWidget", u"Create tally", None))
        self.commit_button.setText(QCoreApplication.translate("MainMenuWidget", u"Commit changes", None))
    # retranslateUi

