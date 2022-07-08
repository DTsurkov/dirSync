import glob, os, time, itertools, shutil, queue
import numpy as np

class Item:
    directory = []
    def __init__(self, relpath, itempath, directory):
        self.relpath = relpath
        self.isFile = os.path.isfile(itempath)
        self.isSync = True
        self.addDirectory(directory)
        print("[Item] Item {0} has been created".format(self.relpath))
    def __del__(self):
        print("[Item] Item {0} has been removed".format(self.relpath))
    def addDirectory(self,directory):
        self.directory.append(Dir(self.relpath, directory, self.isFile))
    def removeDirectory(self,directory):
        toDel = list(filter(lambda dir: dir.directory == directory, self.directory))
        try:
            self.directory.remove(toDel[0])
        except:
            pass
class Dir:
    def __init__(self, relpath, directory, isFile):
        self.directory = directory
        self.relpath = relpath
        self.fullPath = os.path.join(directory, relpath)
        self.lastModTime = (os.path.getmtime(self.fullPath)*int(isFile))
        self.direction = 0 #0 - sync; 1 - 1->2; -1 - 2->1; 2 - delete; 3 - item not exists
        print("[DIR] Dir {0} for item {1} has been created".format(self.directory,self.relpath))
    def setDirection(self,Direction):
        self.direction = Direction
    def __del__(self):
        print("[DIR] Dir {0} for item {1} has been removed".format(self.directory,self.relpath))


#ITEM object:
    #relpath
    #isFile
    #isSync
    #directory object:
        #directory
        #relpath
        #fullPath
        #lastModTime
        #direction

def enumItems3(directory):
    items = []
    for path, subdirs, files in os.walk(directory):
        for fsobj in files, subdirs:
            for name in fsobj:
                itempath = os.path.join(path, name)
                items.append(
                    {'relpath':(os.path.relpath(itempath,directory)),
                    'fullpath': itempath,
                    'directory':directory})
    return items

def updateIndex(index,directory):
    if len(index) == 0:
        for dir in directory:
            index.append(Item(dir["relpath"], dir["fullpath"], dir["directory"]))
    else:
        new = []
        for item in index:
            isExist = False
            for dir in directory:
                if (item.relpath == dir["relpath"]):
                    item.addDirectory(dir["directory"])
                    isExist = True
            if not isExist:
                new.append(Item(dir["relpath"], dir["fullpath"], dir["directory"]))
        for n in new:
            index.append(n)

def compareItems(index):
    for item in index:
        if not item.isSync:
            continue
        latest = (item.directory)[0]
        isModified = False
        for dir in item.directory:
            if dir.lastModTime > latest.lastModTime: #found latest version
                latest = dir
                isModified = True
            elif dir.lastModTime == latest.lastModTime: #all versions equal
                pass
            else:
                isModified = True
        for dir in item.directory: #set direction for synchronization
            if isModified:
                if dir == latest:
                    dir.setDirection(1)
                else:
                    dir.setDirection(-1)
            else:
                dir.setDirection(0) #if isModified = 0 => already synchronized
        if isModified:
            item.isSync = False
        print("[IndexCompare] isFile: {0}, isSync: {1}, item:{2}".format(int(item.isFile), int(item.isSync), item.relpath))
        for dir in item.directory:
            print("Dir:{0},Direction:{1}".format(dir.directory,dir.direction))

def getItemsToSync(items, index):
    for item in index:
        if item.isSync == False:
#    for item in list(filter(lambda item: item.isSync == False, index)):
            print("found item")
            items.put(item)

def syncItem(item):
    target = list(filter(lambda dir: dir.direction == -1, item.directory))
    source = list(filter(lambda dir: dir.direction == 1, item.directory))
    if target and source:
        for t in target:
            shutil.copy2(source[0].fullPath,t.fullPath)
            t.direction = 0

    #
    # if abs(item["Direction"]) == 2:
    #     shifter = 4.0
    # else:
    #     shifter = 2.0
    # syncItems = [os.path.join(path1, item["Path"]),os.path.join(path2, item["Path"])]
    # position = int(item["Direction"] / shifter + 0.5) #conver -1 to 0 and 1 to 1
    #
    # if abs(item["Direction"]) == 2:
    #     try:
    #         shutil.rmtree(syncItems[abs(1-position)], ignore_errors=True)
    #         os.remove(syncItems[abs(1-position)])
    #     except:
    #         pass
    #     try:
    #         shutil.rmtree(syncItems[abs(position)], ignore_errors=True)
    #         os.remove(syncItems[abs(position)])
    #     except:
    #         pass
    # elif abs(item["Direction"]) == 1:
    #     try:
    #         os.makedirs(os.path.dirname(syncItems[position]), exist_ok=True)
    #         if not item["isFile"]:
    #             os.makedirs(syncItems[position], exist_ok=True)
    #         else:
    #             shutil.copy2(syncItems[abs(1-position)],syncItems[position])
    #     except IOError as e:
    #         print(u'Error in copy:{0}'.format(e));
    # else:
    #     pass
def syncItemsAsync(items,interval):
    print("[Syncer] Async copier started")
    while True:
        if not items.empty():
            print("[Syncer] found items to update")
            item = items.get()
            if item:
                print("[Syncer] starting update files. Item: {0}".format(item.relpath))
                syncItem(item)
                item.isSync = True
        else:
            pass
        time.sleep(interval)



#OLD:
# def enumItems2(directory):
#     items = []
#     for path, subdirs, files in os.walk(directory):
#         for fsobj in files, subdirs:
#             for name in fsobj:
#                 itempath = os.path.join(path, name)
#                 isFile = os.path.isfile(itempath)
#                 items.append(
#                     {'FullPath':itempath,
#                     'Source':directory,
#                     'Path': (os.path.relpath(itempath,directory)),
#                     'LastModTime': (os.path.getmtime(itempath)*int(isFile)),
#                     'Direction': 0, #0 - sync; 1 - 1->2; -1 - 2->1; 2 - delete; 3 - item not exists
#                     'isFile':isFile})
#     return items
# def enumItems(directory):
#     items = []
#     for path, subdirs, files in os.walk(directory):
#         for fsobj in files, subdirs:
#             for name in fsobj:
#                 itempath = os.path.join(path, name)
#                 relpath = os.path.relpath(itempath,directory)
#                 currentItem = list(filter(lambda item: item.relpath == relpath, items))
#                 if currentItem:
#                     currentItem[0].addDirectory(directory)
#                 else:
#                     items.append(Item(relpath, itempath, directory))
#     return items
# def compareItems2(dir1,dir2):
#     for item1 in dir1:
#         isExist = False
#         for item2 in dir2:
#             if item1["Path"] == item2["Path"] and abs(item1["Direction"]) != 2:
#                 isExist = True
#                 item1["Direction"] = np.sign(item1["LastModTime"] - item2["LastModTime"])
#                 break
#         if isExist != True and abs(item1["Direction"]) != 2:
#             item1["Direction"] = 1
#     for item2 in dir2:
#         isExist = False
#         for item1 in dir1:
#             if item2["Path"] == item1["Path"] and abs(item2["Direction"]) != 2:
#                 isExist = True
#                 break
#         if isExist != True and abs(item2["Direction"]) != 2:
#             item2["Direction"] = -1
# def markItemsToDelete(dir1,dir2,dir3):
#     new = []
#     for item in dir2:
#         if list(filter(lambda item1: item1['Path'] == item["Path"], dir1)):
#             pass
#         else:
#             new.append(item)
#     for n in new:
#         for d in dir3:
#             if d["Path"] == n["Path"]:
#                 d["Direction"] = 2
# def getItemsToSync2(items,dir):
#     for item in list(filter(lambda item: item['Direction'] != 0, dir)):
#         items.put(item)
# def syncItem2(item,path1,path2):
#     if abs(item["Direction"]) == 2:
#         shifter = 4.0
#     else:
#         shifter = 2.0
#     syncItems = [os.path.join(path1, item["Path"]),os.path.join(path2, item["Path"])]
#     position = int(item["Direction"] / shifter + 0.5) #conver -1 to 0 and 1 to 1
#
#     if abs(item["Direction"]) == 2:
#         try:
#             shutil.rmtree(syncItems[abs(1-position)], ignore_errors=True)
#             os.remove(syncItems[abs(1-position)])
#         except:
#             pass
#         try:
#             shutil.rmtree(syncItems[abs(position)], ignore_errors=True)
#             os.remove(syncItems[abs(position)])
#         except:
#             pass
#     elif abs(item["Direction"]) == 1:
#         try:
#             os.makedirs(os.path.dirname(syncItems[position]), exist_ok=True)
#             if not item["isFile"]:
#                 os.makedirs(syncItems[position], exist_ok=True)
#             else:
#                 shutil.copy2(syncItems[abs(1-position)],syncItems[position])
#         except IOError as e:
#             print(u'Error in copy:{0}'.format(e));
#     else:
#         pass
# def syncItemsAsync2(items,path1,path2,interval):
#     print("Async copier started")
#     while True:
#         if not items.empty():
#             print("found items to update")
#             item = items.get()
#             if item:
#                 print("starting update files")
#                 syncItem(item,path1,path2)
#                 item["Direction"] = 0
#         else:
#             pass
#         time.sleep(interval)
