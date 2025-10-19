#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import threading
import queue
import os
import sys
import platform

# Check if we're on macOS
is_macos = platform.system() == 'Darwin'

# Nuitka/PyInstallerバイナリ実行時の検出
is_frozen = getattr(sys, 'frozen', False) or hasattr(sys, '__compiled__')

# macOS かつ バイナリ実行時は、playsoundを使わずafplayを直接使用
if is_macos and is_frozen:
    # afplayを使用するカスタム実装
    def playsound(sound_file, block=True):
        if not os.path.exists(sound_file):
            print(f"Sound file not found: {sound_file}")
            return

        cmd = f"afplay '{sound_file}'"
        if block:
            os.system(cmd)
        else:
            threading.Thread(target=os.system, args=(cmd,)).start()

    playsound_available = True
else:
    # 通常のPython実行時、またはmacOS以外の環境
    try:
        from playsound import playsound
        playsound_available = True
    except ImportError as e:
        playsound_available = False
        import_error = e

class Sound:
    def __init__(self, config):
        self.config = config
        self.sound_queue = queue.Queue()

    def run(self):
        if self.config.Debug: print("run, sound play thread...")
        thread_sound = threading.Thread(target=self.sound_play)
        thread_sound.start()

    def put(self, obj):
        self.sound_queue.put(obj)

    #####################################
    # !sound 音声再生スレッド -------------
    def sound_play(self):
        if not playsound_available:
            print("Sound playback is not available:")
            if 'import_error' in globals():
                print(import_error)
            return
            
        while True:
            q = self.sound_queue.get()
            if q is None:
                time.sleep(1)
            else:
                try:
                    playsound('./sound/{}.mp3'.format(q), True)
                except Exception as e:
                    print('sound error: [!sound] command can not play sound...')
                    if self.config.Debug: print(e.args)
