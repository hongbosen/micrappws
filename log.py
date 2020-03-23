import datetime
import logging, logging.handlers
import os.path
import time


class LogOjbect(object):
    def __init__(self, INFO, logfilename):
        super(LogOjbect, self).__init__()
        self.__logger = logging.getLogger()
        self.__logger.setLevel(INFO)  # Log等级总开关
        self.__formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")

        #输出到文件
        # self.__log_path = os.path.dirname(os.getcwd()) + '/logs/'
        if logfilename is None or '/' not in logfilename:
            # self.__rq = time.strftime('%Y%m%d', time.localtime(time.time()))
            self.__log_path = os.path.dirname(os.path.abspath(__file__)) + '/logs/'
            self.__logfile = self.__log_path+'tempmicrappws.log'
        else:
            self.__logfile = logfilename
        # self.__fh = logging.FileHandler(self.__logfile, mode='a+')
        self.__fh = logging.handlers.TimedRotatingFileHandler(self.__logfile, when='midnight', interval=1,
                                                              backupCount=7,atTime=datetime.time(0, 0, 0, 0))
        self.__fh.setLevel(INFO)  # 输出到file的log等级的开关
        self.__fh.setFormatter(self.__formatter)
        self.__logger.addHandler(self.__fh)
        #输出到终端
        self.__ch = logging.StreamHandler()
        self.__ch.setLevel(INFO)  # 输出到终端的log等级的开关
        self.__ch.setFormatter(self.__formatter)
        self.__logger.addHandler(self.__ch)

    @property
    def logger(self):
        return self.__logger

