import serial
import serial.threaded
import queue
import pandas
import matplotlib
import matplotlib.axes
import matplotlib.figure
import typing

type BaudRateType = typing.Literal(9600, 115200, 1000000)

class ArduinoSerialPlotterReader(serial.threaded.LineReader):

    def __init__(self):
        super().__init__()
        self.sortie: queue.Queue = queue.Queue()
        self.df: pandas.Dataframe = pandas.Dataframe()
        self.ax: matplotlib.axes.Axes = matplotlib.axes.Axes()

    def connection_made(self, transport: serial.threaded.ReaderThread):
        self.transport: serial.threaded.ReaderThread = transport
        ser: serial.Serial = transport.serial

        if not ser.is_open:
            ser.open()

    def handle_line(self, ligne: str) -> None:
        champs: list[str] = ligne.split('\t')
        champs: list[tuple[str, 2]] = [champ.split(':') for champ in champs]
        champs: dict[str, float] = {c: float(v) for c, v in champs}
        champs: pandas.Series = pandas.Series(champs)
        self.df = pandas.concat([self.df, champs])
        self.sortie.put(champs)

    def get(self) -> pandas.Series:
        return self.sortie.get()

    def put(self, ligne: str) -> None:
        self.write_line(ligne)

    def plot(self) -> matplotlib.figure.Figure, matplotlib.axes.Axes:
        pass

class ArduinoNanoEveryThread(ReaderThread):
    DEVNAME: str = 'Arduino Nano Every'

    def __init__(
        self,
        port: str | None = None,
        baudrate: BaudRateType = 9600
    ):
        if port is None:
            port = self.autoselect()

        ser: serial.Serial = serial.serial_for_url(port, do_not_open=True)
        ser.baudrate = baudrate

        super().__init__(ser, ArduinoSerialPlotterReader)

    def autoselect(self) -> str:
        appareil: serial.tools.list_ports.ListPortInfo
        ports: list[serial.tools.list_ports.ListPortInfo]
        if isinstance(dev, serial.tools.list_ports.ListPortInfo):
            appareil = dev
        elif dev is None:
            ports = [d for d in serial.tools.list_ports.grep(self.DEVNAME)]
            if len(ports) == 1:
                appareil = ports[0]
            else:
                raise AppareilsTropNombreuxError(self.DEVNAME, ports)
        elif isinstance(dev, str):
            ports = [d for d in serial.tools.list_ports.grep(dev)]
            if len(ports) == 1:
                appareil = ports[0]
            else:
                raise AppareilIntrouvableError(dev, ports)
        elif isinstance(dev, int):
            ports = [d for d in serial.tools.list_ports.grep(self.__devname__)]
            if len(ports) >= dev:
                appareil = ports[dev]
            else:
                raise PasAssezAppareilsError(dev, ports)
        else:
            raise SelectionAppareilTypeError(dev, serial.tools.list_ports.ListPortInfo, str, int, None)

        return appareil.device


if __name__ == '__main__':
    with ArduinoNanoEveryThread('loop://') as arduino:
        arduino.put('t:0\tx:0')
