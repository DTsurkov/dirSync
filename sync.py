import time
import argparse
import queue
import threading
import sys
import synchelper as sh
import prettyPrint as pp

def main():
    logprefix = "Main"
    parser = argparse.ArgumentParser()
    parser.add_argument('-d','-dirs', nargs='+', help='directories',required=True)
    parser.add_argument('-i','-interval', type=int, help='sync interval in seconds', default = 1)
    parser.add_argument('--verbose', help='enable verbose print', action="store_true")
    args = parser.parse_args()

    index = []
    itemsToSync = queue.Queue()
    copyInterval = 1
    copyThreadRun = threading.Event()
    copyThreadRun.set()
    copyThread = threading.Thread(target=sh.syncItemsAsync, args=(itemsToSync,copyInterval,copyThreadRun))
    copyThread.start()

    try:
        while(1):
            sh.enumItems(index, args.d)
            sh.compareItems(index)
            if args.verbose:
                sh.printItems(index)
            sh.getitemsToSync(itemsToSync, index)
            sh.delRemovedItems(index)
            time.sleep(args.i)
    except KeyboardInterrupt:
        pp.print(logprefix,"Stop signal has been received")
        copyThreadRun.clear()
        pp.print(logprefix,"Waiting to close copier thread")
        copyThread.join()
        pp.print(logprefix,"Script has been stopped")
        sys.exit(0)


if __name__ == "__main__":
    main()
