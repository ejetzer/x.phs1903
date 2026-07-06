import threading
import sys

def deboguer():

    def thread_excepthook(args, /):
        # https://docs.python.org/3/library/threading.html#threading.excepthook
        threading.__excepthook__(args)

    threading.excepthook = thread_excepthook

    def sys_excepthook(_type, value, traceback):
        # https://docs.python.org/3/library/sys.html#sys.excepthook
        sys.__excepthook__(_type, value, traceback)

    sys.excepthook = sys_excepthook
