import os, shutil

dir_path = os.getcwd()
openVrDll='openvr_api.dll'
openVrPath = dir_path+'/libs/files/OpenVR/'+openVrDll
openVrConfig='openvr_mod.cfg'
openVrConfigPath=dir_path+'/libs/files/OpenVR/'+openVrConfig

class vars():
    found=False
    unistall=False

def installMod(path, ogDll):
    try:
        print(dir_path)
        if (os.path.isfile(path+'/'+ogDll) and os.path.isfile(openVrPath)):
            os.rename(path+'/'+ogDll, path+'/'+ogDll+'_bak')
            print('Moving New OpenVR Dll...')
            shutil.copy(openVrPath, path+'/'+ogDll)
            shutil.copy(openVrConfigPath, path+'/'+openVrConfig)
            print('Mod Installed!')
        else:
            raise SystemError('ERROR Path is not file!')
    except Exception as e:
        if ("[WinError 183]" in str(e)):
            print('Mod Installed Already!')
            raise SystemError("Mod Installed Already! " + str(path))
        elif ("[Errno 2]" in str(e)):
            print('Cant Find Mod Files!')
            raise SystemError("Cant Find Mod Files!")
        else:
            print(e)
            raise e

def uninstallMod(path, ogDll):
    try:
        if (os.path.isfile(path+'/'+ogDll)):
            if ('_bak' in ogDll):
                print('Deleting OpenVR Mod...')
                os.remove(path+'/'+openVrDll)
                os.remove(path+'/'+openVrConfig)
                os.rename(path+'/'+ogDll, path+'/'+openVrDll)
                print('Mod Uninstalled!')
                vars.unistall=True
            else:
                raise SystemError('Mod Not Installed!')
        else:
            raise SystemError('ERROR Path is not file!')
    except Exception as e:
        if ("[WinError 183]" in str(e)):
            print(f'Mod Uninstall ERROR: {e}')
            raise SystemError(f'Mod Uninstall ERROR: {e}')
        else:
            print (e)
            raise e

def findAndUninstallOpenVR(path):
    try:
        for x in os.listdir(path=path):
            if (os.path.isdir(path+'/'+x)):
                findAndUninstallOpenVR(path=path+'/'+x)
            if (x=='openvr_api.dll_bak'):
                uninstallMod(path=path, ogDll=x)
                break
    except Exception as e:
        pass
    return vars.unistall

def findAndInstallOpenVR(path):
    for x in os.listdir(path=path):
        if (os.path.isdir(path+'/'+x)):
            findAndInstallOpenVR(path=path+'/'+x)
        if (x=='openvr_api.dll'):
            installMod(path=path, ogDll=x)    
            vars.found=True
            break
           
    return vars.found