# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'MainWindow.ui'
##
## Created by: Qt User Interface Compiler version 6.7.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QMainWindow, QMenu, QMenuBar,
    QSizePolicy, QStackedWidget, QStatusBar, QVBoxLayout,
    QWidget)

from ConnectWidget import ConnectWidget
from MainMenuWidget import MainMenuWidget
from OverviewWidget import OverviewWidget
from TallyWidget import TallyWidget

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 612)
        self.actionMember = QAction(MainWindow)
        self.actionMember.setObjectName(u"actionMember")
        self.actionSession = QAction(MainWindow)
        self.actionSession.setObjectName(u"actionSession")
        self.main_widget = QWidget(MainWindow)
        self.main_widget.setObjectName(u"main_widget")
        self.verticalLayout = QVBoxLayout(self.main_widget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.page_stack = QStackedWidget(self.main_widget)
        self.page_stack.setObjectName(u"page_stack")
        self.connect_page = ConnectWidget()
        self.connect_page.setObjectName(u"connect_page")
        self.page_stack.addWidget(self.connect_page)
        self.main_menu = MainMenuWidget()
        self.main_menu.setObjectName(u"main_menu")
        self.page_stack.addWidget(self.main_menu)
        self.overview = OverviewWidget()
        self.overview.setObjectName(u"overview")
        self.page_stack.addWidget(self.overview)
        self.tally_page = TallyWidget()
        self.tally_page.setObjectName(u"tally_page")
        self.page_stack.addWidget(self.tally_page)

        self.verticalLayout.addWidget(self.page_stack)

        MainWindow.setCentralWidget(self.main_widget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 30))
        self.menuNew = QMenu(self.menubar)
        self.menuNew.setObjectName(u"menuNew")
        self.menuNew.setEnabled(False)
        self.menuNew.setTearOffEnabled(False)
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuNew.menuAction())
        self.menuNew.addAction(self.actionMember)
        self.menuNew.addAction(self.actionSession)

        self.retranslateUi(MainWindow)

        self.page_stack.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.actionMember.setText(QCoreApplication.translate("MainWindow", u"&Member", None))
        self.actionSession.setText(QCoreApplication.translate("MainWindow", u"&Session", None))
        self.menuNew.setTitle(QCoreApplication.translate("MainWindow", u"&New", None))
    # retranslateUi

