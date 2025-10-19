#!/usr/bin/env python
# -*- coding: utf-8 -*-

from async_google_trans_new import AsyncTranslator, constant
from http.client import HTTPSConnection as hc
from twitchio.ext import commands
from emoji import distinct_emoji_list
import json, os, shutil, re, asyncio, deepl, sys, signal, tts, sound
import database_controller as db # ja:既訳語データベース   en:Translation Database

version = '2.7.13'
'''
v2.7.13 : - is_frozen判定を一時ディレクトリチェックに変更（Nuitka onefile完全対応）（@sayonari）
          - EXE_DIRをsys.argv[0]ベースに変更（正しいパスを取得）（@sayonari）
v2.7.12 : - is_frozen判定を'__compiled__' in sys.modulesに修正（Nuitka検出修正）（@sayonari）
          - sys.argv[0]とsys.executableのデバッグ出力を追加（@sayonari）
v2.7.11 : - EXE_DIR取得をsys.executableに変更（Nuitka onefileモード対応）（@sayonari）
          - is_frozen判定のデバッグ出力を追加（問題診断用）（@sayonari）
v2.7.10 : - tmpディレクトリの相対パス問題を完全に修正（@sayonari）
          - TMP_DIRとSOUND_DIRを明示的にTTS/Soundクラスに渡すように変更（@sayonari）
v2.7.9  : - tmpディレクトリとデータベースを実行ファイルのディレクトリに生成するように修正（@sayonari）
          - macOS Nuitkaバイナリでの音声再生問題を修正（afplay直接使用）（@sayonari）
v2.7.8  : - uvパッケージマネージャーへの移行（@sayonari）
          - GitHub Actions改善（ビルド高速化）（@sayonari）
v2.7.6  : - SSLエラーにならないように，cacert.pemを同梱（@sayonari）
v2.7.5  : - deepl翻訳が429(要求過多)エラーなので，標準翻訳設定をgoogleにした（とりあえず）（@sayonari）
          - 翻訳結果がない時投稿しないように変更（@sayonari）
          - 翻訳後のテキストからも，Delete_Wordsを削除するように変更（@sayonari）
          - 読み上げ時の末尾の追加語（以下略）を config.py から削除（@sayonari）
v2.7.4  : - _MEI削除部分がコントリビュータによって削除されていたので，再度追加（@sayonari)
          - zh-TWの翻訳先言語をzh-twに変更
v2.7.3  : - Windows版 .exe をPyInstallerでビルドするときに，trojanが検出される問題を修正（build.ymlの修正）
v2.7.2  : - 開発者（さぁたん，さよなりω）のアカウント名が起動時に表示されるようになった
v2.7.1  : - bug fix
          - non_twitch_emotes()をコメントアウト（うまく動かなかったので）
v2.7.0  : - 単芝チェック追加（wのみの発言を無視）
          - 長過ぎるコメント文をTTS読み上げに対して省略する機能（@yuniruyuni）
          - tts.py, sound.py を作成し，それぞれの機能を分離
          - DeepLが無料翻訳の単語制限に達しないようにするためのアップデートです。（@didotb）
v2.5.1  : - bug fix for TTS(さとうささら) by yuniruyuni
v2.5.0  : - 実行バイナリをリポジトリに含めず，ActionsでReleaseするように変更（yuniruyuni先生，ちゃらひろ先生による）
          - 様々なバグ修正（ちゃらひろせんせいによる）
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

wakeup_message = f'TwitchTransFreeNext v.{version}, by さぁたん @saatan_pion and さよなりω @husband_sayonari_omega'

#####################################
# 初期設定 ###########################

# 実行ファイルのディレクトリを取得（Nuitka/PyInstaller対応）
# Nuitkaの--onefileモードではsys.executableが一時ディレクトリを指す
# その場合はsys.argv[0]を使用する
exe_path = sys.executable
is_frozen = (
    getattr(sys, 'frozen', False) or
    '__compiled__' in sys.modules or
    '/tmp/' in exe_path or '/var/folders/' in exe_path  # 一時ディレクトリチェック
)

# デバッグ出力
print(f"[Main DEBUG] is_frozen: {is_frozen}")
print(f"[Main DEBUG] sys.argv[0]: {sys.argv[0]}")
print(f"[Main DEBUG] sys.executable: {sys.executable}")

if is_frozen:
    # Nuitkaまたはその他のバイナリ実行時
    # sys.argv[0]を使用（onefileモードではこちらが正しいパス）
    EXE_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))
    print(f"[Main DEBUG] Binary mode: Using sys.argv[0] for EXE_DIR: {EXE_DIR}")
else:
    # 通常のPythonスクリプト実行時
    EXE_DIR = os.path.dirname(os.path.abspath(__file__))
    print(f"[Main DEBUG] Script mode: Using __file__ for EXE_DIR: {EXE_DIR}")

# configure for Google TTS & play
TMP_DIR = os.path.join(EXE_DIR, 'tmp')
SOUND_DIR = os.path.join(EXE_DIR, 'sound')

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
    sys.path.append(os.path.dirname(sys.argv[0]))
    config = importlib.import_module('config')
except Exception as e:
    print(e)
    print('Please make [config.py] and put it with twitchTransFN')
    input() # stop for error!!

###################################
# fix some config errors ##########

# convert depreated gTTS_In, gTTS_Out => TTS_in, TTS_Out ------
if hasattr(config, 'gTTS_In') and not hasattr(config, 'TTS_In'):
    print('[warn] gTTS_In is already deprecated, please use TTS_In instead.')
    config.TTS_In = config.gTTS_In

if hasattr(config, 'gTTS_Out') and not hasattr(config, 'TTS_Out'):
    print('[warn] gTTS_Out is already deprecated, please use TTS_Out instead.')
    config.TTS_Out = config.gTTS_Out


# 無視言語リストの準備 ##################
Ignore_Lang = [x.strip() for x in config.Ignore_Lang]

# 無視ユーザリストの準備 ################
Ignore_Users = [x.strip() for x in config.Ignore_Users]

# 無視ユーザリストのユーザ名を全部小文字にする
Ignore_Users = [str.lower() for str in Ignore_Users]

# 無視テキストリストの準備 ##############
Ignore_Line = [x.strip() for x in config.Ignore_Line]

# 無視単芝リストの準備 #################
Ignore_WWW = [x.strip() for x in config.Ignore_WWW]

# 無視単語リストの準備 #################
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
tts = tts.TTS(config, TMP_DIR)
sound = sound.Sound(config, SOUND_DIR)

##########################################
# cacert.pem の場所を特定
if getattr(sys, 'frozen', False):
    # PyInstaller でビルドされた場合
    bundle_dir = sys._MEIPASS
else:
    # 通常の Python スクリプトとして実行された場合
    bundle_dir = os.path.dirname(os.path.abspath(__file__))

cacert_path = os.path.join(bundle_dir, 'cacert.pem')
# cacert_path = os.path.join(bundle_dir, 'data', 'cacert.pem') # dataフォルダに配置した場合

# 環境変数 SSL_CERT_FILE を設定
os.environ['SSL_CERT_FILE'] = cacert_path

# cacert.pem が存在するか確認
if not os.path.exists(cacert_path):
    print(f"Error: cacert.pem not found at {cacert_path}")
    sys.exit(1)

##########################################
# 関連関数 ################################
##########################################

#####################################
# Google Apps Script 翻訳
async def GAS_Trans(session, text, lang_source, lang_target):
    if text is None:
        if config.Debug: print("[GAS_Trans] text is empty")
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

# async def non_twitch_emotes(channel:str):
#     emotes_list = [] # List of non-Twitch emotes
#     conn = hc("emotes.adamcy.pl") # non-Twitch emotes API
    
#     # Get non-Twitch channel emotes
#     for path in [f"/v1/channel/{channel}/emotes/bttv.7tv.ffz","/v1/global/emotes/bttv.7tv.ffz"]:
#         conn.request("GET", path) # Get non-Twitch emotes
#         resp = conn.getresponse() # Get API response
#         for i in json.loads(resp.read()):
#             emotes_list.append(i['code'])
#     return emotes_list

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
    
    # Get the parent directory in a cross-platform way
    parent_dir = os.path.dirname(base_path)
    
    # Get all directories in the parent directory
    try:
        all_dirs = [os.path.join(parent_dir, d) for d in os.listdir(parent_dir) 
                   if os.path.isdir(os.path.join(parent_dir, d))]
        
        # Filter for _MEI directories
        mei_folders = [d for d in all_dirs if '_MEI' in d]
        
        # Sort by creation time
        mei_folders = sorted(mei_folders, key=os.path.getctime)
        
        # Remove all but the newest folder
        if len(mei_folders) > 1:
            for item in mei_folders[:-1]:
                if config.Debug: print(f'Removing old _MEI folder: {item}')
                rmtree(item)
    except Exception as e:
        if config.Debug: print(f'Error cleaning _MEI folders: {e}')
    
    # if len(mei_folders) > 1:
    #     for item in mei_folders:
    #         if item.find('_MEI') != -1 and item != sys._MEIPASS + "\\":
    #             rmtree(item)




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
        await channel.send(f"/me {wakeup_message}")

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
        # non_twitch_emote_list = await non_twitch_emotes(config.Twitch_Channel)

        # 無視ユーザリストチェック -------------
        if config.Debug: print('USER:{}'.format(user))
        if user in Ignore_Users:
            return

        # 無視テキストリストチェック -----------
        for w in Ignore_Line:
            if w in message:
                return
            
        # 単芝チェック ------------------------
        # １行が単芝だけだったら無視
        if message in Ignore_WWW:
            return

        # emoteの削除 --------------------------
        # エモート抜き出し
        emote_list = []
        # Twitch Emotes
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
                        ed_pos = e_pos.split(',') # ed_pos = "emote duplicate position"?
                        for e in ed_pos:
                            if config.Debug: print(f'{e}')
                            if config.Debug: print(e.split('-'))
                            e_s, e_e = e.split('-') # e_s = "emote start", e_e = "emote end"
                            if config.Debug: print(msg.content[int(e_s):int(e_e)+1])

                            # リストにエモートを追加
                            emote_list.append(msg.content[int(e_s):int(e_e)+1])

                    else:
                        e = e_pos
                        e_s, e_e = e.split('-')
                        if config.Debug: print(msg.content[int(e_s):int(e_e)+1])

                        # リストにエモートを追加
                        emote_list.append(msg.content[int(e_s):int(e_e)+1])

        # # en:Remove non-Twitch emotes from message     ja:メッセージからTwitch以外のエモートを削除
        # temp_msg = message.split(' ')
        # # en:Place non-Twitch emotes in temporary variable  ja:Twitch以外のエモートを一時的な変数に配置する。
        # nte = list(set(non_twitch_emote_list) & set(temp_msg)) # nte = "non-Twitch emotes"
        # for i in nte:
        #     if config.Debug: print(i)
        #     emote_list.append(i)

        # en:Place unicode emoji in temporary variable  ja:ユニコード絵文字をテンポラリ変数に入れる
        uEmoji = distinct_emoji_list(message) # uEmoji = "Unicode Emoji"
        for i in uEmoji:
            if config.Debug: print(i)
            emote_list.append(i)

        # message(msg.contextの編集用変数)から，エモート削除
        if config.Debug: print(f'message with emote:{message}')
        for w in sorted(emote_list, key=len, reverse=True):
            if config.Debug: print(w)
            message = message.replace(w, '')

        if config.Debug: print(f'message without emote:{message}')

        # 削除単語リストチェック --------------
        for w in Delete_Words:
            message = message.replace(w, '')

        # @ユーザー名を削除
        message = re.sub(r'@\S+', '', message)

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

        # zh-TW バグ対応（言語検出系はzh-TWだが，翻訳系はzh-twにしないといけない）
        if lang_dest == 'zh-TW':
            lang_dest = 'zh-tw'

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
        if config.TTS_In: tts.put(in_text, lang_detect)

        # 検出言語と翻訳先言語が同じだったら無視！
        if lang_detect == lang_dest:
            return

        ################################
        # 翻訳 --------------------------
        if config.Debug: print(f'--- Translation ---')
        translatedText = ''

        # en:Use database to reduce deepl limit     ja:データベースの活用でDeepLの字数制限を軽減
        translation_from_database = await db.get(in_text,lang_dest) if in_text is not None else None

        if translation_from_database is not None:
            translatedText = translation_from_database[0]
            if config.Debug: print(f'[Local Database](SQLite database file)')
        elif (translation_from_database is None) and (in_text is not None):
            # use deepl --------------
            # (try to use deepl, but if the language is not supported, text will be translated by google!)
            if config.Translator == 'deepl':
                try:
                    if lang_detect in deepl_lang_dict.keys() and lang_dest in deepl_lang_dict.keys():
                        translatedText = (
                            await asyncio.gather(asyncio.to_thread(deepl.translate, source_language= deepl_lang_dict[lang_detect], target_language=deepl_lang_dict[lang_dest], text=in_text))
                            )[0]
                        if config.Debug: print(f'[DeepL Tlanslate]({deepl_lang_dict[lang_detect]} > {deepl_lang_dict[lang_dest]})')
                    else:
                        if not config.GAS_URL:
                            try:
                                translatedText = await translator.translate(in_text, lang_dest)
                                if config.Debug: print('[Google Tlanslate (google_trans_new)]')
                            except Exception as e:
                                if config.Debug: print(e)
                        else:
                            try:
                                translatedText = await GAS_Trans(self._http.session, in_text, '', lang_dest)
                                if config.Debug: print('[Google Tlanslate (Google Apps Script)]')
                            except Exception as e:
                                if config.Debug: print(e)
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

            # en:Save the translation to database   ja:翻訳をデータベースに保存する
            await db.save(in_text,translatedText,lang_dest)

        # チャットへの投稿 ----------------

        # 翻訳後のメッセージでも，削除単語リストチェック＆削除 --------------
        for w in Delete_Words:
            translatedText = translatedText.replace(w, '')

        # 投稿内容整形(名前，言語表示)-------------
        out_text = translatedText
        if config.Show_ByName:
            out_text = '{} [by {}]'.format(out_text, user)
        if config.Show_ByLang:
            out_text = '{} ({} > {})'.format(out_text, lang_detect, lang_dest)

        # コンソールへの表示 --------------
        print(out_text)

        # チャットへの投稿 --------------
        # 翻訳結果がない時は投稿しない　(つまり：translatedTextが空でない時は投稿する！)
        if translatedText and (in_text is not None):
            await msg.channel.send("/me " + out_text)

        # 音声合成（出力文） --------------
        # if len(translatedText) > int(config.TooLong_Cut):
        #     translatedText = translatedText[0:int(config.TooLong_Cut)]
        if config.TTS_Out: tts.put(translatedText, lang_dest)


    ##############################
    # コマンド ####################
    @commands.command(name='ver')
    async def ver(self, ctx):
        await ctx.send('this is tTFN. ver: ' + version)

    @commands.command(name='sound')
    async def sound(self, ctx):
        sound_name = ctx.message.content.strip().split(" ")[1]
        sound.put(sound_name)

    @commands.command(name='timer')
    async def timer(self, ctx):
        timer_min = 0
        timer_name = ''

        d = ctx.message.content.strip().split(" ")
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

# メイン処理 ###########################
def main():
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
        if config.Debug: print(f"making tmp dir...: {TMP_DIR}")
        if os.path.exists(TMP_DIR):
            shutil.rmtree(TMP_DIR)

        os.mkdir(TMP_DIR)
        if config.Debug: print("made tmp dir.")

        # 音声合成スレッド起動 ################
        tts.run()

        # 音声再生スレッド起動 ################
        sound.run()

        # bot
        bot = Bot()
        bot.run()

    except Exception as e:
        if config.Debug: print(e)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    main()
    db.close()
    db.delete()
