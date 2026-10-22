import enum
import logging
import queue
import socket
import struct
import threading

DEFAULT_HOST = ("localhost", 50001)

logger = logging.getLogger(__name__)


class Cmd(enum.IntEnum):
    Talk = 0x0001
    Pause = 0x0010
    Resume = 0x0020
    Skip = 0x0030
    Clear = 0x0040
    GetPause = 0x0110
    GetNowPlaying = 0x0120
    GetTaskCount = 0x0130


def talk(text: str, **kwargs):
    """Read aloud the text.

    Parameters
    ----------
    text : str
    speed : int  default=-1 (50-300)
    tone : int   default=-1 (50-200)
    volume : int default=-1 (0-100)
    voice : int  default=0 (1-8: AquesTalk, 10001-: SAPI5)
    timeout : float
        timeout for socket
    host : tuple
        address to connect

    Raises
    ------
        socket.error
    """
    if hasattr(talk, "q"):
        q: queue.Queue = talk.q
    else:
        q = queue.Queue()
        talk.q = q  # ty: ignore[unresolved-attribute]
        threading.Thread(target=lambda: _talk_daemon(q), daemon=True).start()

    q.put((text, kwargs))


def _talk_daemon(q: queue.Queue):
    logger.debug("_talk_daemon started")
    while True:
        text, kwargs = q.get()
        try:
            _send_talk_command(text, **kwargs)
        except OSError:
            while not q.empty():
                q.get_nowait()
        except Exception as e:
            logger.exception(e)  # noqa: TRY401


def _send_talk_command(text: str, **kwargs):
    data = _make_talk_data(text, **kwargs)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        host = kwargs.get("host", DEFAULT_HOST)
        timeout = kwargs.get("timeout")
        if timeout is not None:
            sock.settimeout(timeout)
        sock.connect(host)
        sock.sendall(data)

    if logger.isEnabledFor(logging.DEBUG):
        if len(text) > 40:
            text = text[:40] + "..."
        logger.debug(text + " " + str(kwargs))


def _make_talk_data(text: str, **kwargs) -> bytes:
    message = bytes(text, "utf-8")
    code = 0  # 0:UTF-8, 1:Unicode, 2:Shift-JIS
    data = struct.pack(
        "<hhhhhbL",
        Cmd.Talk,
        kwargs.get("speed", -1),
        kwargs.get("tone", -1),
        kwargs.get("volume", -1),
        kwargs.get("voice", 0),
        code,
        len(message),
    )
    data += message
    return data


def _send_command(host, cmdid: Cmd, timeout):
    """Send command to bouyomichan.

    Returns
    -------
    int : result code
    None : socket error
    """
    host = host or DEFAULT_HOST
    data = struct.pack("<h", cmdid)
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            if timeout is not None:
                sock.settimeout(timeout)
            sock.connect(host)
            sock.sendall(data)
            buf = sock.recv(4)
    except OSError as e:
        logger.error(e)
        return None

    return int.from_bytes(buf, "little")


def pause(*, host=None, timeout=None):
    """Pauses audio playback.

    Returns
    -------
    0 : success
    None : socket error
    """
    return _send_command(host, Cmd.Pause, timeout)


def resume(*, host=None, timeout=None):
    """Release the pause.

    Returns
    -------
    0 : success
    None : socket error
    """
    return _send_command(host, Cmd.Resume, timeout)


def skip(*, host=None, timeout=None):
    """Skip the current line and move on to the next line.

    Returns
    -------
    0 : success
    None : socket error
    """
    return _send_command(host, Cmd.Skip, timeout)


def clear(*, host=None, timeout=None):
    """Cancel all lines.

    Returns
    -------
    0 : success
    None : socket error
    """
    return _send_command(host, Cmd.Clear, timeout)


def getpause(*, host=None, timeout=None):
    """Get if it is paused.

    Returns
    -------
    0 : not paused
    1 : paused
    None : socket error
    """
    return _send_command(host, Cmd.GetPause, timeout)


def getnowplaying(*, host=None, timeout=None):
    """Get if the audio is playing.

    Returns
    -------
    0 : not playing
    1 : playing
    None : socket error
    """
    return _send_command(host, Cmd.GetNowPlaying, timeout)


def gettalktaskcount(*, host=None, timeout=None):
    """Get the number of remaining tasks.

    Returns
    -------
    int
    None : socket error
    """
    return _send_command(host, Cmd.GetTaskCount, timeout)
