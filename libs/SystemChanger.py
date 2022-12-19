import pywintypes,win32api,win32con,re,subprocess,os,ctypes,psutil,win32api,win32process,win32con

def getCurrentPowerPlan():
    result = subprocess.run(['powercfg', '/GetActiveScheme'], stdout=subprocess.PIPE)
    string = result.stdout.decode('utf-8')

    guid_regex = re.compile(r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}')

    guid = guid_regex.search(string).group()

    return guid

def changePowerPlan(plan, id=None):
    try:
        match plan:
            case 'High':
                os.system("powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c")
            case 'Default':
                os.system(f"powercfg /setactive {id}")
        print(f'Power Plan Changed! {plan}')
    except:
        print('Couldnt Change Power Plan!')

def getCurrentResolution():
    # Get the screen width and height using the `GetSystemMetrics` function
    screen_width = ctypes.windll.user32.GetSystemMetrics(0)
    screen_height = ctypes.windll.user32.GetSystemMetrics(1)

    # Print the screen resolution
    return screen_width, screen_height

def changeResolution(width,height):
    devmode = pywintypes.DEVMODEType()
    devmode.PelsWidth = width
    devmode.PelsHeight = height

    devmode.Fields = win32con.DM_PELSWIDTH | win32con.DM_PELSHEIGHT

    win32api.ChangeDisplaySettings(devmode, 0)

def getRunningProcesses():
    '''
    Get list of running process sorted by Memory Usage
    '''
    nameList=[]
    listOfProcObjectsTemp = []
    listOfProcObjects = []
    # Iterate over the list
    for proc in psutil.process_iter():
        try:
            # Fetch process details as dict
            pinfo = proc.as_dict(attrs=['pid', 'name', 'username'])
            pinfo['vms'] = proc.memory_info().vms / (1024 * 1024)
            # Append dict to list
            listOfProcObjectsTemp.append(pinfo)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    # Sort list of dict by key vms i.e. memory usage
    listOfProcObjectsTemp = sorted(listOfProcObjectsTemp, key=lambda procObj: procObj['vms'], reverse=True)

    for x in listOfProcObjectsTemp:
        if (x["name"] not in nameList):
            nameList.append(x["name"])
            listOfProcObjects.append([x["name"],x["pid"]])
    return listOfProcObjects

def changePriority(pid, priority):
    handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, True, pid)
    match priority:
        case 'normal':
            priority=win32process.NORMAL_PRIORITY_CLASS
        case 'high':
            priority=win32process.HIGH_PRIORITY_CLASS
    win32process.SetPriorityClass(handle, priority)

def loopThroughChangePriority(list, priority):
    for x in getRunningProcesses():
        name=x[0]
        if (name in list):
            pid=x[1]
            changePriority(pid=pid, priority=priority)

def openPowerPlans():
    os.system("powercfg.cpl")