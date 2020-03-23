import asyncio
import json
import logging
import signal
import websockets
from comm import Comm
from config import get_config
from log import LogOjbect
from redisservice import RedisService

# logging.basicConfig(level=logging.DEBUG)

redisService = None
logger = None
wslist = {}


class ServerProtocol(websockets.WebSocketServerProtocol):

    async def process_request(self, path, request_headers):
        print(request_headers)
        try:
            wskey = Comm.md5fun(hash(self))
            token = await redisService.getCache(wskey)
            if token is None:
                if "Authorization" in request_headers:
                    Authorization = Comm.rsa_decrypt(request_headers["Authorization"])
                    token = Authorization.split('|')[0]
                    tokenexists = await redisService.getCache("temp_user_token_%s" % token)
                    if tokenexists is not None:
                        await redisService.setCache(wskey, token)
                        wslist[token] = self
                        logger.info("ws register:%s " % (token))
                    else:
                        await self.close_connection()
        except Exception as ex:
            logger.info(ex)
            await self.close_connection()


class Master(object):
    def __init__(self, redisService, logger, config):
        super(Master, self).__init__()
        self.__redis_Service = redisService
        self.__config = config
        self.__logger = logger

    async def echo_server(self, stop):
        await redisService.connect(self.__config.redisconfig)
        asyncio.ensure_future(self.notify_users())
        # asyncio.ensure_future(self.auto_notify_users())
        self.__logger.info("ws is starting... port:%s " % self.__config.port)
        async with websockets.serve(self.service, self.__config.host, self.__config.port, create_protocol=ServerProtocol):
            await stop

    async def notify_users(self):
        ## {"msgtype":1, "data":["47f287b3330e69b1a1a4b3f352c93894"]}
        ## {\"msgtype\":1, \"data\":[\"47f287b3330e69b1a1a4b3f352c93894\"]}
        ch = await self.__redis_Service.subscribe("wxmsg")
        async for msg in ch.iter():
            if msg is not None:
                msgstr = str(msg, encoding="utf-8")
                print(msgstr)
                try:
                    msg = json.loads(msgstr)
                    if msg["msgtype"] in [1, 2]:
                        for token in msg["data"]:
                            if token in wslist:
                                await wslist[token].send('{"msgtype":%d}' % msg["msgtype"])
                                self.__logger.info("ws send message:%s" % msgstr)

                except Exception as ex:
                    self.__logger.error("notify_users:%s" % ex)

    async def service(self, websocket, path):
        try:
            while True:
                message = await asyncio.gather(websocket.recv())
                self.__logger.info(message)
                asyncio.sleep(3)
                await wslist["4a464abfcb6794cce6d64be2184e750a"].send('{"msgtype":1}')
        except Exception as ex:
            self.__logger.error(ex)
        finally:
            websocket_key = Comm.md5fun(hash(websocket))
            token = await asyncio.gather(self.__redis_Service.getCache(websocket_key))
            if token[0] is not None:
                token = token[0]
                await asyncio.gather(self.__redis_Service.delCache(websocket_key))
                if token in wslist:
                    del wslist[token]
                self.__logger.info("ws unregister:%s" % token)
                await websocket.close_connection()


if __name__ == "__main__":

    logger = LogOjbect(logging.DEBUG).logger

    loop = asyncio.get_event_loop()

    stop = asyncio.Future()

    # loop.add_signal_handler(signal.SIGINT, stop.set_result, None)
    #
    # loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)
    config = get_config("Test")

    redisService = RedisService(loop)

    master = Master(redisService, logger, config)

    loop.run_until_complete(master.echo_server(stop))