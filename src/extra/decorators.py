from functools import wraps
from multiprocessing import Process
from typing import Callable, Any, Final
import numpy as np

def nanos():
    return np.datetime64('now', 'ns')
    
def micros():
    return np.datetime64('now', 'us')

def millis():
    return np.datetime64('now', 'ms')

def seconds():
    return np.datetime64('now', 's')

horloges: list[np.datetime64] = []
processus: list[Process] = []

DT: Final[np.timedelta64] = np.timedelta64(10, 'us')

def après_au_moins(
    dt: np.timedelta64 = DT,
    horloge: Callable[[], np.datetime64] = nanos,
    signaler: bool = False
                  ) -> Callable[Callable[..., Any], Callable[..., Any]]:
    i: int = len(horloges)
    horloges.append(horloge())
    
    def déco(f: Callable[..., Any]) -> Callable[..., Any]:
        
        @wraps(f)
        def f_décoré(*args, **kargs):
            if horloge() >= horloge[i] + dt:
                return f(*args, **kargs)
            elif signaler:
                desc = f'Il faut attendre {dt} pour exécuter {f}.'
                raise DélaiTropCourt(desc)
    
    return déco

def en_parallèle(f: Callable[..., Any]) -> Callable[..., Any]:
    
    @wraps(f)
    @contextmanager
    def f_décoré(*args, **kargs):
        proc: Process = Process(target=f, args=args, kargs=kargs)
        processus.append(proc)
        
        try:
            proc.start()
            yield proc
        finally:
            proc.terminate()
            proc.close()
    
    return f_décoré