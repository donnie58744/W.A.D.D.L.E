import os
from PyQt6.QtWidgets import QLabel, QFileDialog
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from PyQt6 import QtTest

dir_path = os.getcwd()

def loadingScreen(ui, loadingScreenStop=None, first=None):
    #Loading Screen
    if (first):
        loadingWidth=500
        loadingHeight=500
        ui.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        ui.setFixedWidth(loadingWidth)
        ui.setFixedHeight(loadingHeight)
        pic = createImage(ui=ui, image="/res/loadingScreen.png", width=loadingWidth+1, height=loadingHeight+1)
        pic.show()
        ui.show()
    #-------------#
    # End Loading
    if (loadingScreenStop):
        QtTest.QTest.qWait(1000)
        ui.setWindowFlags(ui.windowFlags() & ~Qt.WindowType.FramelessWindowHint)
        ui.hide()

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

def CenterWindow(ui, app):
    qr = ui.frameGeometry()
                
    cp = app.primaryScreen().availableGeometry().center()
    qr.moveCenter(cp)
    ui.move(qr.topLeft())

def CortexFileDialog(ui):
    dlg = QFileDialog(ui)
    dlg.setFileMode(QFileDialog.FileMode.ExistingFile)
    dlg.setDirectory("C:\Program Files (x86)\Razer\Razer Cortex")
    dlg.setNameFilter("EXE File (*.exe)")

    if (dlg.exec()):
        dlgFilename = dlg.selectedFiles()
        return dlgFilename