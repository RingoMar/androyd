import os
import enchant
import spacy
import operator
import json
import random
import re
import socket
import sys
import time
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
emotecool = ""


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
        self.pingged = False
        self.ping_sent = ""
        self.before = ""

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

    def shouldSayHi(self, uName):
        global lastwave
        configFile = loadFile("config.json")
        tnow = str(dt.now().strftime('%Y%m%d%H%M%S'))
        format = '%Y%m%d%H%M%S'
        if lastwave == "":
            if str(uName.lower()) in configFile["blacklisthello"]:
                return False
            else:
                return True

        delta = dt.strptime(tnow, format) - dt.strptime(lastwave, format)
        if int(delta.total_seconds()) > 5:
            if str(uName.lower()) in configFile["blacklisthello"]:
                return False
            else:
                return True
        else:
            return False

    def shouldEmote(self):
        global emotecool
        tnow = str(dt.now().strftime('%Y%m%d%H%M%S'))
        format = '%Y%m%d%H%M%S'
        if emotecool == "":
            return True

        delta = dt.strptime(tnow, format) - dt.strptime(emotecool, format)
        if int(delta.total_seconds()) > 120:
            return True
        else:
            return False

    def connectsock(self):
        global intstart
        print(Fore.GREEN)
        print("""
.  (   ( (   ( .    (   
 . )\  )\)\ ())  (  )\  
  ((_)((_)_)_)() )\((_) 
 / _ \| || | _ )((_) |_ 
| (_) |\_. | _ \ _ \  _|
 \___/ |__/|___/___/\__|""" + Style.RESET_ALL)
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

    def ping(self, text):
        if str("PRIVMSG") in text:
            stream = re.search(r"#([a-zA-Z0-9-_\w]+) :", text)
            currchan = stream.group(1)
            findprv = ("PRIVMSG #{} :".format(stream.group(1)))
            pri = text.split(findprv)
            cmds = re.split(" ", pri[1])
            if str(cmds[0]) == "!ping":
                self.pingged = True
                ttime = dt.now().strftime('%Y%m%d%H%M%S')
                self.ping_sent = ttime
                self.before = time.monotonic()
                sock.send(("PRIVMSG #rinb0t_ :pong!\r\n").encode("utf-8"))
                sock.send(("ping\r\n").encode("utf-8"))

        return

    def seed_name(self, rname):
        try:
            wrdType = {"ADJ": "adjective", "ADP": "adposition", "ADV": "adverb", "AUX": "auxiliary verb",
            "CONJ": "coordinating conjunction", "DET": "determiner", "INTJ": "interjection", "NOUN": "noun",
            "NUM": "numeral", "PART": "particle", "PRON": "pronoun", "PROPN": "proper noun",
            "PUNCT": "punctuation", "SCONJ": "subordinating conjunction", "SYM": "symbol",
            "VERB": "verb","X": "other"}
            nlp = spacy.load("en_core_web_sm")
            wordPredict = enchant.Dict("en_US")
            foundWords = []
            derivedWords = []
            suggestWords = []
            finalWords = {}
            tags = []
            name = rname.replace("_", " ")
            # If user has a capitals in name split it up 
            r1 = re.findall(r"([A-z][a-z]+)", name)
            try:
                if r1[1]:
                    for Fragname in r1:
                        suggestWords.append(Fragname)
            except IndexError:
                # User doesn't have capitals now looking for other names in name
                for namer in name:
                    try:
                        if wordPredict.check(derivedWords[-1]) and len(derivedWords[-1]) >= 3:
                            foundWords.append(derivedWords[-1])
                            del derivedWords[:]
                        derivedWords.append(derivedWords[-1] + namer)
                    except IndexError:
                        derivedWords.append(namer)

                for decon in derivedWords:
                    suggestWords.append(wordPredict.suggest(decon))
                for decon in foundWords:
                    suggestWords.append(wordPredict.suggest(decon))


            # Take suggested words and put into percentage cal
            for userWord in suggestWords:
                try:
                    if r1[1]:
                        try:
                            wordper = re.search(userWord, name)
                            types = nlp(wordper[0])
                            divF = 100/(len(wordper[0])+len(name))
                            finalWords[round((len(name) * divF), 2)] = [wordper[0]]
                            for token in types:
                                finalWords[round((len(name) * divF), 2)].append(token.text)
                                finalWords[round((len(name) * divF), 2)].append(token.pos_)
                                finalWords[round((len(name) * divF), 2)].append(token.lemma_)
                                finalWords[round((len(name) * divF), 2)].append(token.tag_)
                                finalWords[round((len(name) * divF), 2)].append(token.dep_)
                                finalWords[round((len(name) * divF), 2)].append(token.shape_)
                                finalWords[round((len(name) * divF), 2)].append(token.is_alpha)
                                finalWords[round((len(name) * divF), 2)].append(token.is_stop)
                        except TypeError:
                            pass
                except:
                    for rWordRE in userWord:
                        wordRE = rWordRE.replace("-", "")
                        rWordRE.replace(" ", "")
                        try:
                            wordper = re.search(wordRE, name)
                            types = nlp(wordper[0])
                            divF = 100/(len(wordper[0])+len(name))
                            finalWords[round((len(name) * divF), 2)] = [wordper[0]]
                            for token in types:
                                finalWords[round((len(name) * divF), 2)].append(token.text)
                                finalWords[round((len(name) * divF), 2)].append(token.pos_)
                                finalWords[round((len(name) * divF), 2)].append(token.lemma_)
                                finalWords[round((len(name) * divF), 2)].append(token.tag_)
                                finalWords[round((len(name) * divF), 2)].append(token.dep_)
                                finalWords[round((len(name) * divF), 2)].append(token.shape_)
                                finalWords[round((len(name) * divF), 2)].append(token.is_alpha)
                                finalWords[round((len(name) * divF), 2)].append(token.is_stop)
                        except TypeError:
                            pass

            sorted_dict = dict(sorted(finalWords.items(), key=operator.itemgetter(0)))
            # print(foundWords, derivedWords, suggestWords, finalWords)
            try:
                if len(finalWords[next(iter(sorted_dict))]) >= 3:
                    if int(next(iter(sorted_dict))) <= 80:
                        nameWeWant = ""
                        weWant = {"noun" : True, "pronoun": True, "adverb": True, "adjective": True}
                        for namesWeHave in finalWords.keys():
                                namesWeHAve = (wrdType[finalWords[namesWeHave][2]])
                                try:
                                    if weWant[namesWeHAve]:
                                        nameWeWant = finalWords[namesWeHave][1]
                                except KeyError:
                                    pass
                                
                        if nameWeWant:
                            return nameWeWant
                        else:
                            return rname
                    else:
                        return rname
                else:
                    return rname
            except:
                return rname

        except:
            return rname


    def readfuntion(self):
        global lastping
        global mgft
        global giftcount
        global lastmessage
        global lastwave
        global seen
        global emotecool
        pringtime = ("{:{tfmt}}".format(dt.now(), tfmt="%H:%M:%S"))
        buffer = ""
        buffer += sock.recv(2048).decode('utf-8')
        temp = buffer.split("\r\n")
        buffer = temp.pop()
        greetingWord = ["hey", "hi", "hello", "sup", "zaqHi", "yo"]
        greetings = ["Hey", "Hi", "Hello", "Sup", "Hola", "Bonjour",
                     "zaqHi", "zaqWave", "zaqHugA", "Waddup", "Oh Hey", "DONTPETTHERACCOON Hey"]
        try:
            for line in temp:
                if not "PRIVMSG" in line:
                    print(Fore.GREEN + ">>>" + Style.RESET_ALL, line)
                if self.pingged == True:
                    if line == "PONG :tmi.twitch.tv":
                        self.pingged = False
                        tnow = str(dt.now().strftime('%Y%m%d%H%M%S'))
                        format = '%Y%m%d%H%M%S'
                        delta = dt.strptime(tnow, format) - dt.strptime(self.ping_sent, format)
                        thepingnumber = str(delta.total_seconds())
                        tping = (time.monotonic() - self.before) * 1000
                        sock.send((f"PRIVMSG {chan} :Twitch:{thepingnumber[:-2]}ms, Oybot:{round(float(tping))}ms\r\n").encode("utf-8"))
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
                            giftcount = 0
                            print(Fore.BLUE + "[USERNOTICE INFO] " +
                                  Style.RESET_ALL + f"[{pringtime}] - RESUB")
                            sock.send(("PRIVMSG {} :{}\r\n").format(
                                chan, submsgmsg).encode("utf-8"))
                        elif str(messagetype.group(1)) == "sub":
                            giftcount = 0
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
                    greetingWords = re.search(
                        r"hey|hi|hello|sup|zaqHi|yo|hullo", pri[1].lower())
                    zaqT = re.search(r"(zaqT$)", pri[1])
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
                        if greetingWords:
                            if self.shouldSayHi(DPN):
                                if not DPN.lower() in seen:
                                    sock.send(("PRIVMSG {} :{} {}\r\n").format(
                                        chan, random.choice(greetings), self.seed_name(DPN)).encode("utf-8"))
                                    seen.append(DPN.lower())
                                else:
                                    print(
                                        Fore.BLUE + "[GREETING INFO] " + f"[{pringtime}]" + Style.RESET_ALL + f"I saw {DPN} today already, I won't be greeting.")
                            else:
                                seen.append(DPN.lower())
                                print(
                                    Fore.BLUE + "[GREETING INFO] " + f"[{pringtime}]" + Style.RESET_ALL + f"{DPN} Doesn't like when I say Hi to them. sadKEK")

                        elif not DPN.lower() in seen:
                            offset = int(random.randint(2, 4))
                            if self.shouldSayHi(DPN):
                                if DPN not in seen:
                                    sleep(offset)
                                    sock.send(("PRIVMSG {} :{} {}\r\n").format(
                                        chan, random.choice(greetings), self.seed_name(DPN)).encode("utf-8"))
                                    seen.append(DPN.lower())
                                else:
                                    print(
                                        Fore.BLUE + "[GREETING INFO] " + f"[{pringtime}]" + Style.RESET_ALL + f"I saw {DPN} today already, I won't be greeting.")
                            else:
                                seen.append(DPN.lower())
                                print(
                                    Fore.BLUE + "[GREETING INFO] " + f"[{pringtime}]" + Style.RESET_ALL + f"{DPN} Doesn't like when I say Hi to them. from the seen sadKEK")

                        lastwave = dt.now().strftime('%Y%m%d%H%M%S')
                    except IndexError:
                        pass
                    self.ping(line)
                    if str(cmds[0]) == "!blacklist" and DPN.lower() == "ringomar" or str(cmds[0]) == "!blacklist" and DPN.lower() == "oythebrave" :
                        configFile = loadFile("config.json")
                        configFile["blacklisthello"].append(cmds[1].lower())
                        saveFile("config.json", configFile)
                        sock.send(("PRIVMSG {} :{}\r\n").format(
                            chan, "Adding them to the LIST zaqNA").encode("utf-8"))
                    elif str(cmds[0]) == "!version":
                        req = requests.get("https://raw.githubusercontent.com/RingoMar/androyd/master/version.json", timeout=10).json()
                        sock.send(("PRIVMSG {} :Androyd Version: {}\r\n").format(
                            chan, req["version"]).encode("utf-8"))
                    elif zaqT  and DPN.lower() != "oythebrave":
                        if self.shouldEmote():
                            emotecool = dt.now().strftime('%Y%m%d%H%M%S')
                            sock.send(("PRIVMSG {} :{}\r\n").format(
                                chan, "zaqT").encode("utf-8"))
                    elif "zaqCA" in str(pri[1]) and DPN.lower() != "oythebrave" or "zaqCop" in str(pri[1]) and DPN.lower() != "oythebrave":
                        if self.shouldEmote():
                            emotecool = dt.now().strftime('%Y%m%d%H%M%S')
                            sock.send(("PRIVMSG {} :{}\r\n").format(
                                chan, "zaqCA").encode("utf-8"))
                    elif DPN == "RichardHarrow_" and "1v1" in str(pri[1]):
                            sock.send(("PRIVMSG {} :{}\r\n").format(
                                chan, "!roll").encode("utf-8"))

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
                    os.execv(sys.executable, ['python'] + sys.argv)
            except Exception as e:
                print(Fore.RED + "[HEARTHBEAT INFO] " +
                      Style.RESET_ALL, hearthbeat.has_internet(self))
                print(Fore.RED + traceback.format_exc() + Style.RESET_ALL)
                os.execv(sys.executable, ['python'] + sys.argv)
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
