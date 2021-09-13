# bouyomichan
# Text to speech interface for BouyomiChan via socket.
import enum
import queue
import socket
import struct
import threading

DEFAULT_HOST = ('localhost', 50001)

_talk_q = queue.Queue()


class Cmd(enum.IntEnum):
    Talk = 0x0001
    Pause = 0x0010
    Resume = 0x0020
    Skip = 0x0030
    Clear = 0x0040
    GetPause = 0x0110
    GetNowPlaying = 0x0120
    GetTaskCount = 0x0130


def talk(text, voice=None, volume=None, speed=None, tone=None, host=None):
    """読み上げる"""
    _talk_q.put((text, voice, volume, speed, tone, host))


def _talk_daemon():
    while True:
        text, voice, volume, speed, tone, host = _talk_q.get()
        cmdid = Cmd.Talk
        voice = voice or 0
        volume = volume or -1
        speed = speed or -1
        tone = tone or -1
        code = 0  # 0:UTF-8, 1:Unicode, 2:Shift-JIS
        message = bytes(text, "utf-8")
        length = len(message)
        data = struct.pack("<hhhhhbL", cmdid, speed, tone,
                           volume, voice, code, length) + message
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect(host or DEFAULT_HOST)
                sock.sendall(data)
        except socket.error:  # 棒読みちゃんが起動していない
            while not _talk_q.empty():
                _talk_q.get_nowait()


def _cmd(host, cmdid: int, res_len=0):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect(host or DEFAULT_HOST)
            sock.sendall(struct.pack("<h", cmdid))
            if res_len > 0:
                buf = sock.recv(res_len)
                return int.from_bytes(buf, "little")

    except socket.error:
        return None

    return None


def pause(host=None):
    """一時停止する"""
    return _cmd(host, Cmd.Pause)


def resume(host=None):
    """一時停止を解除する"""
    return _cmd(host, Cmd.Resume)


def skip(host=None):
    """現在の行をスキップして次の行へ"""
    return _cmd(host, Cmd.Skip)


def clear(host=None):
    """全ての行をキャンセルする"""
    return _cmd(host, Cmd.Clear)


def getpause(host=None):
    """一時停止中かどうかを取得する"""
    return _cmd(host, Cmd.GetPause, 1)


def getnowplaying(host=None):
    """音声再生中かどうかを取得する"""
    return _cmd(host, Cmd.GetNowPlaying, 1)


def gettalktaskcount(host=None):
    """残りのタスク数を取得する"""
    return _cmd(host, Cmd.GetTaskCount, 4)


_talkth = threading.Thread(target=_talk_daemon, daemon=True)
_talkth.start()

if __name__ == '__main__':
    import time

    # talk("棒読みちゃんテスト")
    # talk("three, two, one, zero!")

    def fizzbuzz(a, b):
        for i in range(a, b + 1):
            s = '馬' if (i % 3) == 0 else ''
            s += '鹿' if (i % 5) == 0 else ''
            s = str(i) if s == '' else s
            yield s
    talk(' '.join(fizzbuzz(1, 100)), speed=100, voice=1, volume=100)
    time.sleep(1)  # _talk_daemonが動く猶予を与える
