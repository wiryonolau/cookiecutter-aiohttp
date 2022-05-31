import asyncio
import sys
import typing
import abc
import copy
import json
import datetime
import traceback

from {{ cookiecutter.project_slug }}.util import get_logger, dt2str, str2dt

class AbstractAsyncioFuture(abc.ABC):
    def __init__(self, *args, **kwargs):
        # Task to cleanup
        self._tasks: list = []
        self._logger = get_logger(self.__class__.__name__)
        self._init(*args, **kwargs)

    def _init(self, *args, **kwargs):
        pass

    @typing.final
    def start(self) -> None:
        self._pre_start()
        for t in self._tasks:
            t["task"] = asyncio.ensure_future(t["task"](*t["args"], **t["kwargs"]))
        self._post_start()

    def _pre_start(self) -> None:
        pass

    def _post_start(self) -> None:
        pass

    def _add_task(self, task: typing.Callable, label: str=None, *args, **kwargs) -> None:
        self._tasks.append({
            "task" : task,
            "label" : label,
            "args" : args,
            "kwargs": kwargs
        })

    def _has_task(self, label:str) -> bool:
        return True if len([t for t in self._tasks if t.get("label") == label]) > 0 else False

    async def _stop_task(self, label: str, remove: bool=False, timeout: int=5) -> None:
        if len(self._tasks) > 0:
            try:
                task = [t.get("task") for t in self._tasks if t.get("label") == label][0]
                task.cancel()
                await asyncio.sleep(1)

                if remove is True:
                    self._tasks = [t for t in self._tasks if t.get("label") != label]
            except:
                self._logger.debug(sys.exc_info())

    @typing.final
    async def shutdown(self, timeout: int=5) -> None:
        await self._pre_shutdown()
        for t in self._tasks:
            t.get("task").cancel()
            await asyncio.sleep(1)
        await self._post_shutdown()

    async def _pre_shutdown(self) -> None:
        pass

    async def _post_shutdown(self) -> None:
        pass


class AbstractViewHelper(abc.ABC):
    def __init__(self, *args, **kwargs):
        self._logger = get_logger(self.__class__.__name__)
        self._init(*args, **kwargs)

    def _init(self, *args, **kwargs):
        pass

    def __call__(self):
        return ""

class AbstractHttpAction(abc.ABC):
    def __init__(self, *args, **kwargs):
        self._logger = get_logger(self.__class__.__name__)
        self._init(*args, **kwargs)

    def _init(self, *args, **kwargs):
        pass


class AbstractMiddleware(abc.ABC):
    def __init__(self, *args, **kwargs):
        self._logger = get_logger(self.__class__.__name__)
        self._init(*args, **kwargs)

    def _init(self, *args, **kwargs):
        pass

class AbstractService(abc.ABC):
    def __init__(self, *args, **kwargs):
        self._logger = get_logger(self.__class__.__name__)
        self._init(*args, **kwargs)

    def _init(self, *args, **kwargs):
        pass

class AbstractProvider(abc.ABC):
    def __init__(self, *args, **kwargs):
        self._logger = get_logger(self.__class__.__name__)
        self._init(*args, **kwargs)

    def _init(self, *args, **kwargs):
        pass

class AbstractRepository(abc.ABC):
    def __init__(self, db, *args, **kwargs):
        self._db = db
        self._logger = get_logger(self.__class__.__name__)
        self._init(*args, **kwargs)

    def _init(self, *args, **kwargs):
        pass

class AbstractModel(abc.ABC):
    def __getattr__(self, name):
        if "get_" + name in dir(self.__class__):
            return getattr(self, "get_" + name)(v)
        return self.__dict__.get(name, self.__dict__.get("_" + name, None))

    def populate(self, data={}):
        try:
            for k, v in data.items():
                if "_" + k not in self.__dict__:
                    continue

                if k == "logger" :
                    continue

                if isinstance(getattr(self, "_" + k), AbstractModel):
                    getattr(self, "_" + k).populate(v)
                elif "set_" + k in dir(self.__class__):
                    getattr(self, "set_" + k)(v)
                else:
                    setattr(self, "_" + k, v)
        except:
            print(traceback.print_exc())

    def dict(self, date_to_string=False):
        d = {}
        for k, v in self.__dict__.items():
            if "__" in k:
                continue
            if k == "_logger" :
                continue
            if isinstance(v, AbstractModel):
                d[k.lstrip("_")] = v.dict()
            elif isinstance(v, datetime.datetime) and date_to_string:
                d[k.lstrip("_")] = dt2str(v)
            else:
                d[k.lstrip("_")] = v
        return d

    def json(self):
        return json.dumps(self.dict(date_to_string=True))
