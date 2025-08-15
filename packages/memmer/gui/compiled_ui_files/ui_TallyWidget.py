# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'TallyWidget.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QDateEdit, QFormLayout,
    QGroupBox, QHBoxLayout, QLabel, QPushButton,
    QSizePolicy, QSpacerItem, QSpinBox, QVBoxLayout,
    QWidget)

from ..PathSelectorWidget import PathSelectorWidget

class Ui_TallyWidget(object):
    def setupUi(self, TallyWidget):
        if not TallyWidget.objectName():
            TallyWidget.setObjectName(u"TallyWidget")
        TallyWidget.resize(514, 375)
        self.verticalLayout = QVBoxLayout(TallyWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.tally_group = QGroupBox(TallyWidget)
        self.tally_group.setObjectName(u"tally_group")
        self.formLayout_3 = QFormLayout(self.tally_group)
        self.formLayout_3.setObjectName(u"formLayout_3")
        self.year_label = QLabel(self.tally_group)
        self.year_label.setObjectName(u"year_label")

        self.formLayout_3.setWidget(0, QFormLayout.ItemRole.LabelRole, self.year_label)

        self.year_spinner = QSpinBox(self.tally_group)
        self.year_spinner.setObjectName(u"year_spinner")
        self.year_spinner.setMaximum(9999)

        self.formLayout_3.setWidget(0, QFormLayout.ItemRole.FieldRole, self.year_spinner)

        self.month_label = QLabel(self.tally_group)
        self.month_label.setObjectName(u"month_label")

        self.formLayout_3.setWidget(1, QFormLayout.ItemRole.LabelRole, self.month_label)

        self.month_combo = QComboBox(self.tally_group)
        self.month_combo.addItem("")
        self.month_combo.addItem("")
        self.month_combo.addItem("")
        self.month_combo.addItem("")
        self.month_combo.addItem("")
        self.month_combo.addItem("")
        self.month_combo.addItem("")
        self.month_combo.addItem("")
        self.month_combo.addItem("")
        self.month_combo.addItem("")
        self.month_combo.addItem("")
        self.month_combo.addItem("")
        self.month_combo.setObjectName(u"month_combo")

        self.formLayout_3.setWidget(1, QFormLayout.ItemRole.FieldRole, self.month_combo)

        self.collection_date_label = QLabel(self.tally_group)
        self.collection_date_label.setObjectName(u"collection_date_label")

        self.formLayout_3.setWidget(2, QFormLayout.ItemRole.LabelRole, self.collection_date_label)

        self.out_dir_label = QLabel(self.tally_group)
        self.out_dir_label.setObjectName(u"out_dir_label")

        self.formLayout_3.setWidget(3, QFormLayout.ItemRole.LabelRole, self.out_dir_label)

        self.collection_date_input = QDateEdit(self.tally_group)
        self.collection_date_input.setObjectName(u"collection_date_input")
        self.collection_date_input.setCalendarPopup(True)

        self.formLayout_3.setWidget(2, QFormLayout.ItemRole.FieldRole, self.collection_date_input)

        self.out_dir_input = PathSelectorWidget(self.tally_group)
        self.out_dir_input.setObjectName(u"out_dir_input")
        self.out_dir_input.setMinimumSize(QSize(10, 0))

        self.formLayout_3.setWidget(3, QFormLayout.ItemRole.FieldRole, self.out_dir_input)


        self.verticalLayout.addWidget(self.tally_group)

        self.verticalSpacer = QSpacerItem(20, 138, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.back_button = QPushButton(TallyWidget)
        self.back_button.setObjectName(u"back_button")

        self.horizontalLayout_8.addWidget(self.back_button)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_8.addItem(self.horizontalSpacer_4)

        self.create_button = QPushButton(TallyWidget)
        self.create_button.setObjectName(u"create_button")

        self.horizontalLayout_8.addWidget(self.create_button)


        self.verticalLayout.addLayout(self.horizontalLayout_8)


        self.retranslateUi(TallyWidget)
    # setupUi

    def retranslateUi(self, TallyWidget):
        TallyWidget.setWindowTitle(QCoreApplication.translate("TallyWidget", u"Form", None))
        self.tally_group.setTitle(QCoreApplication.translate("TallyWidget", u"Tally", None))
        self.year_label.setText(QCoreApplication.translate("TallyWidget", u"Year", None))
        self.month_label.setText(QCoreApplication.translate("TallyWidget", u"Month", None))
        self.month_combo.setItemText(0, QCoreApplication.translate("TallyWidget", u"January", None))
        self.month_combo.setItemText(1, QCoreApplication.translate("TallyWidget", u"February", None))
        self.month_combo.setItemText(2, QCoreApplication.translate("TallyWidget", u"March", None))
        self.month_combo.setItemText(3, QCoreApplication.translate("TallyWidget", u"April", None))
        self.month_combo.setItemText(4, QCoreApplication.translate("TallyWidget", u"May", None))
        self.month_combo.setItemText(5, QCoreApplication.translate("TallyWidget", u"June", None))
        self.month_combo.setItemText(6, QCoreApplication.translate("TallyWidget", u"July", None))
        self.month_combo.setItemText(7, QCoreApplication.translate("TallyWidget", u"August", None))
        self.month_combo.setItemText(8, QCoreApplication.translate("TallyWidget", u"September", None))
        self.month_combo.setItemText(9, QCoreApplication.translate("TallyWidget", u"October", None))
        self.month_combo.setItemText(10, QCoreApplication.translate("TallyWidget", u"November", None))
        self.month_combo.setItemText(11, QCoreApplication.translate("TallyWidget", u"December", None))

        self.collection_date_label.setText(QCoreApplication.translate("TallyWidget", u"Collection date", None))
        self.out_dir_label.setText(QCoreApplication.translate("TallyWidget", u"Output directory", None))
        self.back_button.setText(QCoreApplication.translate("TallyWidget", u"Back", None))
        self.create_button.setText(QCoreApplication.translate("TallyWidget", u"Create", None))
    # retranslateUi

