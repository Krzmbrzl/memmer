# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'MainWindow.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
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

from ..ConnectWidget import ConnectWidget
from ..MainMenuWidget import MainMenuWidget
from ..OverviewWidget import OverviewWidget
from ..TallyWidget import TallyWidget

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 612)
        self.new_member_action = QAction(MainWindow)
        self.new_member_action.setObjectName(u"new_member_action")
        self.new_session_action = QAction(MainWindow)
        self.new_session_action.setObjectName(u"new_session_action")
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
        self.overview_page = OverviewWidget()
        self.overview_page.setObjectName(u"overview_page")
        self.page_stack.addWidget(self.overview_page)
        self.tally_page = TallyWidget()
        self.tally_page.setObjectName(u"tally_page")
        self.page_stack.addWidget(self.tally_page)

        self.verticalLayout.addWidget(self.page_stack)

        MainWindow.setCentralWidget(self.main_widget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 30))
        self.menu_new = QMenu(self.menubar)
        self.menu_new.setObjectName(u"menu_new")
        self.menu_new.setEnabled(False)
        self.menu_new.setTearOffEnabled(False)
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menu_new.menuAction())
        self.menu_new.addAction(self.new_member_action)
        self.menu_new.addAction(self.new_session_action)

        self.retranslateUi(MainWindow)

        self.page_stack.setCurrentIndex(0)

    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.new_member_action.setText(QCoreApplication.translate("MainWindow", u"&Member", None))
        self.new_session_action.setText(QCoreApplication.translate("MainWindow", u"&Session", None))
        self.menu_new.setTitle(QCoreApplication.translate("MainWindow", u"&New", None))
    # retranslateUi

