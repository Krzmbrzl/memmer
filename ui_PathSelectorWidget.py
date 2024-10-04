# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'PathSelectorWidget.ui'
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLineEdit, QPushButton,
    QSizePolicy, QWidget)

class Ui_PathSelectorWidget(object):
    def setupUi(self, PathSelectorWidget):
        if not PathSelectorWidget.objectName():
            PathSelectorWidget.setObjectName(u"PathSelectorWidget")
        PathSelectorWidget.resize(393, 34)
        self.horizontalLayout = QHBoxLayout(PathSelectorWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.path_input = QLineEdit(PathSelectorWidget)
        self.path_input.setObjectName(u"path_input")

        self.horizontalLayout.addWidget(self.path_input)

        self.browse_button = QPushButton(PathSelectorWidget)
        self.browse_button.setObjectName(u"browse_button")

        self.horizontalLayout.addWidget(self.browse_button)


        self.retranslateUi(PathSelectorWidget)

        QMetaObject.connectSlotsByName(PathSelectorWidget)
    # setupUi

    def retranslateUi(self, PathSelectorWidget):
        PathSelectorWidget.setWindowTitle(QCoreApplication.translate("PathSelectorWidget", u"Form", None))
        self.browse_button.setText(QCoreApplication.translate("PathSelectorWidget", u"\u2026", None))
    # retranslateUi

