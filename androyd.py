#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
import os
import random
import re
import socket
import sys
import traceback
from datetime import datetime as dt
from threading import Thread
from time import sleep as sleep

import requests
from colorama import Back, Fore, Style, init
from requests import Session

init()

HOST = "irc.twitch.tv"
PORT = 6667
botname = "Oythebrave"
chan = "#zaquelle"
sock = socket.socket()
intstart = True
lastping = ""
subgifts = 0
mgft = False
giftcount = 0
seen = []

lastping = dt.now().strftime('%Y%m%d%H%M%S')
lastmessage = dt.now().strftime('%Y%m%d%H%M%S')
lastwave = ""


def loadFile(name):
    with open(name, "rb") as json_file:
        data = json.load(json_file)
    return data

cid = loadFile("creds.json")["cid"]
OAuth = loadFile("creds.json")["OAuth"]

def saveFile(infile, data):
    with open(infile, 'w') as outfile:
        json.dump(data, outfile, indent=4)
        outfile.close()
    return


class sitinchat(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.start()

    def randommessage(self):
        global lastmessage
        configFile = loadFile("config.json")
        tnow = str(dt.now().strftime('%Y%m%d%H%M%S'))
        format = '%Y%m%d%H%M%S'
        delta = dt.strptime(tnow, format) - dt.strptime(lastmessage, format)
        if int(delta.total_seconds()) > int(configFile["interval"]):
            return random.choice(configFile["talk"])
        else:
            return False

    def shouldSayHi(self):
        global lastwave
        configFile = loadFile("config.json")
        tnow = str(dt.now().strftime('%Y%m%d%H%M%S'))
        format = '%Y%m%d%H%M%S'
        if lastwave == "":
            return True

        delta = dt.strptime(tnow, format) - dt.strptime(lastwave, format)
        if int(delta.total_seconds()) > 5:
            return True
        else:
            return False

    def connectsock(self):
        global intstart
        print(Fore.GREEN)
        print("""
                _______ _____   __________ ________ _______ __  __________     
                ___    |___  | / /___  __ \___  __ \__  __ \_ \/ /___  __ \    
                __  /| |__   |/ / __  / / /__  /_/ /_  / / /__  / __  / / /    
                _  ___ |_  /|  /  _  /_/ / _  _, _/ / /_/ / _  /  _  /_/ /     
                /_/  |_|/_/ |_/   /_____/  /_/ |_|  \____/  /_/   /_____/ """ + Style.RESET_ALL)
        print(Fore.GREEN + "[INFO] " + Style.RESET_ALL +
              "Trying to connect to... irc.twitch.tv:6667")
        try:
            sock.connect((HOST, PORT))
            sock.send(f"PASS {OAuth}\r\n".encode("utf-8"))
            sock.send(f"NICK {botname}\r\n".encode("utf-8"))
            sock.send(bytes("CAP REQ :twitch.tv/tags\r\n", "UTF-8"))
            sock.send(bytes("CAP REQ :twitch.tv/membership\r\n", "UTF-8"))
            sock.send(bytes("CAP REQ :twitch.tv/commands\r\n", "UTF-8"))
            sock.send("JOIN {} \r\n".format(chan).encode("utf-8"))
            print(Fore.GREEN + "[INFO] " + Style.RESET_ALL + f"Joined {chan}")
        except Exception as e:
            print(Fore.RED + "[INFO] " + Style.RESET_ALL + e)
        intstart = False
        return

    def readfuntion(self):
        global lastping
        global mgft
        global giftcount
        global lastmessage
        global lastwave
        global seen
        pringtime = ("{:{tfmt}}".format(dt.now(), tfmt="%H:%M:%S"))
        buffer = ""
        buffer += sock.recv(2048).decode('utf-8')
        temp = buffer.split("\r\n")
        buffer = temp.pop()
        greetingWord = ["hey", "hi", "hello", "sup", "zaqHi", "yo"]
        greetings = ["Hey", "Hi", "Hello", "Sup",
                     "zaqHi", "zaqWave", "zaqHugA", "Waddup"]
        try:
            for line in temp:
                print(line)
                _line = str(line.encode("utf-8").decode("utf-8"))
                if line == "PING :tmi.twitch.tv":
                    lastping = dt.now().strftime('%Y%m%d%H%M%S')
                    sock.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
                if str("tmi.twitch.tv USERNOTICE ") in _line:
                    messagetype = re.search(r"msg-id=([a-zA-Z]+)", _line)
                    submsgmsg = "zaqHeart " * int(random.randint(30, 38))
                    gs = re.search(
                        r"system-msg=[a-zA-Z0-9-_\w]+ (gifted)", _line.replace("\s", " "))
                    try:
                        if str(messagetype.group(1)) == "resub":
                            print(Fore.BLUE + "[USERNOTICE INFO] " +
                                  Style.RESET_ALL + f"[{pringtime}] - RESUB")
                            sock.send(("PRIVMSG {} :{}\r\n").format(
                                chan, submsgmsg).encode("utf-8"))
                        elif str(messagetype.group(1)) == "sub":
                            print(Fore.BLUE + "[USERNOTICE INFO] " +
                                  Style.RESET_ALL + f"[{pringtime}] - SUB")
                            sock.send(("PRIVMSG {} :{}\r\n").format(
                                chan, submsgmsg).encode("utf-8"))
                        elif str(messagetype.group(1)) == "primepaidupgrade":
                            print(Fore.BLUE + "[USERNOTICE INFO] " +
                                  Style.RESET_ALL + f"[{pringtime}] - PRIMEPAIDUPGRADE")
                            sock.send(("PRIVMSG {} :{}\r\n").format(
                                chan, submsgmsg).encode("utf-8"))
                        elif str(messagetype.group(1)) == "giftpaidupgrade":
                            print(Fore.BLUE + "[USERNOTICE INFO] " +
                                  Style.RESET_ALL + f"[{pringtime}] - GIFTPAIDUPGRADE")
                            sock.send(("PRIVMSG {} :{}\r\n").format(
                                chan, submsgmsg).encode("utf-8"))
                        elif str(messagetype.group(1)) == "subgift" or gs:
                            print(Fore.BLUE + "[USERNOTICE INFO] " +
                                  Style.RESET_ALL + f"[{pringtime}] - SUBGIFT")
                            if (giftcount) > 0:
                                giftcount -= 1
                                pass
                            elif mgft == True:
                                mgft = False
                                sock.send(("PRIVMSG {} :{}\r\n").format(
                                    chan, submsgmsg).encode("utf-8"))
                            else:
                                sock.send(("PRIVMSG {} :{}\r\n").format(
                                    chan, submsgmsg).encode("utf-8"))
                        elif str(messagetype.group(1)) == "submysterygift":
                            print(Fore.BLUE + "[USERNOTICE INFO] " +
                                  Style.RESET_ALL + f"[{pringtime}] - SUBMYSTERYGIFT")
                            giftcounta = re.search(
                                r"msg-param-mass-gift-count=([0-9]+)", _line)
                            deting = int(giftcounta.group(1))
                            fcount = (deting - 1)
                            if fcount > 0:
                                mgft = True
                            giftcount += int(fcount)

                    except Exception as e:
                        pass
                if (self.randommessage()):
                    offset = int(random.randint(0, 60))
                    print(Fore.BLUE + "[RANDOM MESSAGE INFO]" + Style.RESET_ALL +
                          f"[{('{:{tfmt}}'.format(dt.now(), tfmt='%H:%M:%S'))}]Running message offset for {offset}s to trick the humans.")
                    sleep(offset)

                    print(Fore.BLUE + "[RANDOM MESSAGE INFO]" + Style.RESET_ALL +
                          f"[{('{:{tfmt}}'.format(dt.now(), tfmt='%H:%M:%S'))}]Sending '{self.randommessage()}' to the socket.")
                    sock.send(("PRIVMSG {} :{}\r\n").format(
                        chan, self.randommessage()).encode("utf-8"))
                    lastmessage = dt.now().strftime('%Y%m%d%H%M%S')

                if "PRIVMSG" in _line:
                    DPN = ""
                    stream = re.search(r"#([a-zA-Z0-9-_\w]+) :", _line)
                    currchan = stream.group(1)
                    findprv = ("PRIVMSG #{} :".format(stream.group(1)))
                    pri = _line.split(findprv)
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

                    try:
                        if str(cmds[0]).lower() in greetingWord or str(cmds[1]).lower() in greetingWord:
                            if self.shouldSayHi():
                                if DPN not in seen:
                                    sock.send(("PRIVMSG {} :{} {}\r\n").format(
                                        chan, random.choice(greetings), DPN).encode("utf-8"))
                                    seen.append(DPN)
                                else:
                                    print(
                                        Fore.BLUE + "[GREETING INFO] " + f"[{pringtime}]" + Style.RESET_ALL + f"I saw {DPN} today already, I won't be greeting.")
                                lastwave = dt.now().strftime('%Y%m%d%H%M%S')
                    except IndexError:
                        pass

                    if str(cmds[0]) == "!ping":
                        sock.send(("PRIVMSG {} :{}\r\n").format(
                            chan, "Pong!").encode("utf-8"))
                    # ErrorData.error(e)
                    # ErrorData.info('"{}"'.format(_line))
                    # ErrorData.error(traceback.format_exc())
        except Exception as e:
            # pass
            print(e)
            print("\n " + _line + "\n")
            print(traceback.format_exc())
        return

    def run(self):
        global intstart
        try:
            if intstart:
                sitinchat.connectsock(self)
        except Exception as e:
            print(Fore.RED + "[INFO] " + Style.RESET_ALL + e)

        while True:
            try:
                sitinchat.readfuntion(self)
            except Exception as e:
                pass
        return


class hearthbeat(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.start()

    def has_internet(self, url='http://www.google.com/', timeout=5):
        try:
            req = requests.get(url, timeout=timeout)
            req.raise_for_status()
            return True
        except requests.HTTPError as e:
            print(Fore.RED + "[HEARTHBEAT INFO] " + Style.RESET_ALL + "Checking internet connection failed, status code {0}.".format(
                e.response.status_code))
        except requests.ConnectionError:
            print(Fore.RED + "[HEARTHBEAT INFO] " +
                  Style.RESET_ALL + "No internet connection available.")
        return False

    def run(self):
        global lastping
        while True:
            sleep(60)
            try:
                sock.send(("ping\r\n").encode("utf-8"))
            except BrokenPipeError:
                if str(hearthbeat.has_internet(self)) == "True":
                    print(Fore.RED + "[HEARTHBEAT INFO] " +
                          Style.RESET_ALL + hearthbeat.has_internet(self))
                    os.execv(sys.executable, ['python3'] + sys.argv)
            except Exception as e:
                print(Fore.RED + "[HEARTHBEAT INFO] " +
                      Style.RESET_ALL + hearthbeat.has_internet(self))
                print(Fore.RED + traceback.format_exc() + Style.RESET_ALL)
            tnow = str(dt.now().strftime('%Y%m%d%H%M%S'))
            format = '%Y%m%d%H%M%S'
            delta = dt.strptime(tnow, format) - dt.strptime(lastping, format)
            if int(delta.total_seconds()) > 600.0:
                if str(hearthbeat.has_internet(self)) == "True":
                    os.execv(sys.executable, ['python3'] + sys.argv)
        return


try:
    sitinchat()
    hearthbeat()
    while True:
        pass
except KeyboardInterrupt:
    sys.exit(0)