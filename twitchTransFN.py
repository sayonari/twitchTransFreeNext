#!/usr/bin/env python
# -*- coding: utf-8 -*-

from async_google_trans_new import AsyncTranslator, constant

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
import deepl

from twitchio.ext import commands

import sys
import signal

# import warnings
# if not sys.warnoptions:
#     warnings.simplefilter("ignore")

version = '2.4.0'
'''
v2.4.0  : - yuniruyuni先生によるrequirements環境の整理
          - それに合わせたソースの改変
          - CeVIOへの対応
v2.3.0  : google_trans_new 修正，
v2.2.2  : GoogleAppsScriptを使って翻訳できるようにした
v2.2.1  : !timerコマンド追加
v2.2.0  : - 翻訳サーバの選択（ちゃらひろ先生による実装）
          - emoteを削除する
          - MacOS版と一本化（pyinstallerでのconfig.py読み込み対策）
（v2.1.5  : 音声再生速度の変更オプション）
v2.1.4  : 読み上げ言語指定ができるようにした
v2.1.3  : 関連モジュールアップデート、バグフィクス
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

#####################################
# 初期設定 ###########################

synth_queue = queue.Queue()
sound_queue = queue.Queue()

# configure for Google TTS & play
TMP_DIR = './tmp/'

# translate.googleのサフィックスリスト
URL_SUFFIX_LIST = [re.search('translate.google.(.*)', url.strip()).group(1) for url in constant.DEFAULT_SERVICE_URLS]

TargetLangs = ["af", "sq", "am", "ar", "hy", "az", "eu", "be", "bn", "bs", "bg", "ca", "ceb", "ny", "zh-CN", "zh-TW", "co",
                "hr", "cs", "da", "nl", "en", "eo", "et", "tl", "fi", "fr", "fy", "gl", "ka", "de", "el", "gu", "ht", "ha",
                "haw", "iw", "hi", "hmn", "hu", "is", "ig", "id", "ga", "it", "ja", "jw", "kn", "kk", "km", "ko", "ku", "ky",
                "lo", "la", "lv", "lt", "lb", "mk", "mg", "ms", "ml", "mt", "mi", "mr", "mn", "my", "ne", "no", "ps", "fa",
                "pl", "pt", "ma", "ro", "ru", "sm", "gd", "sr", "st", "sn", "sd", "si", "sk", "sl", "so", "es", "su", "sw",
                "sv", "tg", "ta", "te", "th", "tr", "uk", "ur", "uz", "vi", "cy", "xh", "yi", "yo", "zu"]

deepl_lang_dict = {'de':'DE', 'en':'EN', 'fr':'FR', 'es':'ES', 'pt':'PT', 'it':'IT', 'nl':'NL', 'pl':'PL', 'ru':'RU', 'ja':'JA', 'zh-CN':'ZH'}


##########################################
# load config text #######################
import importlib

# For [directly run from Python script at Windows, MacOS] -----------------------
try:
    sys.path.append(os.path.join(os.path.dirname(__file__), '.'))
    config = importlib.import_module('config')
except Exception as e:
    print(e)
    print('Please make [config.py] and put it with twitchTransFN')
    input() # stop for error!!

# # For [MacOS & pyinstaller] --------------------------------------------------
# from AppKit import NSBundle

# path = NSBundle.mainBundle().pathForResource_ofType_("config", "py")
# path = path.replace('config.py','')
# try:
#     sys.path.append(os.path.join(path, '.'))
#     config = importlib.import_module('config')
# except Exception as e:
#     print(e)
#     print(path)
#     print('Please make [config.py] and put it with twitchTransFN')
#     input() # stop for error!!

###################################
# fix some config errors ##########

# convert depreated gTTS_In, gTTS_Out => TTS_in, TTS_Out ------
if hasattr(config, 'gTTS_In') and not hasattr(config, 'TTS_In'):
    print('[warn] gTTS_In is already deprecated, please use TTS_In instead.')
    config.TTS_In = config.gTTS_In

if hasattr(config, 'gTTS_Out') and not hasattr(config, 'TTS_Out'):
    print('[warn] gTTS_Out is already deprecated, please use TTS_Out instead.')
    config.TTS_Out = config.gTTS_Out


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

# suffixのチェック、google_trans_newインスタンス生成
if hasattr(config, 'GoogleTranslate_suffix'):
    if config.GoogleTranslate_suffix not in URL_SUFFIX_LIST:
        url_suffix = 'co.jp'
    else:
        url_suffix = config.GoogleTranslate_suffix
else:
    url_suffix = 'co.jp'

translator = AsyncTranslator(url_suffix=url_suffix)

##########################################
# 関連関数 ################################
##########################################

#####################################
# Google Apps Script 翻訳
async def GAS_Trans(session, text, lang_source, lang_target):
    if text is None:
        config.Debug: print("[GAS_Trans] text is empty")
        return False

    url = config.GAS_URL
    payload = {
        "text"  : text,
        "source": lang_source,
        "target": lang_target
    }
    headers = {
        'Content-Type': 'application/json',
    }

    async with session.post(url, json=payload, headers=headers) as res:
        if res.status == 200:
            if config.Debug: print("[GAS_Trans] post success!")
            return await res.text()
        else:
            if config.Debug: print("[GAS_Trans] post failed...")
        return False



##########################################
# メイン動作 ##############################
##########################################

class Bot(commands.Bot):

    def __init__(self):
        super().__init__(
            token               = config.Trans_OAUTH,
            prefix              = "!",
            initial_channels    = [config.Twitch_Channel]
        )

    # 起動時 ####################
    async def event_channel_joined(self, channel):
        'Called once when the bot goes online.'
        print(f"{self.nick} is online!")
        await channel.send(f"/color {config.Trans_TextColor}")
        await channel.send(f"/me has landed!")

    # メッセージを受信したら ####################
    async def event_message(self, msg):
        'Runs every time a message is sent in chat.'

        # # bot自身の投稿は無視 -----------------
        if config.Debug: print(f'echo: {msg.echo}, {msg.content}')
        if msg.echo:
            return

        # コマンド処理 -----------------------
        if not msg.echo:
            await self.handle_commands(msg)

        if msg.content.startswith('!'):
            return

        # 変数入れ替え ------------------------
        message = msg.content
        user    = msg.author.name.lower()

        # 無視ユーザリストチェック -------------
        if config.Debug: print('USER:{}'.format(user))
        if user in Ignore_Users:
            return

        # 無視テキストリストチェック -----------
        for w in Ignore_Line:
            if w in message:
                return

        # 削除単語リストチェック --------------
        for w in Delete_Words:
            message = message.replace(w, '')

        # emoteの削除 --------------------------
        # エモート抜き出し
        emote_list = []
        if msg.tags:
            if msg.tags['emotes']:
                # エモートの種類数分 '/' で分割されて提示されてくる
                emotes_s = msg.tags['emotes'].split('/')
                for emo in emotes_s:
                    if config.Debug: print()
                    if config.Debug: print(emo)
                    e_id, e_pos = emo.split(':')

                    # 同一エモートが複数使われてたら，その数分，情報が入ってくる
                    # （例：1110537:4-14,16-26）
                    if config.Debug: print(f'e_pos:{e_pos}')
                    if ',' in e_pos:
                        ed_pos = e_pos.split(',')
                        for e in ed_pos:
                            if config.Debug: print(f'{e}')
                            if config.Debug: print(e.split('-'))
                            e_s, e_e = e.split('-')
                            if config.Debug: print(msg.content[int(e_s):int(e_e)+1])

                            # リストにエモートを追加
                            emote_list.append(msg.content[int(e_s):int(e_e)+1])

                    else:
                        e = e_pos
                        e_s, e_e = e.split('-')
                        if config.Debug: print(msg.content[int(e_s):int(e_e)+1])

                        # リストにエモートを追加
                        emote_list.append(msg.content[int(e_s):int(e_e)+1])

                # message(msg.contextの編集用変数)から，エモート削除
                if config.Debug: print(f'message with emote:{message}')
                for w in sorted(emote_list, key=len, reverse=True):
                    if config.Debug: print(w)
                    message = message.replace(w, '')

                if config.Debug: print(f'message without emote:{message}')

        # 複数空文字を一つにまとめる --------
        message = " ".join( message.split() )

        if not message:
            return

        # 入力 --------------------------
        in_text = message
        print(in_text)

        # 言語検出 -----------------------
        if config.Debug: print(f'--- Detect Language ---')
        lang_detect = ''

        # use google_trans_new ---
        if not config.GAS_URL or config.Translator == 'deepl':
            try:
                detected = await translator.detect(in_text)
                lang_detect = detected[0]
            except Exception as e:
                if config.Debug: print(e)

        # use GAS ---
        else:
            try:
                trans_text = await GAS_Trans(self._http.session, in_text, '', config.lang_TransToHome)
                if trans_text == in_text:
                    lang_detect = config.lang_TransToHome
                else:
                    lang_detect = 'GAS'
            except Exception as e:
                if config.Debug: print(e)

        if config.Debug: print(f'lang_detect:{lang_detect}')

        # 翻訳先言語の選択 ---------------
        if config.Debug: print(f'--- Select Destinate Language ---')
        lang_dest = config.lang_TransToHome if lang_detect != config.lang_TransToHome else config.lang_HomeToOther
        if config.Debug: print(f"lang_detect:{lang_detect} lang_dest:{lang_dest}")

        # 翻訳先言語が文中で指定されてたら変更 -------
        m = in_text.split(':')
        if len(m) >= 2:
            if m[0] in TargetLangs:
                lang_dest = m[0]
                in_text = ':'.join(m[1:])
        else:
            # 翻訳先が (:)で指定されてなくて、
            # なおかつ 無視対象言語だったら全部無視して終了↑ ---------
            if lang_detect in Ignore_Lang:
                return

        if config.Debug: print(f"lang_dest:{lang_dest} in_text:{in_text}")

        # 音声合成（入力文） --------------
        # if len(in_text) > int(config.TooLong_Cut):
        #     in_text = in_text[0:int(config.TooLong_Cut)]
        if config.TTS_In: synth_queue.put([in_text, lang_detect])

        # 検出言語と翻訳先言語が同じだったら無視！
        if lang_detect == lang_dest:
            return

        ################################
        # 翻訳 --------------------------
        if config.Debug: print(f'--- Translation ---')
        translatedText = ''

        # use deepl --------------
        # (try to use deepl, but if the language is not supported, text will be translated by google!)
        if config.Translator == 'deepl':
            try:
                if lang_detect in deepl_lang_dict.keys() and lang_dest in deepl_lang_dict.keys():
                    translatedText = deepl.translate(source_language=deepl_lang_dict[lang_detect], target_language=deepl_lang_dict[lang_dest], text=in_text)
                    if config.Debug: print(f'[DeepL Tlanslate]({deepl_lang_dict[lang_detect]} > {deepl_lang_dict[lang_dest]})')
                else:
                    translatedText = await translator.translate(in_text, lang_dest)
                    if config.Debug: print('[Google Tlanslate]')
            except Exception as e:
                if config.Debug: print(e)

        # NOT use deepl ----------
        elif config.Translator == 'google':
            # use google_trans_new ---
            if not config.GAS_URL:
                try:
                    translatedText = await translator.translate(in_text, lang_dest)
                    if config.Debug: print('[Google Tlanslate (google_trans_new)]')
                except Exception as e:
                    if config.Debug: print(e)

            # use GAS ---
            else:
                try:
                    translatedText = await GAS_Trans(self._http.session, in_text, '', lang_dest)
                    if config.Debug: print('[Google Tlanslate (Google Apps Script)]')
                except Exception as e:
                    if config.Debug: print(e)

        else:
            print(f'ERROR: config TRANSLATOR is set the wrong value with [{config.Translator}]')
            return

        # チャットへの投稿 ----------------
        # 投稿内容整形 & 投稿
        out_text = translatedText
        if config.Show_ByName:
            out_text = '{} [by {}]'.format(out_text, user)
        if config.Show_ByLang:
            out_text = '{} ({} > {})'.format(out_text, lang_detect, lang_dest)

        # コンソールへの表示 --------------
        print(out_text)

        await msg.channel.send("/me " + out_text)


        # 音声合成（出力文） --------------
        # if len(translatedText) > int(config.TooLong_Cut):
        #     translatedText = translatedText[0:int(config.TooLong_Cut)]
        if config.TTS_Out: synth_queue.put([translatedText, lang_dest])


    ##############################
    # コマンド ####################
    @commands.command(name='ver')
    async def ver(self, ctx):
        await ctx.send('this is tTFN. ver: ' + version)

    @commands.command(name='sound')
    async def sound(ctx):
        sound_name = ctx.content.strip().split(" ")[1]
        sound_queue.put(sound_name)

    @commands.command(name='timer')
    async def timer(ctx):
        timer_min = 0
        timer_name = ''

        d = ctx.content.strip().split(" ")
        if len(d) == 2:
            try:
                timer_min = int(d[1])
            except Exception as e:
                    print('timer error: !timer [min] [name]')
                    if config.Debug: print(e.args)
                    return 0

        elif len(d) == 3:
            try:
                timer_min = int(d[1])
                timer_name = d[2]
            except Exception as e:
                    print('timer error: !timer [min] [name]')
                    if config.Debug: print(e.args)
                    return 0

        else:
            print(f'command error [{ctx.content}]')
            return 0

        await ctx.send(f'#### timer [{timer_name}] ({timer_min} min.) start! ####')
        await asyncio.sleep(timer_min*60)
        await ctx.send(f'#### timer [{timer_name}] ({timer_min} min.) end! ####')

bot = Bot()

# CeVIOを呼び出すための関数を生成する関数
# つまり cast 引数を与えることで、この関数から
# 該当のCeVIOキャストにより音声再生を行える関数が帰ってきます。
# 例("さとうささら"に"ささらちゃん読み上げて！"を読ませる呼び出し):
#   f = CeVIO("さとうささら")
#   f("ささらちゃん読み上げて！", "ja")
# TODO: ただし第二引数(tl)は現状実装されていないため、
# 該当キャストのデフォルト言語で読み上げは行われます。
def CeVIO(cast):
    # CeVIOとそれを呼び出すためのWin32COMの仕組みはWindowsにしかありません。
    # そこでこのCeVIO関数内にimport実行を閉じることで
    # ライブラリの不在を回避して他環境と互換させます。
    import win32com.client
    cevio = win32com.client.Dispatch("CeVIO.Talk.RemoteService2.ServiceControl2")
    cevio.StartHost(False)
    talker = win32com.client.Dispatch("CeVIO.Talk.RemoteService2.Talker2V40")
    talker.Cast = cast
    # in this routine, we will omit tl because CeVIO doesn't support language paramter.
    def play(text, _):
        try:
            state = talker.Speak(text)
            if config.Debug: print(f"text '{text}' has dispatched to CeVIO.")
            state.Wait()
        except Exception as e:
            print('CeVIO error: TTS sound is not generated...')
            if config.Debug: print(e.args)
    return play

# gTTSを利用して
# 音声合成 ＆ ファイル保存 ＆ ファイル削除
# までを行う音声合成の実行関数。
def gTTS_play(text, tl):
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

# 音声合成(TTS)の待ち受けスレッド
# このスレッドにより各音声合成(TTS)が起動して音声読み上げされます。
# このスレッドに対するメッセージ入力は
# グローバルに定義されたsynth_queueを介して行います。
def voice_synth():
    global synth_queue

    tts = Determine_TTS()
    while True:
        q = synth_queue.get()
        if q is None:
            time.sleep(1)
        else:
            text    = q[0]
            tl      = q[1]

            if config.Debug: print('debug in Voice_Thread')
            if config.Debug: print(f'config.ReadOnlyTheseLang : {config.ReadOnlyTheseLang}')
            if config.Debug: print(f'tl not in config.ReadOnlyTheseLang : {tl not in config.ReadOnlyTheseLang}')

            # 「この言語だけ読み上げて」リストが空じゃなく，なおかつそのリストにに入ってなかったら無視
            if config.ReadOnlyTheseLang and (tl not in config.ReadOnlyTheseLang):
                continue

            tts(text, tl)

# どのTextToSpeechを利用するかをconfigから選択して再生用の関数を返す
def Determine_TTS():
    kind = config.TTS_Kind.strip().upper()
    if kind == "CeVIO".upper():
        return CeVIO(config.CeVIO_Cast)
    else:
        return gTTS_play

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
        print('Translator ENGINE        : {}'.format(config.Translator))

        if not config.GAS_URL:
            print('Google Translate         : translate.google.{}'.format(url_suffix))
        else:
            print(f'Translate using Google Apps Script')
            if config.Debug: print(f'GAS URL: {config.GAS_URL}')

        # 作業用ディレクトリ削除 ＆ 作成 ----
        if config.Debug: print("making tmp dir...")
        if os.path.exists(TMP_DIR):
            du = shutil.rmtree(TMP_DIR)
            time.sleep(0.3)

        os.mkdir(TMP_DIR)
        if config.Debug: print("made tmp dir.")

        # 音声合成スレッド起動 ################
        if config.Debug: print("run, voice synth thread...")
        if config.TTS_In or  config.TTS_Out:
            thread_voice = threading.Thread(target=voice_synth)
            thread_voice.start()

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
