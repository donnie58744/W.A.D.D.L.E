import os,pystray,sys
from PIL import Image
from PyQt6 import uic, QtTest
from PyQt6.QtWidgets import QApplication, QMainWindow, QGridLayout, QVBoxLayout
from PyQt6.QtCore import Qt, QThread, pyqtSignal, pyqtSlot, QObject
from libs.Config import *
from libs.SystemChanger import *
from libs.UiFunctions import *
from libs.RazerCortex import *
from libs.OpenVRMod import *

dir_path = os.path.dirname(os.path.realpath(__file__))

class vars():
    # Settings Memory
    defaultWidth = 0
    defaultHeight = 0

    # AutoVR Memory
    currentTrackedProgram = ''

    # Process Window Memory
    programWatchlist = []

    # Other Memory
    runningThreads=True
    stopLoadingScreen=False

class Ui(QMainWindow):
    programsToAdd=[]
    programsToRemove=[]
    windowVis=None

    def __init__(self):
        super().__init__()
        app.setQuitOnLastWindowClosed(False)
        self.setFixedSize(self.size())
        loadingScreen(ui=self, first=True)
        # Center
        CenterWindow(self,app)
        # Setup Config Files
        setupConfigFiles(path='/files/')
        # Load Everything First
        setupWatchList()
        configData=getConfig(file='/files/config.json')
        configMem(all=True)
        # Restore Cortex
        CortexRestore(configData["cortexPath"])
        # Setup Threads
        self.trayIconThread = TrayIcon()
        self.watchlistThread=AutoVR()
        self.priorityWatchlistThread=PriortyChanger()

        self.trayIconFoo = QThread(self)
        # Connect UI Functions to Tray
        self.trayIconThread.processManagerSig.connect(self.openProcessManager)
        self.trayIconThread.settingsMenuSig.connect(self.openSettingsMenu)
        self.trayIconThread.quitSig.connect(self.shutdown)
        self.trayIconThread.moveToThread(self.trayIconFoo)

        self.watchlistFoo=QThread(self)
        # Connect UI Functions to AutoVR
        self.watchlistThread.resFixPhase1Sig.connect(self.ResFixPhase1)
        self.watchlistThread.resFixPhase2Sig.connect(self.ResFixPhase2)
        self.watchlistThread.stopLoadingScreenSig.connect(self.stopLoadingScreen)
        self.watchlistThread.moveToThread(self.watchlistFoo)

        self.priorityWatchlistFoo=QThread(self)
        self.priorityWatchlistThread.moveToThread(self.priorityWatchlistFoo)

        self.trayIconFoo.started.connect(self.trayIconThread.executeThread)
        self.watchlistFoo.started.connect(self.watchlistThread.executeThread)
        self.priorityWatchlistFoo.started.connect(self.priorityWatchlistThread.executeThread)
        
        # Start Threads
        self.trayIconFoo.start()
        self.priorityWatchlistFoo.start()
        self.watchlistFoo.start()

    @pyqtSlot()
    def shutdown(self):
        vars.runningThreads=False
        loadingScreen(ui=self, loadingScreenStop=True)
        self.watchlistThread.default(quit=True)
        # Stop Threads
        self.trayIconFoo.terminate()
        self.priorityWatchlistFoo.terminate()
        self.watchlistFoo.terminate()
        app.quit()
        
    @pyqtSlot()
    def stopLoadingScreen(self):
        vars.stopLoadingScreen=True
        loadingScreen(ui=self, loadingScreenStop=True)

    @pyqtSlot()
    def openProcessManager(self):
        if (vars.stopLoadingScreen):
            self.refreshProcessManager()
            self.show()
            self.activateWindow()
            CenterWindow(self, app)
            
    @pyqtSlot()
    def openSettingsMenu(self):
        if (vars.stopLoadingScreen):
            self.refreshSettingsMenu(menu='base')
            self.show()
            self.activateWindow()
            CenterWindow(self, app)

    @pyqtSlot()
    def ResFixPhase1(self):
        self.windowVis=self.isVisible()
        self.show()
        QtTest.QTest.qWait(1000)
        CenterWindow(self, app)

    @pyqtSlot()
    def ResFixPhase2(self):
        CenterWindow(self, app)
        if (not self.windowVis):
            self.windowVis=None
            self.hide()
        QtTest.QTest.qWait(1000)
        CenterWindow(self, app)

    def toggledBtn(self, button, request):
        match request:
            case 'add':
                if (button.isChecked()):
                    self.programsToAdd.append([button.text(), button.objectName()])
                else:
                    self.programsToAdd.remove([button.text(), button.objectName()])
            case 'remove':
                if (button.isChecked()):
                    self.programsToRemove.append(button.text())
                else:
                    self.programsToRemove.remove(button.text())

    def createProcessButtons(self):
        runningList=[i[0] for i in getRunningProcesses()]
        createScrollArea(frame=self.processesFrame, request='button', layout=QGridLayout(), list=runningList, width=self.processesFrame.width(), height=self.processesFrame.height(), verticalScrollBarPolicy=Qt.ScrollBarPolicy.ScrollBarAsNeeded, horizontalScrollBarPolicy=Qt.ScrollBarPolicy.ScrollBarAlwaysOff, function=self.toggledBtn, functionArgs='add', buttonWidth=150, buttonHeight=35, css='background-color:rgb(159, 189, 237); color:black; font-size:14px; text-align: left;')

    def createWatchlistButtons(self):
        createScrollArea(frame=self.watchlistFrame, request='button', layout=QVBoxLayout(), list=vars.programWatchlist, width=150, height=340, verticalScrollBarPolicy=Qt.ScrollBarPolicy.ScrollBarAsNeeded, horizontalScrollBarPolicy=Qt.ScrollBarPolicy.ScrollBarAlwaysOff, function=self.toggledBtn, functionArgs='remove', buttonWidth=110, buttonHeight=25, css='background-color:rgb(159, 189, 237); color:black; font-size:14px; text-align: left;')

    def refreshProcessManager(self):
        uic.loadUi(dir_path+'/ui/runningProcesses.ui', self)

        # Button Functions
        def addToWatchlist():
            try:
                if (self.programsToAdd):
                    for x in self.programsToAdd:
                        programName=x[0]
                        writeTxtConfig(file='/files/watchlist.txt', value=str(programName))
                    self.programsToAdd=[]
                    self.addBtn.setText('DONE!')
                    self.addBtn.setStyleSheet("background:green")
                    setupWatchList()
                    QtTest.QTest.qWait(2500)
                    self.refreshProcessManager()
            except Exception as e:
                self.addBtn.setText('ERROR!')
                self.addBtn.setStyleSheet("background:red")

        def removeFromWatchlist():
            try:
                if (self.programsToRemove):
                    newWatchlist=[]
                    default=False
                    with open(dir_path+'/files/watchlist.txt', 'r') as f:
                        watchlist=f.read()
                        for x in str(watchlist).split('\n'):
                            if (x!=''):
                                if (x not in self.programsToRemove):
                                    newWatchlist.append(x)
                                else:
                                    try:
                                        vars.programWatchlist.remove(x)
                                        if (x == vars.currentTrackedProgram):
                                            default=True
                                    except Exception as e:
                                        continue

                        self.programsToRemove=[]
                    f.close()

                    writeTxtConfig(file='/files/watchlist.txt', value=("\n".join(newWatchlist)), mode='w')
                    setupWatchList()
                    self.refreshProcessManager()
                    if (default):
                        self.watchlistThread.default()
            except Exception as e:
                self.removeBtn.setText('ERROR!')
                self.removeBtn.setStyleSheet("background:red")

        self.programsToAdd=[]
        self.programsToRemove=[]
        setupWatchList()
        self.createProcessButtons()
        self.createWatchlistButtons()
        self.addBtn.clicked.connect(addToWatchlist)
        self.removeBtn.clicked.connect(removeFromWatchlist)
        self.refreshBtn.clicked.connect(self.refreshProcessManager)

    # Settings Menu

    def applySettings(self, menu):
        match menu:
            case 'base':
                writeConfig(file='/files/config.json', key='cortexPath', value=self.cortexPathLabel.text())
            case 'display':
                writeConfig(file='/files/config.json', key='optimizedWidth', value=self.optimizedWidthTxtBox.text())
                writeConfig(file='/files/config.json', key='optimizedHeight', value=self.optimizedHeightTxtBox.text())
            case 'oculus':
                writeConfig(file='/files/config.json', key='oculusBoost', value=self.oculusPriorityCheckbox.isChecked())
                self.priorityWatchlistThread.check()
        checkmarkIcon(ui=self)

    def refreshSettingsMenu(self, menu):
        match menu:
            case 'base':
                # Reset Vars
                self.programsToAdd=[]
                self.programsToRemove=[]
                uic.loadUi(dir_path+'/ui/settingsMenu.ui', self)
                configData=getConfig(file='/files/config.json')
                # Create and Load UI elements
                createScrollArea(request='button', layout=QVBoxLayout(), frame=self.fsrFrame, width=505, height=130, list=getTxtConfig(file='/files/OpenVR.txt'), verticalScrollBarPolicy=Qt.ScrollBarPolicy.ScrollBarAsNeeded, horizontalScrollBarPolicy=Qt.ScrollBarPolicy.ScrollBarAlwaysOff,  function=self.toggledBtn, functionArgs='remove', buttonWidth=300, buttonHeight=35, css='background-color:rgb(159, 189, 237); color:black; font-size:14px; text-align: right; margin-right:20px')
                self.cortexPathLabel.setText(configData["cortexPath"])
                # Button Functions
                def cortexFileDialogBtnClick():
                    try:
                        path=FileDialog(ui=self, request='file', nameFilter="EXE File (*.exe)" ,defaultDir="C:\Program Files (x86)\Razer\Razer Cortex")[0]
                    except Exception:
                        path=configData["cortexPath"]
                        pass
                    self.cortexPathLabel.setText(path)
                def injectFsrBtnClick():
                    consoleMsg=''
                    try:
                        path=FileDialog(ui=self, request='folder', defaultDir="C:")[0]
                        # Inject FSR
                        if (findAndInstallOpenVR(path=path)):
                            writeTxtConfig(file='/files/OpenVR.txt', value=path)
                            consoleMsg=consoleMsg+'\n FSR Installed: ' + str(path)
                            self.refreshSettingsMenu(menu='base')
                            checkmarkIcon(ui=self)
                        else:
                            consoleMsg=consoleMsg+'\n FSR ERROR: ' + str(path)
                    except Exception as e:
                        consoleMsg=consoleMsg+'\n FSR ERROR: ' + str(e)
                        pass
                    console(self.consoleFrame, self.consoleLabel, consoleMsg)
                def removeFsrBtnClick():
                    try:
                        consoleMsg=''
                        newList=[]
                        unistalled=False
                        if (self.programsToRemove):
                            for x in getTxtConfig(file='/files/OpenVR.txt'):
                                if (x!=''):
                                    if (x not in self.programsToRemove):
                                        newList.append(x)
                                    else:
                                        try:
                                            if(not findAndUninstallOpenVR(path=x)):
                                                consoleMsg=consoleMsg+"\n FSR Cant Uninstall: "+str(x)
                                            else:
                                                unistalled=True
                                        except Exception as e:
                                            consoleMsg=consoleMsg+"\n FSR ERROR: "+str(x)
                                            
                            if (unistalled):
                                newList='\n'.join(newList)
                                # Remove FSR from config
                                if(writeTxtConfig(file='/files/OpenVR.txt', value=newList, mode='w')):
                                    consoleMsg=consoleMsg+"\n Uninstalled FSR: "+str(x)
                                    self.refreshSettingsMenu(menu='base')
                                else:
                                    consoleMsg=consoleMsg+"\n Config ERROR: "+str(x)
                            # Show whats going on in console
                            console(self.consoleFrame, self.consoleLabel, consoleMsg)
                            checkmarkIcon(ui=self)
                    except Exception as e:
                        consoleMsg=consoleMsg+"\n "+str(e)
                        # Show whats going on in console
                        console(self.consoleFrame, self.consoleLabel, consoleMsg)
                        pass
                # Setup Buttons
                self.injectFsrBtn.clicked.connect(injectFsrBtnClick)
                self.removeFsrBtn.clicked.connect(removeFsrBtnClick)
                self.applyBtn.clicked.connect(lambda: self.applySettings(menu='base'))
                self.cortexFileDialogBtn.clicked.connect(cortexFileDialogBtnClick)
                self.cortexClearBtn.clicked.connect(lambda: self.cortexPathLabel.setText(''))
            case 'display':
                configData=getConfig(file='/files/config.json')
                defaultResolutionData=getCurrentResolution()

                def resetBtnClicked():
                    defaultResolutionData=getCurrentResolution()
                    setupWatchList()
                    self.defaultWidthTxtBox.setText(str(defaultResolutionData[0]))
                    self.defaultHeightTxtBox.setText(str(defaultResolutionData[1]))
                    checkmarkIcon(ui=self)

                uic.loadUi(dir_path+'/ui/settings/displaySettings.ui', self)
                self.defaultWidthTxtBox.setText(str(defaultResolutionData[0]))
                self.defaultHeightTxtBox.setText(str(defaultResolutionData[1]))
                self.optimizedWidthTxtBox.setValue(int(configData['optimizedWidth']))
                self.optimizedHeightTxtBox.setValue(int(configData['optimizedHeight']))

                self.resetBtn.clicked.connect(resetBtnClicked)
                self.applyBtn.clicked.connect(lambda: self.applySettings(menu='display'))
                self.cancelBtn.clicked.connect(lambda: self.refreshSettingsMenu(menu='display'))
            case 'powerPlan':
                uic.loadUi(dir_path+'/ui/settings/powerPlanSettings.ui', self)
                configData=getConfig(file='/files/config.json')
                self.resetBtn.clicked.connect(lambda: (writeConfig(file='/files/config.json', key='defaultPowerPlan', value=getCurrentPowerPlan()),self.defaultPowerPlanTxtBox.setText(getConfig(file='/files/config.json')["defaultPowerPlan"]), checkmarkIcon(ui=self)))
                self.plansBtn.clicked.connect(openPowerPlans)
                self.defaultPowerPlanTxtBox.setText(configData["defaultPowerPlan"])
                self.defaultPowerPlanTxtBox.setStyleSheet('background-color: rgb(86, 86, 86);\ncolor: rgb(255, 255, 255);')
            case 'oculus':
                configData=getConfig(file='/files/config.json')
                uic.loadUi(dir_path+'/ui/settings/oculusSettings.ui', self)
                self.oculusPriorityCheckbox.setChecked(bool(configData["oculusBoost"]))
                self.applyBtn.clicked.connect(lambda: self.applySettings(menu='oculus'))
                self.cancelBtn.clicked.connect(lambda: self.refreshSettingsMenu(menu='oculus'))

        self.settingsBtn.clicked.connect(lambda: self.refreshSettingsMenu(menu='base'))
        self.displayBtn.clicked.connect(lambda: self.refreshSettingsMenu(menu='display'))
        self.powerPlanBtn.clicked.connect(lambda: self.refreshSettingsMenu(menu='powerPlan'))
        self.oculusBtn.clicked.connect(lambda: self.refreshSettingsMenu(menu='oculus'))

    #--------------#

# Public Functions
def setupWatchList():
    print("Chekcing Watch List...")
    vars.programWatchlist=[]
    #Convert Json Dict to Pythhon Array
    for i in getTxtConfig('/files/watchlist.txt'):
        if (i != ''):
            vars.programWatchlist.append(i)
    print('Watchlist Checked')

def configMem(request=None, all=None, overide=None):
    configData=getConfig(file='/files/config.json')
    if (all):
        if (not configData["defaultPowerPlan"]):
            writeConfig(file='/files/config.json', key='defaultPowerPlan', value=getCurrentPowerPlan())
    if(request=='defaultResoultion' or all):
        defaultResolutionData=getCurrentResolution()
        vars.defaultWidth = int(defaultResolutionData[0])
        vars.defaultHeight = int(defaultResolutionData[1])

class PriortyChanger(QObject):
    priortyWatchList=['OVRServer_x64.exe']
    def __init__(self):
        super().__init__()

    def check(self):
        oculusBoost=bool(getConfig(file='/files/config.json')["oculusBoost"])
        if (oculusBoost):
            loopThroughChangePriority(list=self.priortyWatchList, priority='high')
        else:
            loopThroughChangePriority(list=self.priortyWatchList, priority='normal')

    @pyqtSlot()
    def executeThread(self):
        while vars.runningThreads:
            self.check()
            QtTest.QTest.qWait(10000)

class TrayIcon(QObject):
    processManagerSig = pyqtSignal()
    settingsMenuSig = pyqtSignal()
    quitSig=pyqtSignal()

    def __init__(self):
        super().__init__()

    def create_image(self):
        # Generate an image and draw a pattern
        image = Image.open(dir_path+'/res/duckWithVRHeadset.png')
        return image

    @pyqtSlot()
    def executeThread(self):
        # In order for the icon to be displayed, you must provide an icon
        self.icon = pystray.Icon(
            name='WADDLE',
            icon=self.create_image(),title='WADDLE')
        self.icon.menu=pystray.Menu(
            pystray.MenuItem("Process Manager", lambda: self.processManagerSig.emit()),
            pystray.MenuItem("Settings", lambda: self.settingsMenuSig.emit()),
            pystray.MenuItem("Quit", self.quitProgram)
        )

        try:
            # To finally show you icon, call run
            self.icon.run_detached()
        except Exception as e:
            self.icon.stop()

    def stopTray(self):
        self.icon.icon=''
        self.icon.stop()

    def quitProgram(self):
        self.stopTray()
        QtTest.QTest.qWait(700)
        self.quitSig.emit()

class AutoVR(QObject):
    resFixPhase1Sig=pyqtSignal()
    resFixPhase2Sig=pyqtSignal()
    stopLoadingScreenSig=pyqtSignal()
    exeRunning=False

    def __init__(self):
        super().__init__()

    def getRunningProcessNames(self):
        # Check if the program is running
        try:
            runningProcesses=[]
            for p in psutil.process_iter():
                runningProcesses.append(p.name())
            return runningProcesses
        except Exception as e:
            print(e)
            pass

    @pyqtSlot()
    def optimize(self, programName):
        configData=getConfig(file='/files/config.json')
        vars.currentTrackedProgram = programName
        self.exeRunning = True
        self.resFixPhase1Sig.emit()
        QtTest.QTest.qWait(1000)
        changeResolution(int(configData["optimizedWidth"]),int(configData["optimizedHeight"]))
        self.resFixPhase2Sig.emit()
        # Wait for Cortex BS if using cortex
        if (CortexBoost(cortexExePath=configData["cortexPath"])):
            QtTest.QTest.qWait(20000)
        changePowerPlan('High')
    
    @pyqtSlot()
    def default(self, quit=None):
        configData=getConfig(file='/files/config.json')
        if (not quit):
            self.resFixPhase1Sig.emit()
            QtTest.QTest.qWait(1000)
            changeResolution(vars.defaultWidth,vars.defaultHeight)
            self.resFixPhase2Sig.emit()
        vars.currentTrackedProgram = ''
        self.exeRunning = False
        # Wait for Cortex BS if using cortex
        if (CortexRestore(cortexExePath=configData["cortexPath"])):
            QtTest.QTest.qWait(20000)
        changePowerPlan('Default', id=configData["defaultPowerPlan"])

    def checkForRunningProgram(self, programWatchList):
        running=self.getRunningProcessNames()
        for x in programWatchList:
            if (x in running and not self.exeRunning):
                self.optimize(programName=x)
            elif (x not in running and vars.currentTrackedProgram == x):
                self.default()

    @pyqtSlot()
    def executeThread(self):
        while vars.runningThreads:
            print('RUNNING...')
            # Keep this function runnin
            self.checkForRunningProgram(programWatchList=vars.programWatchlist)
            if (not vars.stopLoadingScreen):
                self.stopLoadingScreenSig.emit()
                print('Done Loading')
            QtTest.QTest.qWait(5000)

app = QApplication(sys.argv)
w = Ui()
app.exec()