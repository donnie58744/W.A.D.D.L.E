import os, json, shutil
dir_path = os.getcwd()

def setupConfigFiles(path):
    if (not os.path.exists(dir_path+path)):
        os.mkdir(dir_path+path)
    if (not os.path.exists(dir_path+path+'/config.json')):
        shutil.copy(dir_path+'/setup/config.json', dir_path+path)
    if (not os.path.exists(dir_path+path+'/watchlist.txt')):
        shutil.copy(dir_path+'/setup/watchlist.txt', dir_path+path)

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

def getWatchList(file):
    with open(dir_path + file) as f:
        data = f.read()

    return data.split('\n')