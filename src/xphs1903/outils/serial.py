import serial
import queue
import pandas
import matplotlib
import matplotlib.axes
import matplotlib.figure
import typing
import threading

type BaudRateType = typing.Literal(9600, 115200, 1000000)

from .acq import Format

class LigneSerie:

    def __init__(self):
        self.__thread = threading.Thread(target=self.run)
        self.__serial = serial.Serial()
        self.__formatter = Format
        self.__input = queue.Queue()
        self.__output = queue.Queue()
        self.__arret = threading.Event()
        self.__loquet = threading.Lock()

    def open(self):
        self.__serial.open()

    def close(self):
        self.shutdown()

    def acquire(self):
        self.__loquet.acquire()

    def release(self):
        self.__loquet.release()

    def put(self, data):
        self.__input.put(data)

    def get(self):
        return self.__output.get()

    def join(self):
        self.__input.shutdown()
        self.__thread.join()
        self.__serial.close()
        self.__output.shutdown()

    def shutdown(self):
        self.__input.shutdown()
        self.__thread.shutdown()
        self.__serial.close()
        self.__output.shutdown()

    def run(self):
        while True:
            loop()

    def loop(self):
        cmd = self.__input.get()

        with self.__loquet:
            self.__serial.write(cmd)

            while not self.__serial.in_waiting:
                pass

            self.__output.put(self.__serial.read())

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, *exc):
        self.close()
        return None not in exc

    def read(self):
        return self.get()

    def read_all(self):
        cumul = [self.read()]
        while self.out_waiting:
            cumul.append(self.read())
        return cumul

    def read_until(self, until='\n'):
        cumul = [self.read()]
        while until not in cumul[-1]:
            cumul.append(self.read())
        return cumul

    def write(self, data):
        self.put(data)

    def flush(self):
        try:
            while True:
                self.__input.get()
                self.__input.task_done()
        except Exception:
            pass

        try:
            while True:
                self.__output.get()
                self.__output.task_done()
        except Exception:
            pass

        self.__serial.reset_input_buffer()
        self.__serial.reset_output_buffer()
        self.__serial.flush()

    def task_done(self):
        self.__output.task_done()

    def __len__(self):
        return NotImplemented

    @property
    def in_waiting(self):
        return self.__serial.in_waiting + self.__input.qsize()

    @property
    def out_waiting(self):
        return self.__serial.out_waiting + self.__output.qsize()

    def __next__(self):
        try:
            return self.__output.get()
        except Exception:
            raise StopIteration

class Echo(LigneSerie):
    pass

class Appareil(LigneSerie):
    APPAREIL: str|None = None


    def autoconnect(self):
        pass

    def filtre(self, description):
        return description.startswith(self.APPAREIL):

class ArduinoNanoEvery(Appareil):
    APPAREIL: str = 'Arduino Nano Every'

if __name__ == '__main__':
    with Echo() as com:
        com.write('t:0\tx:0')
        print(com.read())
