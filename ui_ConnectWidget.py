# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ConnectWidget.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QFormLayout, QFrame,
    QGroupBox, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QScrollArea, QSizePolicy, QSpacerItem,
    QSpinBox, QVBoxLayout, QWidget)

from PathSelectorWidget import PathSelectorWidget

class Ui_ConnectWidget(object):
    def setupUi(self, ConnectWidget):
        if not ConnectWidget.objectName():
            ConnectWidget.setObjectName(u"ConnectWidget")
        ConnectWidget.resize(697, 576)
        self.verticalLayout = QVBoxLayout(ConnectWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.scrollArea = QScrollArea(ConnectWidget)
        self.scrollArea.setObjectName(u"scrollArea")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scrollArea.sizePolicy().hasHeightForWidth())
        self.scrollArea.setSizePolicy(sizePolicy)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 660, 525))
        self.verticalLayout_2 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout_17 = QHBoxLayout()
        self.horizontalLayout_17.setObjectName(u"horizontalLayout_17")
        self.connection_type_label = QLabel(self.scrollAreaWidgetContents)
        self.connection_type_label.setObjectName(u"connection_type_label")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.connection_type_label.sizePolicy().hasHeightForWidth())
        self.connection_type_label.setSizePolicy(sizePolicy1)

        self.horizontalLayout_17.addWidget(self.connection_type_label)

        self.connection_type_combo = QComboBox(self.scrollAreaWidgetContents)
        self.connection_type_combo.addItem("")
        self.connection_type_combo.addItem("")
        self.connection_type_combo.setObjectName(u"connection_type_combo")

        self.horizontalLayout_17.addWidget(self.connection_type_combo)

        self.horizontalSpacer_13 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_17.addItem(self.horizontalSpacer_13)


        self.verticalLayout_2.addLayout(self.horizontalLayout_17)

        self.line_3 = QFrame(self.scrollAreaWidgetContents)
        self.line_3.setObjectName(u"line_3")
        self.line_3.setFrameShape(QFrame.Shape.HLine)
        self.line_3.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_2.addWidget(self.line_3)

        self.database_group = QGroupBox(self.scrollAreaWidgetContents)
        self.database_group.setObjectName(u"database_group")
        self.formLayout_7 = QFormLayout(self.database_group)
        self.formLayout_7.setObjectName(u"formLayout_7")
        self.db_backend_label = QLabel(self.database_group)
        self.db_backend_label.setObjectName(u"db_backend_label")

        self.formLayout_7.setWidget(0, QFormLayout.LabelRole, self.db_backend_label)

        self.db_backend_combo = QComboBox(self.database_group)
        self.db_backend_combo.addItem("")
        self.db_backend_combo.addItem("")
        self.db_backend_combo.addItem("")
        self.db_backend_combo.setObjectName(u"db_backend_combo")

        self.formLayout_7.setWidget(0, QFormLayout.FieldRole, self.db_backend_combo)

        self.db_user_label = QLabel(self.database_group)
        self.db_user_label.setObjectName(u"db_user_label")

        self.formLayout_7.setWidget(1, QFormLayout.LabelRole, self.db_user_label)

        self.db_user_input = QLineEdit(self.database_group)
        self.db_user_input.setObjectName(u"db_user_input")

        self.formLayout_7.setWidget(1, QFormLayout.FieldRole, self.db_user_input)

        self.db_password_label = QLabel(self.database_group)
        self.db_password_label.setObjectName(u"db_password_label")

        self.formLayout_7.setWidget(2, QFormLayout.LabelRole, self.db_password_label)

        self.db_password_edit = QLineEdit(self.database_group)
        self.db_password_edit.setObjectName(u"db_password_edit")
        self.db_password_edit.setEchoMode(QLineEdit.EchoMode.Password)

        self.formLayout_7.setWidget(2, QFormLayout.FieldRole, self.db_password_edit)

        self.db_host_label = QLabel(self.database_group)
        self.db_host_label.setObjectName(u"db_host_label")

        self.formLayout_7.setWidget(3, QFormLayout.LabelRole, self.db_host_label)

        self.db_host_input = QLineEdit(self.database_group)
        self.db_host_input.setObjectName(u"db_host_input")

        self.formLayout_7.setWidget(3, QFormLayout.FieldRole, self.db_host_input)

        self.db_port_label = QLabel(self.database_group)
        self.db_port_label.setObjectName(u"db_port_label")

        self.formLayout_7.setWidget(4, QFormLayout.LabelRole, self.db_port_label)

        self.db_port_spinner = QSpinBox(self.database_group)
        self.db_port_spinner.setObjectName(u"db_port_spinner")
        self.db_port_spinner.setMaximum(999999)

        self.formLayout_7.setWidget(4, QFormLayout.FieldRole, self.db_port_spinner)

        self.db_name_label = QLabel(self.database_group)
        self.db_name_label.setObjectName(u"db_name_label")

        self.formLayout_7.setWidget(5, QFormLayout.LabelRole, self.db_name_label)

        self.db_name_input = QLineEdit(self.database_group)
        self.db_name_input.setObjectName(u"db_name_input")

        self.formLayout_7.setWidget(5, QFormLayout.FieldRole, self.db_name_input)


        self.verticalLayout_2.addWidget(self.database_group)

        self.ssh_group = QGroupBox(self.scrollAreaWidgetContents)
        self.ssh_group.setObjectName(u"ssh_group")
        self.formLayout_8 = QFormLayout(self.ssh_group)
        self.formLayout_8.setObjectName(u"formLayout_8")
        self.ssh_user_label = QLabel(self.ssh_group)
        self.ssh_user_label.setObjectName(u"ssh_user_label")

        self.formLayout_8.setWidget(0, QFormLayout.LabelRole, self.ssh_user_label)

        self.ssh_user_input = QLineEdit(self.ssh_group)
        self.ssh_user_input.setObjectName(u"ssh_user_input")

        self.formLayout_8.setWidget(0, QFormLayout.FieldRole, self.ssh_user_input)

        self.ssh_port_label = QLabel(self.ssh_group)
        self.ssh_port_label.setObjectName(u"ssh_port_label")

        self.formLayout_8.setWidget(1, QFormLayout.LabelRole, self.ssh_port_label)

        self.ssh_port_spinner = QSpinBox(self.ssh_group)
        self.ssh_port_spinner.setObjectName(u"ssh_port_spinner")
        self.ssh_port_spinner.setMaximum(999999)
        self.ssh_port_spinner.setValue(22)

        self.formLayout_8.setWidget(1, QFormLayout.FieldRole, self.ssh_port_spinner)

        self.ssh_password_label = QLabel(self.ssh_group)
        self.ssh_password_label.setObjectName(u"ssh_password_label")

        self.formLayout_8.setWidget(2, QFormLayout.LabelRole, self.ssh_password_label)

        self.ssh_password_input = QLineEdit(self.ssh_group)
        self.ssh_password_input.setObjectName(u"ssh_password_input")
        self.ssh_password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.formLayout_8.setWidget(2, QFormLayout.FieldRole, self.ssh_password_input)

        self.ssh_key_label = QLabel(self.ssh_group)
        self.ssh_key_label.setObjectName(u"ssh_key_label")

        self.formLayout_8.setWidget(3, QFormLayout.LabelRole, self.ssh_key_label)

        self.ssh_key_input = PathSelectorWidget(self.ssh_group)
        self.ssh_key_input.setObjectName(u"ssh_key_input")

        self.formLayout_8.setWidget(3, QFormLayout.FieldRole, self.ssh_key_input)


        self.verticalLayout_2.addWidget(self.ssh_group)

        self.verticalSpacer_9 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer_9)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout.addWidget(self.scrollArea)

        self.horizontalLayout_19 = QHBoxLayout()
        self.horizontalLayout_19.setObjectName(u"horizontalLayout_19")
        self.horizontalSpacer_14 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_19.addItem(self.horizontalSpacer_14)

        self.pushButton_22 = QPushButton(ConnectWidget)
        self.pushButton_22.setObjectName(u"pushButton_22")
        self.pushButton_22.setEnabled(False)

        self.horizontalLayout_19.addWidget(self.pushButton_22)

        self.connect_button_3 = QPushButton(ConnectWidget)
        self.connect_button_3.setObjectName(u"connect_button_3")
        sizePolicy1.setHeightForWidth(self.connect_button_3.sizePolicy().hasHeightForWidth())
        self.connect_button_3.setSizePolicy(sizePolicy1)

        self.horizontalLayout_19.addWidget(self.connect_button_3)


        self.verticalLayout.addLayout(self.horizontalLayout_19)


        self.retranslateUi(ConnectWidget)

        QMetaObject.connectSlotsByName(ConnectWidget)
    # setupUi

    def retranslateUi(self, ConnectWidget):
        ConnectWidget.setWindowTitle(QCoreApplication.translate("ConnectWidget", u"Form", None))
        self.connection_type_label.setText(QCoreApplication.translate("ConnectWidget", u"Connection type", None))
        self.connection_type_combo.setItemText(0, QCoreApplication.translate("ConnectWidget", u"Regular", None))
        self.connection_type_combo.setItemText(1, QCoreApplication.translate("ConnectWidget", u"SSH-Tunnel", None))

        self.database_group.setTitle(QCoreApplication.translate("ConnectWidget", u"Database", None))
        self.db_backend_label.setText(QCoreApplication.translate("ConnectWidget", u"Backend", None))
        self.db_backend_combo.setItemText(0, QCoreApplication.translate("ConnectWidget", u"SQLite", None))
        self.db_backend_combo.setItemText(1, QCoreApplication.translate("ConnectWidget", u"PostgreSQL", None))
        self.db_backend_combo.setItemText(2, QCoreApplication.translate("ConnectWidget", u"MySQL", None))

        self.db_user_label.setText(QCoreApplication.translate("ConnectWidget", u"User", None))
        self.db_user_input.setPlaceholderText(QCoreApplication.translate("ConnectWidget", u"db_username", None))
        self.db_password_label.setText(QCoreApplication.translate("ConnectWidget", u"Password", None))
        self.db_host_label.setText(QCoreApplication.translate("ConnectWidget", u"Host", None))
        self.db_host_input.setPlaceholderText(QCoreApplication.translate("ConnectWidget", u"mydb.example.com", None))
        self.db_port_label.setText(QCoreApplication.translate("ConnectWidget", u"Port", None))
        self.db_name_label.setText(QCoreApplication.translate("ConnectWidget", u"Database", None))
        self.db_name_input.setPlaceholderText(QCoreApplication.translate("ConnectWidget", u"awesome_dataset", None))
        self.ssh_group.setTitle(QCoreApplication.translate("ConnectWidget", u"SSH", None))
        self.ssh_user_label.setText(QCoreApplication.translate("ConnectWidget", u"User", None))
        self.ssh_user_input.setPlaceholderText(QCoreApplication.translate("ConnectWidget", u"ssh_username", None))
        self.ssh_port_label.setText(QCoreApplication.translate("ConnectWidget", u"Port", None))
        self.ssh_password_label.setText(QCoreApplication.translate("ConnectWidget", u"Password", None))
        self.ssh_key_label.setText(QCoreApplication.translate("ConnectWidget", u"Private key", None))
        self.pushButton_22.setText(QCoreApplication.translate("ConnectWidget", u"Cancel", None))
        self.connect_button_3.setText(QCoreApplication.translate("ConnectWidget", u"Connect", None))
    # retranslateUi

