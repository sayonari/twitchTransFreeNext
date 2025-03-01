#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gtts import gTTS
from playsound import playsound
from datetime import datetime
import time
import os
import queue
import threading
import asyncio
import openai

# 引入Edge TTS相关包
import edge_tts
import tempfile

class TTS:
    """
    TTS(Text To Speach)を取り扱うクラス
    putされた文面をスレッドで処理し、
    必要な加工を施した上で適切なタイミングで読み上げる
    """

    def __init__(self, config):
        self.config = config
        self.synth_queue = queue.Queue()
        # 支持的Edge TTS语音列表
        self.edge_tts_voices = {
            'zh-CN': 'zh-CN-XiaoxiaoNeural',   # 中文（普通话，女声）
            'zh-TW': 'zh-TW-HsiaoChenNeural',  # 中文（台湾，女声）
            'en': 'en-US-AriaNeural',         # 英语（美国，女声）
            'ja': 'ja-JP-NanamiNeural',       # 日语（女声）
            'ko': 'ko-KR-SunHiNeural',        # 韩语（女声）
            'fr': 'fr-FR-DeniseNeural',       # 法语（女声）
            'de': 'de-DE-KatjaNeural',        # 德语（女声）
            'es': 'es-ES-ElviraNeural',       # 西班牙语（女声）
            'ru': 'ru-RU-SvetlanaNeural',     # 俄语（女声）
            'pt': 'pt-BR-FranciscaNeural',    # 葡萄牙语（女声）
            'it': 'it-IT-ElsaNeural',         # 意大利语（女声）
        }

        # 从配置文件读取自定义语音设置
        self._load_custom_voices()

        # 默认语音
        self.default_voice = 'zh-CN-XiaoxiaoNeural'

    # 从配置文件加载自定义Edge TTS语音设置
    def _load_custom_voices(self):
        try:
            # 检查配置文件中是否有自定义的语音设置
            # 格式例如：EdgeTTS_Voice_ZhCN = "zh-CN-YunxiNeural"
            for attr in dir(self.config):
                if attr.startswith('EdgeTTS_Voice_'):
                    lang_key = attr.replace('EdgeTTS_Voice_', '')
                    # 将配置名称转换为语言代码，例如：ZhCN -> zh-CN
                    if lang_key == 'ZhCN':
                        lang_code = 'zh-CN'
                    elif lang_key == 'ZhTW':
                        lang_code = 'zh-TW'
                    else:
                        # 将驼峰形式转为小写，例如：En -> en
                        lang_code = lang_key.lower()

                    # 获取语音值
                    voice_value = getattr(self.config, attr)
                    # 更新语音字典
                    self.edge_tts_voices[lang_code] = voice_value
                    if self.config.Debug:
                        print(f"Custom Edge TTS voice for {lang_code}: {voice_value}")
        except Exception as e:
            print("Error loading custom Edge TTS voices:")
            if self.config.Debug: print(e)

    def put(self, text, lang, username=None):
        """
        将文本放入队列等待朗读

        Args:
            text: 要朗读的文本
            lang: 文本的语言
            username: 发言者用户名，如果不提供则不会读出用户名
        """
        self.synth_queue.put([text, lang, username])

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

    # 处理用户名，添加"说"字
    def format_with_username(self, text, lang, username):
        """
        根据配置添加用户名和连接词

        Args:
            text: 要朗读的文本
            lang: 文本的语言
            username: 发言者用户名

        Returns:
            处理后的带有用户名的文本
        """
        if not username or not hasattr(self.config, 'TTS_ReadUsername') or not self.config.TTS_ReadUsername:
            return text

        # 截断过长的用户名
        max_username_len = getattr(self.config, 'TTS_UsernameMaxLength', 10)
        if len(username) > max_username_len:
            username = username[:max_username_len]

        # 根据语言选择连接词
        say_word = self.config.TTS_SayWord  # 默认使用中文"说"

        # 英文环境
        if lang == 'en' or lang.startswith('en-'):
            say_word = getattr(self.config, 'TTS_SayWord_EN', 'says')
            return f"{username} {say_word}: {text}"

        # 日文环境
        elif lang == 'ja' or lang.startswith('ja-'):
            say_word = getattr(self.config, 'TTS_SayWord_JA', 'さん、')
            return f"{username}{say_word}{text}"

        # 默认中文环境或其他语言
        else:
            return f"{username}{say_word}：{text}"


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
        def play(text, tl, username=None):
            try:
                # 添加用户名
                if username and hasattr(self.config, 'TTS_ReadUsername') and self.config.TTS_ReadUsername:
                    text = self.format_with_username(text, tl, username)

                state = talker.Speak(text)
                if self.config.Debug: print(f"text '{text}' has dispatched to CeVIO.")
                state.Wait()
            except Exception as e:
                print('CeVIO error: TTS sound is not generated...')
                if self.config.Debug: print(e.args)
        return play
    
    def openai_tts(self, text, tl, username=None):
        try:
            # 添加用户名
            if username and hasattr(self.config, 'TTS_ReadUsername') and self.config.TTS_ReadUsername:
                text = self.format_with_username(text, tl, username)

            tts_file = './tmp/cnt_{}.mp3'.format(datetime.now().microsecond)
            response = openai.audio.speech.create(
                model=self.config.TTS_Model,
                voice=self.config.TTS_Voice,
                input=text
            )
            response.stream_to_file(tts_file)
            playsound(tts_file, True)
            os.remove(tts_file)
        except Exception as e:
            print('openai error: TTS sound is not generated...')
            if self.config.Debug: print(e.args)


    # gTTSを利用して
    # 音声合成 ＆ ファイル保存 ＆ ファイル削除
    # までを行う音声合成の実行関数。
    def gTTS_play(self, text, tl, username=None):
        try:
            # 添加用户名
            if username and hasattr(self.config, 'TTS_ReadUsername') and self.config.TTS_ReadUsername:
                text = self.format_with_username(text, tl, username)

            tts = gTTS(text, lang=tl)
            tts_file = './tmp/cnt_{}.mp3'.format(datetime.now().microsecond)
            if self.config.Debug: print('gTTS file: {}'.format(tts_file))
            tts.save(tts_file)
            playsound(tts_file, True)
            os.remove(tts_file)
        except Exception as e:
            print('gTTS error: TTS sound is not generated...')
            if self.config.Debug: print(e.args)

    # Edge TTS 文本转语音
    # 使用更自然的Microsoft Edge TTS实现
    def EdgeTTS_play(self, text, tl, username=None):
        try:
            # 添加用户名
            if username and hasattr(self.config, 'TTS_ReadUsername') and self.config.TTS_ReadUsername:
                text = self.format_with_username(text, tl, username)

            # 创建事件循环
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # 映射语言到Edge TTS语音
            voice = self.default_voice
            # 处理语言代码转换（将Google翻译语言代码转成Edge TTS支持的语言）
            lang_code = tl
            if lang_code.startswith('zh-'):
                lang_code = 'zh-CN' if lang_code == 'zh-cn' else 'zh-TW'
            elif len(lang_code) > 2:
                lang_code = lang_code[:2]  # 提取主要语言代码，如 'en-US' -> 'en'

            # 如果语言代码在支持列表中，使用对应的语音
            if lang_code in self.edge_tts_voices:
                voice = self.edge_tts_voices[lang_code]

            # 设置临时文件用于存储音频
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                tts_file = tmp_file.name

            if self.config.Debug: print(f'EdgeTTS using voice: {voice} for language: {tl}, file: {tts_file}')

            # 获取语音列表（仅在Debug模式下）
            if self.config.Debug and hasattr(self.config, 'Debug_EdgeTTS_Voices') and self.config.Debug_EdgeTTS_Voices:
                async def list_voices():
                    # 获取可用的语音列表
                    voices = await edge_tts.list_voices()
                    print("Available Edge TTS voices:")
                    for v in voices:
                        print(f" - {v['Name']}: {v['ShortName']} ({v['Locale']})")

                loop.run_until_complete(list_voices())

            # 生成语音文件
            async def generate_speech():
                communicate = edge_tts.Communicate(text, voice)
                await communicate.save(tts_file)

            # 运行异步任务
            loop.run_until_complete(generate_speech())

            # 播放音频
            playsound(tts_file, True)

            # 删除临时文件
            os.remove(tts_file)

        except Exception as e:
            print('EdgeTTS error: TTS sound is not generated...')
            if self.config.Debug: print(e.args)


    # どのTextToSpeechを利用するかをconfigから選択して再生用の関数を返す
    def Determine_TTS(self):
        kind = self.config.TTS_Kind.strip().upper()
        if kind == "CeVIO".upper():
            return self.CeVIO(self.config.CeVIO_Cast)
        elif kind == "EDGE".upper():
            return self.EdgeTTS_play
        elif kind == "OPENAI".upper():
            return self.openai_tts
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
                text = q[0]
                tl = q[1]
                username = q[2] if len(q) > 2 else None

                if self.config.Debug: print('debug in Voice_Thread')
                if self.config.Debug: print(f'tl: {tl}')
                if self.config.Debug: print(f'config.ReadOnlyTheseLang : {self.config.ReadOnlyTheseLang}')
                if self.config.Debug: print(f'tl not in config.ReadOnlyTheseLang : {tl not in self.config.ReadOnlyTheseLang}')

                # 「この言語だけ読み上げて」リストが空じゃなく，なおかつそのリストにに入ってなかったら無視
                if self.config.ReadOnlyTheseLang and (tl not in self.config.ReadOnlyTheseLang):
                    continue

                text = self.shorten_tts_comment(text)
                tts(text, tl, username)
