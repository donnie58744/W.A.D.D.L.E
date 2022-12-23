import os, json, shutil
dir_path = os.getcwd()

def setupConfigFiles(path):
    if (not os.path.exists(dir_path+path)):
        os.mkdir(dir_path+path)
    if (not os.path.exists(dir_path+path+'/config.json')):
        shutil.copy(dir_path+'/setup/config.json', dir_path+path)
    if (not os.path.exists(dir_path+path+'/watchlist.txt')):
        open(dir_path+path+'/watchlist.txt', "x")
    if (not os.path.exists(dir_path+path+'/OpenVR.txt')):
        open(dir_path+path+'/OpenVR.txt', "x")

def getConfig(file):
    with open(dir_path + file) as f:
        data = json.load(f)

    return data
        
def writeConfig(file, key, value):
    with open(dir_path + file) as f:
        data = json.load(f)
        if key in data:
            del data[key]
            cacheDict = dict(data)
            cacheDict.update({key:value})
            with open(dir_path + file, 'w') as f:
                json.dump(cacheDict, f, indent=4)

def writeTxtConfig(file, value, mode='a'):
    try:
        with open(dir_path + file, mode) as f:
            f.write('\n'+value)
        f.close()

        return True
    except Exception as e:
        return False

def getTxtConfig(file):
    with open(dir_path + file) as f:
        data = f.read()

    return list(data.split('\n'))

def getParentDir(dirPath, exe):
    
    d = os.path.dirname(os.path.realpath(rf"{dirPath}"))
    list = str(d).split('\\')
    parentDir=[]
    for x in list:
        if (x in exe):
            break
        parentDir.append(x)
    parentDir='\\'.join(parentDir)

    return parentDir