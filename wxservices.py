import asyncio
import json
import contextvars as contextvars
import websockets
from comm import Comm

redisService = None
logger = None
wslist = {}

redisService_context = contextvars.ContextVar('redisService')
logger_context = contextvars.ContextVar('logger')
wslist_context = contextvars.ContextVar('wslist')


class ServerProtocol(websockets.WebSocketServerProtocol):

    async def process_request(self, path, request_headers):
        # print(request_headers)
        wskey = Comm.md5fun(hash(self))
        try:
            token = await redisService_context.get().getCache(wskey)
            logger_context.get().info(token)
            if token is None:
                if "Authorization" in request_headers:

                    authorization = Comm.rsa_decrypt(request_headers["Authorization"])
                    logger_context.get().info(authorization)
                    token = authorization.split('|')[0]
                    logger_context.get().info(token)
                    token_cache = await redisService_context.get().getCache("temp_user_token_%s" % token)

                    if token_cache is not None:
                        if token not in wslist_context.get():
                            wslist_context.get()[token] = self
                            await redisService_context.get().setCache(wskey, token)
                            logger_context.get().info("ws register:%s is successed" % (token))
                    else:
                        logger_context.get().info("ws register:%s is failed " % (token))
                        self.ws_server.close()
            else:
                logger_context.get().info("token:%s is exists" % token)

        except Exception as ex:
            logger_context.get().error(ex)
            self.ws_server.close()


class Master(object):

    def __init__(self, redis_service, logger, config):
        super(Master, self).__init__()
        self.__config = config
        self.__logger = logger
        self.__redisService = redis_service
        redisService_context.set(self.__redisService)
        logger_context.set(self.__logger)
        wslist_context.set({})

    async def echo_server(self, stop):
        await self.__redisService.connect(self.__config.redisconfig)
        asyncio.ensure_future(self.__notify_users())
        self.__logger.info("ws is starting...host:%s, port:%s " % (self.__config.host, self.__config.port))
        async with websockets.serve(self.__service, self.__config.host, self.__config.port,
                                    create_protocol=ServerProtocol):
            await stop

    async def __notify_users(self):
        ## {\"msgtype\":1, \"data\":[\"47f287b3330e69b1a1a4b3f352c93894\"]}
        ch = await self.__redisService.subscribe("wxmsg")
        async for msg in ch.iter():
            if msg is not None:
                msgstr = str(msg, encoding="utf-8")
                try:
                    msg = json.loads(msgstr)
                    if msg["msgtype"] in [1, 2]:
                        for token in msg["data"]:
                            if token in wslist_context.get():
                                await wslist_context.get()[token].send('{"msgtype":%d}' % msg["msgtype"])
                                self.__logger.info("ws send message:%s" % msgstr)
                except Exception as ex:
                    self.__logger.error("error notify_users:%s" % ex)

    async def __service(self, websocket, path):
        try:
            while True:
                message = await asyncio.gather(websocket.recv())
                self.__logger.info(message)

        except Exception as ex:
            self.__logger.error(ex)
        finally:
            websocket_key = Comm.md5fun(hash(websocket))
            token = await self.__redisService.getCache(websocket_key)
            if token is not None:
                if token in wslist_context.get():
                    del wslist_context.get()[token]
                self.__logger.info("ws unregister:%s" % token)
                await websocket.close()
                await self.__redisService.delCache(websocket_key)
