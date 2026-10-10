# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'MemberListWidget.ui'
##
## Created by: Qt User Interface Compiler version 6.11.2
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
    QFormLayout, QGroupBox, QHBoxLayout, QHeaderView,
    QLabel, QLineEdit, QListWidget, QListWidgetItem,
    QProgressBar, QPushButton, QSizePolicy, QSpacerItem,
    QTableView, QVBoxLayout, QWidget)

from ..FilterWidget import FilterWidget
from ..PathSelectorWidget import PathSelectorWidget

class Ui_MemberListWidget(object):
    def setupUi(self, MemberListWidget):
        if not MemberListWidget.objectName():
            MemberListWidget.setObjectName(u"MemberListWidget")
        MemberListWidget.resize(720, 640)
        self.verticalLayout = QVBoxLayout(MemberListWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.selection_group = QGroupBox(MemberListWidget)
        self.selection_group.setObjectName(u"selection_group")
        self.selection_layout = QVBoxLayout(self.selection_group)
        self.selection_layout.setObjectName(u"selection_layout")
        self.selection_combo_layout = QHBoxLayout()
        self.selection_combo_layout.setObjectName(u"selection_combo_layout")
        self.selection_label = QLabel(self.selection_group)
        self.selection_label.setObjectName(u"selection_label")

        self.selection_combo_layout.addWidget(self.selection_label)

        self.selection_combo = QComboBox(self.selection_group)
        self.selection_combo.setObjectName(u"selection_combo")

        self.selection_combo_layout.addWidget(self.selection_combo)


        self.selection_layout.addLayout(self.selection_combo_layout)

        self.member_tables_layout = QHBoxLayout()
        self.member_tables_layout.setObjectName(u"member_tables_layout")
        self.included_group = QGroupBox(self.selection_group)
        self.included_group.setObjectName(u"included_group")
        self.included_layout = QVBoxLayout(self.included_group)
        self.included_layout.setObjectName(u"included_layout")
        self.included_table = QTableView(self.included_group)
        self.included_table.setObjectName(u"included_table")

        self.included_layout.addWidget(self.included_table)


        self.member_tables_layout.addWidget(self.included_group)

        self.available_group = QGroupBox(self.selection_group)
        self.available_group.setObjectName(u"available_group")
        self.available_layout = QVBoxLayout(self.available_group)
        self.available_layout.setObjectName(u"available_layout")
        self.available_filter = FilterWidget(self.available_group)
        self.available_filter.setObjectName(u"available_filter")

        self.available_layout.addWidget(self.available_filter)

        self.available_table = QTableView(self.available_group)
        self.available_table.setObjectName(u"available_table")

        self.available_layout.addWidget(self.available_table)


        self.member_tables_layout.addWidget(self.available_group)


        self.selection_layout.addLayout(self.member_tables_layout)

        self.selection_hint = QLabel(self.selection_group)
        self.selection_hint.setObjectName(u"selection_hint")

        self.selection_layout.addWidget(self.selection_hint)


        self.verticalLayout.addWidget(self.selection_group)

        self.columns_group = QGroupBox(MemberListWidget)
        self.columns_group.setObjectName(u"columns_group")
        self.columns_layout = QHBoxLayout(self.columns_group)
        self.columns_layout.setObjectName(u"columns_layout")
        self.available_columns_layout = QVBoxLayout()
        self.available_columns_layout.setObjectName(u"available_columns_layout")
        self.available_columns_label = QLabel(self.columns_group)
        self.available_columns_label.setObjectName(u"available_columns_label")

        self.available_columns_layout.addWidget(self.available_columns_label)

        self.available_columns = QListWidget(self.columns_group)
        self.available_columns.setObjectName(u"available_columns")

        self.available_columns_layout.addWidget(self.available_columns)


        self.columns_layout.addLayout(self.available_columns_layout)

        self.column_buttons_layout = QVBoxLayout()
        self.column_buttons_layout.setObjectName(u"column_buttons_layout")
        self.column_buttons_top_spacer = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.column_buttons_layout.addItem(self.column_buttons_top_spacer)

        self.add_column_button = QPushButton(self.columns_group)
        self.add_column_button.setObjectName(u"add_column_button")

        self.column_buttons_layout.addWidget(self.add_column_button)

        self.remove_column_button = QPushButton(self.columns_group)
        self.remove_column_button.setObjectName(u"remove_column_button")

        self.column_buttons_layout.addWidget(self.remove_column_button)

        self.add_empty_button = QPushButton(self.columns_group)
        self.add_empty_button.setObjectName(u"add_empty_button")

        self.column_buttons_layout.addWidget(self.add_empty_button)

        self.add_checkbox_button = QPushButton(self.columns_group)
        self.add_checkbox_button.setObjectName(u"add_checkbox_button")

        self.column_buttons_layout.addWidget(self.add_checkbox_button)

        self.column_buttons_bottom_spacer = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.column_buttons_layout.addItem(self.column_buttons_bottom_spacer)


        self.columns_layout.addLayout(self.column_buttons_layout)

        self.chosen_columns_layout = QVBoxLayout()
        self.chosen_columns_layout.setObjectName(u"chosen_columns_layout")
        self.chosen_columns_label = QLabel(self.columns_group)
        self.chosen_columns_label.setObjectName(u"chosen_columns_label")

        self.chosen_columns_layout.addWidget(self.chosen_columns_label)

        self.chosen_columns = QListWidget(self.columns_group)
        self.chosen_columns.setObjectName(u"chosen_columns")

        self.chosen_columns_layout.addWidget(self.chosen_columns)


        self.columns_layout.addLayout(self.chosen_columns_layout)

        self.reorder_buttons_layout = QVBoxLayout()
        self.reorder_buttons_layout.setObjectName(u"reorder_buttons_layout")
        self.reorder_top_spacer = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.reorder_buttons_layout.addItem(self.reorder_top_spacer)

        self.up_button = QPushButton(self.columns_group)
        self.up_button.setObjectName(u"up_button")

        self.reorder_buttons_layout.addWidget(self.up_button)

        self.down_button = QPushButton(self.columns_group)
        self.down_button.setObjectName(u"down_button")

        self.reorder_buttons_layout.addWidget(self.down_button)

        self.reorder_bottom_spacer = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.reorder_buttons_layout.addItem(self.reorder_bottom_spacer)


        self.columns_layout.addLayout(self.reorder_buttons_layout)


        self.verticalLayout.addWidget(self.columns_group)

        self.template_group = QGroupBox(MemberListWidget)
        self.template_group.setObjectName(u"template_group")
        self.template_layout = QHBoxLayout(self.template_group)
        self.template_layout.setObjectName(u"template_layout")
        self.template_combo = QComboBox(self.template_group)
        self.template_combo.setObjectName(u"template_combo")

        self.template_layout.addWidget(self.template_combo)

        self.save_template_button = QPushButton(self.template_group)
        self.save_template_button.setObjectName(u"save_template_button")

        self.template_layout.addWidget(self.save_template_button)

        self.update_template_button = QPushButton(self.template_group)
        self.update_template_button.setObjectName(u"update_template_button")

        self.template_layout.addWidget(self.update_template_button)

        self.delete_template_button = QPushButton(self.template_group)
        self.delete_template_button.setObjectName(u"delete_template_button")

        self.template_layout.addWidget(self.delete_template_button)


        self.verticalLayout.addWidget(self.template_group)

        self.options_group = QGroupBox(MemberListWidget)
        self.options_group.setObjectName(u"options_group")
        self.options_layout = QFormLayout(self.options_group)
        self.options_layout.setObjectName(u"options_layout")
        self.format_label = QLabel(self.options_group)
        self.format_label.setObjectName(u"format_label")

        self.options_layout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.format_label)

        self.format_combo = QComboBox(self.options_group)
        self.format_combo.setObjectName(u"format_combo")

        self.options_layout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.format_combo)

        self.as_of_label = QLabel(self.options_group)
        self.as_of_label.setObjectName(u"as_of_label")

        self.options_layout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.as_of_label)

        self.as_of_input = QDateEdit(self.options_group)
        self.as_of_input.setObjectName(u"as_of_input")
        self.as_of_input.setCalendarPopup(True)

        self.options_layout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.as_of_input)

        self.out_file_label = QLabel(self.options_group)
        self.out_file_label.setObjectName(u"out_file_label")

        self.options_layout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.out_file_label)

        self.out_file_input = PathSelectorWidget(self.options_group)
        self.out_file_input.setObjectName(u"out_file_input")
        self.out_file_input.setMinimumSize(QSize(10, 0))

        self.options_layout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.out_file_input)


        self.verticalLayout.addWidget(self.options_group)

        self.pdf_options_group = QGroupBox(MemberListWidget)
        self.pdf_options_group.setObjectName(u"pdf_options_group")
        self.pdf_options_layout = QFormLayout(self.pdf_options_group)
        self.pdf_options_layout.setObjectName(u"pdf_options_layout")
        self.title_label = QLabel(self.pdf_options_group)
        self.title_label.setObjectName(u"title_label")

        self.pdf_options_layout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.title_label)

        self.title_input = QLineEdit(self.pdf_options_group)
        self.title_input.setObjectName(u"title_input")

        self.pdf_options_layout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.title_input)

        self.orientation_label = QLabel(self.pdf_options_group)
        self.orientation_label.setObjectName(u"orientation_label")

        self.pdf_options_layout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.orientation_label)

        self.orientation_combo = QComboBox(self.pdf_options_group)
        self.orientation_combo.setObjectName(u"orientation_combo")

        self.pdf_options_layout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.orientation_combo)

        self.zebra_check = QCheckBox(self.pdf_options_group)
        self.zebra_check.setObjectName(u"zebra_check")
        self.zebra_check.setChecked(True)

        self.pdf_options_layout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.zebra_check)


        self.verticalLayout.addWidget(self.pdf_options_group)

        self.progress_bar = QProgressBar(MemberListWidget)
        self.progress_bar.setObjectName(u"progress_bar")
        self.progress_bar.setVisible(False)
        self.progress_bar.setValue(0)

        self.verticalLayout.addWidget(self.progress_bar)

        self.progress_label = QLabel(MemberListWidget)
        self.progress_label.setObjectName(u"progress_label")
        self.progress_label.setVisible(False)

        self.verticalLayout.addWidget(self.progress_label)

        self.buttons_layout = QHBoxLayout()
        self.buttons_layout.setObjectName(u"buttons_layout")
        self.back_button = QPushButton(MemberListWidget)
        self.back_button.setObjectName(u"back_button")

        self.buttons_layout.addWidget(self.back_button)

        self.buttons_spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.buttons_layout.addItem(self.buttons_spacer)

        self.create_button = QPushButton(MemberListWidget)
        self.create_button.setObjectName(u"create_button")

        self.buttons_layout.addWidget(self.create_button)


        self.verticalLayout.addLayout(self.buttons_layout)


        self.retranslateUi(MemberListWidget)
    # setupUi

    def retranslateUi(self, MemberListWidget):
        MemberListWidget.setWindowTitle(QCoreApplication.translate("MemberListWidget", u"Form", None))
        self.selection_group.setTitle(QCoreApplication.translate("MemberListWidget", u"Members", None))
        self.selection_label.setText(QCoreApplication.translate("MemberListWidget", u"Selection", None))
        self.included_group.setTitle(QCoreApplication.translate("MemberListWidget", u"Included", None))
        self.available_group.setTitle(QCoreApplication.translate("MemberListWidget", u"Available", None))
        self.selection_hint.setText(QCoreApplication.translate("MemberListWidget", u"Double-click a member to move them between the lists.", None))
        self.columns_group.setTitle(QCoreApplication.translate("MemberListWidget", u"Columns", None))
        self.available_columns_label.setText(QCoreApplication.translate("MemberListWidget", u"Available", None))
        self.add_column_button.setText(QCoreApplication.translate("MemberListWidget", u"Add >", None))
        self.remove_column_button.setText(QCoreApplication.translate("MemberListWidget", u"< Remove", None))
        self.add_empty_button.setText(QCoreApplication.translate("MemberListWidget", u"Add empty", None))
        self.add_checkbox_button.setText(QCoreApplication.translate("MemberListWidget", u"Add checkbox", None))
        self.chosen_columns_label.setText(QCoreApplication.translate("MemberListWidget", u"Chosen (printed left to right; double-click to rename)", None))
        self.up_button.setText(QCoreApplication.translate("MemberListWidget", u"Up", None))
        self.down_button.setText(QCoreApplication.translate("MemberListWidget", u"Down", None))
        self.template_group.setTitle(QCoreApplication.translate("MemberListWidget", u"Column template", None))
        self.save_template_button.setText(QCoreApplication.translate("MemberListWidget", u"Save as\u2026", None))
        self.update_template_button.setText(QCoreApplication.translate("MemberListWidget", u"Update", None))
        self.delete_template_button.setText(QCoreApplication.translate("MemberListWidget", u"Delete", None))
        self.options_group.setTitle(QCoreApplication.translate("MemberListWidget", u"Output", None))
        self.format_label.setText(QCoreApplication.translate("MemberListWidget", u"Format", None))
        self.as_of_label.setText(QCoreApplication.translate("MemberListWidget", u"Reference date", None))
        self.out_file_label.setText(QCoreApplication.translate("MemberListWidget", u"Output file", None))
        self.pdf_options_group.setTitle(QCoreApplication.translate("MemberListWidget", u"PDF options", None))
        self.title_label.setText(QCoreApplication.translate("MemberListWidget", u"Title", None))
        self.orientation_label.setText(QCoreApplication.translate("MemberListWidget", u"Orientation", None))
        self.zebra_check.setText(QCoreApplication.translate("MemberListWidget", u"Shade alternating rows", None))
        self.progress_label.setText("")
        self.back_button.setText(QCoreApplication.translate("MemberListWidget", u"Back", None))
        self.create_button.setText(QCoreApplication.translate("MemberListWidget", u"Create", None))
    # retranslateUi

