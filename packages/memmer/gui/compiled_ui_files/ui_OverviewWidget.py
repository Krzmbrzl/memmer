# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'OverviewWidget.ui'
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QHBoxLayout, QHeaderView,
    QPushButton, QSizePolicy, QSpacerItem, QTabWidget,
    QTableView, QVBoxLayout, QWidget)

from ..FilterWidget import FilterWidget

class Ui_OverviewWidget(object):
    def setupUi(self, OverviewWidget):
        if not OverviewWidget.objectName():
            OverviewWidget.setObjectName(u"OverviewWidget")
        OverviewWidget.resize(850, 625)
        self.verticalLayout = QVBoxLayout(OverviewWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.tabWidget = QTabWidget(OverviewWidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.members_tab = QWidget()
        self.members_tab.setObjectName(u"members_tab")
        self.verticalLayout_4 = QVBoxLayout(self.members_tab)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.member_filter = FilterWidget(self.members_tab)
        self.member_filter.setObjectName(u"member_filter")
        self.member_filter.setMinimumSize(QSize(0, 10))

        self.verticalLayout_4.addWidget(self.member_filter)

        self.member_table = QTableView(self.members_tab)
        self.member_table.setObjectName(u"member_table")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.member_table.sizePolicy().hasHeightForWidth())
        self.member_table.setSizePolicy(sizePolicy)
        self.member_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.member_table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.member_table.setAutoScroll(True)
        self.member_table.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked|QAbstractItemView.EditTrigger.EditKeyPressed)
        self.member_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.member_table.setSortingEnabled(True)

        self.verticalLayout_4.addWidget(self.member_table)

        self.tabWidget.addTab(self.members_tab, "")
        self.sessions_tab = QWidget()
        self.sessions_tab.setObjectName(u"sessions_tab")
        self.verticalLayout_5 = QVBoxLayout(self.sessions_tab)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.session_filter = FilterWidget(self.sessions_tab)
        self.session_filter.setObjectName(u"session_filter")
        self.session_filter.setMinimumSize(QSize(0, 10))

        self.verticalLayout_5.addWidget(self.session_filter)

        self.session_table = QTableView(self.sessions_tab)
        self.session_table.setObjectName(u"session_table")
        self.session_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.session_table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.session_table.setAutoScroll(True)
        self.session_table.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked|QAbstractItemView.EditTrigger.EditKeyPressed)
        self.session_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.session_table.setSortingEnabled(True)

        self.verticalLayout_5.addWidget(self.session_table)

        self.tabWidget.addTab(self.sessions_tab, "")

        self.verticalLayout.addWidget(self.tabWidget)

        self.horizontalLayout_10 = QHBoxLayout()
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.back_button = QPushButton(OverviewWidget)
        self.back_button.setObjectName(u"back_button")

        self.horizontalLayout_10.addWidget(self.back_button)

        self.horizontalSpacer_5 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_10.addItem(self.horizontalSpacer_5)


        self.verticalLayout.addLayout(self.horizontalLayout_10)


        self.retranslateUi(OverviewWidget)

        self.tabWidget.setCurrentIndex(0)

    # setupUi

    def retranslateUi(self, OverviewWidget):
        OverviewWidget.setWindowTitle(QCoreApplication.translate("OverviewWidget", u"Form", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.members_tab), QCoreApplication.translate("OverviewWidget", u"Members", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.sessions_tab), QCoreApplication.translate("OverviewWidget", u"Sessions", None))
        self.back_button.setText(QCoreApplication.translate("OverviewWidget", u"Back", None))
    # retranslateUi

