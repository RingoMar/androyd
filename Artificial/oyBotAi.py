#1.4
import os
import operator
import enchant
import spacy
import json
import random
import re
import socket
import sys
import time
import traceback
from multiprocessing import Process
from datetime import datetime as dt
from multiprocessing import Process
from time import sleep as sleep

import requests
from colorama import Back, Fore, Style, init
from requests import Session
from ml import rinProcess
from nltk.sentiment.vader import SentimentIntensityAnalyzer

init()
sock = socket.socket()
analyzer = SentimentIntensityAnalyzer()
lastping = ""

lastping = dt.now().strftime('%Y%m%d%H%M%S')
lastmessage = dt.now().strftime('%Y%m%d%H%M%S')
lastwave = ""
emotecool = ""

def loadFile(name):
    with open(name, "rb") as json_file:
        data = json.load(json_file)
    return data

def saveFile(infile, data):
    with open(infile, 'w') as outfile:
        json.dump(data, outfile, indent=4)
        outfile.close()
    return

cid = loadFile("creds2.json")["cid"]
OAuth = loadFile("creds2.json")["OAuth"]
botname = "Oythebrave"
chan = "#zaquelle"

replay = loadFile("Artificial/src/reply.json")

startText = """
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

class oyBotMain():
    def __init__(self):
        self.oyBotSockConnect = True
        self.pingged = False
        self.before = ""
        self.intentsList = ""
        self.lastmessage = ""

    def randomPick(self, aList):
        try:
            fullList = random.sample(aList, 3)
            return fullList[1]
        except ValueError:
            liteList = random.sample(aList, len(aList))
            return liteList[0]

    def connectsock(self):
        print(Fore.GREEN + startText + Style.RESET_ALL)
        print(Fore.GREEN + "[INFO] " + Style.RESET_ALL + "Trying to connect to... irc.twitch.tv:6667")
        verFile = loadFile("version.json")
        req = requests.get("https://raw.githubusercontent.com/RingoMar/androyd/master/version.json", timeout=10).json()
        if req["version"] > verFile["version"]:
            print(Fore.RED + Back.WHITE + "[INFO] " + Style.RESET_ALL + "OyBot is outdated Cloud {}".format(req["version"]))
        else:
            print(Fore.GREEN + Back.WHITE + "[INFO] " + Style.RESET_ALL + "OyBot is up to date; Cloud: {}, Local: {}".format(req["version"], verFile["version"]))

        try:
            sock.connect(("irc.twitch.tv", 6667))
            sock.send(f"PASS {OAuth}\r\n".encode("utf-8"))
            sock.send(f"NICK {botname}\r\n".encode("utf-8"))
            sock.send(bytes("CAP REQ :twitch.tv/tags\r\n", "UTF-8"))
            sock.send(bytes("CAP REQ :twitch.tv/membership\r\n", "UTF-8"))
            sock.send(bytes("CAP REQ :twitch.tv/commands\r\n", "UTF-8"))
            sock.send("JOIN {} \r\n".format(chan).encode("utf-8"))
            print(Fore.GREEN + "[INFO] " + Style.RESET_ALL + f"Joined {chan}")
        except Exception as e:
            print(Fore.RED + "[INFO] " + Style.RESET_ALL + e)
        self.oyBotSockConnect = False
        return

    ############################################
    # MACHINE LEARNING MODULE                  #
    ############################################
    def oyBotML(self):
        buffer = ""
        buffer += sock.recv(2048).decode('utf-8')
        temp = buffer.split("\r\n")
        buffer = temp.pop()
        try:
            for line in temp:
                _line = str(line.encode("utf-8").decode("utf-8"))
                if line == "PING :tmi.twitch.tv":
                    sock.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))

                if "PRIVMSG" in _line:
                    DPN = ""
                    stream = re.search(r"#([a-zA-Z0-9-_\w]+) :", _line)
                    findprv = ("PRIVMSG #{} :".format(stream.group(1)))
                    pri = _line.split(findprv)
                    mlMsg = pri[1]
                    cmds = re.split(" ", pri[1])
                    user = re.search(r"display-name=([a-zA-Z0-9-_\w]+)", _line)
                    try:
                        DPN += user.group(1)
                    except AttributeError:
                        user = re.search(
                            r":([a-zA-Z0-9-_\w]+)!([a-zA-Z0-9-_\w]+)@([a-zA-Z0-9-_\w]+)", _line)
                        try:
                            DPN += user.group(1)
                        except AttributeError:
                            DPN += "Chatter"

                    if "oybot" in mlMsg.lower():
                    # if "oybot" in mlMsg.lower() and DPN.lower() != botname.lower():
                        p = rinProcess().think(mlMsg.replace("oybot", ""))
                        if p == "":
                            pass
                        else:
                            print(p)
                            with open('Artificial/src/data.json', "rb") as json_data:
                                intents = json.load(json_data)

                            for x in range(0, len(intents["intents"])):
                                if p == [] or str(p[0][0]) == "untrained":
                                    score = analyzer.polarity_scores(mlMsg.replace("oybot", ""))
                                    if score['compound'] > 0.05:
                                        result = replay['pos']
                                    elif score['compound'] < -0.05:
                                        result = replay['neg']
                                    else:
                                        result = replay['neu']

                                    self.intentsList = result
                                elif str(intents["intents"][x]["tag"]) == str(p[0][0]):
                                    self.intentsList = intents["intents"][x]["responses"]
                                    
                            sock.send(("PRIVMSG {} :{}\r\n").format(chan, self.randomPick(self.intentsList)).encode("utf-8"))


        except Exception as e:
            print(Fore.RED + "<<<<<<<<<<<< Bot Chatting Error >>>>>>>>>>>>>"+ "\n" + e + "\n<<<" + _line)
            print(traceback.format_exc())
            print(Style.RESET_ALL)
        return

    def oyBotStart(self):
        try:
            if self.oyBotSockConnect:
                self.connectsock()
        except Exception as e:
            print(Fore.RED + "[INFO] " + Style.RESET_ALL + e)

        while True:
            try:
                self.oyBotML()
            except KeyboardInterrupt:
                sys.exit(0) 
            except Exception as e:
                pass
        return

if __name__ == '__main__':
    try:
        oyBotMain().oyBotStart()
    except KeyboardInterrupt:
        sys.exit(0) 
