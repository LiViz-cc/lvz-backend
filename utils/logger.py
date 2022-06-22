import csv
import datetime
import io
import logging
import os

'''
Import example: from utils.logger import logger
or from utils.logger import silent_logger
'''


class CsvFormatter(logging.Formatter):
    def __init__(self):
        super().__init__()
        self.output = io.StringIO()
        self.writer = csv.writer(self.output, quoting=csv.QUOTE_ALL)

    def format(self, record):
        dt = datetime.datetime.now()
        # self.writer.writerow([dt.strftime('%Y-%m-%d'), dt.strftime('%H:%M:%S'),
        #                       record.levelname, record.name,  record.module, record.msg])
        self.writer.writerow(
            [dt.strftime('%Y-%m-%d'), dt.strftime('%H:%M:%S'), record.module, record.msg])
        data = self.output.getvalue()
        self.output.truncate(0)
        self.output.seek(0)
        return data.strip()


def get_logger():
    # create directory if not exists
    log_directory = os.path.abspath(os.path.join(
        os.path.dirname(__file__), os.pardir, "log"))
    if not os.path.isdir(log_directory):
        os.mkdir(log_directory)

    # create log file if not exists
    filename = "{}_log.csv".format(datetime.date.today())
    filepath = os.path.join(log_directory, filename)
    f = open(filepath, "a")
    f.close()

    # # Log file export
    # logging.basicConfig(level=logging.INFO,
    #                     filename=filepath,
    #                     datefmt='%Y/%m/%d %H:%M:%S')

    # # logging.basicConfig(level=logging.DEBUG,
    # #                     filename=filepath,
    # #                     datefmt='%Y/%m/%d %H:%M:%S',
    # #                     format='%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(module)s - %(message)s')

    # logger = logging.getLogger(__name__)

    # # Set file export format
    # logging.root.handlers[0].setFormatter(CsvFormatter())

    # # Logs export to concole
    # chlr = logging.StreamHandler()
    

    # # chlr.setLevel('DEBUG')
    # chlr.setLevel('INFO')
    # logger.addHandler(chlr)

    # # Set concole export format
    # format_concole = logging.Formatter('[%(levelname)s] %(message)s')
    # chlr.setFormatter(format_concole)

    # import logging

    # Create a custom logger
    logger = logging.getLogger(__name__)

    # Create handlers
    c_handler = logging.StreamHandler()
    f_handler = logging.FileHandler(filepath)
    c_handler.setLevel(logging.INFO)
    f_handler.setLevel(logging.INFO)

    # Create formatters and add it to handlers
    c_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(module)s - %(message)s')
    f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    c_handler.setFormatter(c_format)
    f_handler.setFormatter(f_format)

    # Add handlers to the logger
    logger.addHandler(c_handler)
    logger.addHandler(f_handler)

    logger.warning('This is a warning')
    logger.error('This is an error')

    return logger


logger = get_logger()


class SilentLogger:
    '''
    A logger ignoring only `info`
    '''

    def __init__(self, logger) -> None:
        self.logger = logger

    def info(self, *args, **kargs):
        pass

    def debug(self, *args, **kargs):
        self.logger.debug(*args, **kargs)

    def error(self, *args, **kargs):
        self.logger.error(*args, **kargs)


silent_logger = SilentLogger(logger)
