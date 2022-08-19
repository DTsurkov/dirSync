#import glob
import os
import time
#import itertools
import shutil
import queue
import enum
import prettyPrint as pp
#import numpy as np


class Direction(enum.Enum):
    SYNCED = 0
    SOURCE = 1
    TARGET = -1
    TO_DELETE = 2
    FOR_CREATE = 3


class Item:
    log = pp.Log("Item")
    def __init__(self, relpath, itempath, directory):
        self.relpath = relpath
        self.isFile = os.path.isfile(itempath)
        self.isSync = True
        self.toRemove = False
        self.isModified = False
        self.toCreate = False
        self.directory = []
        #print("[Item] Item {0} has been created [{1}]. isFile {2}, isSync {3}"
        self.log.print("Item {0} has been created. isFile {1}\tisSync {2}"
            .format(self.relpath,
                    self.isFile,
                    self.isSync))

    def __del__(self):
        self.log.print("Item {0} has been removed. isFile {1}\tisSync {2}"
            .format(self.relpath,
                    self.isFile,
                    self.isSync))

    def addDirectory(self,directory):
        self.directory.append(Dir(self.relpath, directory, self.isFile))

    def removeDirectory(self,directory):
        toDel = list(filter(lambda dir: dir.directory == directory, self.directory))
        try:
            self.directory.remove(toDel[0])
        except BaseException as e:
            self.log.print(u'Error in removeDirectory method:{0}'
                .format(e))

    def markForDelete(self):
        if list(filter(lambda dir: dir.direction == Direction.TO_DELETE, self.directory)):# or (not list(filter(lambda dir: dir.direction != 3, self.directory))):
            for dir in self.directory:
                dir.setDirection(Direction.TO_DELETE)
            self.toRemove = True
            self.isSync = False
            self.log.print("Item {0} marked for remove"
                .format(self.relpath))

    def markForCreate(self):
        source = list(filter(lambda dir: dir.direction == Direction.SYNCED, self.directory))
        target = list(filter(lambda dir: dir.direction == Direction.FOR_CREATE, self.directory))
        if source and target:
            for dir in self.directory:
                dir.setDirection(Direction.TARGET)
            (source[0]).setDirection(Direction.SOURCE)
            self.toCreate = True
            self.isSync = False
            self.log.print("Item {0} marked for create"
                .format(self.relpath))
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
            print("\tItem:{0}, Dir:{1}\tDirection:{2}"
                .format(self.relpath,
                        dir.directory,
                        dir.direction))

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
                        dir.setDirection(Direction.SOURCE)
                    else:
                        dir.setDirection(Direction.TARGET)
                self.isSync = False
            else:
                for dir in self.directory:
                    dir.setDirection(Direction.SYNCED)
                self.isSync = True
        #self.printDirsStatus()


class Dir:
    log = pp.Log("DIR")
    def __init__(self, relpath, directory, isFile):
        self.directory = directory
        self.relpath = relpath
        self.fullPath = os.path.join(directory, relpath)
        self.isFile = isFile
        self.lastModTime = 0
        self.setDirection(Direction.FOR_CREATE)
        self.update()
        self.log.print( "Dir {0} for item {1} has been created. Direction: {2}"
            .format(self.directory,
                    self.relpath,
                    self.direction))

    def setDirection(self,direction:Direction):
        self.direction = direction

    def update(self):
        oldDirection = self.direction
        try:
            self.lastModTime = (os.path.getmtime(self.fullPath)*int(self.isFile))
            self.setDirection(Direction.SYNCED) #0 - sync; 1 - 1->2; -1 - 2->1; 2 - delete; 3 - item not exists
        except:
            self.lastModTime = 0
            self.setDirection(Direction.FOR_CREATE)
        if (oldDirection != Direction.TO_DELETE and oldDirection != Direction.FOR_CREATE) and self.direction == Direction.FOR_CREATE:
            self.setDirection(Direction.TO_DELETE)

    def __del__(self):
        self.log.print( "Dir {0} for item {1} has been removed"
            .format(self.directory,
                    self.relpath))


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
    log = pp.Log("printItems")
    print("=====================================")
    log.print("Current state")
    for item in items:
        log.print("isFile: {0}\tisSync: {1}\ttoCreate: {2}\ttoRemove: {3}\titem:{4}"
            .format(int(item.isFile),
                    int(item.isSync),
                    int(item.toCreate),
                    int(item.toRemove),
                    item.relpath))
        for dir in item.directory:
            print("\tDir:{0}\tDirection:{1}"
                .format(dir.directory,
                        dir.direction))

def compareItems(index):
    for item in index:
        item.update()

def delRemovedItems(index):
    log = pp.Log("Remover")
    toRemove = []
    for item in index:
        if item.isSync == True and item.toRemove == True:
            log.print("isFile: {0}\tisSync: {1}\tItem: {2}"
                .format(item.isFile,
                        item.isSync,
                        item.relpath))
            toRemove.append(item)
    for t in toRemove:
        index.remove(t)

def getitemsToSync(items, index):
    for item in index:
        if item.isSync == False:
            items.put(item)


def syncItem(item):
    log = pp.Log("syncItem")
    if item.toRemove:
        for dir in item.directory:
            try:
                shutil.rmtree(dir.fullPath, ignore_errors=True)
                os.remove(dir.fullPath)
            except IOError:
                pass    #при удалении директории рутовый путь может быть удалён раньше чилдов. Поэтому могут быть лжидаемые ошибки "директория не найдена"
            except BaseException as e:
                log.print(u'Error in remove item:{0}'.format(e))
    else:
        target = list(filter(lambda dir: dir.direction == Direction.TARGET, item.directory))
        source = list(filter(lambda dir: dir.direction == Direction.SOURCE, item.directory))
        if target and source:
            for t in target:
                try:
                    os.makedirs(os.path.dirname(t.fullPath), exist_ok=True)
                    if not t.isFile:
                        os.makedirs(t.fullPath, exist_ok=True)
                    else:
                        shutil.copy2(source[0].fullPath,t.fullPath)
                except BaseException as e:
                    log.print(u'Error in copy:{0}'.format(e))
                t.setDirection(Direction.SYNCED)
            source[0].setDirection(Direction.SYNCED)

def syncItemsAsync(items,interval,copyThreadRun):
    log = pp.Log("Syncher")
    log.print("Async item synchronizer started")
    while copyThreadRun.is_set():
        if not items.empty():
            print("=====================================")
            log.print("Starting items synchronization")
            while not items.empty():
                item = items.get()
                if item:
                    log.print("Updating file.\tisSync: {0}\tItem: {1}"
                        .format(item.isSync,
                                item.relpath))
                    syncItem(item)
                    item.isSync = True
                    log.print("Updating done.\tisSync: {0}\tItem: {1}"
                        .format(item.isSync,
                                item.relpath))
                else:
                    pass
            log.print("Synchronization has been done")
            print("=====================================")
        time.sleep(interval)
