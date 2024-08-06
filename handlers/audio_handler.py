#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import wave
import pyaudio
import threading

class AudioPlayer:
    """
    音频播放操作
    """
    def __init__(self, file_path):
        self.file_path = file_path
        self.wav_file = None
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.is_playing = False
        self.thread = None

    def open_file(self):
        """
        打开音频文件
        """
        self.wav_file = wave.open(self.file_path, 'rb')

    def setup_stream(self):
        """
        打开音频流
        """
        self.stream = self.p.open(format=self.p.get_format_from_width(self.wav_file.getsampwidth()),
                                  channels=self.wav_file.getnchannels(),
                                  rate=self.wav_file.getframerate(),
                                  output=True)

    def play(self):
        """
        播放音频
        :return:
        """
        if self.is_playing:
            return

        self.is_playing = True
        self.thread = threading.Thread(target=self._play_audio)
        self.thread.start()

    def _play_audio(self):
        self.open_file()
        self.setup_stream()

        data = self.wav_file.readframes(1024)
        while data and self.is_playing:
            self.stream.write(data)
            data = self.wav_file.readframes(1024)

        self.close()

    def pause(self):
        """
        暂停
        """
        self.is_playing = False

    def resume(self):
        """
        继续
        """
        if not self.is_playing:
            self.is_playing = True
            self.thread = threading.Thread(target=self._play_audio)
            self.thread.start()

    def stop(self):
        """
        停止
        """
        self.is_playing = False
        self.close()

    def close(self):
        """
        关闭音频流
        """
        if self.stream is not None:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
        if self.wav_file is not None:
            self.wav_file.close()
            self.wav_file = None
        self.p.terminate()


# 使用示例
if __name__ == "__main__":
    player = AudioPlayer(r"C:\Users\panwy\Desktop\小立管家关灯.wav")  # 替换为你的 WAV 文件路径
    player.play()
