#!/usr/bin/env python
# -*- coding: utf-8 -*-

#from googletrans import Translator
from google_trans_new import google_translator  

from gtts import gTTS
from playsound import playsound
import os
from datetime import datetime
import threading
import queue
import time
import shutil
import re

import asyncio

# from python_twitch_irc import TwitchIrc
from twitchio.ext import commands

import sys
from sys import exit
import signal

# import warnings
# if not sys.warnoptions:
#     warnings.simplefilter("ignore")

version = '2.1.2'
'''
v2.1.2  : _MEI関連
v2.1.1  : googletrans -> google_trans_new へ置き換え
v2.1.0  : config.py の導入
v2.0.11 : gTTSアップデート＆twitch接続モジュール変更＆色々修正
v2.0.10 : python コードの文字コードをUTF-8と指定
v2.0.10 : オプション gTTS を gTTS_In, gTTS_Out に分割
v2.0.8  : オプション「無視する言語」「Show_ByName」「Show_ByLang」追加`
v2.0.7  : チャット内の別ルームを指定して，そこに翻訳結果を書く
v2.0.6  : テキストの色変更
v2.0.5  : 裏技「翻訳先言語選択機能」実装 
v2.0.4  : 
v2.0.3  : いろいろ実装した
'''


# 設定 ###############################


#####################################
# 初期設定 ###########################
#translator = Translator()
translator = google_translator(timeout=5)

gTTS_queue = queue.Queue()
sound_queue = queue.Queue()

# configure for Google TTS & play
TMP_DIR = './tmp/'

TargetLangs = ["af", "sq", "am", "ar", "hy", "az", "eu", "be", "bn", "bs", "bg", "ca", "ceb", "ny", "zh-CN", "zh-TW", "co",
                "hr", "cs", "da", "nl", "en", "eo", "et", "tl", "fi", "fr", "fy", "gl", "ka", "de", "el", "gu", "ht", "ha",
                "haw", "iw", "hi", "hmn", "hu", "is", "ig", "id", "ga", "it", "ja", "jw", "kn", "kk", "km", "ko", "ku", "ky",
                "lo", "la", "lv", "lt", "lb", "mk", "mg", "ms", "ml", "mt", "mi", "mr", "mn", "my", "ne", "no", "ps", "fa",
                "pl", "pt", "ma", "ro", "ru", "sm", "gd", "sr", "st", "sn", "sd", "si", "sk", "sl", "so", "es", "su", "sw",
                "sv", "tg", "ta", "te", "th", "tr", "uk", "ur", "uz", "vi", "cy", "xh", "yi", "yo", "zu"]

##########################################
# load config text #######################
import importlib
try:
    sys.path.append(os.path.join(os.path.dirname(__file__), '.'))
    config = importlib.import_module('config')
except Exception as e:
    print(e)
    print('Please make [config.py] and put it with twitchTransFN')
    input() # stop for error!!

###################################
# fix some config errors ##########
# lowercase channel and username ------
config.Twitch_Channel = config.Twitch_Channel.lower()
config.Trans_Username = config.Trans_Username.lower()

# remove "#" mark ------
if config.Twitch_Channel.startswith('#'):
    # print("Find # mark at channel name! I remove '#' from 'config:Twitch_Channel'")
    config.Twitch_Channel = config.Twitch_Channel[1:]

# remove "oauth:" mark ------
if config.Trans_OAUTH.startswith('oauth:'):
    # print("Find 'oauth:' at OAUTH text! I remove 'oauth:' from 'config:Trans_OAUTH'")
    config.Trans_OAUTH = config.Trans_OAUTH[6:]


# 無視言語リストの準備 ################
Ignore_Lang = [x.strip() for x in config.Ignore_Lang]

# 無視ユーザリストの準備 ################
Ignore_Users = [x.strip() for x in config.Ignore_Users]

# 無視ユーザリストのユーザ名を全部小文字にする
Ignore_Users = [str.lower() for str in Ignore_Users]

# 無視テキストリストの準備 ################
Ignore_Line = [x.strip() for x in config.Ignore_Line]

# 無視単語リストの準備 ################
Delete_Words = [x.strip() for x in config.Delete_Words]


####################################################
#####################################
# Simple echo bot.
bot = commands.Bot(
    irc_token           = "oauth:" + config.Trans_OAUTH,
    client_id           = "",
    nick                = config.Trans_Username,
    prefix              = "!",
    initial_channels    = [config.Twitch_Channel]
)

##########################################
# メイン動作 ##############################
##########################################

# 起動時 ####################
@bot.event
async def event_ready():
    'Called once when the bot goes online.'
    print(f"{config.Trans_Username} is online!")
    ws = bot._ws  # this is only needed to send messages within event_ready
    await ws.send_privmsg(config.Twitch_Channel, f"/color {config.Trans_TextColor}")
    await ws.send_privmsg(config.Twitch_Channel, f"/me has landed!")


# メッセージを受信したら ####################
@bot.event
async def event_message(ctx):
    'Runs every time a message is sent in chat.'

    # コマンド処理 -----------------------
    await bot.handle_commands(ctx)

    if ctx.content.startswith('!'):
        return

    # 変数入れ替え ------------------------
    message = ctx.content
    user    = ctx.author.name.lower()

    # # bot自身の投稿は無視 -----------------
    if config.Debug: print(f'echo: {ctx.echo}, {ctx.content}')
    if ctx.echo:
        return

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

    # 入力 --------------------------
    in_text = message
    print(in_text)

    # 言語検出 -----------------------
    lang_detect = ''
    try:
        # lang_detect = translator.detect(in_text).lang
        lang_detect = translator.detect(in_text)[0]
    except Exception as e:
        if config.Debug: print(e)

    # 無視対象言語だったら無視 ---------
    if lang_detect in Ignore_Lang:
        return

    # 翻訳先言語の選択 ---------------
    lang_dest = config.lang_TransToHome if lang_detect != config.lang_TransToHome else config.lang_HomeToOther

    # 翻訳先言語が文中で指定されてたら変更 -------
    m = in_text.split(':')
    if len(m) >= 2:
        if m[0] in TargetLangs:
            lang_dest = m[0]
            in_text = ':'.join(m[1:])
    else:
        pass

    if config.Debug: print(f"lang_dest:{lang_dest} in_text:{in_text}")

    # 音声合成（入力文） --------------
    # if len(in_text) > int(config.TooLong_Cut):
    #     in_text = in_text[0:int(config.TooLong_Cut)]
    if config.gTTS_In: gTTS_queue.put([in_text, lang_detect])


    ################################
    # 翻訳 --------------------------
    translatedText = ''
    try:
        # translatedText = translator.translate(in_text, src=lang_detect, dest=lang_dest).text
        translatedText = translator.translate(in_text, lang_dest)
    except Exception as e:
        if config.Debug: print(e)

    # チャットへの投稿 ----------------
    # 投稿内容整形 & 投稿
    out_text = translatedText
    if config.Show_ByName:
        out_text = '{} [by {}]'.format(out_text, user)            
    if config.Show_ByLang:
        out_text = '{} ({} > {})'.format(out_text, lang_detect, lang_dest)
    await ctx.channel.send("/me " + out_text)

    # コンソールへの表示 --------------
    print(out_text)

    # 音声合成（出力文） --------------
    # if len(translatedText) > int(config.TooLong_Cut):
    #     translatedText = translatedText[0:int(config.TooLong_Cut)]
    if config.gTTS_Out: gTTS_queue.put([translatedText, lang_dest])

    print()


##############################
# コマンド ####################
@bot.command(name='ver')
async def ver(ctx):
    await ctx.send('this is tTFN. ver: ' + version)

@bot.command(name='sound')
async def sound(ctx):
    sound_name = ctx.content.strip().split(" ")[1]
    sound_queue.put(sound_name)


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
                if config.Debug: print('gTTS file: {}'.format(tts_file))
                tts.save(tts_file)
                playsound(tts_file, True)
                os.remove(tts_file)
            except Exception as e:
                print('gTTS error: TTS sound is not generated...')
                if config.Debug: print(e.args)

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
                print('sound error: [!sound] command can not play sound...')
                if config.Debug: print(e.args)

#####################################
# 最後のクリーンアップ処理 -------------
def cleanup():
    print("!!!Clean up!!!")

    # Cleanup処理いろいろ

    time.sleep(1)
    print("!!!Clean up Done!!!")

#####################################
# sig handler  -------------
def sig_handler(signum, frame) -> None:
    sys.exit(1)


#####################################
# _MEI cleaner  -------------
# Thanks to Sadra Heydari @ https://stackoverflow.com/questions/57261199/python-handling-the-meipass-folder-in-temporary-folder
import glob
import sys
import os
from shutil import rmtree

def CLEANMEIFOLDERS():
    try:
        base_path = sys._MEIPASS

    except Exception:
        base_path = os.path.abspath(".")

    if config.Debug: print(f'_MEI base path: {base_path}')
    base_path = base_path.split("\\") 
    base_path.pop(-1)                
    temp_path = ""                    
    for item in base_path:
        temp_path = temp_path + item + "\\"

    mei_folders = [f for f in glob.glob(temp_path + "**/", recursive=False)]
    for item in mei_folders:
        if item.find('_MEI') != -1 and item != sys._MEIPASS + "\\":
            rmtree(item)




# メイン処理 ###########################
def main():
    signal.signal(signal.SIGTERM, sig_handler)

    try:
        # 以前に生成された _MEI フォルダを削除する
        CLEANMEIFOLDERS()

        # 初期表示 -----------------------
        print('twitchTransFreeNext (Version: {})'.format(version))
        print('Connect to the channel   : {}'.format(config.Twitch_Channel))
        print('Translator Username      : {}'.format(config.Trans_Username))

        # 作業用ディレクトリ削除 ＆ 作成 ----
        if config.Debug: print("making tmp dir...")
        if os.path.exists(TMP_DIR):
            du = shutil.rmtree(TMP_DIR)
            time.sleep(0.3)

        os.mkdir(TMP_DIR)
        if config.Debug: print("made tmp dir.")

        # 音声合成スレッド起動 ################
        if config.Debug: print("run, tts thread...")
        if config.gTTS_In or  config.gTTS_Out:
            thread_gTTS = threading.Thread(target=gTTS_play)
            thread_gTTS.start()

        # 音声再生スレッド起動 ################
        if config.Debug: print("run, sound play thread...")
        thread_sound = threading.Thread(target=sound_play)
        thread_sound.start()

        # bot
        bot.run()


    except Exception as e:
        if config.Debug: print(e)
        input() # stop for error!!

    finally:
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        cleanup()
        signal.signal(signal.SIGTERM, signal.SIG_DFL)
        signal.signal(signal.SIGINT, signal.SIG_DFL)


if __name__ == "__main__":
    sys.exit(main())