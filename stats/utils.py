from datetime import datetime


def read_file(filename):
    return open(filename).read().strip()


def get_datetime(fmt="%Y%m%d%H%M"):
    return datetime.strftime(datetime.now(), fmt)
