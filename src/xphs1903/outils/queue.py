from collections.abc import Callable
from queue import Queue
from typing import Self


class FileBase[A](Queue):
    def __init__(
        self,
        maxsize: int = 0,
        _cls: type[A] | Callable[..., A] = lambda x: x,
        aval: list[Self] | None = None,
    ) -> None:
        self._cls: type[A] = _cls
        self._aval: list[Self] = [] if aval is None else aval
        super().__init__(maxsize=maxsize)

    def _avaliser(self, fct: str, *args: Any, **kargs: Any) -> None:
        _file: Self
        for _file in self._aval:
            fct: Callable[..., None] = getattr(_file, fct)
            fct(*args, **kargs)

    def put(
        self, item: A, block: bool = True, timeout: float | None = None
    ) -> None:
        item: A = self._cls(item)
        try:
            super().put(item, block=block, timeout=timeout)
        except Full, ShutDown:
            raise
        else:
            self._avaliser('put', item)

    def put_nowait(self, item: A) -> None:
        self.put(item, block=False)

    def shutdown(self, immediate: bool = False) -> None:
        self._avaliser('shutdown', immediate=immediate)
        super().shutdown()

    def join(self) -> None:
        self._avaliser('join')
        super().join()

    def envoyer_à(self, autre: Self) -> None:
        self._aval.append(autre)

    def recevoir_de(self, autre: Self) -> None:
        autre.envoyer_à(self)

    def get(self, block: bool = True, timeout: float | None = None) -> A:
        return super().get(block, timeout)

    def get_nowait(self) -> A:
        return super().get_nowait()


def file[A](_cls: type[A]) -> type[FileBase]:

    class _Q[A](FileBase):
        def __init__(
            self, maxsize: int = 0, aval: list[FileBase[A]] | None = None
        ) -> None:
            super().__init__(maxsize, _cls, aval)

    return _Q


FileStr = file(str)
FileBytes = file(bytes)
