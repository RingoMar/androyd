# 1.1
import json
import os
import sys
import requests
from time import sleep as sleep
from colorama import Fore, Style, init
init()

# init Color Scheme
clear = lambda: os.system('clear')
print(Fore.GREEN)
clear() #for dev remove that shit before distrabuting 

oybotpy = "https://raw.githubusercontent.com/RingoMar/androyd/master/oybot.py"
verson = "https://raw.githubusercontent.com/RingoMar/androyd/master/version.json"
reqf = "https://raw.githubusercontent.com/RingoMar/androyd/master/requirements.text"
updaterf = "https://raw.githubusercontent.com/RingoMar/androyd/master/updater.py"
intro = """
:::::::::::::::>>>>>>>>>>>>>>>>>>::::::::::::::::::::
.....................................................
:'#######::'##:::'##:'########:::'#######::'########:
'##.... ##:. ##:'##:: ##.... ##:'##.... ##:... ##..::
 ##:::: ##::. ####::: ##:::: ##: ##:::: ##:::: ##::::
 ##:::: ##:::. ##:::: ########:: ##:::: ##:::: ##::::
 ##:::: ##:::: ##:::: ##.... ##: ##:::: ##:::: ##::::
 ##:::: ##:::: ##:::: ##:::: ##: ##:::: ##:::: ##::::
. #######::::: ##:::: ########::. #######::::: ##::::
:.......::::::..:::::........::::.......::::::..:::::
...<<<<<<<<<<...........................by @_ringomar
:::::::::::........:::::::...........::::::::::::::::
"""


class update ():
    def __init__(self):
        self.IS_WINDOWS = os.name == "nt"
        self.IS_MAC = sys.platform == "darwin"
        self.PYTHON_OK = sys.version_info >= (3, 5)

    def loadFile(self, name):
        with open(name, "r") as json_file:
            data = json.load(json_file)
        return data

    def saveFile(self, infile, data):
        with open(infile, 'w') as outfile:
            json.dump(data, outfile, indent=4)
            outfile.close()
        return

    def saveFileF(self, infile, data):
        dumpFile = open(infile, "w")
        dumpFile.write(data)
        dumpFile.close()
        return

    def create_fast_start_scripts(self):
        interpreter = sys.executable
        if not interpreter:
            return

        call = "\"{}\" oybot.py".format(interpreter)
        calll = "\"{}\" updater.py".format(interpreter)
        start_oybot = "{} --start".format(call)
        start_update = "{}".format(calll)
        modified = False

        if self.IS_WINDOWS:
            ccd = "pushd %~dp0\n"
            pause = "\npause"
            ext = ".bat"
        else:
            ccd = 'cd "$(dirname "$0")"\n'
            pause = "\nread -rsp $'Press enter to continue...\\n'"
            if not IS_MAC:
                ext = ".sh"
            else:
                ext = ".command"

        start_oybot             = ccd + start_oybot             + pause
        start_update             = ccd + start_update             + pause

        files = {
            "start_oybot"             + ext : start_oybot,
            "start_update"             + ext : start_update
        }

        if not self.IS_WINDOWS:
            files["start_launcher" + ext] = ccd + call

        for filename, content in files.items():
            if not os.path.isfile(filename):
                print("Creating {}... (fast start scripts)".format(filename))
                modified = True
                with open(filename, "w") as f:
                    f.write(content)

        if not self.IS_WINDOWS and modified: # Let's make them executable on Unix
            for script in files:
                st = os.stat(script)
                os.chmod(script, st.st_mode | stat.S_IEXEC)


    def versionCheck(self):
        versionReturn = False
        req = requests.get(verson, timeout=10).json()
        verFile = os.path.isfile("version.json")
        if verFile:
            if req["version"] > self.loadFile("version.json")["version"]:
                print(f"//> Oybot {req['version']} is ready for install...")
                saveFile("version.json", req)
                versionReturn = True
            else:
                versionReturn = False
        else:
            print('//> 404 "version.json" not found\nDownloading update anyway.')
            saveFile("version.json", req)
            versionReturn = True
        return versionReturn

    def check_files(self):

        files = {
            "config.json" : {"talk": ["Zaq smells raccPog"], "interval": 1800, "blacklisthello": ["tahhp", "richardharrow_", "oythebrave", "dwingert", "msotaku", "nightbot", "jediknight223", "classickerobel", "ringomar"]},
            "fragmentnames.json" : {},
            "creds.json" : {"cid": "", "OAuth": ""},
        }

        for filename, value in files.items():
            if not os.path.isfile("{}".format(filename)):
                print("//> Creating empty {}".format(filename))
                self.saveFile("{}".format(filename), value)

    def clearFiles(self):

        files = {
            "config.json" : {"talk": ["Zaq smells raccPog"], "interval": 1800, "blacklisthello": ["tahhp", "richardharrow_", "oythebrave", "dwingert", "msotaku", "nightbot", "jediknight223", "classickerobel", "ringomar"]},
            "fragmentnames.json" : {},
            "creds.json" : {"cid": "", "OAuth": ""},
        }

        for filename, value in files.items():
            print("//> Cleaning File {}".format(filename))
            self.saveFile("{}".format(filename), value)

    def updateLite(self):
        req = requests.get(oybotpy, timeout=10)
        verFile = os.path.isfile("androyd.py") 
        mainFile = os.path.isfile("oybot.py") 
        if verFile:
            print("//> Removing old file")
            os.remove("androyd.py") 
        if mainFile:
            print("//> Starting update check")
            if self.versionCheck():
                self.saveFileF("oybot.py", req.text)
                print("//> Starting to Updating 'oybot.py'")
            else:
                print("//> Oybot is already up to date.")
        else:
            print("//> Creating new 'Oybot.py' and writng data to file.")
            self.saveFileF("oybot.py", req.text)

    def update(self):
        requir = os.path.isfile("requirements.text") 
        reqc = requests.get(reqf, timeout=10)
        if requir:
            os.system('pip install -r requirements.text')
        else:
            print("//> No requirements file; Downloading from the cloud")
            self.saveFileF("requirements.text", reqc.text)
            os.system('pip install -r requirements.text')

        try:
            self.create_fast_start_scripts()
        except Exception as e:
            print("Failed making fast start scripts: {}\n".format(e))

        print("//> Checking local config files.")
        self.check_files()

        req = requests.get(oybotpy, timeout=10)
        verFile = os.path.isfile("androyd.py") 
        mainFile = os.path.isfile("oybot.py") 

        if verFile:
            print("//> Removing old file")
            os.remove("androyd.py") 
        if mainFile:
            print("//> Starting update check")
            if self.versionCheck():
                self.saveFileF("oybot.py", req.text)
                print("//> Starting to Updating 'oybot.py'")
            else:
                print("//> Oybot is already up to date.")
        else:
            print("//> Creating new 'Oybot.py' and writng data to file.")
            self.saveFileF("oybot.py", req.text)
        
    def cleanCache(self):
        print("//> Cleaning Cache files")
        os.system('rmdir __pycache__ /s /q')
        

    def Userconfirm(self):
        choice = None
        yes = ("yes", "y")
        no = ("no", "n")
        while choice not in yes and choice not in no:
            choice = input("Yes/No > ").lower().strip()
        return choice in yes

    def run(self):
        should_run = False
        clear()

        up_ver = requests.get(updaterf, timeout=10).text
        cl_ver = up_ver.split("\n")
        cloud_ver = float(cl_ver[0].replace("#", "").replace(" ", ""))

        localUpdater = open("updater.py", "r")
        first_line = localUpdater.readlines()[0]
        local_ver = float(first_line.replace("#", "").replace(" ", ""))


        if cloud_ver > local_ver:
            self.saveFileF("updater.py", up_ver)
            print("//> A new update to updater has been installed, please restart.")
        else:
            print("//> Updater is up to date.")
            should_run = True

        localUpdater.close()
        
        while should_run:
            print(intro + "\n")
            print("[0]Update Oybot\n[1]Full Update\n[2]Clean pycache\n[3]Reset Configs\n[4]Quit")
            choice = choice = input("<Updater>: ").lower().strip()
            if choice == "0":
                clear()
                self.updateLite()
                sleep(2)
            elif choice == "1":
                self.update()
                sleep(5)
            elif choice == "2":
                self.cleanCache()
                sleep(5)
            elif choice == "3":
                self.clearFiles()
                sleep(5)
            elif choice == "4":
                break
            clear()

if __name__ == '__main__':
    try:
        update().run()
    finally:
        input('> Press ENTER to exit <')
