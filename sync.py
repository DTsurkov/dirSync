import time, argparse, queue, threading
import synchelper as sh

parser = argparse.ArgumentParser()
parser.add_argument('-d1','-dir1', help='directory 1',required=True)
parser.add_argument('-d2','-dir2', help='directory 2',required=True)
parser.add_argument('-i','-interval', type=int, help='sync interval in seconds', default = 1)
parser.add_argument('--verbose', help='senable verbose print', action="store_true")

args = parser.parse_args()
verboseprint = print if args.verbose else lambda *a, **k: None

items = queue.Queue()
CopyInterval = 1
copyThread = threading.Thread(target=sh.syncItemsAsync, args=(items,args.d1,args.d2,CopyInterval))
copyThread.start()
dir1_old = []
dir2_old = []
isFirstSync = True
while(1):
    try:
        dir1 = sh.enumItems(args.d1)
        dir2 = sh.enumItems(args.d2)
    except IOError as e:
        print(u'Path not found!');
    if isFirstSync:
        sh.compareItems(dir1,dir2)
        print("indexing done")
        isFirstSync = False
    else:
        sh.markItemsToDelete(dir1,dir1_old,dir2)
        sh.markItemsToDelete(dir2,dir2_old,dir1)
        for d1 in (dir1,dir2):
            for d in (list(filter(lambda item: item['Direction'] != 0, d1))):
                print(">{0}".format(d))
        sh.compareItems(dir1,dir2)

    sh.getItemsToSync(items,dir1)
    sh.getItemsToSync(items,dir2)
    if not items.empty():
        verboseprint(list(items.queue))
    dir1_old = dir1.copy()
    dir2_old = dir2.copy()
    time.sleep(args.i)
    #pass
