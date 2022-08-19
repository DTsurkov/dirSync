import builtins
import time

class Log:
    def __init__ (self, prefix="PrettyPrint"):
        self.prefix = prefix

    def setPrefix(self,prefix):
        self.prefix = prefix

    def print(self, *objs, **kwargs):
        builtins.print("[{0}][{1}]"
                    .format(
                        time.strftime("%H:%M:%S"),
                        self.prefix
                    ), *objs, **kwargs)


def print(prefix, *objs, **kwargs):
    builtins.print("[{0}][{1}]"
                .format(
                    time.strftime("%H:%M:%S"),
                    prefix
                ), *objs, **kwargs)
