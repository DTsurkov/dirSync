import glob, os, time, itertools, shutil, queue
import numpy as np

def enumItems(directory):
    items = []
    for path, subdirs, files in os.walk(directory):
        for name in files:
            itempath = os.path.join(path, name)
            items.append({'FullPath':itempath, 'Path': (os.path.relpath(itempath,directory)),'LastModTime': os.path.getmtime(itempath), 'Direction': 0})
            #0 - sync; 1 - 1->2; -1 - 2->1; 2 - delete
    return items

def compareItems(dir1,dir2,isRemove=False):
    if isRemove:
        d = 2
    else:
        d = 1
    for item1 in dir1:
        isExist = False
        for item2 in dir2:
            if item1["Path"] == item2["Path"] and abs(item1["Direction"]) != 2:
                isExist = True
                item1["Direction"] = np.sign(item1["LastModTime"] - item2["LastModTime"])
                break
        if isExist != True and abs(item1["Direction"]) != 2:
            item1["Direction"] = d
    for item2 in dir2:
        isExist = False
        for item1 in dir1:
            if item2["Path"] == item1["Path"] and abs(item2["Direction"]) != 2:
                isExist = True
                #item2["Direction"] = np.sign(item1["LastModTime"] - item2["LastModTime"])
                break
        if isExist != True and abs(item2["Direction"]) != 2:
            item2["Direction"] = -d

def markItemsToDelete(dir1,dir2,dir3):
    new = []
    for item in dir2:
        if list(filter(lambda item1: item1['Path'] == item["Path"], dir1)):
            pass
        else:
            new.append(item)
    for n in new:
        for d in dir3:
            if d["Path"] == n["Path"]:
                d["Direction"] = 2

def getItemsToSync(items,dir):
    for item in list(filter(lambda item: item['Direction'] != 0, dir)):
        items.put(item)

def syncItem(item,path1,path2):
    if abs(item["Direction"]) == 2:
        shifter = 4.0
    else:
        shifter = 2.0
    syncItems = [os.path.join(path1, item["Path"]),os.path.join(path2, item["Path"])]
    position = int(item["Direction"] / shifter + 0.5) #conver -1 to 0 and 1 to 1

    if abs(item["Direction"]) == 2:
        try:
            os.remove(syncItems[abs(1-position)])
        except:
            pass
        try:
            os.remove(syncItems[abs(position)])
        except:
            pass
    elif abs(item["Direction"]) == 1:
        try:
            os.makedirs(os.path.dirname(syncItems[position]), exist_ok=True)
            shutil.copy2(syncItems[abs(1-position)],syncItems[position])
        except IOError as e:
            print(u'Error in copy:{0}'.format(e));
    else:
        pass

def syncItemsAsync(items,path1,path2,interval):
    print("Async copier started")
    while True:
        if not items.empty():
            print("found items to update")
            item = items.get()
            if item:
                print("starting update files")
                syncItem(item,path1,path2)
                item["Direction"] = 0
        else:
            pass
        time.sleep(interval)
