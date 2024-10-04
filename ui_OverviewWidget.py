# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'OverviewWidget.ui'
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QHBoxLayout, QHeaderView,
    QPushButton, QSizePolicy, QSpacerItem, QTabWidget,
    QTableView, QVBoxLayout, QWidget)

from FilterWidget import FilterWidget

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
        self.widget = FilterWidget(self.members_tab)
        self.widget.setObjectName(u"widget")
        self.widget.setMinimumSize(QSize(0, 10))

        self.verticalLayout_4.addWidget(self.widget)

        self.tableView = QTableView(self.members_tab)
        self.tableView.setObjectName(u"tableView")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tableView.sizePolicy().hasHeightForWidth())
        self.tableView.setSizePolicy(sizePolicy)
        self.tableView.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.tableView.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.tableView.setAutoScroll(True)
        self.tableView.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked|QAbstractItemView.EditTrigger.EditKeyPressed)
        self.tableView.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tableView.setSortingEnabled(True)

        self.verticalLayout_4.addWidget(self.tableView)

        self.tabWidget.addTab(self.members_tab, "")
        self.sessions_tab = QWidget()
        self.sessions_tab.setObjectName(u"sessions_tab")
        self.verticalLayout_5 = QVBoxLayout(self.sessions_tab)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.widget_2 = FilterWidget(self.sessions_tab)
        self.widget_2.setObjectName(u"widget_2")
        self.widget_2.setMinimumSize(QSize(0, 10))

        self.verticalLayout_5.addWidget(self.widget_2)

        self.tableView_2 = QTableView(self.sessions_tab)
        self.tableView_2.setObjectName(u"tableView_2")
        self.tableView_2.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.tableView_2.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.tableView_2.setAutoScroll(True)
        self.tableView_2.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked|QAbstractItemView.EditTrigger.EditKeyPressed)
        self.tableView_2.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tableView_2.setSortingEnabled(True)

        self.verticalLayout_5.addWidget(self.tableView_2)

        self.tabWidget.addTab(self.sessions_tab, "")

        self.verticalLayout.addWidget(self.tabWidget)

        self.horizontalLayout_10 = QHBoxLayout()
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.pushButton_10 = QPushButton(OverviewWidget)
        self.pushButton_10.setObjectName(u"pushButton_10")

        self.horizontalLayout_10.addWidget(self.pushButton_10)

        self.horizontalSpacer_5 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_10.addItem(self.horizontalSpacer_5)


        self.verticalLayout.addLayout(self.horizontalLayout_10)


        self.retranslateUi(OverviewWidget)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(OverviewWidget)
    # setupUi

    def retranslateUi(self, OverviewWidget):
        OverviewWidget.setWindowTitle(QCoreApplication.translate("OverviewWidget", u"Form", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.members_tab), QCoreApplication.translate("OverviewWidget", u"Members", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.sessions_tab), QCoreApplication.translate("OverviewWidget", u"Sessions", None))
        self.pushButton_10.setText(QCoreApplication.translate("OverviewWidget", u"Back", None))
    # retranslateUi

