# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'TallyWidget.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QDateEdit, QFormLayout,
    QGroupBox, QHBoxLayout, QLabel, QPushButton,
    QSizePolicy, QSpacerItem, QSpinBox, QVBoxLayout,
    QWidget)

from PathSelectorWidget import PathSelectorWidget

class Ui_TallyWidget(object):
    def setupUi(self, TallyWidget):
        if not TallyWidget.objectName():
            TallyWidget.setObjectName(u"TallyWidget")
        TallyWidget.resize(514, 375)
        self.verticalLayout = QVBoxLayout(TallyWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBox_3 = QGroupBox(TallyWidget)
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

        self.dateEdit = QDateEdit(self.groupBox_3)
        self.dateEdit.setObjectName(u"dateEdit")

        self.formLayout_3.setWidget(2, QFormLayout.FieldRole, self.dateEdit)

        self.widget = PathSelectorWidget(self.groupBox_3)
        self.widget.setObjectName(u"widget")
        self.widget.setMinimumSize(QSize(10, 0))

        self.formLayout_3.setWidget(3, QFormLayout.FieldRole, self.widget)


        self.verticalLayout.addWidget(self.groupBox_3)

        self.verticalSpacer = QSpacerItem(20, 138, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.pushButton_9 = QPushButton(TallyWidget)
        self.pushButton_9.setObjectName(u"pushButton_9")

        self.horizontalLayout_8.addWidget(self.pushButton_9)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_8.addItem(self.horizontalSpacer_4)

        self.pushButton_8 = QPushButton(TallyWidget)
        self.pushButton_8.setObjectName(u"pushButton_8")

        self.horizontalLayout_8.addWidget(self.pushButton_8)


        self.verticalLayout.addLayout(self.horizontalLayout_8)


        self.retranslateUi(TallyWidget)

        QMetaObject.connectSlotsByName(TallyWidget)
    # setupUi

    def retranslateUi(self, TallyWidget):
        TallyWidget.setWindowTitle(QCoreApplication.translate("TallyWidget", u"Form", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("TallyWidget", u"Tally", None))
        self.label_15.setText(QCoreApplication.translate("TallyWidget", u"Year", None))
        self.label_16.setText(QCoreApplication.translate("TallyWidget", u"Month", None))
        self.comboBox_3.setItemText(0, QCoreApplication.translate("TallyWidget", u"January", None))
        self.comboBox_3.setItemText(1, QCoreApplication.translate("TallyWidget", u"February", None))
        self.comboBox_3.setItemText(2, QCoreApplication.translate("TallyWidget", u"March", None))
        self.comboBox_3.setItemText(3, QCoreApplication.translate("TallyWidget", u"April", None))
        self.comboBox_3.setItemText(4, QCoreApplication.translate("TallyWidget", u"May", None))
        self.comboBox_3.setItemText(5, QCoreApplication.translate("TallyWidget", u"June", None))
        self.comboBox_3.setItemText(6, QCoreApplication.translate("TallyWidget", u"July", None))
        self.comboBox_3.setItemText(7, QCoreApplication.translate("TallyWidget", u"August", None))
        self.comboBox_3.setItemText(8, QCoreApplication.translate("TallyWidget", u"September", None))
        self.comboBox_3.setItemText(9, QCoreApplication.translate("TallyWidget", u"October", None))
        self.comboBox_3.setItemText(10, QCoreApplication.translate("TallyWidget", u"November", None))
        self.comboBox_3.setItemText(11, QCoreApplication.translate("TallyWidget", u"December", None))

        self.label_17.setText(QCoreApplication.translate("TallyWidget", u"Collection date", None))
        self.label_18.setText(QCoreApplication.translate("TallyWidget", u"Output directory", None))
        self.pushButton_9.setText(QCoreApplication.translate("TallyWidget", u"Back", None))
        self.pushButton_8.setText(QCoreApplication.translate("TallyWidget", u"Generate", None))
    # retranslateUi

