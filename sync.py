import time, argparse, queue, threading
import synchelper as sh

parser = argparse.ArgumentParser()
parser.add_argument('-d','-dirs', nargs='+', help='directories',required=True)
parser.add_argument('-i','-interval', type=int, help='sync interval in seconds', default = 1)
parser.add_argument('--verbose', help='enable verbose print', action="store_true")

args = parser.parse_args()
verboseprint = print if args.verbose else lambda *a, **k: None

index = []
itemsToSync = queue.Queue()
CopyInterval = 1
copyThread = threading.Thread(target=sh.syncItemsAsync, args=(itemsToSync,CopyInterval))
copyThread.start()


while(1):
    #dirs = []
    #dirs = args.d
    #sh.printItems(index)
    sh.enumItems(index, args.d)
    #sh.printItems(index)
    sh.compareItems(index)
    #sh.printItems(index)
    #sh.RemoveItems(index)
    #sh.printItems(index)
    #sh.printItems(index)
    sh.getItemsToSync(itemsToSync, index)
    sh.delRemovedItems(index)


    #for d in args.d:
    #    sh.enumItems(dirs, d)

    #sh.updateIndex(index,dirs)
    #sh.compareItems(index)
    #sh.getItemsToSync(items, index)
    time.sleep(args.i)


# items = queue.Queue()
# CopyInterval = 1
# copyThread = threading.Thread(target=sh.syncItemsAsync, args=(items,args.d1,args.d2,CopyInterval))
# copyThread.start()
# dir1_old = []
# dir2_old = []
# isFirstSync = True

# while(1):
#     dir1 = sh.enumItems(args.d1)
#     dir2 = sh.enumItems(args.d2)
#     if isFirstSync:
#         sh.compareItems(dir1,dir2)
#         print("indexing done")
#         isFirstSync = False
#     else:
#         sh.markItemsToDelete(dir1,dir1_old,dir2)
#         sh.markItemsToDelete(dir2,dir2_old,dir1)
#         for d1 in (dir1,dir2):
#             for d in (list(filter(lambda item: item['Direction'] != 0, d1))):
#                 print(">{0}".format(d))
#         sh.compareItems(dir1,dir2)
#
#     sh.getItemsToSync(items,dir1)
#     sh.getItemsToSync(items,dir2)
#     if not items.empty():
#         verboseprint(list(items.queue))
#     dir1_old = dir1.copy()
#     dir2_old = dir2.copy()
#     time.sleep(args.i)
    #pass
