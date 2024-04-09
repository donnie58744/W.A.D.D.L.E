import os
from PyQt6.QtWidgets import QLabel, QFileDialog, QScrollArea, QWidget, QVBoxLayout, QGridLayout, QPushButton
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from PyQt6 import QtTest
from functools import partial

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

def console(consoleFrame, consoleTextEdit, value):
    if (value):
        consoleFrame.setStyleSheet("background: rgb(195, 177, 225); font-size:12px; font-weight: 800;")
        consoleTextEdit.appendPlainText(str(value))

def createImage(ui, image, width, height):
    pic = QLabel(ui)
    pic.setPixmap(QPixmap(dir_path+image).scaledToWidth(width))
    pic.setFixedWidth(width)
    pic.setFixedHeight(height)
    pic.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
    pic.setAutoFillBackground(True)
    pic.move(int(ui.rect().center().x()-int(width/2)),int(ui.rect().center().y()-int(height/2)))
    return pic

def createScrollArea(frame, request, layout, list, width, height, verticalScrollBarPolicy, horizontalScrollBarPolicy, function=None, functionArgs=None, buttonWidth=None, buttonHeight=None, css=None):
        countX=1
        countY=1
        scroll = QScrollArea(frame)
        widget = QWidget()

        match request:
            case 'label':
                for i in list:
                    if i != '':
                        object = QLabel(i)
                        layout.addWidget(object)
            case 'button':
                for i in list:
                    if i != '':
                        b1 = QPushButton(i)
                        b1.setFixedHeight(buttonHeight)
                        b1.setFixedWidth(buttonWidth)
                        b1.setCursor(Qt.CursorShape.CrossCursor)
                        b1.setStyleSheet(css)
                        b1.setCheckable(True)
                        b1.clicked.connect(partial(function, b1, functionArgs))
                        match layout:
                            case QGridLayout():
                                layout.addWidget(b1, countY, countX, 1, 1)
                                if (countX >= 3):
                                    countY+=1
                                    countX=0
                                countX+=1
                            case other:
                                layout.addWidget(b1)

        widget.setLayout(layout)

        #Scroll Area Properties
        scroll.setVerticalScrollBarPolicy(verticalScrollBarPolicy)
        scroll.setHorizontalScrollBarPolicy(horizontalScrollBarPolicy)
        scroll.setFixedWidth(width)
        scroll.setFixedHeight(height)
        scroll.setWidgetResizable(True)
        scroll.setWidget(widget)

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

def FileDialog(ui, request, nameFilter=None, defaultDir=None):
    dlg = QFileDialog(ui)
    match request:
        case "file":
            dlg.setFileMode(QFileDialog.FileMode.ExistingFile)
        case "folder":
            dlg.setFileMode(QFileDialog.FileMode.Directory)
    dlg.setDirectory(defaultDir)
    dlg.setNameFilter(nameFilter)

    if (dlg.exec()):
        dlgFilename = dlg.selectedFiles()
        return dlgFilename