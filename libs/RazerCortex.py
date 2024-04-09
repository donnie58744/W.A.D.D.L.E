import keyboard, os

def CheckCortex(cortexExePath):
    if (cortexExePath and os.access(cortexExePath, os.X_OK) and 'Razer Cortex' in cortexExePath):
        return True
    else:
        return False

def CortexBoost(cortexExePath):
    if (CheckCortex(cortexExePath=cortexExePath)):
        keyboard.press_and_release('ctrl+alt+b')
        return True

def CortexRestore(cortexExePath):
    if (CheckCortex(cortexExePath=cortexExePath)):
        keyboard.press_and_release('ctrl+alt+r')
        return True