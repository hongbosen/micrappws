import asyncio
import platform
import signal

from config import get_config
from log import LogOjbect
from redisservice import RedisService
from wxservices import Master


class Application(object):
    def __init__(self):
        super(Application, self).__init__()

    def run(self, host: str="", port: int=0, env: str=""):

        if env is None or len(env) == 0:
            raise Exception("evn is not None")

        config = get_config(env)

        if len(host) > 0 or host is not None:
            config.host = host

        if port != 0:
            config.port = port

        logger = LogOjbect(config.loglevel, config.logpath).logger

        loop = asyncio.get_event_loop()

        stop = asyncio.Future()

        sys_type = platform.system()

        if sys_type == "Linux":
            loop.add_signal_handler(signal.SIGINT, stop.set_result, None)

            loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)

        master = Master(RedisService(loop), logger, config)

        loop.run_until_complete(master.echo_server(stop))
