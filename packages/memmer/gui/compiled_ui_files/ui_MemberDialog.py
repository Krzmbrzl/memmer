# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'MemberDialog.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateEdit,
    QDialog, QDoubleSpinBox, QFormLayout, QGroupBox,
    QHBoxLayout, QHeaderView, QLabel, QLineEdit,
    QListView, QPushButton, QScrollArea, QSizePolicy,
    QSpacerItem, QTabWidget, QTableView, QVBoxLayout,
    QWidget)

from ..FilterWidget import FilterWidget

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(591, 752)
        self.verticalLayout_2 = QVBoxLayout(Dialog)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.scrollArea = QScrollArea(Dialog)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 575, 694))
        self.verticalLayout_3 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.tabWidget = QTabWidget(self.scrollAreaWidgetContents)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.verticalLayout = QVBoxLayout(self.tab)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBox_2 = QGroupBox(self.tab)
        self.groupBox_2.setObjectName(u"groupBox_2")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_2.sizePolicy().hasHeightForWidth())
        self.groupBox_2.setSizePolicy(sizePolicy)
        self.formLayout = QFormLayout(self.groupBox_2)
        self.formLayout.setObjectName(u"formLayout")
        self.label = QLabel(self.groupBox_2)
        self.label.setObjectName(u"label")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label)

        self.comboBox = QComboBox(self.groupBox_2)
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.setObjectName(u"comboBox")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.comboBox)

        self.label_2 = QLabel(self.groupBox_2)
        self.label_2.setObjectName(u"label_2")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_2)

        self.label_3 = QLabel(self.groupBox_2)
        self.label_3.setObjectName(u"label_3")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_3)

        self.label_4 = QLabel(self.groupBox_2)
        self.label_4.setObjectName(u"label_4")

        self.formLayout.setWidget(3, QFormLayout.ItemRole.LabelRole, self.label_4)

        self.lineEdit = QLineEdit(self.groupBox_2)
        self.lineEdit.setObjectName(u"lineEdit")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.lineEdit)

        self.lineEdit_2 = QLineEdit(self.groupBox_2)
        self.lineEdit_2.setObjectName(u"lineEdit_2")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.lineEdit_2)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.dateEdit = QDateEdit(self.groupBox_2)
        self.dateEdit.setObjectName(u"dateEdit")

        self.horizontalLayout_2.addWidget(self.dateEdit)

        self.horizontalSpacer_2 = QSpacerItem(10, 10, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)

        self.label_5 = QLabel(self.groupBox_2)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setText(u"(Age)")

        self.horizontalLayout_2.addWidget(self.label_5)


        self.formLayout.setLayout(3, QFormLayout.ItemRole.FieldRole, self.horizontalLayout_2)


        self.verticalLayout.addWidget(self.groupBox_2)

        self.groupBox = QGroupBox(self.tab)
        self.groupBox.setObjectName(u"groupBox")
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.formLayout_2 = QFormLayout(self.groupBox)
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.label_6 = QLabel(self.groupBox)
        self.label_6.setObjectName(u"label_6")

        self.formLayout_2.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_6)

        self.label_7 = QLabel(self.groupBox)
        self.label_7.setObjectName(u"label_7")

        self.formLayout_2.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_7)

        self.label_8 = QLabel(self.groupBox)
        self.label_8.setObjectName(u"label_8")

        self.formLayout_2.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_8)

        self.label_9 = QLabel(self.groupBox)
        self.label_9.setObjectName(u"label_9")

        self.formLayout_2.setWidget(3, QFormLayout.ItemRole.LabelRole, self.label_9)

        self.lineEdit_3 = QLineEdit(self.groupBox)
        self.lineEdit_3.setObjectName(u"lineEdit_3")

        self.formLayout_2.setWidget(0, QFormLayout.ItemRole.FieldRole, self.lineEdit_3)

        self.lineEdit_4 = QLineEdit(self.groupBox)
        self.lineEdit_4.setObjectName(u"lineEdit_4")

        self.formLayout_2.setWidget(1, QFormLayout.ItemRole.FieldRole, self.lineEdit_4)

        self.lineEdit_5 = QLineEdit(self.groupBox)
        self.lineEdit_5.setObjectName(u"lineEdit_5")

        self.formLayout_2.setWidget(3, QFormLayout.ItemRole.FieldRole, self.lineEdit_5)

        self.lineEdit_6 = QLineEdit(self.groupBox)
        self.lineEdit_6.setObjectName(u"lineEdit_6")

        self.formLayout_2.setWidget(2, QFormLayout.ItemRole.FieldRole, self.lineEdit_6)


        self.verticalLayout.addWidget(self.groupBox)

        self.groupBox_3 = QGroupBox(self.tab)
        self.groupBox_3.setObjectName(u"groupBox_3")
        sizePolicy.setHeightForWidth(self.groupBox_3.sizePolicy().hasHeightForWidth())
        self.groupBox_3.setSizePolicy(sizePolicy)
        self.formLayout_3 = QFormLayout(self.groupBox_3)
        self.formLayout_3.setObjectName(u"formLayout_3")
        self.label_10 = QLabel(self.groupBox_3)
        self.label_10.setObjectName(u"label_10")

        self.formLayout_3.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_10)

        self.lineEdit_8 = QLineEdit(self.groupBox_3)
        self.lineEdit_8.setObjectName(u"lineEdit_8")

        self.formLayout_3.setWidget(0, QFormLayout.ItemRole.FieldRole, self.lineEdit_8)

        self.label_11 = QLabel(self.groupBox_3)
        self.label_11.setObjectName(u"label_11")

        self.formLayout_3.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_11)

        self.lineEdit_7 = QLineEdit(self.groupBox_3)
        self.lineEdit_7.setObjectName(u"lineEdit_7")

        self.formLayout_3.setWidget(1, QFormLayout.ItemRole.FieldRole, self.lineEdit_7)


        self.verticalLayout.addWidget(self.groupBox_3)

        self.groupBox_4 = QGroupBox(self.tab)
        self.groupBox_4.setObjectName(u"groupBox_4")
        sizePolicy.setHeightForWidth(self.groupBox_4.sizePolicy().hasHeightForWidth())
        self.groupBox_4.setSizePolicy(sizePolicy)
        self.formLayout_4 = QFormLayout(self.groupBox_4)
        self.formLayout_4.setObjectName(u"formLayout_4")
        self.label_12 = QLabel(self.groupBox_4)
        self.label_12.setObjectName(u"label_12")

        self.formLayout_4.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_12)

        self.label_13 = QLabel(self.groupBox_4)
        self.label_13.setObjectName(u"label_13")

        self.formLayout_4.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_13)

        self.dateEdit_2 = QDateEdit(self.groupBox_4)
        self.dateEdit_2.setObjectName(u"dateEdit_2")

        self.formLayout_4.setWidget(0, QFormLayout.ItemRole.FieldRole, self.dateEdit_2)

        self.dateEdit_3 = QDateEdit(self.groupBox_4)
        self.dateEdit_3.setObjectName(u"dateEdit_3")

        self.formLayout_4.setWidget(1, QFormLayout.ItemRole.FieldRole, self.dateEdit_3)


        self.verticalLayout.addWidget(self.groupBox_4)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.verticalLayout_4 = QVBoxLayout(self.tab_2)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.groupBox_5 = QGroupBox(self.tab_2)
        self.groupBox_5.setObjectName(u"groupBox_5")
        self.formLayout_5 = QFormLayout(self.groupBox_5)
        self.formLayout_5.setObjectName(u"formLayout_5")
        self.label_14 = QLabel(self.groupBox_5)
        self.label_14.setObjectName(u"label_14")

        self.formLayout_5.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_14)

        self.label_15 = QLabel(self.groupBox_5)
        self.label_15.setObjectName(u"label_15")

        self.formLayout_5.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_15)

        self.label_16 = QLabel(self.groupBox_5)
        self.label_16.setObjectName(u"label_16")

        self.formLayout_5.setWidget(4, QFormLayout.ItemRole.LabelRole, self.label_16)

        self.label_17 = QLabel(self.groupBox_5)
        self.label_17.setObjectName(u"label_17")

        self.formLayout_5.setWidget(3, QFormLayout.ItemRole.LabelRole, self.label_17)

        self.label_18 = QLabel(self.groupBox_5)
        self.label_18.setObjectName(u"label_18")

        self.formLayout_5.setWidget(5, QFormLayout.ItemRole.LabelRole, self.label_18)

        self.lineEdit_9 = QLineEdit(self.groupBox_5)
        self.lineEdit_9.setObjectName(u"lineEdit_9")

        self.formLayout_5.setWidget(2, QFormLayout.ItemRole.FieldRole, self.lineEdit_9)

        self.lineEdit_10 = QLineEdit(self.groupBox_5)
        self.lineEdit_10.setObjectName(u"lineEdit_10")

        self.formLayout_5.setWidget(3, QFormLayout.ItemRole.FieldRole, self.lineEdit_10)

        self.lineEdit_11 = QLineEdit(self.groupBox_5)
        self.lineEdit_11.setObjectName(u"lineEdit_11")

        self.formLayout_5.setWidget(4, QFormLayout.ItemRole.FieldRole, self.lineEdit_11)

        self.lineEdit_12 = QLineEdit(self.groupBox_5)
        self.lineEdit_12.setObjectName(u"lineEdit_12")

        self.formLayout_5.setWidget(5, QFormLayout.ItemRole.FieldRole, self.lineEdit_12)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.checkBox_2 = QCheckBox(self.groupBox_5)
        self.checkBox_2.setObjectName(u"checkBox_2")

        self.horizontalLayout_5.addWidget(self.checkBox_2)

        self.horizontalSpacer_3 = QSpacerItem(20, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer_3)

        self.dateEdit_4 = QDateEdit(self.groupBox_5)
        self.dateEdit_4.setObjectName(u"dateEdit_4")

        self.horizontalLayout_5.addWidget(self.dateEdit_4)


        self.formLayout_5.setLayout(0, QFormLayout.ItemRole.FieldRole, self.horizontalLayout_5)


        self.verticalLayout_4.addWidget(self.groupBox_5)

        self.groupBox_6 = QGroupBox(self.tab_2)
        self.groupBox_6.setObjectName(u"groupBox_6")
        self.formLayout_6 = QFormLayout(self.groupBox_6)
        self.formLayout_6.setObjectName(u"formLayout_6")
        self.label_19 = QLabel(self.groupBox_6)
        self.label_19.setObjectName(u"label_19")

        self.formLayout_6.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_19)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.doubleSpinBox = QDoubleSpinBox(self.groupBox_6)
        self.doubleSpinBox.setObjectName(u"doubleSpinBox")

        self.horizontalLayout_3.addWidget(self.doubleSpinBox)

        self.checkBox = QCheckBox(self.groupBox_6)
        self.checkBox.setObjectName(u"checkBox")

        self.horizontalLayout_3.addWidget(self.checkBox)


        self.formLayout_6.setLayout(0, QFormLayout.ItemRole.FieldRole, self.horizontalLayout_3)

        self.label_20 = QLabel(self.groupBox_6)
        self.label_20.setObjectName(u"label_20")

        self.formLayout_6.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_20)

        self.tableView = QTableView(self.groupBox_6)
        self.tableView.setObjectName(u"tableView")
        self.tableView.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tableView.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tableView.setAutoScroll(False)

        self.formLayout_6.setWidget(1, QFormLayout.ItemRole.FieldRole, self.tableView)


        self.verticalLayout_4.addWidget(self.groupBox_6)

        self.verticalSpacer_2 = QSpacerItem(20, 116, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_4.addItem(self.verticalSpacer_2)

        self.tabWidget.addTab(self.tab_2, "")
        self.tab_3 = QWidget()
        self.tab_3.setObjectName(u"tab_3")
        self.verticalLayout_5 = QVBoxLayout(self.tab_3)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.tableView_2 = QTableView(self.tab_3)
        self.tableView_2.setObjectName(u"tableView_2")
        self.tableView_2.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tableView_2.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tableView_2.setAutoScroll(False)

        self.verticalLayout_5.addWidget(self.tableView_2)

        self.tabWidget.addTab(self.tab_3, "")
        self.tab_4 = QWidget()
        self.tab_4.setObjectName(u"tab_4")
        self.verticalLayout_6 = QVBoxLayout(self.tab_4)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.label_21 = QLabel(self.tab_4)
        self.label_21.setObjectName(u"label_21")

        self.verticalLayout_6.addWidget(self.label_21)

        self.listView = QListView(self.tab_4)
        self.listView.setObjectName(u"listView")
        self.listView.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.listView.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.listView.setAutoScroll(False)

        self.verticalLayout_6.addWidget(self.listView)

        self.label_22 = QLabel(self.tab_4)
        self.label_22.setObjectName(u"label_22")

        self.verticalLayout_6.addWidget(self.label_22)

        self.listView_2 = QListView(self.tab_4)
        self.listView_2.setObjectName(u"listView_2")
        self.listView_2.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.listView_2.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.listView_2.setAutoScroll(False)

        self.verticalLayout_6.addWidget(self.listView_2)

        self.label_23 = QLabel(self.tab_4)
        self.label_23.setObjectName(u"label_23")

        self.verticalLayout_6.addWidget(self.label_23)

        self.widget = FilterWidget(self.tab_4)
        self.widget.setObjectName(u"widget")

        self.verticalLayout_6.addWidget(self.widget)

        self.listView_3 = QListView(self.tab_4)
        self.listView_3.setObjectName(u"listView_3")
        self.listView_3.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.listView_3.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.listView_3.setAutoScroll(False)

        self.verticalLayout_6.addWidget(self.listView_3)

        self.tabWidget.addTab(self.tab_4, "")

        self.verticalLayout_3.addWidget(self.tabWidget)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout_2.addWidget(self.scrollArea)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.pushButton_3 = QPushButton(Dialog)
        self.pushButton_3.setObjectName(u"pushButton_3")

        self.horizontalLayout.addWidget(self.pushButton_3)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.pushButton_2 = QPushButton(Dialog)
        self.pushButton_2.setObjectName(u"pushButton_2")

        self.horizontalLayout.addWidget(self.pushButton_2)

        self.pushButton = QPushButton(Dialog)
        self.pushButton.setObjectName(u"pushButton")

        self.horizontalLayout.addWidget(self.pushButton)


        self.verticalLayout_2.addLayout(self.horizontalLayout)


        self.retranslateUi(Dialog)

        self.tabWidget.setCurrentIndex(3)
        self.comboBox.setCurrentIndex(-1)

    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("Dialog", u"Personal", None))
        self.label.setText(QCoreApplication.translate("Dialog", u"Gender", None))
        self.comboBox.setItemText(0, QCoreApplication.translate("Dialog", u"Male", None))
        self.comboBox.setItemText(1, QCoreApplication.translate("Dialog", u"Female", None))
        self.comboBox.setItemText(2, QCoreApplication.translate("Dialog", u"Diverse", None))

        self.label_2.setText(QCoreApplication.translate("Dialog", u"First name", None))
        self.label_3.setText(QCoreApplication.translate("Dialog", u"Last name", None))
        self.label_4.setText(QCoreApplication.translate("Dialog", u"Birthday", None))
        self.lineEdit.setPlaceholderText(QCoreApplication.translate("Dialog", u"Sarah", None))
        self.lineEdit_2.setPlaceholderText(QCoreApplication.translate("Dialog", u"Walker", None))
        self.groupBox.setTitle(QCoreApplication.translate("Dialog", u"Address", None))
        self.label_6.setText(QCoreApplication.translate("Dialog", u"Street", None))
        self.label_7.setText(QCoreApplication.translate("Dialog", u"Street number", None))
        self.label_8.setText(QCoreApplication.translate("Dialog", u"Postal code", None))
        self.label_9.setText(QCoreApplication.translate("Dialog", u"City", None))
        self.lineEdit_3.setPlaceholderText(QCoreApplication.translate("Dialog", u"Hollywood Boulevard", None))
        self.lineEdit_4.setPlaceholderText(QCoreApplication.translate("Dialog", u"12", None))
        self.lineEdit_5.setPlaceholderText(QCoreApplication.translate("Dialog", u"Los Angeles", None))
        self.lineEdit_6.setPlaceholderText(QCoreApplication.translate("Dialog", u"90059", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("Dialog", u"Contact", None))
        self.label_10.setText(QCoreApplication.translate("Dialog", u"Phone number", None))
        self.lineEdit_8.setPlaceholderText(QCoreApplication.translate("Dialog", u"773-702-1000", None))
        self.label_11.setText(QCoreApplication.translate("Dialog", u"Email", None))
        self.lineEdit_7.setPlaceholderText(QCoreApplication.translate("Dialog", u"sarah.walker@gmail.com", None))
        self.groupBox_4.setTitle(QCoreApplication.translate("Dialog", u"Membership", None))
        self.label_12.setText(QCoreApplication.translate("Dialog", u"Entry date", None))
        self.label_13.setText(QCoreApplication.translate("Dialog", u"Exit date", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("Dialog", u"General", None))
        self.groupBox_5.setTitle(QCoreApplication.translate("Dialog", u"Bank details", None))
        self.label_14.setText(QCoreApplication.translate("Dialog", u"SEPA mandate", None))
        self.label_15.setText(QCoreApplication.translate("Dialog", u"IBAN", None))
        self.label_16.setText(QCoreApplication.translate("Dialog", u"Institute", None))
        self.label_17.setText(QCoreApplication.translate("Dialog", u"BIC", None))
        self.label_18.setText(QCoreApplication.translate("Dialog", u"Account owner", None))
        self.checkBox_2.setText(QCoreApplication.translate("Dialog", u"Given", None))
        self.groupBox_6.setTitle(QCoreApplication.translate("Dialog", u"Fees", None))
        self.label_19.setText(QCoreApplication.translate("Dialog", u"Monthly fee", None))
        self.doubleSpinBox.setSuffix(QCoreApplication.translate("Dialog", u"\u20ac", None))
        self.checkBox.setText(QCoreApplication.translate("Dialog", u"Overwrite", None))
        self.label_20.setText(QCoreApplication.translate("Dialog", u"One-time fees", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QCoreApplication.translate("Dialog", u"Payment", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), QCoreApplication.translate("Dialog", u"Sessions", None))
        self.label_21.setText(QCoreApplication.translate("Dialog", u"Relatives", None))
        self.label_22.setText(QCoreApplication.translate("Dialog", u"Likely relatives", None))
        self.label_23.setText(QCoreApplication.translate("Dialog", u"Potential relatives", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_4), QCoreApplication.translate("Dialog", u"Relatives", None))
        self.pushButton_3.setText(QCoreApplication.translate("Dialog", u"Delete", None))
        self.pushButton_2.setText(QCoreApplication.translate("Dialog", u"Cancel", None))
        self.pushButton.setText(QCoreApplication.translate("Dialog", u"Save", None))
    # retranslateUi

