# bouyomichan
# Text to speech interface for BouyomiChan via http.
import json
import queue
import threading
import urllib.request
from urllib.error import URLError

DEFAULT_HOST = 'localhost:50080'
_talk_q = queue.Queue()


def talk(text, voice=None, volume=None, speed=None, tone=None, host=None):
    """読み上げる"""
    _talk_q.put((text, voice, volume, speed, tone, host))


def _talk_daemon():
    while True:
        text, voice, volume, speed, tone, host = _talk_q.get()
        text = urllib.parse.quote(text)
        post = len(text) >= 1000  # textが長すぎるときはPOSTメソッドを使う
        host = DEFAULT_HOST if host is None else host
        params = {}
        if post:
            data = f"text={text}".encode("ascii")
        else:
            params["text"] = text
        if voice is not None:
            params["voice"] = voice
        if volume is not None:
            params["volume"] = volume
        if speed is not None:
            params["speed"] = speed
        if tone is not None:
            params["tone"] = tone
        q = "&".join(map(lambda x: f"{x[0]}={str(x[1])}", params.items()))
        url = f'http://{host}/talk?{q}'
        try:
            if post:
                # POSTするとparamsが反映されない?
                req = urllib.request.Request(url, data)
            else:
                req = urllib.request.Request(url)
            urllib.request.urlopen(req)
        except URLError:  # 棒読みちゃんが起動していない
            while not _talk_q.empty():
                _talk_q.get_nowait()


def _cmd(command, host=None):
    host = DEFAULT_HOST if host is None else host
    url = f'http://{host}/{command}'
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as res:
        obj = json.load(res)
    vals = list(obj.values())
    if vals:
        return vals[0] if len(vals) == 1 else vals


def pause(host=None):
    """一時停止する"""
    try:
        _cmd("pause", host)
    except URLError:
        pass


def resume(host=None):
    """一時停止を解除する"""
    try:
        _cmd("resume", host)
    except URLError:
        pass


def skip(host=None):
    """現在の行をスキップして次の行へ"""
    try:
        _cmd("skip", host)
    except URLError:
        pass


def clear(host=None):
    """全ての行をキャンセルする"""
    try:
        _cmd("clear", host)
    except URLError:
        pass


def getpause(host=None):
    """一時停止中かどうかを取得する"""
    try:
        return _cmd("getpause", host)
    except URLError:
        return None


def getnowplaying(host=None):
    """音声再生中かどうかを取得する"""
    try:
        return _cmd("getnowplaying", host)
    except URLError:
        return None


def getnowtaskid(host=None):
    """現在のタスク番号を取得する"""
    try:
        return _cmd("getnowtaskid", host)
    except URLError:
        return None


def gettalktaskcount(host=None):
    """残りのタスク数を取得する"""
    try:
        return _cmd("gettalktaskcount", host)
    except URLError:
        return None


def getvoicelist(host=None):
    """利用可能な音声合成エンジンの一覧を取得する"""
    try:
        return _cmd("getvoicelist", host)
    except URLError:
        return None


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
