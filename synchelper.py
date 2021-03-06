import glob, os, time, itertools, shutil, queue
import numpy as np

class Item:
    def __init__(self, relpath, itempath, directory):
        self.relpath = relpath
        self.isFile = os.path.isfile(itempath)
        self.isSync = True
        self.toRemove = False
        self.isModified = False
        self.toCreate = False
        self.directory = []
        print("[Item] Item {0} has been created [{1}]. isFile {2}, isSync {3}".format(self.relpath, time.strftime("%H:%M:%S"), self.isFile, self.isSync))
    def __del__(self):
        print("[Item] Item {0} has been removed [{1}]. isFile {2}, isSync {3}".format(self.relpath, time.strftime("%H:%M:%S"), self.isFile, self.isSync))
    def addDirectory(self,directory):
        self.directory.append(Dir(self.relpath, directory, self.isFile))
    def removeDirectory(self,directory):
        toDel = list(filter(lambda dir: dir.directory == directory, self.directory))
        try:
            self.directory.remove(toDel[0])
        except:
            pass
    def markForDelete(self):
        if list(filter(lambda dir: dir.direction == 2, self.directory)):# or (not list(filter(lambda dir: dir.direction != 3, self.directory))):
            for dir in self.directory:
                dir.setDirection(2)
            self.toRemove = True
            self.isSync = False
            print("[Item] Item {0} marked for remove [{1}]".format(self.relpath, time.strftime("%H:%M:%S")))
    def markForCreate(self):
        source = list(filter(lambda dir: dir.direction == 0, self.directory))
        target = list(filter(lambda dir: dir.direction == 3, self.directory))
        if source and target:
            for dir in self.directory:
                dir.setDirection(-1)
            (source[0]).setDirection(1)
            self.toCreate = True
            self.isSync = False
            print("[Item] Item {0} marked for create [{1}]".format(self.relpath, time.strftime("%H:%M:%S")))
        if self.isSync:
            self.toCreate = False

    def foundLatestVersion(self):
        latest = (self.directory)[0]
        self.isModified = False
        for dir in self.directory:
            if self.isFile:
                if dir.lastModTime > latest.lastModTime: #found latest version
                    latest = dir
                    self.isModified = True
                elif dir.lastModTime < latest.lastModTime:
                    self.isModified = True
                else: #all versions equal
                    pass
        return latest
    def updateDirs(self):
        for dir in self.directory:
            dir.update()
    def printDirsStatus(self):
        for dir in self.directory:
            print("\tItem:{0}, Dir:{1}, Direction:{2}".format(self.relpath, dir.directory,dir.direction))
    def update(self):
        if not self.isSync:
            return
        self.updateDirs()
        self.markForDelete()
        self.markForCreate()
        if not self.toRemove and not self.toCreate:
            latest = self.foundLatestVersion()
            if self.isModified:
                for dir in self.directory:
                    if dir == latest:
                        dir.setDirection(1)
                    else:
                        dir.setDirection(-1)
                self.isSync = False
            else:
                for dir in self.directory:
                    dir.setDirection(0)
                self.isSync = True
        #self.printDirsStatus()
class Dir:
    def __init__(self, relpath, directory, isFile):
        self.directory = directory
        self.relpath = relpath
        self.fullPath = os.path.join(directory, relpath)
        self.isFile = isFile
        self.lastModTime = 0
        self.direction = 3
        self.update()
        print("[DIR] Dir {0} for item {1} has been created. Direction: {2}".format(self.directory,self.relpath,self.direction))
    def setDirection(self,Direction):
        self.direction = Direction
    def update(self):
        oldVaule = self.direction
        try:
            self.lastModTime = (os.path.getmtime(self.fullPath)*int(self.isFile))
            self.direction = 0 #0 - sync; 1 - 1->2; -1 - 2->1; 2 - delete; 3 - item not exists
        except:
            self.lastModTime = 0
            self.direction = 3
        if (oldVaule != 2 and oldVaule !=3) and self.direction == 3:
            self.direction = 2
    def __del__(self):
        print("[DIR] Dir {0} for item {1} has been removed".format(self.directory,self.relpath))

def enumItems(items, directories):
    for directory in directories:
        for path, subdirs, files in os.walk(directory):
            for fsobj in files, subdirs:
                for name in fsobj:
                    fsobjpath = os.path.join(path, name)
                    fsobjrelpath = (os.path.relpath(fsobjpath,directory))
                    isExist = False
                    for item in items:
                        if item.relpath == fsobjrelpath:
                            isExist = True
                            break
                    if not isExist:
                        item = Item(fsobjrelpath, fsobjpath, directory)
                        for dir in directories:
                            item.addDirectory(dir)
                        items.append(item)
def printItems(items):
    print("=====================================")
    print("[printItems] Current state. [{0}]".format(time.strftime("%H:%M:%S")))
    for item in items:
        print("[printItems] isFile: {0}, isSync: {1}, toCreate: {2}, toRemove: {3}, item:{4}".format(int(item.isFile), int(item.isSync), int(item.toCreate),int(item.toRemove),item.relpath))
        for dir in item.directory:
            print("\tDir:{0},Direction:{1}".format(dir.directory,dir.direction))
def compareItems(index):
    for item in index:
        item.update()
def delRemovedItems(index):
    toRemove = []
    for item in index:
        if item.isSync == True and item.toRemove == True:
            print("[Remover] isFile: {0}, isSync: {1}, item:{2}".format(int(item.isFile), int(item.isSync), item.relpath))
            toRemove.append(item)
    for t in toRemove:
        index.remove(t)
def getItemsToSync(items, index):
    for item in index:
        if item.isSync == False:
            items.put(item)

def syncItem(item):
    if item.toRemove:
        for dir in item.directory:
            try:
                shutil.rmtree(dir.fullPath, ignore_errors=True)
                os.remove(dir.fullPath)
            except:
                pass
    else:
        target = list(filter(lambda dir: dir.direction == -1, item.directory))
        source = list(filter(lambda dir: dir.direction == 1, item.directory))
        if target and source:
            for t in target:
                try:
                    os.makedirs(os.path.dirname(t.fullPath), exist_ok=True)
                    if not t.isFile:
                        os.makedirs(t.fullPath, exist_ok=True)
                    else:
                        shutil.copy2(source[0].fullPath,t.fullPath)
                except IOError as e:
                    print(u'Error in copy:{0}'.format(e));
                t.direction = 0
            source[0].direction = 0
def syncItemsAsync(items,interval):
    print("[Syncher] Async item synchronizer started")
    while True:
        if not items.empty():
            print("=====================================")
            print("[Syncher] Starting item synchronization. [{0}]".format(time.strftime("%H:%M:%S")))
            while not items.empty():
                item = items.get()
                if item:
                    print("[Syncher] Updating file.\tisSync: {0}, Item: {1}".format(item.isSync,item.relpath))
                    syncItem(item)
                    item.isSync = True
                    print("[Syncher] Updating done.\tisSync: {0}, Item: {1}".format(item.isSync,item.relpath))
                else:
                    pass
            print("[Syncher] Synchronization has been done. [{0}]".format(time.strftime("%H:%M:%S")))
            print("=====================================")
        time.sleep(interval)
