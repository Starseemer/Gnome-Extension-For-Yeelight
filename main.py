from logging import error
import time
import yeelight
import sys
import os
from yeelight import Bulb
from yeelight import discover_bulbs
import json
# 'tavan': '192.168.1.30', 'masa': '192.168.1.49'

CONF = {}
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# def checkKeyValues():
#     for bulb in discover_bulbs():
#         found = False

#         for key in CONF.keys():
#             if(CONF[key] == bulb["ip"]):
#                 found = True
#         if(not(found)):


def checkIfConfigExists():
    return os.path.isfile(BASE_DIR+"/config.json")


def writeToConfig():
    conf = open(BASE_DIR+"/config.json", "w")
    json.dump(CONF, conf)
    conf.close()


def getConfig():
    with open(BASE_DIR+'/config.json') as conff:
        conf = json.load(conff)

    return conf


def checkIfExit(str):
    return(str.strip() == "exit()")


def rgbStringToTupple(str):
    values = str.split(",")
    return (int(values[0].strip()), int(values[1].strip()), int(values[2].strip()))


def checkIfSceneNameExists(scenes, name):
    for scene in scenes:
        if(scene["name"] == name):
            return True
    return False


def onboarding():
    '''
    This function is used to setup Yeelight Controller CLI.
    '''
    if(not(checkIfConfigExists())):
        bulbs = discover_bulbs()
        print("Welcome new user")
        print("""Let's setup your light...

        There are 3 steps you should do to finish your setup.

            1) Make sure that all of your bulb can found in the local network
            2) For you to setup names of your bulbs, we will blink each one 5 times and ask you to name it
            3) For ease of use we will create different scenes such as work, normal, chill etc. You can name and set the colors of each bulb.

        Bear in mind that names of the scenes and bulbs are going to be used for both gnome extention and cli...
        we can start when ever you are ready.
        """)
        input("Press enter to start\n")
        index = 0
        while(index < len(bulbs)):
            blinkBulb(bulbs[index]["ip"])
            inp = input(
                "To name the bulb simply write it and enter. To reblink the bulb enter again()\n")
            if(inp.strip() != "again()"):
                CONF["Bulbs"].append(
                    {"name": inp.strip(), "ip": bulbs[index]["ip"]})
                print("Bulb has been added...")
                index += 1
            elif(inp.strip() == "again()"):
                print("OK, let's try this one again!")
        print("It seems al of the bulbs are named")

        print("""Now let's create those scenes. First you are going to be asked to give a name to the scene and then we will ask you to input rgb and brightness levels to each bulb

        To finish type exit() to name input

        """)
        inp = input("Press enter to start or exit() to finish\n")

        if(inp.strip() == "exit()"):
            writeToConfig()
            return
        scenes = []
        while(True):
            scene = {}
            print("------------------------NEW SCENE------------------------")
            name = input("Name of the scene: ").strip()
            if(checkIfExit(name)):
                writeToConfig()
                break
            if(checkIfSceneNameExists(scenes, name)):
                print(f"{name} is already exists in the list please choose another")
                continue
            scene["name"] = name

            bulbSettings = {}
            for bulb in CONF["Bulbs"]:

                currentBulbName = bulb['name']
                rgbValuesStr = input(
                    f"Write Red(0-255), Green(0-255), Blue(0-255) color values seperated with commas for {currentBulbName}: ")
                r, g, b = rgbStringToTupple(rgbValuesStr)
                brightness = int(
                    input(f"Write brightness(1-100) value for {currentBulbName}: ").strip())
                powerMode = int(input(
                    f"Write power mode(1 Normal - 2 RGB not that mormal is for white color on the other hand RGB is for real rgb gamut) value for {currentBulbName}: ").strip())
                bulbSettings[currentBulbName] = {
                    "r": r, "g": g, "b": b, "brightness": brightness, "power_mode": powerMode}

            scene["bulbSettings"] = bulbSettings
            scenes.append(scene)
        CONF["Scenes"] = scenes
        writeToConfig()
        print("You are all setup. Bye bye...")


def blinkBulb(ip, blinkCount=5):
    print("Starting blinking...")
    bulb = Bulb(ip)
    for i in range(blinkCount):
        bulb.set_brightness(10)
        time.sleep(1.2)
        bulb.set_brightness(90)
        time.sleep(1.2)


def getCurrentState(ip):
    bulb = Bulb(ip)
    return bulb.get_properties()["power"]


def getBulbDict():
    bulbs = {}
    for bulb in CONF["Bulbs"]:
        bulbs[bulb["name"]] = bulb["ip"]
    return bulbs


def setLight(bulbName, r, g, b, brightness, powerMode):
    try:
        for bulb in CONF["Bulbs"]:
            if(bulb["name"] == bulbName):
                bulb = Bulb(bulb["ip"], auto_on=True)

                bulb.set_rgb(r, g, b)
                bulb.set_brightness(brightness)
                if(powerMode == 1):
                    bulb.set_power_mode(yeelight.PowerMode.NORMAL)
                else:
                    bulb.set_power_mode(yeelight.PowerMode.RGB)
                break

    except Exception as error:
        print(error)


def closeLight(ip):
    try:
        b = Bulb(ip)
        b.turn_off()
    except Exception as error:
        print(error)


def closeAllLights():
    bulbs = getBulbDict()
    for bulbName in bulbs.keys():
        closeLight(bulbs[bulbName])


def toggleLight(ip):
    t = Bulb(ip)
    t.toggle()


def controller():
    '''
    Usage:
        To toggle a bulb use "python path/to/file/main.py -c --BulbName"
        To get the state of the bulb "python path/to/file/main.py -state --BulbName"
        To close all the bulbs "python path/to/file/main.py -close"
        To run a scene "python path/to/file/main.py --SceneName"


    -onboarding function helps users to configure their Bulbs and Scenes.
    '''
    onboarding()
    CONF = getConfig()
    if(len(sys.argv) == 1):
        print("Try running with options")
    else:
        inp = sys.argv[1]

        if(len(sys.argv) > 2):
            sinp = sys.argv[2]
            bulbs = getBulbDict()
            if(inp == "-c"):
                toggleLight(bulbs[sinp[2:]])
            elif(inp == "-state"):
                print(getCurrentState(bulbs[sinp[2:]]))
        elif(inp == "-close"):
            closeAllLights()
        else:
            for scene in CONF["Scenes"]:
                if(scene["name"] == inp[2:]):
                    for bulbName in getBulbDict().keys():
                        setLight(bulbName, scene["bulbSettings"][bulbName]
                                 ["r"], scene["bulbSettings"][bulbName]
                                 ["g"], scene["bulbSettings"][bulbName]
                                 ["b"], scene["bulbSettings"][bulbName]["brightness"],
                                 scene["bulbSettings"][bulbName]["power_mode"])


if __name__ == "__main__":
    controller()
