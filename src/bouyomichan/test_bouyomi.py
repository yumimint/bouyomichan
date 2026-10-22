import logging
from functools import partial
from time import sleep

from bouyomichan import getnowplaying, talk

logger = logging.getLogger(__package__)


def main():
    logging.basicConfig(
        level=logging.DEBUG, format="%(levelname)s : %(asctime)s : %(message)s"
    )

    if getnowplaying(timeout=0.1) is None:
        logger.warning("BouyomiChan has not available")

    speak = partial(talk, tone=100, speed=100)

    talk("棒読みちゃんテスト")
    speak("ゆっくり霊夢です", voice=1)
    speak("魔理沙だぜ", voice=2)

    voicez = [
        "デフォルト",
        "女性1 霊夢だよ",
        "女性2 魔理沙だぜ",
        "男性1",
        "男性2",
        "中性",
        "ロボット",
        "機械1",
        "機械2",
    ]
    for i, text in enumerate(voicez):
        speak(f"{i}番 {text}", voice=i)

    # _talk_daemonが動く猶予を与える

    sleep(5)


if __name__ == "__main__":
    main()
