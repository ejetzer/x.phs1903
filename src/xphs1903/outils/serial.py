# (c) Copyright 2026 Émile Jetzer. All Rights Reserved.
"""Utilitaires de communication série.

"""
import logging
import queue
import threading
import typing

import serial

__logger = logging.getLogger(__name__)
__logger.addHandler(logging.NullHandler())

if typing.TYPE_CHECKING:
    from types import TracebackType
    from typing import Self

"""Valeurs permises pour les débits de communication."""
type BaudRateType = typing.Literal(9600, 115200, 1000000)


class LigneSerie:
    """Classe de lien série."""
    __logger = logging.getLogger(f'{__name__}.LigneSerie')
    __logger.addHandler(logging.NullHandler())

    def __init__(
        self,
        port: str = 'loop://',
        baudrate: BaudRateType = 115_200,
        *,
        stop_event: threading.Event | None = None,
    ) -> None:
        thread_name = str(port) if port is not None else None

        self.__thread: threading.Thread = threading.Thread(
            group=None,
            target=self.__run,
            name=f'{thread_name}',
            daemon=None,
            context=None,
        )
        self.__logger.debug('%s', self.__thread)

        self.__serial: serial.Serial = serial.serial_for_url(
            port, do_not_open=True
        )
        self.__serial.baudrate = baudrate
        self.__serial.timeout = 1.0
        self.__logger.debug('%s', self.__serial)

        self.__input: queue.Queue = queue.Queue()
        self.__logger.debug('%s', self.__input)
        self.__output: queue.Queue = queue.Queue()
        self.__logger.debug('%s', self.__output)

        self.__arret: threading.Event = (
            threading.Event() if stop_event is None else stop_event
        )
        self.__logger.debug('%s', self.__arret)

        self.__loquet: threading.Lock = threading.Lock()
        self.__logger.debug('%s', self.__loquet)

    def print(
        self, data: str | list[dict[str, str]], *, end: str = '\n'
    ) -> None:
        self.__logger.debug('%s (%s)', repr(data), type(data))
        if isinstance(data, list):
            self.__logger.debug('data is list')
            if all(isinstance(x, dict) for x in data):
                self.__logger.debug('data is list[dict]')
                if all(all(isinstance(x, str) for x in d) for d in data):
                    self.__logger.debug('data is list[dict[str]]')
                    data = '\n'.join(
                        '\t'.join(f'{k}:{v}' for k, v in d.items())
                        for d in data
                    )

        if isinstance(data, str):
            self.__logger.debug('Queueing %r', data)
            self.__input.put((data + end).encode('utf-8'))
        else:
            msg: str = f'Expected {str} or {list[dict]} but got {type(data)}.'
            raise TypeError(msg)

    def __run(self) -> None:
        self.__logger.debug('')
        while True:
            if self.__arret.is_set():
                self.__logger.debug('%s', self.__arret)
                return

            if not self.__input.empty() and not self.__serial.out_waiting:
                try:
                    cmd: bytes = self.__input.get()
                    self.__logger.debug('%r', cmd)
                except queue.ShutDown as err:
                    self.__arret.set()
                    self.__logger.debug('%s', self.__arret, exc_info=err)
                else:
                    with self.__loquet:
                        self.__serial.write(cmd)
                        self.__input.task_done()

            if not self.__output.full() and self.__serial.in_waiting:
                with self.__loquet:
                    val: bytes = self.__serial.read_until(b'\n')
                    self.__logger.debug('%s', val)

                try:
                    self.__output.put(val)
                except queue.ShutDown as err:
                    self.__arret.set()
                    self.__logger.debug('%s', self.__arret, exc_info=err)

    def __enter__(self) -> Self:
        self.__serial.open()
        self.__logger.debug('%s', self.__serial)
        self.__thread.start()
        self.__logger.debug('%s', self.__thread)
        return self

    def __exit__(
        self,
        typ: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> bool:
        if typ is not None:
            self.__logger.warning('', exc_info=exc)

        self.__input.shutdown()
        self.__logger.debug('%s', self.__input)

        self.__thread.join(timeout=1.0)
        self.__logger.debug('%s', self.__thread)

        if self.__thread.is_alive():
            self.__arret.set()
            self.__logger.debug('%s', self.__arret)

        self.__thread.join()
        self.__logger.debug('%s', self.__thread)

        self.__serial.close()
        self.__logger.debug('%s', self.__serial)

        self.__output.shutdown()
        self.__logger.debug('%s', self.__output)

        return typ is not None

    def __next__(self) -> str:
        try:
            val: bytes = self.__output.get(block=True)
        except queue.ShutDown as err:
            self.__logger.warning('Stopping iteration.', exc_info=err)
            raise StopIteration from err
        except queue.Empty as err:
            self.__logger.warning('Nothing received.', exc_info=err)
            return None
        else:
            self.__logger.info('%s', val)
            self.__output.task_done()
            return val.decode('utf-8').strip()

    def __iter__(self) -> Self:
        return self

    def parse(self) -> iter[dict[str, float]]:
        yield from (
            {k: float(v) for k, v in (w.split(':') for w in ligne.split('\t'))}
            for ligne in self
        )

    def __str__(self) -> str:
        return str(self.__serial)


class Appareil(LigneSerie):
    APPAREIL: str = 'hwgrep://&skip_busy'

    def __init__(
        self,
        port: str | None = None,
        baudrate: BaudRateType = 115_200,
        *,
        stop_event: threading.Event | None = None,
    ) -> None:
        if port is None:
            port: str = self.APPAREIL

        super().__init__(port, baudrate=baudrate, stop_event=stop_event)


class ArduinoNanoEvery(Appareil):
    APPAREIL: str = 'hwgrep://Arduino Nano Every&skip_busy'


def main(*, debug: bool = False) -> None:
    from pprint import pprint  # noqa: PLC0415

    if debug:
        __logger.setLevel(logging.DEBUG)
        __handler = logging.StreamHandler()
        fmt: str = (
            '%(levelname)s\t'
            '%(threadName)s\t'
            '%(funcName)s (%(lineno)s)\t'
            '%(message)s'
        )
        __formatter = logging.Formatter(fmt)
        __handler.setFormatter(__formatter)
        __logger.addHandler(__handler)

    data: list[dict[str, int]]
    with LigneSerie() as com:
        data = [{'t': t, 'x': x} for t, x in enumerate(range(10))]
        pprint(data)
        com.print(data)

    data = list(com.parse())
    pprint(data)


if __name__ == '__main__':
    main()
