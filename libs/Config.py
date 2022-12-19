import os, json
dir_path = os.getcwd()

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