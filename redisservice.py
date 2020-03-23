import aioredis
from aioredis import Channel


class RedisService(object):

    def __init__(self, loop):
        super(RedisService, self).__init__()
        # self.redis = StrictRedis(host='192.168.88.184', port=6379, db=10)
        self.__redisconn = None
        self.__loop = loop

    async def connect(self, redisconfig):
        self.__redisconn = await aioredis.create_redis_pool(redisconfig, loop=self.__loop)

    async def subscribe(self, channelname):

        channel = Channel(channelname, is_pattern=False, loop=self.__loop)

        await self.__redisconn.subscribe(channel)

        return self.__redisconn.channels[channelname]

    async def setCache(self, key, value, expire=3600*24*7):
        # self.redisconn.set(key, value, ex=expire)
        return await self.__redisconn.set(key, value, expire=expire)

    async def getCache(self, key):
        return await self.__redisconn.get(key, encoding="utf-8")

    async def delCache(self, key):
        return await self.__redisconn.delete(key)
