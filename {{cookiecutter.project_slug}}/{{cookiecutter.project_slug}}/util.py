import asyncio
import collections
import io
import logging
import subprocess
import sys
import typing
import datetime
import time

def get_logger(name: str):
    return logging.getLogger("hfcomstor.{}".format(name))

async def async_shell(
    cmd,
    stdout=None,
    stderr=None
):
    logger = get_logger("util.async_shell")

    if not isinstance(cmd, list):
        cmd = cmd.split(" ")

    if isinstance(cmd, list):
        cmd = str.join(" ", cmd)

    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.DEVNULL)

    stdout, stderr = await proc.communicate()

    return {
        "stdout": stdout,
        "stderr": stderr
    }

def dict_merge(d, u):
    for k, v in u.items():
        if isinstance(v, collections.abc.Mapping):
            d[k] = dict_merge(d.get(k, {}), v)
        else:
            d[k] = v
    return d

def dict_order(d: dict):
    def make_tuple(v):
        return (*v,) if isinstance(v, (list, dict)) else (v,)

    if isinstance(d, list):
        return sorted(map(dict_order, d), key=make_tuple)
    if isinstance(d, dict):
        return {k: dict_order(d[k]) for k in sorted(d)}
    return d

def intval(val: str):
    try:
        return int(''.join([n for n in val if n.isdigit()]))
    except:
        return 0

def str2dt(date_time_str, format="%Y-%m-%d %H:%M:%S"):
    return datetime.datetime.strptime(date_time_str, format).replace(tzinfo=datetime.timezone.utc)

def dt2str(date_time, format="%Y-%m-%d %H:%M:%S"):
    return date_time.strftime("%Y-%m-%d %H:%M:%S")

def dt2ut(date_time):
    if isinstance(date_time, datetime.datetime):
        return int(time.mktime(date_time.timetuple()))
    return date_time

def str_or_none(value):
    if value is None:
        return None
    elif len(value.strip()) == 0:
        return None
    return value

class Map(dict):
    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)
        for arg in args:
            if isinstance(arg, dict):
                for k, v in arg.items():
                    self[k] = v

        if kwargs:
            for k, v in kwargs.items():
                self[k] = v

    """
    Intercept attribute for better exception message
    def __getitem__(self, key):
        val = dict.__getitem__(self, key)
        return val
    """

    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        super(Map, self).__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        super(Map, self).__delitem__(key)
        del self.__dict__[key]
