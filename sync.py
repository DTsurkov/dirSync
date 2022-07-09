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
    sh.enumItems(index, args.d)
    sh.compareItems(index)
    sh.getItemsToSync(itemsToSync, index)
    sh.delRemovedItems(index)
    time.sleep(args.i)
