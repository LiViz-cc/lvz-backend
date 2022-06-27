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


def _generate_logger(name=__name__, console_level=logging.WARNING, file_level=logging.INFO):
    # create directory if not exists
    log_directory = os.path.abspath(os.path.join(
        os.path.dirname(__file__), os.pardir, "log"))
    if not os.path.isdir(log_directory):
        os.mkdir(log_directory)

    # create log file if not exists
    filename = "{}_log.csv".format(datetime.date.today())
    filepath = os.path.join(log_directory, filename)

    is_new_file = not os.path.exists(filepath)
    f = open(filepath, "a")
    if is_new_file:
        f.write('asctime,mills,levelname,filename,funcName,lineno,message\n')
    f.close()

    # Create a custom logger
    logger = logging.getLogger(name)

    # Create handlers
    c_handler = logging.StreamHandler()
    f_handler = logging.FileHandler(filepath)
    c_handler.setLevel(console_level)
    f_handler.setLevel(file_level)

    # Create formatters and add it to handlers
    c_format = logging.Formatter(
        '%(asctime)s - %(levelname)s\n  - %(filename)s - %(funcName)s - %(lineno)d\n  - %(message)s')
    f_format = logging.Formatter(
        '%(asctime)s,%(levelname)s,%(filename)s,%(funcName)s,%(lineno)d,%(message)s')
    c_handler.setFormatter(c_format)
    f_handler.setFormatter(f_format)

    # Add handlers to the logger
    logger.addHandler(c_handler)
    logger.addHandler(f_handler)

    logger.setLevel(min(console_level, file_level))

    # logger.warning('This is a warning')
    # logger.error('This is an error')

    return logger


_logger = _generate_logger()


def get_the_logger():
    # singleton pattern
    return _logger


class SilentLogger:
    '''
    A logger ignoring only `info`
    '''

    def __init__(self) -> None:
        self.logger = _generate_logger('SilentLogger')

    def info(self, *args, **kargs):
        pass

    def debug(self, *args, **kargs):
        self.logger.debug(*args, **kargs)

    def error(self, *args, **kargs):
        self.logger.error(*args, **kargs)


silent_logger = SilentLogger()
