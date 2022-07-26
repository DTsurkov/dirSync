import builtins
import time

# class Print:
#     prefix = "PrettyPrint"
#     def setPrefix(self,prefix):
#         self.prefix = prefix
#     def print(self, *objs, **kwargs):
#         builtins.print("[{0}][{1}]"
#                     .format(
#                         time.strftime("%H:%M:%S"),
#                         self.prefix
#                     ), *objs, **kwargs)

def print(prefix, *objs, **kwargs):
    builtins.print("[{0}][{1}]"
                .format(
                    time.strftime("%H:%M:%S"),
                    prefix
                ), *objs, **kwargs)
