import os
from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from PyQt6 import QtTest

dir_path = os.getcwd()

def createImage(ui, image, width, height):
    pic = QLabel(ui)
    pic.setPixmap(QPixmap(dir_path+image).scaledToWidth(width))
    pic.setFixedWidth(width)
    pic.setFixedHeight(height)
    pic.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
    pic.setAutoFillBackground(True)
    pic.move(int(ui.rect().center().x()-int(width/2)),int(ui.rect().center().y()-int(height/2)))
    return pic

def checkmarkIcon(ui):
    pic = createImage(ui=ui, image='/res/checkmarkIcon.png', width=158, height=159)
    pic.show()
    QtTest.QTest.qWait(3000)
    pic.hide()
    pic.destroy()