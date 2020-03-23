import logging


class Config(object):
    def __init__(self):
        super(Config, self).__init__()
        self.__host = "0.0.0.0"
        self.__port = 3025
        self.__redisconfig = 'redis://192.168.88.184:6379/9?encoding=utf-8'
        self.__logpath = None
        self.__loglevel = logging.DEBUG

    @property
    def host(self)->str:
        return self.__host

    @host.setter
    def host(self, host: str):
        self.__host = host

    @property
    def port(self)->int:
        return self.__port

    @port.setter
    def port(self, port: int):
        self.__port = port

    @property
    def redisconfig(self):
        return self.__redisconfig

    @redisconfig.setter
    def redisconfig(self, redisconfig):
        self.__redisconfig = redisconfig

    @property
    def logpath(self):
        return self.__logpath

    @logpath.setter
    def logpath(self, logpath):
        self.__logpath = logpath

    @property
    def loglevel(self):
        return self.__loglevel

    @loglevel.setter
    def loglevel(self, loglevel):
        self.__loglevel = loglevel


class DevConfig(Config):
    def __init__(self):
        super(DevConfig, self).__init__()
        self.port = 9191


class TestConfig(Config):
    def __init__(self):
        super(TestConfig, self).__init__()


class ProdConfig(Config):
    def __init__(self):
        super(ProdConfig, self).__init__()
        self.host = "127.0.0.1"
        self.port = 9191
        self.redisconfig = 'redis://127.0.0.1:16379/0?encoding=utf-8'
        self.logpath = "/home/www/logs/tempwxmicrappws/ws/tempmicrappws.log"
        self.loglevel = logging.INFO


def get_config(env):
    config_dict = {"Dev": DevConfig(), "Test": TestConfig(), "Prod": ProdConfig()}
    return config_dict[env]
