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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QComboBox, QDateEdit,
    QFormLayout, QFrame, QGridLayout, QGroupBox,
    QHBoxLayout, QHeaderView, QLabel, QLineEdit,
    QMainWindow, QMenu, QMenuBar, QPushButton,
    QScrollArea, QSizePolicy, QSpacerItem, QSpinBox,
    QStackedWidget, QStatusBar, QTabWidget, QTableView,
    QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 714)
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
        self.main_scroller = QScrollArea(self.main_widget)
        self.main_scroller.setObjectName(u"main_scroller")
        self.main_scroller.setFrameShape(QFrame.Shape.StyledPanel)
        self.main_scroller.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 800, 661))
        self.verticalLayout_2 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.page_stack = QStackedWidget(self.scrollAreaWidgetContents)
        self.page_stack.setObjectName(u"page_stack")
        self.connect_page = QWidget()
        self.connect_page.setObjectName(u"connect_page")
        self.verticalLayout_6 = QVBoxLayout(self.connect_page)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.label_4 = QLabel(self.connect_page)
        self.label_4.setObjectName(u"label_4")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy)

        self.horizontalLayout_5.addWidget(self.label_4)

        self.comboBox = QComboBox(self.connect_page)
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.setObjectName(u"comboBox")

        self.horizontalLayout_5.addWidget(self.comboBox)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer_3)


        self.verticalLayout_6.addLayout(self.horizontalLayout_5)

        self.line = QFrame(self.connect_page)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_6.addWidget(self.line)

        self.groupBox = QGroupBox(self.connect_page)
        self.groupBox.setObjectName(u"groupBox")
        self.formLayout = QFormLayout(self.groupBox)
        self.formLayout.setObjectName(u"formLayout")
        self.label_5 = QLabel(self.groupBox)
        self.label_5.setObjectName(u"label_5")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label_5)

        self.comboBox_2 = QComboBox(self.groupBox)
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.setObjectName(u"comboBox_2")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.comboBox_2)

        self.label_6 = QLabel(self.groupBox)
        self.label_6.setObjectName(u"label_6")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.label_6)

        self.lineEdit_4 = QLineEdit(self.groupBox)
        self.lineEdit_4.setObjectName(u"lineEdit_4")

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.lineEdit_4)

        self.label_7 = QLabel(self.groupBox)
        self.label_7.setObjectName(u"label_7")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.label_7)

        self.lineEdit_3 = QLineEdit(self.groupBox)
        self.lineEdit_3.setObjectName(u"lineEdit_3")
        self.lineEdit_3.setEchoMode(QLineEdit.EchoMode.Password)

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.lineEdit_3)

        self.label_8 = QLabel(self.groupBox)
        self.label_8.setObjectName(u"label_8")

        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.label_8)

        self.lineEdit_5 = QLineEdit(self.groupBox)
        self.lineEdit_5.setObjectName(u"lineEdit_5")

        self.formLayout.setWidget(3, QFormLayout.FieldRole, self.lineEdit_5)

        self.label_9 = QLabel(self.groupBox)
        self.label_9.setObjectName(u"label_9")

        self.formLayout.setWidget(4, QFormLayout.LabelRole, self.label_9)

        self.spinBox = QSpinBox(self.groupBox)
        self.spinBox.setObjectName(u"spinBox")

        self.formLayout.setWidget(4, QFormLayout.FieldRole, self.spinBox)

        self.label_10 = QLabel(self.groupBox)
        self.label_10.setObjectName(u"label_10")

        self.formLayout.setWidget(5, QFormLayout.LabelRole, self.label_10)

        self.lineEdit_6 = QLineEdit(self.groupBox)
        self.lineEdit_6.setObjectName(u"lineEdit_6")

        self.formLayout.setWidget(5, QFormLayout.FieldRole, self.lineEdit_6)


        self.verticalLayout_6.addWidget(self.groupBox)

        self.groupBox_2 = QGroupBox(self.connect_page)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.formLayout_2 = QFormLayout(self.groupBox_2)
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.label_11 = QLabel(self.groupBox_2)
        self.label_11.setObjectName(u"label_11")

        self.formLayout_2.setWidget(0, QFormLayout.LabelRole, self.label_11)

        self.lineEdit_7 = QLineEdit(self.groupBox_2)
        self.lineEdit_7.setObjectName(u"lineEdit_7")

        self.formLayout_2.setWidget(0, QFormLayout.FieldRole, self.lineEdit_7)

        self.label_12 = QLabel(self.groupBox_2)
        self.label_12.setObjectName(u"label_12")

        self.formLayout_2.setWidget(1, QFormLayout.LabelRole, self.label_12)

        self.spinBox_2 = QSpinBox(self.groupBox_2)
        self.spinBox_2.setObjectName(u"spinBox_2")
        self.spinBox_2.setValue(22)

        self.formLayout_2.setWidget(1, QFormLayout.FieldRole, self.spinBox_2)

        self.label_13 = QLabel(self.groupBox_2)
        self.label_13.setObjectName(u"label_13")

        self.formLayout_2.setWidget(2, QFormLayout.LabelRole, self.label_13)

        self.lineEdit_8 = QLineEdit(self.groupBox_2)
        self.lineEdit_8.setObjectName(u"lineEdit_8")
        self.lineEdit_8.setEchoMode(QLineEdit.EchoMode.Password)

        self.formLayout_2.setWidget(2, QFormLayout.FieldRole, self.lineEdit_8)

        self.label_14 = QLabel(self.groupBox_2)
        self.label_14.setObjectName(u"label_14")

        self.formLayout_2.setWidget(3, QFormLayout.LabelRole, self.label_14)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.lineEdit_9 = QLineEdit(self.groupBox_2)
        self.lineEdit_9.setObjectName(u"lineEdit_9")

        self.horizontalLayout_6.addWidget(self.lineEdit_9)

        self.pushButton_6 = QPushButton(self.groupBox_2)
        self.pushButton_6.setObjectName(u"pushButton_6")

        self.horizontalLayout_6.addWidget(self.pushButton_6)


        self.formLayout_2.setLayout(3, QFormLayout.FieldRole, self.horizontalLayout_6)


        self.verticalLayout_6.addWidget(self.groupBox_2)

        self.verticalSpacer_4 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_6.addItem(self.verticalSpacer_4)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalSpacer_6 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_6)

        self.pushButton_5 = QPushButton(self.connect_page)
        self.pushButton_5.setObjectName(u"pushButton_5")
        self.pushButton_5.setEnabled(False)

        self.horizontalLayout_3.addWidget(self.pushButton_5)

        self.connect_button = QPushButton(self.connect_page)
        self.connect_button.setObjectName(u"connect_button")
        sizePolicy.setHeightForWidth(self.connect_button.sizePolicy().hasHeightForWidth())
        self.connect_button.setSizePolicy(sizePolicy)

        self.horizontalLayout_3.addWidget(self.connect_button)


        self.verticalLayout_6.addLayout(self.horizontalLayout_3)

        self.page_stack.addWidget(self.connect_page)
        self.main_menu = QWidget()
        self.main_menu.setObjectName(u"main_menu")
        self.gridLayout = QGridLayout(self.main_menu)
        self.gridLayout.setObjectName(u"gridLayout")
        self.pushButton_2 = QPushButton(self.main_menu)
        self.pushButton_2.setObjectName(u"pushButton_2")

        self.gridLayout.addWidget(self.pushButton_2, 3, 1, 1, 1)

        self.verticalSpacer_3 = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)

        self.gridLayout.addItem(self.verticalSpacer_3, 1, 1, 1, 1)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer, 2, 0, 1, 1)

        self.pushButton = QPushButton(self.main_menu)
        self.pushButton.setObjectName(u"pushButton")

        self.gridLayout.addWidget(self.pushButton, 2, 1, 1, 1)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer_2, 4, 1, 1, 1)

        self.label = QLabel(self.main_menu)
        self.label.setObjectName(u"label")
        font = QFont()
        font.setPointSize(14)
        self.label.setFont(font)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout.addWidget(self.label, 0, 1, 1, 1)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer_2, 2, 2, 1, 1)

        self.page_stack.addWidget(self.main_menu)
        self.overview = QWidget()
        self.overview.setObjectName(u"overview")
        self.verticalLayout_3 = QVBoxLayout(self.overview)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(-1, -1, -1, 6)
        self.tabWidget = QTabWidget(self.overview)
        self.tabWidget.setObjectName(u"tabWidget")
        self.members_tab = QWidget()
        self.members_tab.setObjectName(u"members_tab")
        self.verticalLayout_4 = QVBoxLayout(self.members_tab)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label_2 = QLabel(self.members_tab)
        self.label_2.setObjectName(u"label_2")
        font1 = QFont()
        font1.setBold(True)
        self.label_2.setFont(font1)

        self.horizontalLayout.addWidget(self.label_2)

        self.lineEdit = QLineEdit(self.members_tab)
        self.lineEdit.setObjectName(u"lineEdit")

        self.horizontalLayout.addWidget(self.lineEdit)

        self.pushButton_3 = QPushButton(self.members_tab)
        self.pushButton_3.setObjectName(u"pushButton_3")

        self.horizontalLayout.addWidget(self.pushButton_3)


        self.verticalLayout_4.addLayout(self.horizontalLayout)

        self.tableView = QTableView(self.members_tab)
        self.tableView.setObjectName(u"tableView")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.tableView.sizePolicy().hasHeightForWidth())
        self.tableView.setSizePolicy(sizePolicy1)
        self.tableView.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tableView.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tableView.setAutoScroll(False)
        self.tableView.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked|QAbstractItemView.EditTrigger.EditKeyPressed)
        self.tableView.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tableView.setSortingEnabled(True)

        self.verticalLayout_4.addWidget(self.tableView)

        self.tabWidget.addTab(self.members_tab, "")
        self.sessions_tab = QWidget()
        self.sessions_tab.setObjectName(u"sessions_tab")
        self.verticalLayout_5 = QVBoxLayout(self.sessions_tab)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_3 = QLabel(self.sessions_tab)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setFont(font1)

        self.horizontalLayout_2.addWidget(self.label_3)

        self.lineEdit_2 = QLineEdit(self.sessions_tab)
        self.lineEdit_2.setObjectName(u"lineEdit_2")

        self.horizontalLayout_2.addWidget(self.lineEdit_2)

        self.pushButton_4 = QPushButton(self.sessions_tab)
        self.pushButton_4.setObjectName(u"pushButton_4")

        self.horizontalLayout_2.addWidget(self.pushButton_4)


        self.verticalLayout_5.addLayout(self.horizontalLayout_2)

        self.tableView_2 = QTableView(self.sessions_tab)
        self.tableView_2.setObjectName(u"tableView_2")
        self.tableView_2.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tableView_2.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tableView_2.setAutoScroll(False)
        self.tableView_2.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked|QAbstractItemView.EditTrigger.EditKeyPressed)
        self.tableView_2.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tableView_2.setSortingEnabled(True)

        self.verticalLayout_5.addWidget(self.tableView_2)

        self.tabWidget.addTab(self.sessions_tab, "")

        self.verticalLayout_3.addWidget(self.tabWidget)

        self.horizontalLayout_10 = QHBoxLayout()
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.pushButton_10 = QPushButton(self.overview)
        self.pushButton_10.setObjectName(u"pushButton_10")

        self.horizontalLayout_10.addWidget(self.pushButton_10)

        self.horizontalSpacer_5 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_10.addItem(self.horizontalSpacer_5)


        self.verticalLayout_3.addLayout(self.horizontalLayout_10)

        self.page_stack.addWidget(self.overview)
        self.tally_page = QWidget()
        self.tally_page.setObjectName(u"tally_page")
        self.verticalLayout_7 = QVBoxLayout(self.tally_page)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.groupBox_3 = QGroupBox(self.tally_page)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.formLayout_3 = QFormLayout(self.groupBox_3)
        self.formLayout_3.setObjectName(u"formLayout_3")
        self.label_15 = QLabel(self.groupBox_3)
        self.label_15.setObjectName(u"label_15")

        self.formLayout_3.setWidget(0, QFormLayout.LabelRole, self.label_15)

        self.spinBox_3 = QSpinBox(self.groupBox_3)
        self.spinBox_3.setObjectName(u"spinBox_3")

        self.formLayout_3.setWidget(0, QFormLayout.FieldRole, self.spinBox_3)

        self.label_16 = QLabel(self.groupBox_3)
        self.label_16.setObjectName(u"label_16")

        self.formLayout_3.setWidget(1, QFormLayout.LabelRole, self.label_16)

        self.comboBox_3 = QComboBox(self.groupBox_3)
        self.comboBox_3.addItem("")
        self.comboBox_3.addItem("")
        self.comboBox_3.addItem("")
        self.comboBox_3.addItem("")
        self.comboBox_3.addItem("")
        self.comboBox_3.addItem("")
        self.comboBox_3.addItem("")
        self.comboBox_3.addItem("")
        self.comboBox_3.addItem("")
        self.comboBox_3.addItem("")
        self.comboBox_3.addItem("")
        self.comboBox_3.addItem("")
        self.comboBox_3.setObjectName(u"comboBox_3")

        self.formLayout_3.setWidget(1, QFormLayout.FieldRole, self.comboBox_3)

        self.label_17 = QLabel(self.groupBox_3)
        self.label_17.setObjectName(u"label_17")

        self.formLayout_3.setWidget(2, QFormLayout.LabelRole, self.label_17)

        self.label_18 = QLabel(self.groupBox_3)
        self.label_18.setObjectName(u"label_18")

        self.formLayout_3.setWidget(3, QFormLayout.LabelRole, self.label_18)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.lineEdit_10 = QLineEdit(self.groupBox_3)
        self.lineEdit_10.setObjectName(u"lineEdit_10")

        self.horizontalLayout_7.addWidget(self.lineEdit_10)

        self.pushButton_7 = QPushButton(self.groupBox_3)
        self.pushButton_7.setObjectName(u"pushButton_7")

        self.horizontalLayout_7.addWidget(self.pushButton_7)


        self.formLayout_3.setLayout(3, QFormLayout.FieldRole, self.horizontalLayout_7)

        self.dateEdit = QDateEdit(self.groupBox_3)
        self.dateEdit.setObjectName(u"dateEdit")

        self.formLayout_3.setWidget(2, QFormLayout.FieldRole, self.dateEdit)


        self.verticalLayout_7.addWidget(self.groupBox_3)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_7.addItem(self.verticalSpacer)

        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.pushButton_9 = QPushButton(self.tally_page)
        self.pushButton_9.setObjectName(u"pushButton_9")

        self.horizontalLayout_8.addWidget(self.pushButton_9)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_8.addItem(self.horizontalSpacer_4)

        self.pushButton_8 = QPushButton(self.tally_page)
        self.pushButton_8.setObjectName(u"pushButton_8")

        self.horizontalLayout_8.addWidget(self.pushButton_8)


        self.verticalLayout_7.addLayout(self.horizontalLayout_8)

        self.page_stack.addWidget(self.tally_page)

        self.verticalLayout_2.addWidget(self.page_stack)

        self.main_scroller.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout.addWidget(self.main_scroller)

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
        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.actionMember.setText(QCoreApplication.translate("MainWindow", u"&Member", None))
        self.actionSession.setText(QCoreApplication.translate("MainWindow", u"&Session", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"Connection type", None))
        self.comboBox.setItemText(0, QCoreApplication.translate("MainWindow", u"Regular", None))
        self.comboBox.setItemText(1, QCoreApplication.translate("MainWindow", u"SSH-Tunnel", None))

        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"Database", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"Backend", None))
        self.comboBox_2.setItemText(0, QCoreApplication.translate("MainWindow", u"SQLite", None))
        self.comboBox_2.setItemText(1, QCoreApplication.translate("MainWindow", u"PostgreSQL", None))
        self.comboBox_2.setItemText(2, QCoreApplication.translate("MainWindow", u"MySQL", None))

        self.label_6.setText(QCoreApplication.translate("MainWindow", u"User", None))
        self.lineEdit_4.setPlaceholderText(QCoreApplication.translate("MainWindow", u"db_username", None))
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"Password", None))
        self.label_8.setText(QCoreApplication.translate("MainWindow", u"Host", None))
        self.lineEdit_5.setPlaceholderText(QCoreApplication.translate("MainWindow", u"mydb.example.com", None))
        self.label_9.setText(QCoreApplication.translate("MainWindow", u"Port", None))
        self.label_10.setText(QCoreApplication.translate("MainWindow", u"Database", None))
        self.lineEdit_6.setPlaceholderText(QCoreApplication.translate("MainWindow", u"awesome_dataset", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("MainWindow", u"SSH", None))
        self.label_11.setText(QCoreApplication.translate("MainWindow", u"User", None))
        self.lineEdit_7.setPlaceholderText(QCoreApplication.translate("MainWindow", u"ssh_username", None))
        self.label_12.setText(QCoreApplication.translate("MainWindow", u"Port", None))
        self.label_13.setText(QCoreApplication.translate("MainWindow", u"Password", None))
        self.label_14.setText(QCoreApplication.translate("MainWindow", u"Private key", None))
        self.lineEdit_9.setPlaceholderText(QCoreApplication.translate("MainWindow", u"/path/to/private_key", None))
        self.pushButton_6.setText(QCoreApplication.translate("MainWindow", u"\u2026", None))
        self.pushButton_5.setText(QCoreApplication.translate("MainWindow", u"Cancel", None))
        self.connect_button.setText(QCoreApplication.translate("MainWindow", u"Connect", None))
        self.pushButton_2.setText(QCoreApplication.translate("MainWindow", u"Create tally", None))
        self.pushButton.setText(QCoreApplication.translate("MainWindow", u"Overview", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Main menu", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Filter", None))
        self.lineEdit.setInputMask("")
        self.lineEdit.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Amy", None))
        self.pushButton_3.setText(QCoreApplication.translate("MainWindow", u"Apply", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.members_tab), QCoreApplication.translate("MainWindow", u"Members", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Filter", None))
        self.lineEdit_2.setInputMask("")
        self.lineEdit_2.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Breakdance", None))
        self.pushButton_4.setText(QCoreApplication.translate("MainWindow", u"Apply", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.sessions_tab), QCoreApplication.translate("MainWindow", u"Sessions", None))
        self.pushButton_10.setText(QCoreApplication.translate("MainWindow", u"Back", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("MainWindow", u"Tally", None))
        self.label_15.setText(QCoreApplication.translate("MainWindow", u"Year", None))
        self.label_16.setText(QCoreApplication.translate("MainWindow", u"Month", None))
        self.comboBox_3.setItemText(0, QCoreApplication.translate("MainWindow", u"January", None))
        self.comboBox_3.setItemText(1, QCoreApplication.translate("MainWindow", u"February", None))
        self.comboBox_3.setItemText(2, QCoreApplication.translate("MainWindow", u"March", None))
        self.comboBox_3.setItemText(3, QCoreApplication.translate("MainWindow", u"April", None))
        self.comboBox_3.setItemText(4, QCoreApplication.translate("MainWindow", u"May", None))
        self.comboBox_3.setItemText(5, QCoreApplication.translate("MainWindow", u"June", None))
        self.comboBox_3.setItemText(6, QCoreApplication.translate("MainWindow", u"July", None))
        self.comboBox_3.setItemText(7, QCoreApplication.translate("MainWindow", u"August", None))
        self.comboBox_3.setItemText(8, QCoreApplication.translate("MainWindow", u"September", None))
        self.comboBox_3.setItemText(9, QCoreApplication.translate("MainWindow", u"October", None))
        self.comboBox_3.setItemText(10, QCoreApplication.translate("MainWindow", u"November", None))
        self.comboBox_3.setItemText(11, QCoreApplication.translate("MainWindow", u"December", None))

        self.label_17.setText(QCoreApplication.translate("MainWindow", u"Collection date", None))
        self.label_18.setText(QCoreApplication.translate("MainWindow", u"Output directory", None))
        self.pushButton_7.setText(QCoreApplication.translate("MainWindow", u"\u2026", None))
        self.pushButton_9.setText(QCoreApplication.translate("MainWindow", u"Back", None))
        self.pushButton_8.setText(QCoreApplication.translate("MainWindow", u"Generate", None))
        self.menuNew.setTitle(QCoreApplication.translate("MainWindow", u"&New", None))
    # retranslateUi

