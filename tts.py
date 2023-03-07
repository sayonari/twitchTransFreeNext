#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gtts import gTTS
from playsound import playsound
from datetime import datetime
import time
import os
import queue
import threading

class TTS:
    """
    TTS(Text To Speach)を取り扱うクラス
    putされた文面をスレッドで処理し、
    必要な加工を施した上で適切なタイミングで読み上げる
    """

    def __init__(self, config):
        self.config = config
        self.synth_queue = queue.Queue()

    def put(self, text, lang):
        self.synth_queue.put([text, lang])

    def run(self):
        if self.config.Debug: print("run, voice synth thread...")
        if self.config.TTS_In or self.config.TTS_Out:
            thread_voice = threading.Thread(target=self.voice_synth)
            thread_voice.start()

    # TTS向けのコメントをコンフィグに応じて短縮する
    # もし長過ぎる文面だった場合、省略し、末尾に省略を意味する読み上げを追加する。
    # そうでない場合は、もとのテキストのままとなる。
    def shorten_tts_comment(self, comment):
        maxlen = self.config.TTS_TextMaxLength
        if maxlen == 0:
            return comment
        if len(comment) <= maxlen:
            return comment
        return f"{comment[0:maxlen]} {self.config.TTS_MessageForOmitting}"


    # CeVIOを呼び出すための関数を生成する関数
    # つまり cast 引数を与えることで、この関数から
    # 該当のCeVIOキャストにより音声再生を行える関数が帰ってきます。
    # 例("さとうささら"に"ささらちゃん読み上げて！"を読ませる呼び出し):
    #   f = CeVIO("さとうささら")
    #   f("ささらちゃん読み上げて！", "ja")
    # TODO: ただし第二引数(tl)は現状実装されていないため、
    # 該当キャストのデフォルト言語で読み上げは行われます。
    def CeVIO(self, cast):
        # CeVIOとそれを呼び出すためのWin32COMの仕組みはWindowsにしかありません。
        # そこでこのCeVIO関数内にimport実行を閉じることで
        # ライブラリの不在を回避して他環境と互換させます。
        import win32com.client
        import pythoncom
        pythoncom.CoInitialize()
        cevio = win32com.client.Dispatch("CeVIO.Talk.RemoteService2.ServiceControl2")
        cevio.StartHost(False)
        talker = win32com.client.Dispatch("CeVIO.Talk.RemoteService2.Talker2V40")
        talker.Cast = cast
        # in this routine, we will omit tl because CeVIO doesn't support language paramter.
        def play(text, _):
            try:
                state = talker.Speak(text)
                if self.config.Debug: print(f"text '{text}' has dispatched to CeVIO.")
                state.Wait()
            except Exception as e:
                print('CeVIO error: TTS sound is not generated...')
                if self.config.Debug: print(e.args)
        return play


    # gTTSを利用して
    # 音声合成 ＆ ファイル保存 ＆ ファイル削除
    # までを行う音声合成の実行関数。
    def gTTS_play(self, text, tl):
        try:
            tts = gTTS(text, lang=tl)
            tts_file = './tmp/cnt_{}.mp3'.format(datetime.now().microsecond)
            if self.config.Debug: print('gTTS file: {}'.format(tts_file))
            tts.save(tts_file)
            playsound(tts_file, True)
            os.remove(tts_file)
        except Exception as e:
            print('gTTS error: TTS sound is not generated...')
            if self.config.Debug: print(e.args)


    # どのTextToSpeechを利用するかをconfigから選択して再生用の関数を返す
    def Determine_TTS(self):
        kind = self.config.TTS_Kind.strip().upper()
        if kind == "CeVIO".upper():
            return self.CeVIO(self.config.CeVIO_Cast)
        else:
            return self.gTTS_play


    # 音声合成(TTS)の待ち受けスレッド
    # このスレッドにより各音声合成(TTS)が起動して音声読み上げされます。
    # このスレッドに対するメッセージ入力は
    # グローバルに定義されたsynth_queueを介して行います。
    def voice_synth(self):
        tts = self.Determine_TTS()
        while True:
            q = self.synth_queue.get()
            if q is None:
                time.sleep(1)
            else:
                text    = q[0]
                tl      = q[1]

                if self.config.Debug: print('debug in Voice_Thread')
                if self.config.Debug: print(f'config.ReadOnlyTheseLang : {self.config.ReadOnlyTheseLang}')
                if self.config.Debug: print(f'tl not in config.ReadOnlyTheseLang : {tl not in self.config.ReadOnlyTheseLang}')

                # 「この言語だけ読み上げて」リストが空じゃなく，なおかつそのリストにに入ってなかったら無視
                if self.config.ReadOnlyTheseLang and (tl not in self.config.ReadOnlyTheseLang):
                    continue

                text = self.shorten_tts_comment(text)
                tts(text, tl)
