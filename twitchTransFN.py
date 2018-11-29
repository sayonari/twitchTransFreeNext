from googletrans import Translator
from gtts import gTTS
from playsound import playsound
import os
from datetime import datetime
import threading
import queue
import time
import shutil
import re

from python_twitch_irc import TwitchIrc

import sys
import warnings
if not sys.warnoptions:
    warnings.simplefilter("ignore")

version = '2.0.4'
'''
v2.3.4  : 
v2.0.3  : いろいろ実装した
'''

'''
Thanks to Pioneers!
The developer of ...
- Google
- googletrans by ssut
    - https://github.com/ssut/py-googletrans
- gtts by pndurette
    - https://github.com/pndurette/gTTS
- playsound by TaylorSMarks
    - https://github.com/TaylorSMarks/playsound
- python_twitch_irc by jspaulsen
    - https://github.com/jspaulsen/python-twitch-irc

and Fix some bugs ...
- gTTS-token by Boudewijn26
- googletrans/gtoken by michaeldegroot/cats-blender-plugin

'''

# 設定 ###############################
Debug = False

#####################################
# 初期設定 ###########################
translator = Translator()

gTTS_queue = queue.Queue()
sound_queue = queue.Queue()

# configure for Google TTS & play
TMP_DIR = './tmp/'

# config keys
config = {'Twitch_Channel':'',
          'Trans_Username':'', 'Trans_OAUTH':'',
          'lang_TransToHome':'','lang_HomeToOther':'',
          'Ignore_Users': '', 'Ignore_Line':'', 'Delete_Words':'',
          'gTTS':''}

##########################################
# load config text #######################
readfile = 'config.txt'
f = open(readfile, 'r')
lines = f.readlines()

cnt = 1
for l in lines:
    if l.find("#") == 0 or l.strip() == "":
        continue

    conf_line = l.split('=')
    if conf_line[0].strip() in config.keys():
        config[conf_line[0].strip()] = conf_line[1].strip()
    else:
        print(
            "ERROR: " + conf_line[0].strip() + " is can't use in config.txt [line " + str(cnt) + "]! please check it.")
        exit()
    cnt = cnt + 1

f.close()

# fix some config bugs ##########

# remove "#" mark ------
if config['Twitch_Channel'].startswith('#'):
    print("Find # mark at channel name! I remove '#' from 'config:Twitch_Channel'")
    config["Twitch_Channel"] = config["Twitch_Channel"][1:]

# remove "oauth:" mark ------
if config['Trans_OAUTH'].startswith('oauth:'):
    print("Find 'oauth:' at OAUTH text! I remove 'oauth:' from 'config:Trans_OAUTH'")
    config["Trans_OAUTH"] = config["Trans_OAUTH"][6:]




# 無視ユーザリストの準備 ################
Ignore_Users = [x.strip() for x in config['Ignore_Users'].split(',')]

# 無視ユーザリストのユーザ名を全部小文字にする
Ignore_Users = [str.lower() for str in Ignore_Users]

# 無視テキストリストの準備 ################
Ignore_Line = [x.strip() for x in config['Ignore_Line'].split(',')]

# 無視単語リストの準備 ################
Delete_Words = [x.strip() for x in config['Delete_Words'].split(',')]



####################################################
#####################################
# Simple echo bot.
class MyOwnBot(TwitchIrc):
    def on_connect(self):
         self.join('#{}'.format(config['Twitch_Channel']))

    ##########################################
    # メイン動作 ##############################
    ##########################################

    # メッセージを受信したら ####################
    # Override from base class
    def on_message(self, timestamp, tags, channel, user, message):
        # 無視ユーザリストチェック -------------
        print('USER:{}'.format(user))
        if user in Ignore_Users:
            return

        # 無視テキストリストチェック -----------
        for w in Ignore_Line:
            if w in message:
                return

        # 削除単語リストチェック --------------
        for w in Delete_Words:
            message = message.replace(w, '')

        ################################
        # 入力 --------------------------
        in_text = message
        print(in_text)

        ################################
        # !sound 効果音再生 --------------
        if re.match('^\!sound ', in_text):
            sound_name = in_text.strip().split(" ")[1]
            sound_queue.put(sound_name)
            return



        #################################
        # 言語検出 -----------------------
        lang_detect = ''
        try:
            lang_detect = translator.detect(in_text).lang
        except:
            pass

        # 音声合成（入力文） --------------
        if config['gTTS'] == 'True': gTTS_queue.put([in_text, lang_detect])

        ################################
        # 翻訳先言語の選択 ---------------
        lang_dest = config['lang_TransToHome'] if lang_detect != config['lang_TransToHome'] else config['lang_HomeToOther']

        # 翻訳 --------------------------
        try:
            translatedText = translator.translate(in_text, src=lang_detect, dest=lang_dest).text
        except:
            pass

        out_text = '{} [by {}] ({} > {})'.format(translatedText, user, lang_detect, lang_dest)
        self.message(channel, out_text)
        print(out_text)

        # 音声合成（出力文） --------------
        if config['gTTS'] == 'True': gTTS_queue.put([translatedText, lang_dest])

        print()


#####################################
# 音声合成 ＆ ファイル保存 ＆ ファイル削除
def gTTS_play():
    global gTTS_queue

    while True:
        q = gTTS_queue.get()
        if q is None:
            time.sleep(1)
        else:
            text    = q[0]
            tl      = q[1]
            try:
                tts = gTTS(text, lang=tl)
                tts_file = './tmp/cnt_{}.mp3'.format(datetime.now().microsecond)
                if Debug: print('gTTS file: {}'.format(tts_file))
                tts.save(tts_file)
                playsound(tts_file, True)
                os.remove(tts_file)
            except Exception as e:
                print('gTTS error: 音声合成できないね．')
                if Debug: print(e.args)

#####################################
# !sound 音声再生スレッド -------------
def sound_play():
    global sound_queue

    while True:
        q = sound_queue.get()
        if q is None:
            time.sleep(1)
        else:
            try:
                playsound('./sound/{}.mp3'.format(q), True)
            except Exception as e:
                print('sound error: [!sound]コマンドの再生できないね．')
                if Debug: print(e.args)



# メイン処理 ###########################
# 初期表示 -----------------------
print('翻訳ちゃん twitchTransFreeNext (Version: {})'.format(version))
print('Connect to the channel   : {}'.format(config['Twitch_Channel']))
print('Translator Username      : {}'.format(config['Trans_Username']))

# 作業用ディレクトリ削除 ＆ 作成 ----
if os.path.exists(TMP_DIR):
    du = shutil.rmtree(TMP_DIR)
    time.sleep(0.3)

os.mkdir(TMP_DIR)

# 音声合成スレッド起動 ################
if config['gTTS'] == 'True':
    thread_gTTS = threading.Thread(target=gTTS_play)
    thread_gTTS.start()

# 音声合成スレッド起動 ################
thread_sound = threading.Thread(target=sound_play)
thread_sound.start()

# Twitch IRC 接続開始 ################
client = MyOwnBot(config['Trans_Username'], config['Trans_OAUTH']).start()
client.handle_forever()

