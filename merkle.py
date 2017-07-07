#!/usr/bin/env python

# Cases not handled yet :
# -> If folder is empty, use the folder name for hash - that is the folder itself is the leadf node in this case.
# -> Addition of a new fiel or folder has not been handled here. Need to check that as well in the comparison function.
# -> Files with same content will produce the same hash and will lead to collision. 
#    This case need to be handled using the file name to differentiate between teh content.

import os
from Crypto.Hash import SHA256

class MarkleTree:
    def __init__(self, root):
        self._linelength = 30
        self._root = root
        self._mt = {}                #every entry in this has a node and its children format. So, each entre is a sub - merkle tree. See Github
        self._hashlist = {}
        self._tophash = ''
        self.__MT__()

    def Line(self):                         #prints ------- to format output
        print(self._linelength*'-')

    def PrintHashList(self):                #function to print hashlist
        self.Line()
        for item, itemhash in self._hashlist.items():
            print("%s %s" % (itemhash, item))
        self.Line()
        return

    def PrintMT(self, hash):                 #function to print Merkel Tree
        value = self._mt[hash]
        item = value[0]
        child = value[1]
        print("%s %s" % (hash, item))
        if not child:
            return
        for itemhash, item in child.items():  
            print("    -> %s %s" % (itemhash, item))
        for itemhash, item in child.items():  
            self.PrintMT(itemhash)

    def MT(self):
        for node, hash in self._hashlist.items():
            items = self.GetItems(node)
            value = []
            value.append(node)
            list = {}
            for item in items:
                if node == self._root:
                    list[self._hashlist[item]] = item
                else: 
                    list[self._hashlist[os.path.join(node, item)]] = os.path.join(node, item)
            value.append(list)
            self._mt[hash] = value
        self._tophash = self._hashlist[self._root]
        

    def __MT__(self):
        self.HashList(self._root)                       #creating the hashlist for the root
        #self.PrintHashList()
        self.MT()
        #print("Merkle Tree for %s: " % self._root)
        #self.PrintMT(self._tophash)
        #self.Line()

    def sha256(self, data):                             #function for hashing
        hasher = SHA256.new()
        fn = os.path.join(self._root, data)             #constructing path to the given file/dir from root dir
        if os.path.isfile(fn):                          #if a file is given then read its content
            try:   
                f = open(fn, 'rb')
            except:
                return 'ERROR: unable to open %s' % fn
            while True:
                d = f.read(8096)
                if not d:
                    break
                hasher.update(d)
            f.close()
        else:
            hasher.update(data.encode('utf-8'))         #else use previous(child) hahses
        return hasher.hexdigest()

    def GetItems(self, directory):                      #function to get items in a directory
        value = []
        if directory != self._root:                     #check if given dir is root dir
            directory = os.path.join(self._root, directory) #contruct path to given dir from root dir
        if os.path.isdir(directory):                    #check if given parameter is dir or file
            items = os.listdir(directory)
            for item in items:
                if not item.startswith('.'):            #to ignore hidden files such as .DS_Store files on mac
                    value.append(item)
                    #value.append(os.path.join(".", item))
            value.sort()
        return value
    
    def HashList(self, rootdir):     #done - but check what is it used for as HashListChild is also doing the same job
        self.HashListChild(rootdir)
        items = self.GetItems(rootdir)
        if not items:
            self._hashlist[rootdir] = ''
            return
        s = ''
        for subitem in items:
            s = s + self._hashlist[subitem]
        self._hashlist[rootdir] = self.sha256(s)

    def HashListChild(self, rootdir):                       #recursive function to create a hash list of all items and sub-items in given root dir
        items = self.GetItems(rootdir)                      #getting items in the given dir
        if not items:                                       #if no items in given dir then put null in place of hash
            self._hashlist[rootdir] = ''
            return
        for item in items:
            itemname = os.path.join(rootdir, item)          #getting item name (i.e. path to the item in this case)
            if os.path.isdir(itemname):                     #if item is a dir then recursive call to get the hash of sub-items in it
                self.HashListChild(item)
                subitems = self.GetItems(item)              #get the subitems in the dir
                s = ''
                for subitem in subitems:                    #iterating through each of the sub-items
                    s = s + self._hashlist[os.path.join(item, subitem)] #concatinating the hash of sub-items in the given dir
                if rootdir == self._root:                   #check if given item is in root dir or sub-dir - for chosing the key(of hashlist) accordingly
                    self._hashlist[item] = self.sha256(s)   #finding the hash of the concatenated hashes(non-leaf node of tree)
                else:
                    self._hashlist[itemname] = self.sha256(s)   #finding the hash of the concatenated hashes(non-leaf node of tree)
            else:                                               #if item is a file and not a dir
                if rootdir == self._root:                   #check if given file is in root dir or sub-dir - for chosing the key(of hashlist) accordingly
                    self._hashlist[item] = self.sha256(item)    #finding the hash of the file
                else:
                    self._hashlist[itemname] = self.sha256(itemname)    #finding the hash of the file
 
def MTDiff(mt_a, a_tophash, mt_b, b_tophash):
    if a_tophash == b_tophash:
        print("Top hash is equal for %s and %s" % (mt_a._root, mt_b._root))
    else:
        a_value = mt_a._mt[a_tophash] 
        a_child = a_value[1]    # retrive the child list for merkle tree a
        b_value = mt_b._mt[b_tophash] 
        b_child = b_value[1]    # retrive the child list for merkle tree b

        for itemhash, item in a_child.items():
            try:
                if b_child[itemhash] == item:
                    print("Info: SAME : %s" % item)
            except:
                print("Info: DIFFERENT : %s" % item)
                temp_value = mt_a._mt[itemhash]
                if len(temp_value[1]) > 0:      # check if this is a directory
                    diffhash = list(set(b_child.keys()) - set(a_child.keys()))
                    MTDiff(mt_a, itemhash, mt_b, diffhash[0])
                
if __name__ == "__main__":
    mt_a = MarkleTree('testA')
    print(mt_a._mt)
    mt_b = MarkleTree('testB')
    MTDiff(mt_a, mt_a._tophash, mt_b, mt_b._tophash)

