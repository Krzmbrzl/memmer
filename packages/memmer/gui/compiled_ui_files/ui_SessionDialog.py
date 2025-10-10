# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'SessionDialog.ui'
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QDialog, QDoubleSpinBox,
    QFormLayout, QGroupBox, QHBoxLayout, QHeaderView,
    QLabel, QLineEdit, QPushButton, QRadioButton,
    QSizePolicy, QSpacerItem, QStackedWidget, QTabWidget,
    QTableView, QVBoxLayout, QWidget)

from ..FilterWidget import FilterWidget

class Ui_SessionDialog(object):
    def setupUi(self, SessionDialog):
        if not SessionDialog.objectName():
            SessionDialog.setObjectName(u"SessionDialog")
        SessionDialog.resize(500, 553)
        self.verticalLayout = QVBoxLayout(SessionDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.tabWidget = QTabWidget(SessionDialog)
        self.tabWidget.setObjectName(u"tabWidget")
        self.general_tab = QWidget()
        self.general_tab.setObjectName(u"general_tab")
        self.verticalLayout_5 = QVBoxLayout(self.general_tab)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.name_label = QLabel(self.general_tab)
        self.name_label.setObjectName(u"name_label")

        self.horizontalLayout_3.addWidget(self.name_label)

        self.name_edit = QLineEdit(self.general_tab)
        self.name_edit.setObjectName(u"name_edit")

        self.horizontalLayout_3.addWidget(self.name_edit)


        self.verticalLayout_5.addLayout(self.horizontalLayout_3)

        self.groupBox = QGroupBox(self.general_tab)
        self.groupBox.setObjectName(u"groupBox")
        self.verticalLayout_4 = QVBoxLayout(self.groupBox)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.fixed_fee_button = QRadioButton(self.groupBox)
        self.fixed_fee_button.setObjectName(u"fixed_fee_button")
        self.fixed_fee_button.setChecked(True)

        self.horizontalLayout_2.addWidget(self.fixed_fee_button)

        self.hourly_fee_button = QRadioButton(self.groupBox)
        self.hourly_fee_button.setObjectName(u"hourly_fee_button")

        self.horizontalLayout_2.addWidget(self.hourly_fee_button)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)


        self.verticalLayout_4.addLayout(self.horizontalLayout_2)

        self.fee_stack = QStackedWidget(self.groupBox)
        self.fee_stack.setObjectName(u"fee_stack")
        self.fixed_fee_widget = QWidget()
        self.fixed_fee_widget.setObjectName(u"fixed_fee_widget")
        self.formLayout_3 = QFormLayout(self.fixed_fee_widget)
        self.formLayout_3.setObjectName(u"formLayout_3")
        self.fixed_fee_label = QLabel(self.fixed_fee_widget)
        self.fixed_fee_label.setObjectName(u"fixed_fee_label")

        self.formLayout_3.setWidget(0, QFormLayout.ItemRole.LabelRole, self.fixed_fee_label)

        self.fixed_fee_edit = QDoubleSpinBox(self.fixed_fee_widget)
        self.fixed_fee_edit.setObjectName(u"fixed_fee_edit")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.fixed_fee_edit.sizePolicy().hasHeightForWidth())
        self.fixed_fee_edit.setSizePolicy(sizePolicy)
        self.fixed_fee_edit.setMaximum(999.990000000000009)

        self.formLayout_3.setWidget(0, QFormLayout.ItemRole.FieldRole, self.fixed_fee_edit)

        self.fee_stack.addWidget(self.fixed_fee_widget)
        self.hourly_fee_widget = QWidget()
        self.hourly_fee_widget.setObjectName(u"hourly_fee_widget")
        self.formLayout_2 = QFormLayout(self.hourly_fee_widget)
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.duration_label = QLabel(self.hourly_fee_widget)
        self.duration_label.setObjectName(u"duration_label")

        self.formLayout_2.setWidget(0, QFormLayout.ItemRole.LabelRole, self.duration_label)

        self.duration_edit = QDoubleSpinBox(self.hourly_fee_widget)
        self.duration_edit.setObjectName(u"duration_edit")
        sizePolicy.setHeightForWidth(self.duration_edit.sizePolicy().hasHeightForWidth())
        self.duration_edit.setSizePolicy(sizePolicy)
        self.duration_edit.setSingleStep(0.250000000000000)

        self.formLayout_2.setWidget(0, QFormLayout.ItemRole.FieldRole, self.duration_edit)

        self.fee_stack.addWidget(self.hourly_fee_widget)

        self.verticalLayout_4.addWidget(self.fee_stack)


        self.verticalLayout_5.addWidget(self.groupBox)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_5.addItem(self.verticalSpacer)

        self.tabWidget.addTab(self.general_tab, "")
        self.trainers_tab = QWidget()
        self.trainers_tab.setObjectName(u"trainers_tab")
        self.verticalLayout_3 = QVBoxLayout(self.trainers_tab)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.trainers_group = QGroupBox(self.trainers_tab)
        self.trainers_group.setObjectName(u"trainers_group")
        self.verticalLayout_8 = QVBoxLayout(self.trainers_group)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.trainer_table = QTableView(self.trainers_group)
        self.trainer_table.setObjectName(u"trainer_table")
        self.trainer_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.trainer_table.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.trainer_table.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)

        self.verticalLayout_8.addWidget(self.trainer_table)


        self.verticalLayout_3.addWidget(self.trainers_group)

        self.potential_trainers_group = QGroupBox(self.trainers_tab)
        self.potential_trainers_group.setObjectName(u"potential_trainers_group")
        self.verticalLayout_9 = QVBoxLayout(self.potential_trainers_group)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.potential_traininers_filter = FilterWidget(self.potential_trainers_group)
        self.potential_traininers_filter.setObjectName(u"potential_traininers_filter")

        self.verticalLayout_9.addWidget(self.potential_traininers_filter)

        self.potential_trainers_table = QTableView(self.potential_trainers_group)
        self.potential_trainers_table.setObjectName(u"potential_trainers_table")
        self.potential_trainers_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.potential_trainers_table.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.potential_trainers_table.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)

        self.verticalLayout_9.addWidget(self.potential_trainers_table)


        self.verticalLayout_3.addWidget(self.potential_trainers_group)

        self.tabWidget.addTab(self.trainers_tab, "")
        self.members_tab = QWidget()
        self.members_tab.setObjectName(u"members_tab")
        self.verticalLayout_2 = QVBoxLayout(self.members_tab)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.session_member_group = QGroupBox(self.members_tab)
        self.session_member_group.setObjectName(u"session_member_group")
        self.verticalLayout_6 = QVBoxLayout(self.session_member_group)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.session_member_table = QTableView(self.session_member_group)
        self.session_member_table.setObjectName(u"session_member_table")
        self.session_member_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.session_member_table.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.session_member_table.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)

        self.verticalLayout_6.addWidget(self.session_member_table)


        self.verticalLayout_2.addWidget(self.session_member_group)

        self.remaining_member_group = QGroupBox(self.members_tab)
        self.remaining_member_group.setObjectName(u"remaining_member_group")
        self.verticalLayout_7 = QVBoxLayout(self.remaining_member_group)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.remaining_member_filter = FilterWidget(self.remaining_member_group)
        self.remaining_member_filter.setObjectName(u"remaining_member_filter")

        self.verticalLayout_7.addWidget(self.remaining_member_filter)

        self.remaining_member_table = QTableView(self.remaining_member_group)
        self.remaining_member_table.setObjectName(u"remaining_member_table")
        self.remaining_member_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        self.verticalLayout_7.addWidget(self.remaining_member_table)


        self.verticalLayout_2.addWidget(self.remaining_member_group)

        self.tabWidget.addTab(self.members_tab, "")

        self.verticalLayout.addWidget(self.tabWidget)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.delete_button = QPushButton(SessionDialog)
        self.delete_button.setObjectName(u"delete_button")

        self.horizontalLayout.addWidget(self.delete_button)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.cancel_button = QPushButton(SessionDialog)
        self.cancel_button.setObjectName(u"cancel_button")

        self.horizontalLayout.addWidget(self.cancel_button)

        self.save_button = QPushButton(SessionDialog)
        self.save_button.setObjectName(u"save_button")

        self.horizontalLayout.addWidget(self.save_button)


        self.verticalLayout.addLayout(self.horizontalLayout)


        self.retranslateUi(SessionDialog)

        self.tabWidget.setCurrentIndex(0)
        self.fee_stack.setCurrentIndex(0)

    # setupUi

    def retranslateUi(self, SessionDialog):
        SessionDialog.setWindowTitle(QCoreApplication.translate("SessionDialog", u"Dialog", None))
        self.name_label.setText(QCoreApplication.translate("SessionDialog", u"Name", None))
        self.name_edit.setPlaceholderText(QCoreApplication.translate("SessionDialog", u"Awesome session", None))
        self.groupBox.setTitle(QCoreApplication.translate("SessionDialog", u"Participation fee", None))
        self.fixed_fee_button.setText(QCoreApplication.translate("SessionDialog", u"Fixed", None))
        self.hourly_fee_button.setText(QCoreApplication.translate("SessionDialog", u"Hourly", None))
        self.fixed_fee_label.setText(QCoreApplication.translate("SessionDialog", u"Monthly fee", None))
        self.fixed_fee_edit.setSuffix(QCoreApplication.translate("SessionDialog", u"\u20ac", None))
        self.duration_label.setText(QCoreApplication.translate("SessionDialog", u"Duration", None))
        self.duration_edit.setSuffix(QCoreApplication.translate("SessionDialog", u"h", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.general_tab), QCoreApplication.translate("SessionDialog", u"General", None))
        self.trainers_group.setTitle(QCoreApplication.translate("SessionDialog", u"Trainers", None))
        self.potential_trainers_group.setTitle(QCoreApplication.translate("SessionDialog", u"Potential trainers", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.trainers_tab), QCoreApplication.translate("SessionDialog", u"Trainers", None))
        self.session_member_group.setTitle(QCoreApplication.translate("SessionDialog", u"Session members", None))
        self.remaining_member_group.setTitle(QCoreApplication.translate("SessionDialog", u"Remaining members", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.members_tab), QCoreApplication.translate("SessionDialog", u"Members", None))
        self.delete_button.setText(QCoreApplication.translate("SessionDialog", u"Delete", None))
        self.cancel_button.setText(QCoreApplication.translate("SessionDialog", u"Cancel", None))
        self.save_button.setText(QCoreApplication.translate("SessionDialog", u"Save", None))
    # retranslateUi

