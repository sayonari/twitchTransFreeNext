#!/usr/bin/env python
# -*- coding: utf-8 -*-

from playsound import playsound
import time
import threading
import queue

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