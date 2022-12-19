from pymem import Pymem
import os
import pystray
import sys
from PIL import Image
from PyQt6 import uic, QtTest
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton
from PyQt6.QtCore import Qt, QThread, pyqtSignal, pyqtSlot, QObject
from PyQt6.QtGui import QPixmap
from functools import partial
from libs.Config import *
from libs.SystemChanger import *
from libs.UiFunctions import *

class vars():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    defaultWidth = 0
    defaultHeight = 0

    optimizedWidth = 0
    optimizedHeight = 0
    programWatchlist = []
    priortyWatchList=['OVRServer_x64.exe']
    currentTrackedProgram = ''
    overide=False
    exeRunning=False
    defaultPowerPlan=None
    running=True
    stopLoadingScreen=False

    # Oculus Settings Memory
    oculusBoost=None

    # Process Window Memory
    watchlistBtnAmt=0
    buttonMem=0

dir_path = os.path.dirname(os.path.realpath(__file__))

class Ui(QMainWindow):
    mainThreadSig = pyqtSignal(str)
    programsToAdd=[]
    programsToRemove=[]

    def shutdown(self):
        app.quit()

    def loadingScreen(self, first=None):
        #Loading Screen
        if (first):
            loadingWidth=500
            loadingHeight=500
            self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
            self.setFixedWidth(loadingWidth)
            self.setFixedHeight(loadingHeight)
            pic = createImage(ui=self, image="/res/loadingScreen.png", width=loadingWidth+1, height=loadingHeight+1)
            pic.show()
            self.show()
        #-------------#
        # End Loading
        QtTest.QTest.qWait(2500)
        if (vars.stopLoadingScreen):
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.FramelessWindowHint)
            self.hide()
        else:
            self.loadingScreen()

    def __init__(self):
        super().__init__()
        app.setQuitOnLastWindowClosed(False)
        self.setFixedSize(self.size())
        # Center
        self.centerWindow()
        # Setup Threads
        self.trayIconThread = TrayIcon(self.mainThreadSig)
        self.trayIconFoo = QThread(self) 
        self.trayIconThread.moveToThread(self.trayIconFoo)

        self.watchlistThread=AutoVR(self.mainThreadSig)
        self.watchlistFoo=QThread(self)
        self.watchlistThread.moveToThread(self.watchlistFoo)

        self.priorityWatchlistThread=PriortyChanger(self.mainThreadSig)
        self.priorityWatchlistFoo=QThread(self)
        self.priorityWatchlistThread.moveToThread(self.priorityWatchlistFoo)

        self.trayIconFoo.started.connect(self.trayIconThread.executeThread)
        self.watchlistFoo.started.connect(self.watchlistThread.executeThread)
        self.priorityWatchlistFoo.started.connect(self.priorityWatchlistThread.executeThread)

        # Setup Thread Receiver
        self.mainThreadSig.connect(self.threadReciver)

        # Start Threads
        self.trayIconFoo.start()
        self.watchlistFoo.start()
        self.priorityWatchlistFoo.start()

        self.loadingScreen(first=True)

    @pyqtSlot(str)
    def threadReciver(self, sent):
        match sent:
            case 'ProcessManager':
                self.refreshProcessManager(varibles=True)
                self.show()
                self.activateWindow()
                self.centerWindow()
            case 'SettingsMenu':
                self.refreshSettingsMenu(menu='base')
                self.show()
                self.activateWindow()
                self.centerWindow()
            case 'centerWindow':
                self.centerWindow()
            case 'quit':
                vars.stopLoadingScreen=True
                vars.running=False
                changePowerPlan(plan='Default', id=vars.defaultPowerPlan)
                self.shutdown()

    def centerWindow(self):
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def toggledBtn(self, button, request):
        match request:
            case 'add':
                if (button.isChecked()):
                    self.programsToAdd.append(button.text())
                else:
                    self.programsToAdd.remove(button.text())
            case 'remove':
                if (button.isChecked()):
                    self.programsToRemove.append(button.text())
                else:
                    self.programsToRemove.remove(button.text())

    def refreshBtnClick(self):
        vars.overide = True
        self.refreshProcessManager(varibles=True)

    def addToWatchlist(self):
        try:
            if (self.programsToAdd):
                with open(dir_path+'/files/watchlist.txt', 'a') as f:
                    for x in self.programsToAdd:
                        f.write('\n'+str(x))
                self.programsToAdd=[]
                f.close()
                self.addBtn.setText('DONE!')
                self.addBtn.setStyleSheet("background:green")
                setupWatchList()
                QtTest.QTest.qWait(2500)
                self.refreshProcessManager(varibles=True)
        except Exception as e:
            self.addBtn.setText('ERROR!')
            self.addBtn.setStyleSheet("background:red")

    def removeFromWatchlist(self):
        try:
            if (self.programsToRemove):
                newWatchlist=[]
                with open(dir_path+'/files/watchlist.txt', 'r') as f:
                    watchlist=f.read()
                    for x in str(watchlist).split('\n'):
                        if (x not in self.programsToRemove):
                            newWatchlist.append(x)
                        else:
                            try:
                                vars.programWatchlist.remove(x)
                                print(vars.programWatchlist)
                            except Exception as e:
                                continue
                    self.programsToRemove=[]
                f.close()

                with open(dir_path+'/files/watchlist.txt', 'w') as f:
                    f.write("\n".join(newWatchlist))

                f.close()

                # If Watchlist has one left then change resolution and stuff
                print(len(vars.programWatchlist))
                if (len(vars.programWatchlist)==0):
                    vars.overide=True
                setupWatchList()

                self.refreshProcessManager(varibles=True)
        except Exception as e:
            print(e)
            print(vars.programWatchlist)
            self.removeBtn.setText('ERROR!')
            self.removeBtn.setStyleSheet("background:red")

    def createProcessButtons(self):
        buttonWidth=173
        buttonHeight=35
        maxBtnRow=int((self.processesScrollArea.width())/buttonWidth)
        amtBtn = 0
        gridPosX = 0
        gridPosY = 0
        
        for x in getRunningProcesses():
            name=x[0]
            if (amtBtn >= maxBtnRow):
                amtBtn=0
                gridPosX=0
                gridPosY+=50
            amtBtn+=1
            self.b1 = QPushButton(name, self.processesScrollArea)
            self.b1.setFixedHeight(buttonHeight)
            self.b1.setFixedWidth(buttonWidth)
            self.b1.setCursor(Qt.CursorShape.CrossCursor)
            self.b1.setStyleSheet('background-color:rgb(159, 189, 237); color:black; font-size:14px; text-align: left;')
            self.b1.setCheckable(True)
            self.b1.clicked.connect(partial(self.toggledBtn, self.b1, 'add'))
            self.b1.move(gridPosX,gridPosY)
            gridPosX+=int(self.b1.width())

    def createWatchlistButtons(self, overide=None):
        buttonSpacer=35
        maxButtonWidth=160
        buttonHeight=25
        gridPosX = 0
        gridPosY = 0
        maxBtnRow=int((self.listWidget.width())/maxButtonWidth)
        maxColumBtn = int((self.listWidget.height())/(buttonSpacer))

        match overide:
            case 'next':
                if (vars.buttonMem < len(vars.programWatchlist)):
                    vars.watchlistBtnAmt=0
                    self.refreshProcessManager()
            case 'back':
                if (vars.buttonMem!=maxColumBtn and vars.buttonMem >= maxColumBtn):
                    vars.buttonMem=(vars.buttonMem-maxColumBtn)-maxColumBtn
                    if (vars.buttonMem<0):
                        vars.buttonMem=0
                    vars.watchlistBtnAmt=0
                    self.refreshProcessManager()
        
        for x in vars.programWatchlist[vars.buttonMem:]:
            if (x != ''):
                if (vars.watchlistBtnAmt >= maxColumBtn):
                    pass
                else:
                    self.b1 = QPushButton(x, self.listWidget)
                    self.b1.setCheckable(True)
                    self.b1.setFixedHeight(buttonHeight)
                    self.b1.setMaximumWidth(maxButtonWidth)
                    self.b1.setCursor(Qt.CursorShape.PointingHandCursor)
                    self.b1.setStyleSheet('background-color:rgb(159, 189, 237); color:black; font-size:14px; text-align: left;')
                    self.b1.clicked.connect(partial(self.toggledBtn, self.b1, 'remove'))
                    self.b1.move(gridPosX,gridPosY)
                    gridPosY+=buttonSpacer
                    vars.watchlistBtnAmt+=1
                    vars.buttonMem+=1

    def refreshProcessManager(self, varibles=None, other=None):
        uic.loadUi(dir_path+'/ui/runningProcesses.ui', self)
        if (varibles):
            vars.watchlistBtnAmt=0
            vars.buttonMem=0
        self.programsToAdd=[]
        self.programsToRemove=[]
        setupWatchList()
        self.createProcessButtons()
        self.createWatchlistButtons()
        self.addBtn.clicked.connect(self.addToWatchlist)
        self.removeBtn.clicked.connect(self.removeFromWatchlist)
        self.refreshBtn.clicked.connect(self.refreshBtnClick)
        self.nextBtn.clicked.connect(lambda: self.createWatchlistButtons(overide='next'))
        self.backBtn.clicked.connect(lambda: self.createWatchlistButtons(overide='back'))

    # Settings Menu

    def applySettings(self, menu):
        match menu:
            case 'display':
                writeConfig(file='/files/config.json', key='optimizedWidth', value=self.optimizedWidthTxtBox.text())
                writeConfig(file='/files/config.json', key='optimizedHeight', value=self.optimizedHeightTxtBox.text())
                configMem(request='optimized')
                vars.exeRunning = False
            case 'oculus':
                if (not self.oculusPriorityCheckbox.isChecked()):
                    loopThroughChangePriority(list=vars.priortyWatchList, priority='normal')
                writeConfig(file='/files/config.json', key='oculusBoost', value=self.oculusPriorityCheckbox.isChecked())
                configMem(request='oculusBoost')
        checkmarkIcon(ui=self)

    def refreshSettingsMenu(self, menu):
        match menu:
            case 'base':
                uic.loadUi(dir_path+'/ui/settingsMenu.ui', self)
            case 'display':
                configMem(request='optimized')

                def resetBtnClicked():
                    configMem(request='defaultResoultion')
                    vars.overide=True
                    setupWatchList()
                    self.defaultWidthTxtBox.setText(str(vars.defaultWidth))
                    self.defaultHeightTxtBox.setText(str(vars.defaultHeight))
                    checkmarkIcon(ui=self)

                uic.loadUi(dir_path+'/ui/settings/displaySettings.ui', self)
                self.defaultWidthTxtBox.setText(str(vars.defaultWidth))
                self.defaultHeightTxtBox.setText(str(vars.defaultHeight))
                self.optimizedWidthTxtBox.setValue(vars.optimizedWidth)
                self.optimizedHeightTxtBox.setValue(vars.optimizedHeight)

                self.resetBtn.clicked.connect(resetBtnClicked)
                self.applyBtn.clicked.connect(lambda: self.applySettings(menu='display'))
                self.cancelBtn.clicked.connect(lambda: self.refreshSettingsMenu(menu='display'))
            case 'powerPlan':
                uic.loadUi(dir_path+'/ui/settings/powerPlanSettings.ui', self)

                self.resetBtn.clicked.connect(lambda: (configMem(request='defaultPowerPlan'),self.defaultPowerPlanTxtBox.setText(vars.defaultPowerPlan), checkmarkIcon(ui=self)))
                self.plansBtn.clicked.connect(openPowerPlans)
                self.defaultPowerPlanTxtBox.setText(vars.defaultPowerPlan)
                self.defaultPowerPlanTxtBox.setStyleSheet('background-color: rgb(86, 86, 86);\ncolor: rgb(255, 255, 255);')
            case 'oculus':
                configMem(request='oculusBoost')
                uic.loadUi(dir_path+'/ui/settings/oculusSettings.ui', self)
                self.oculusPriorityCheckbox.setChecked(vars.oculusBoost)
                self.applyBtn.clicked.connect(lambda: self.applySettings(menu='oculus'))
                self.cancelBtn.clicked.connect(lambda: self.refreshSettingsMenu(menu='oculus'))

        self.displayBtn.clicked.connect(lambda: self.refreshSettingsMenu(menu='display'))
        self.powerPlanBtn.clicked.connect(lambda: self.refreshSettingsMenu(menu='powerPlan'))
        self.oculusBtn.clicked.connect(lambda: self.refreshSettingsMenu(menu='oculus'))

    #--------------#

# Public Functions
def getWatchList(file):
    with open(vars.dir_path + file) as f:
        data = f.read()

    return data.split('\n')

def setupWatchList():
    print("Chekcing Watch List...")
    vars.programWatchlist=[]
    #Convert Json Dict to Pythhon Array
    for i in getWatchList('/files/watchlist.txt'):
        if (i != ''):
            vars.programWatchlist.append(i)

def configMem(request=None, all=None):
    if(request=='defaultResoultion' or all):
        defaultResolutionData=getCurrentResolution()
        vars.defaultWidth = int(defaultResolutionData[0])
        vars.defaultHeight = int(defaultResolutionData[1])
    if (request=='optimized'or all):
        configData=getConfig(file='/files/config.json')
        vars.optimizedWidth = int(configData['optimizedWidth'])
        vars.optimizedHeight = int(configData['optimizedHeight'])
    if (request=='oculusBoost'or all):
        vars.oculusBoost = bool(getConfig(file='/files/config.json')['oculusBoost'])
    if (request=='defaultPowerPlan' or all):
        vars.defaultPowerPlan=getCurrentPowerPlan()
        writeConfig(file='/files/config.json', key='defaultPowerPlan', value=vars.defaultPowerPlan)

class PriortyChanger(QObject):
    def __init__(self, signal_to_emit):
        super().__init__()
        self.signal_to_emit = signal_to_emit

    @pyqtSlot()
    def executeThread(self):
        while vars.running:
            if (vars.oculusBoost):
                loopThroughChangePriority(list=vars.priortyWatchList, priority='high')

            QtTest.QTest.qWait(10000)

class TrayIcon(QObject):
    def __init__(self, signal_to_emit):
        super().__init__()
        self.signal_to_emit = signal_to_emit

    def create_image(self):
        # Generate an image and draw a pattern
        image = Image.open(vars.dir_path+'/res/duckWithVRHeadset.png')
        return image

    @pyqtSlot()
    def executeThread(self):
        # In order for the icon to be displayed, you must provide an icon
        self.icon = pystray.Icon(
            name='WADDLE',
            icon=self.create_image(),title='WADDLE')
        self.icon.menu=pystray.Menu(
            pystray.MenuItem("Process Manager", lambda: self.signal_to_emit.emit('ProcessManager')),
            pystray.MenuItem("Settings", lambda: self.signal_to_emit.emit('SettingsMenu')),
            pystray.MenuItem("Quit", self.quitProgram)
        )

        try:
            # To finally show you icon, call run
            self.icon.run_detached()
        except Exception as e:
            self.icon.stop()

    def checkWatchlist(self):
        vars.overide=True
        setupWatchList()

    def stopTray(self):
        self.icon.icon=''
        self.icon.stop()

    def quitProgram(self):
        self.stopTray()
        QtTest.QTest.qWait(700)
        self.signal_to_emit.emit('quit')

class AutoVR(QObject):
    def __init__(self, signal_to_emit):
        super().__init__()
        self.signal_to_emit = signal_to_emit

    def checkForRunningProgram(self, program_name):
        # Check if the program is running
        try:
            pm = Pymem(program_name)
            if (not vars.exeRunning):
                vars.currentTrackedProgram = program_name
                vars.exeRunning = True
                changeResolution(vars.optimizedWidth,vars.optimizedHeight)
                self.signal_to_emit.emit('centerWindow')
                changePowerPlan('High')
                #sendWin10Notification('Auto VR Setup', 'Resolution Optimized!')
        except:
            if (vars.exeRunning and vars.currentTrackedProgram == program_name or vars.overide):
                changeResolution(vars.defaultWidth,vars.defaultHeight)
                self.signal_to_emit.emit('centerWindow')
                changePowerPlan('Default', id=vars.defaultPowerPlan)
                vars.currentTrackedProgram = ''
                vars.exeRunning = False
                vars.overide=False
    
    def finishCheck(self):
        if (len(vars.programWatchlist)==0):
            self.checkForRunningProgram(program_name='')
        for x in vars.programWatchlist:
            self.checkForRunningProgram(program_name=x)

    @pyqtSlot()
    def executeThread(self):
        setupWatchList()
        configMem(all=True)

        while vars.running:
            print('RUNNING...')
            
            self.finishCheck()

            QtTest.QTest.qWait(5000)

            vars.stopLoadingScreen=True

app = QApplication(sys.argv)
w = Ui()
app.exec()