import builtins
import time

def print(prefix, *objs, **kwargs):
    builtins.print("[{0}][{1}]"
                .format(
                    time.strftime("%H:%M:%S"),
                    prefix
                ), *objs, **kwargs)
