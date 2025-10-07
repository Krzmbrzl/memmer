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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QCheckBox, QComboBox,
    QDateEdit, QDialog, QDoubleSpinBox, QFormLayout,
    QGridLayout, QGroupBox, QHBoxLayout, QHeaderView,
    QLabel, QLineEdit, QPushButton, QScrollArea,
    QSizePolicy, QSpacerItem, QTabWidget, QTableView,
    QVBoxLayout, QWidget)

from ..FilterWidget import FilterWidget

class Ui_MemberDialog(object):
    def setupUi(self, MemberDialog):
        if not MemberDialog.objectName():
            MemberDialog.setObjectName(u"MemberDialog")
        MemberDialog.resize(614, 792)
        self.verticalLayout_2 = QVBoxLayout(MemberDialog)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.scrollArea = QScrollArea(MemberDialog)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 598, 734))
        self.verticalLayout_3 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.tabWidget = QTabWidget(self.scrollAreaWidgetContents)
        self.tabWidget.setObjectName(u"tabWidget")
        self.general_tab = QWidget()
        self.general_tab.setObjectName(u"general_tab")
        self.verticalLayout = QVBoxLayout(self.general_tab)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.personal_info_group = QGroupBox(self.general_tab)
        self.personal_info_group.setObjectName(u"personal_info_group")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.personal_info_group.sizePolicy().hasHeightForWidth())
        self.personal_info_group.setSizePolicy(sizePolicy)
        self.formLayout = QFormLayout(self.personal_info_group)
        self.formLayout.setObjectName(u"formLayout")
        self.gender_label = QLabel(self.personal_info_group)
        self.gender_label.setObjectName(u"gender_label")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.gender_label)

        self.gender_combo = QComboBox(self.personal_info_group)
        self.gender_combo.addItem("")
        self.gender_combo.addItem("")
        self.gender_combo.addItem("")
        self.gender_combo.setObjectName(u"gender_combo")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.gender_combo)

        self.first_name_label = QLabel(self.personal_info_group)
        self.first_name_label.setObjectName(u"first_name_label")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.first_name_label)

        self.last_name_label = QLabel(self.personal_info_group)
        self.last_name_label.setObjectName(u"last_name_label")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.last_name_label)

        self.birthday_label = QLabel(self.personal_info_group)
        self.birthday_label.setObjectName(u"birthday_label")

        self.formLayout.setWidget(3, QFormLayout.ItemRole.LabelRole, self.birthday_label)

        self.first_name_edit = QLineEdit(self.personal_info_group)
        self.first_name_edit.setObjectName(u"first_name_edit")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.first_name_edit)

        self.last_name_edit = QLineEdit(self.personal_info_group)
        self.last_name_edit.setObjectName(u"last_name_edit")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.last_name_edit)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.birthday_edit = QDateEdit(self.personal_info_group)
        self.birthday_edit.setObjectName(u"birthday_edit")
        self.birthday_edit.setCalendarPopup(True)

        self.horizontalLayout_2.addWidget(self.birthday_edit)

        self.horizontalSpacer_2 = QSpacerItem(10, 10, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)

        self.age_label = QLabel(self.personal_info_group)
        self.age_label.setObjectName(u"age_label")
        self.age_label.setText(u"(Age)")

        self.horizontalLayout_2.addWidget(self.age_label)


        self.formLayout.setLayout(3, QFormLayout.ItemRole.FieldRole, self.horizontalLayout_2)


        self.verticalLayout.addWidget(self.personal_info_group)

        self.address_group = QGroupBox(self.general_tab)
        self.address_group.setObjectName(u"address_group")
        sizePolicy.setHeightForWidth(self.address_group.sizePolicy().hasHeightForWidth())
        self.address_group.setSizePolicy(sizePolicy)
        self.formLayout_2 = QFormLayout(self.address_group)
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.street_label = QLabel(self.address_group)
        self.street_label.setObjectName(u"street_label")

        self.formLayout_2.setWidget(0, QFormLayout.ItemRole.LabelRole, self.street_label)

        self.street_number_label = QLabel(self.address_group)
        self.street_number_label.setObjectName(u"street_number_label")

        self.formLayout_2.setWidget(1, QFormLayout.ItemRole.LabelRole, self.street_number_label)

        self.postal_code_label = QLabel(self.address_group)
        self.postal_code_label.setObjectName(u"postal_code_label")

        self.formLayout_2.setWidget(2, QFormLayout.ItemRole.LabelRole, self.postal_code_label)

        self.city_label = QLabel(self.address_group)
        self.city_label.setObjectName(u"city_label")

        self.formLayout_2.setWidget(3, QFormLayout.ItemRole.LabelRole, self.city_label)

        self.street_edit = QLineEdit(self.address_group)
        self.street_edit.setObjectName(u"street_edit")

        self.formLayout_2.setWidget(0, QFormLayout.ItemRole.FieldRole, self.street_edit)

        self.street_number_edit = QLineEdit(self.address_group)
        self.street_number_edit.setObjectName(u"street_number_edit")

        self.formLayout_2.setWidget(1, QFormLayout.ItemRole.FieldRole, self.street_number_edit)

        self.city_edit = QLineEdit(self.address_group)
        self.city_edit.setObjectName(u"city_edit")

        self.formLayout_2.setWidget(3, QFormLayout.ItemRole.FieldRole, self.city_edit)

        self.postal_code_edit = QLineEdit(self.address_group)
        self.postal_code_edit.setObjectName(u"postal_code_edit")

        self.formLayout_2.setWidget(2, QFormLayout.ItemRole.FieldRole, self.postal_code_edit)


        self.verticalLayout.addWidget(self.address_group)

        self.contact_group = QGroupBox(self.general_tab)
        self.contact_group.setObjectName(u"contact_group")
        sizePolicy.setHeightForWidth(self.contact_group.sizePolicy().hasHeightForWidth())
        self.contact_group.setSizePolicy(sizePolicy)
        self.formLayout_3 = QFormLayout(self.contact_group)
        self.formLayout_3.setObjectName(u"formLayout_3")
        self.phone_number_label = QLabel(self.contact_group)
        self.phone_number_label.setObjectName(u"phone_number_label")

        self.formLayout_3.setWidget(0, QFormLayout.ItemRole.LabelRole, self.phone_number_label)

        self.phone_number_edit = QLineEdit(self.contact_group)
        self.phone_number_edit.setObjectName(u"phone_number_edit")

        self.formLayout_3.setWidget(0, QFormLayout.ItemRole.FieldRole, self.phone_number_edit)

        self.email_label = QLabel(self.contact_group)
        self.email_label.setObjectName(u"email_label")

        self.formLayout_3.setWidget(1, QFormLayout.ItemRole.LabelRole, self.email_label)

        self.email_edit = QLineEdit(self.contact_group)
        self.email_edit.setObjectName(u"email_edit")

        self.formLayout_3.setWidget(1, QFormLayout.ItemRole.FieldRole, self.email_edit)


        self.verticalLayout.addWidget(self.contact_group)

        self.membership_group = QGroupBox(self.general_tab)
        self.membership_group.setObjectName(u"membership_group")
        sizePolicy.setHeightForWidth(self.membership_group.sizePolicy().hasHeightForWidth())
        self.membership_group.setSizePolicy(sizePolicy)
        self.formLayout_4 = QFormLayout(self.membership_group)
        self.formLayout_4.setObjectName(u"formLayout_4")
        self.entry_date_label = QLabel(self.membership_group)
        self.entry_date_label.setObjectName(u"entry_date_label")

        self.formLayout_4.setWidget(2, QFormLayout.ItemRole.LabelRole, self.entry_date_label)

        self.exit_date_label = QLabel(self.membership_group)
        self.exit_date_label.setObjectName(u"exit_date_label")

        self.formLayout_4.setWidget(3, QFormLayout.ItemRole.LabelRole, self.exit_date_label)

        self.entry_date_edit = QDateEdit(self.membership_group)
        self.entry_date_edit.setObjectName(u"entry_date_edit")
        self.entry_date_edit.setCalendarPopup(True)

        self.formLayout_4.setWidget(2, QFormLayout.ItemRole.FieldRole, self.entry_date_edit)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.exit_date_edit = QDateEdit(self.membership_group)
        self.exit_date_edit.setObjectName(u"exit_date_edit")
        self.exit_date_edit.setEnabled(False)
        self.exit_date_edit.setCalendarPopup(True)

        self.horizontalLayout_4.addWidget(self.exit_date_edit)

        self.horizontalSpacer_4 = QSpacerItem(10, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_4)

        self.exited_checkbox = QCheckBox(self.membership_group)
        self.exited_checkbox.setObjectName(u"exited_checkbox")

        self.horizontalLayout_4.addWidget(self.exited_checkbox)


        self.formLayout_4.setLayout(3, QFormLayout.ItemRole.FieldRole, self.horizontalLayout_4)

        self.honorary_member_checkbox = QCheckBox(self.membership_group)
        self.honorary_member_checkbox.setObjectName(u"honorary_member_checkbox")

        self.formLayout_4.setWidget(1, QFormLayout.ItemRole.FieldRole, self.honorary_member_checkbox)


        self.verticalLayout.addWidget(self.membership_group)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.tabWidget.addTab(self.general_tab, "")
        self.payment_tab = QWidget()
        self.payment_tab.setObjectName(u"payment_tab")
        self.verticalLayout_4 = QVBoxLayout(self.payment_tab)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.bank_group = QGroupBox(self.payment_tab)
        self.bank_group.setObjectName(u"bank_group")
        self.formLayout_5 = QFormLayout(self.bank_group)
        self.formLayout_5.setObjectName(u"formLayout_5")
        self.sepa_mandate_label = QLabel(self.bank_group)
        self.sepa_mandate_label.setObjectName(u"sepa_mandate_label")

        self.formLayout_5.setWidget(0, QFormLayout.ItemRole.LabelRole, self.sepa_mandate_label)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.sepa_mandate_date_edit = QDateEdit(self.bank_group)
        self.sepa_mandate_date_edit.setObjectName(u"sepa_mandate_date_edit")
        self.sepa_mandate_date_edit.setEnabled(False)
        self.sepa_mandate_date_edit.setCalendarPopup(True)

        self.horizontalLayout_5.addWidget(self.sepa_mandate_date_edit)

        self.horizontalSpacer_3 = QSpacerItem(20, 10, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer_3)

        self.sepa_mandate_checkbox = QCheckBox(self.bank_group)
        self.sepa_mandate_checkbox.setObjectName(u"sepa_mandate_checkbox")

        self.horizontalLayout_5.addWidget(self.sepa_mandate_checkbox)


        self.formLayout_5.setLayout(0, QFormLayout.ItemRole.FieldRole, self.horizontalLayout_5)

        self.iban_label = QLabel(self.bank_group)
        self.iban_label.setObjectName(u"iban_label")

        self.formLayout_5.setWidget(2, QFormLayout.ItemRole.LabelRole, self.iban_label)

        self.iban_edit = QLineEdit(self.bank_group)
        self.iban_edit.setObjectName(u"iban_edit")
        self.iban_edit.setEnabled(False)

        self.formLayout_5.setWidget(2, QFormLayout.ItemRole.FieldRole, self.iban_edit)

        self.bic_label = QLabel(self.bank_group)
        self.bic_label.setObjectName(u"bic_label")

        self.formLayout_5.setWidget(3, QFormLayout.ItemRole.LabelRole, self.bic_label)

        self.bic_edit = QLineEdit(self.bank_group)
        self.bic_edit.setObjectName(u"bic_edit")
        self.bic_edit.setEnabled(False)

        self.formLayout_5.setWidget(3, QFormLayout.ItemRole.FieldRole, self.bic_edit)

        self.account_owner_label = QLabel(self.bank_group)
        self.account_owner_label.setObjectName(u"account_owner_label")

        self.formLayout_5.setWidget(5, QFormLayout.ItemRole.LabelRole, self.account_owner_label)

        self.account_owner_edit = QLineEdit(self.bank_group)
        self.account_owner_edit.setObjectName(u"account_owner_edit")
        self.account_owner_edit.setEnabled(False)

        self.formLayout_5.setWidget(5, QFormLayout.ItemRole.FieldRole, self.account_owner_edit)

        self.institute_label = QLabel(self.bank_group)
        self.institute_label.setObjectName(u"institute_label")

        self.formLayout_5.setWidget(4, QFormLayout.ItemRole.LabelRole, self.institute_label)

        self.institute_edit = QLineEdit(self.bank_group)
        self.institute_edit.setObjectName(u"institute_edit")
        self.institute_edit.setEnabled(False)

        self.formLayout_5.setWidget(4, QFormLayout.ItemRole.FieldRole, self.institute_edit)


        self.verticalLayout_4.addWidget(self.bank_group)

        self.fee_group = QGroupBox(self.payment_tab)
        self.fee_group.setObjectName(u"fee_group")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.fee_group.sizePolicy().hasHeightForWidth())
        self.fee_group.setSizePolicy(sizePolicy1)
        self.formLayout_6 = QFormLayout(self.fee_group)
        self.formLayout_6.setObjectName(u"formLayout_6")
        self.formLayout_6.setLabelAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTop|Qt.AlignmentFlag.AlignTrailing)
        self.monthly_fee_label = QLabel(self.fee_group)
        self.monthly_fee_label.setObjectName(u"monthly_fee_label")
        self.monthly_fee_label.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop)

        self.formLayout_6.setWidget(1, QFormLayout.ItemRole.LabelRole, self.monthly_fee_label)

        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.base_fee_label = QLabel(self.fee_group)
        self.base_fee_label.setObjectName(u"base_fee_label")
        self.base_fee_label.setText(u"0,00\u20ac")

        self.horizontalLayout_6.addWidget(self.base_fee_label)

        self.times_label = QLabel(self.fee_group)
        self.times_label.setObjectName(u"times_label")
        self.times_label.setText(u"\u00d7")

        self.horizontalLayout_6.addWidget(self.times_label)

        self.discount_label = QLabel(self.fee_group)
        self.discount_label.setObjectName(u"discount_label")
        self.discount_label.setText(u"100%")

        self.horizontalLayout_6.addWidget(self.discount_label)


        self.gridLayout.addLayout(self.horizontalLayout_6, 0, 0, 1, 1)

        self.monthly_fee_overwrite_checkbox = QCheckBox(self.fee_group)
        self.monthly_fee_overwrite_checkbox.setObjectName(u"monthly_fee_overwrite_checkbox")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.monthly_fee_overwrite_checkbox.sizePolicy().hasHeightForWidth())
        self.monthly_fee_overwrite_checkbox.setSizePolicy(sizePolicy2)

        self.gridLayout.addWidget(self.monthly_fee_overwrite_checkbox, 1, 1, 1, 1)

        self.monthly_fee_edit = QDoubleSpinBox(self.fee_group)
        self.monthly_fee_edit.setObjectName(u"monthly_fee_edit")
        self.monthly_fee_edit.setEnabled(False)
        sizePolicy2.setHeightForWidth(self.monthly_fee_edit.sizePolicy().hasHeightForWidth())
        self.monthly_fee_edit.setSizePolicy(sizePolicy2)
        self.monthly_fee_edit.setMaximum(999.990000000000009)

        self.gridLayout.addWidget(self.monthly_fee_edit, 1, 0, 1, 1)

        self.horizontalSpacer_5 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer_5, 1, 2, 1, 1)


        self.formLayout_6.setLayout(1, QFormLayout.ItemRole.FieldRole, self.gridLayout)

        self.one_time_fees_label = QLabel(self.fee_group)
        self.one_time_fees_label.setObjectName(u"one_time_fees_label")
        self.one_time_fees_label.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop)

        self.formLayout_6.setWidget(2, QFormLayout.ItemRole.LabelRole, self.one_time_fees_label)

        self.one_time_fees_table = QTableView(self.fee_group)
        self.one_time_fees_table.setObjectName(u"one_time_fees_table")
        self.one_time_fees_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.one_time_fees_table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.one_time_fees_table.setAutoScroll(False)
        self.one_time_fees_table.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.one_time_fees_table.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)

        self.formLayout_6.setWidget(2, QFormLayout.ItemRole.FieldRole, self.one_time_fees_table)


        self.verticalLayout_4.addWidget(self.fee_group)

        self.verticalSpacer_2 = QSpacerItem(20, 116, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_4.addItem(self.verticalSpacer_2)

        self.tabWidget.addTab(self.payment_tab, "")
        self.sessions_tab = QWidget()
        self.sessions_tab.setObjectName(u"sessions_tab")
        self.verticalLayout_5 = QVBoxLayout(self.sessions_tab)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.sessions_table = QTableView(self.sessions_tab)
        self.sessions_table.setObjectName(u"sessions_table")
        self.sessions_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.sessions_table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.sessions_table.setAutoScroll(False)
        self.sessions_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.sessions_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.sessions_table.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.sessions_table.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)

        self.verticalLayout_5.addWidget(self.sessions_table)

        self.tabWidget.addTab(self.sessions_tab, "")
        self.relatives_tab = QWidget()
        self.relatives_tab.setObjectName(u"relatives_tab")
        self.verticalLayout_6 = QVBoxLayout(self.relatives_tab)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.relatives_label = QLabel(self.relatives_tab)
        self.relatives_label.setObjectName(u"relatives_label")

        self.verticalLayout_6.addWidget(self.relatives_label)

        self.relatives_table = QTableView(self.relatives_tab)
        self.relatives_table.setObjectName(u"relatives_table")
        self.relatives_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.relatives_table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.relatives_table.setAutoScroll(False)
        self.relatives_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.relatives_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.relatives_table.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.relatives_table.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)

        self.verticalLayout_6.addWidget(self.relatives_table)

        self.likely_relatives_label = QLabel(self.relatives_tab)
        self.likely_relatives_label.setObjectName(u"likely_relatives_label")

        self.verticalLayout_6.addWidget(self.likely_relatives_label)

        self.likely_relatives_table = QTableView(self.relatives_tab)
        self.likely_relatives_table.setObjectName(u"likely_relatives_table")
        self.likely_relatives_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.likely_relatives_table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.likely_relatives_table.setAutoScroll(False)
        self.likely_relatives_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.likely_relatives_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.likely_relatives_table.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.likely_relatives_table.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)

        self.verticalLayout_6.addWidget(self.likely_relatives_table)

        self.potential_relatives_label = QLabel(self.relatives_tab)
        self.potential_relatives_label.setObjectName(u"potential_relatives_label")

        self.verticalLayout_6.addWidget(self.potential_relatives_label)

        self.potential_relatives_search = FilterWidget(self.relatives_tab)
        self.potential_relatives_search.setObjectName(u"potential_relatives_search")

        self.verticalLayout_6.addWidget(self.potential_relatives_search)

        self.potential_relatives_table = QTableView(self.relatives_tab)
        self.potential_relatives_table.setObjectName(u"potential_relatives_table")
        self.potential_relatives_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.potential_relatives_table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.potential_relatives_table.setAutoScroll(False)
        self.potential_relatives_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.potential_relatives_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.potential_relatives_table.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.potential_relatives_table.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)

        self.verticalLayout_6.addWidget(self.potential_relatives_table)

        self.tabWidget.addTab(self.relatives_tab, "")

        self.verticalLayout_3.addWidget(self.tabWidget)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout_2.addWidget(self.scrollArea)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.delete_button = QPushButton(MemberDialog)
        self.delete_button.setObjectName(u"delete_button")

        self.horizontalLayout.addWidget(self.delete_button)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.cancel_button = QPushButton(MemberDialog)
        self.cancel_button.setObjectName(u"cancel_button")

        self.horizontalLayout.addWidget(self.cancel_button)

        self.save_button = QPushButton(MemberDialog)
        self.save_button.setObjectName(u"save_button")

        self.horizontalLayout.addWidget(self.save_button)


        self.verticalLayout_2.addLayout(self.horizontalLayout)


        self.retranslateUi(MemberDialog)

        self.tabWidget.setCurrentIndex(0)
        self.gender_combo.setCurrentIndex(-1)

    # setupUi

    def retranslateUi(self, MemberDialog):
        MemberDialog.setWindowTitle(QCoreApplication.translate("MemberDialog", u"Dialog", None))
        self.personal_info_group.setTitle(QCoreApplication.translate("MemberDialog", u"Personal", None))
        self.gender_label.setText(QCoreApplication.translate("MemberDialog", u"Gender", None))
        self.gender_combo.setItemText(0, QCoreApplication.translate("MemberDialog", u"Male", None))
        self.gender_combo.setItemText(1, QCoreApplication.translate("MemberDialog", u"Female", None))
        self.gender_combo.setItemText(2, QCoreApplication.translate("MemberDialog", u"Diverse", None))

        self.first_name_label.setText(QCoreApplication.translate("MemberDialog", u"First name(s)", None))
        self.last_name_label.setText(QCoreApplication.translate("MemberDialog", u"Last name", None))
        self.birthday_label.setText(QCoreApplication.translate("MemberDialog", u"Birthday", None))
        self.first_name_edit.setPlaceholderText(QCoreApplication.translate("MemberDialog", u"Sarah", None))
        self.last_name_edit.setPlaceholderText(QCoreApplication.translate("MemberDialog", u"Walker", None))
        self.birthday_edit.setDisplayFormat(QCoreApplication.translate("MemberDialog", u"dd.MM.yyyy", None))
        self.address_group.setTitle(QCoreApplication.translate("MemberDialog", u"Address", None))
        self.street_label.setText(QCoreApplication.translate("MemberDialog", u"Street", None))
        self.street_number_label.setText(QCoreApplication.translate("MemberDialog", u"Street number", None))
        self.postal_code_label.setText(QCoreApplication.translate("MemberDialog", u"Postal code", None))
        self.city_label.setText(QCoreApplication.translate("MemberDialog", u"City", None))
        self.street_edit.setPlaceholderText(QCoreApplication.translate("MemberDialog", u"Hollywood Boulevard", None))
        self.street_number_edit.setPlaceholderText(QCoreApplication.translate("MemberDialog", u"12", None))
        self.city_edit.setPlaceholderText(QCoreApplication.translate("MemberDialog", u"Los Angeles", None))
        self.postal_code_edit.setPlaceholderText(QCoreApplication.translate("MemberDialog", u"90059", None))
        self.contact_group.setTitle(QCoreApplication.translate("MemberDialog", u"Contact", None))
        self.phone_number_label.setText(QCoreApplication.translate("MemberDialog", u"Phone number", None))
        self.phone_number_edit.setPlaceholderText(QCoreApplication.translate("MemberDialog", u"773-702-1000", None))
        self.email_label.setText(QCoreApplication.translate("MemberDialog", u"Email", None))
        self.email_edit.setPlaceholderText(QCoreApplication.translate("MemberDialog", u"sarah.walker@gmail.com", None))
        self.membership_group.setTitle(QCoreApplication.translate("MemberDialog", u"Membership", None))
        self.entry_date_label.setText(QCoreApplication.translate("MemberDialog", u"Entry date", None))
        self.exit_date_label.setText(QCoreApplication.translate("MemberDialog", u"Exit date", None))
        self.entry_date_edit.setDisplayFormat(QCoreApplication.translate("MemberDialog", u"dd.MM.yyyy", None))
        self.exit_date_edit.setDisplayFormat(QCoreApplication.translate("MemberDialog", u"dd.MM.yyyy", None))
        self.exited_checkbox.setText(QCoreApplication.translate("MemberDialog", u"Exited", None))
        self.honorary_member_checkbox.setText(QCoreApplication.translate("MemberDialog", u"Honorary member", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.general_tab), QCoreApplication.translate("MemberDialog", u"General", None))
        self.bank_group.setTitle(QCoreApplication.translate("MemberDialog", u"Bank details", None))
        self.sepa_mandate_label.setText(QCoreApplication.translate("MemberDialog", u"SEPA mandate", None))
        self.sepa_mandate_date_edit.setDisplayFormat(QCoreApplication.translate("MemberDialog", u"dd.MM.yyyy", None))
        self.sepa_mandate_checkbox.setText(QCoreApplication.translate("MemberDialog", u"Given", None))
        self.iban_label.setText(QCoreApplication.translate("MemberDialog", u"IBAN", None))
        self.iban_edit.setPlaceholderText(QCoreApplication.translate("MemberDialog", u"DE75 5121 0800 1245 1261 99", None))
        self.bic_label.setText(QCoreApplication.translate("MemberDialog", u"BIC", None))
        self.bic_edit.setPlaceholderText("")
        self.account_owner_label.setText(QCoreApplication.translate("MemberDialog", u"Account owner", None))
        self.account_owner_edit.setPlaceholderText(QCoreApplication.translate("MemberDialog", u"Mr. & Ms. Smith", None))
        self.institute_label.setText(QCoreApplication.translate("MemberDialog", u"Institute", None))
        self.institute_edit.setPlaceholderText("")
        self.fee_group.setTitle(QCoreApplication.translate("MemberDialog", u"Fees", None))
        self.monthly_fee_label.setText(QCoreApplication.translate("MemberDialog", u"Monthly fee", None))
        self.monthly_fee_overwrite_checkbox.setText(QCoreApplication.translate("MemberDialog", u"Overwrite", None))
        self.monthly_fee_edit.setSuffix(QCoreApplication.translate("MemberDialog", u"\u20ac", None))
        self.one_time_fees_label.setText(QCoreApplication.translate("MemberDialog", u"One-time fees", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.payment_tab), QCoreApplication.translate("MemberDialog", u"Payment", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.sessions_tab), QCoreApplication.translate("MemberDialog", u"Sessions", None))
        self.relatives_label.setText(QCoreApplication.translate("MemberDialog", u"Relatives", None))
        self.likely_relatives_label.setText(QCoreApplication.translate("MemberDialog", u"Likely relatives", None))
        self.potential_relatives_label.setText(QCoreApplication.translate("MemberDialog", u"Potential relatives", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.relatives_tab), QCoreApplication.translate("MemberDialog", u"Relatives", None))
        self.delete_button.setText(QCoreApplication.translate("MemberDialog", u"Delete", None))
        self.cancel_button.setText(QCoreApplication.translate("MemberDialog", u"Cancel", None))
        self.save_button.setText(QCoreApplication.translate("MemberDialog", u"Save", None))
    # retranslateUi

