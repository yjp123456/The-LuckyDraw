#!/usr/bin/python2.7
#coding=utf8
r'''
Fuction: 
Created: Tuyj
Created date:2015/07/21
'''
class tNode:
    def __init__(self, id, data):
        self._id,self._data = id,data
        self._father = None
        self._children = []
        self.wait_father_id = None
 
    def id(self):
        return self._id
 
    def data(self):
        return self._data
 
    def children(self):
        return self._children
 
    def father(self):
        return self._father
 
    def updata(self, data):
        self._data = data
 
    def add(self, node):
        if self._children.count(node) == 0:
            self._children.append(node)
        node._onadd(self)
    
    def remove(self, node):
        if self._children.count(node) > 0:
            self._children.remove(node)
        node._onadd(None)
    
    def go(self, id):
        if id == self._id:
            return self
        for child in self._children:
            if child.id() == id:
                return child
        return None
    
    def waitFather(self, id=None):
        if id:
            self.wait_father_id = id
        return self.wait_father_id
        
    def gotWaitFather(self):
        self.wait_father_id = None
    
    def _onadd(self, node):
        self._father = node
 
class tTree:
    def __init__(self, topValues=None, topNode=None):
        if topValues:
            self._head = tNode(*topValues)
        elif topNode:
            self._head = topNode
        else:
            self._head = tNode(None, None)
 
    def checkWait(self):
        checking = True
        while checking:
            for child in self._head.children():
                if child.waitFather() is None:
                    continue
                if self._checkWait(child):
                    break
            checking = False
 
    def searchById(self, id):
        return self._searchById(self._head, id)
 
    def searchByPath(self, id_path):
        cur = self._head
        for step in id_path:
            next = cur.go(step)
            if next == None:
                return None
            else:
                cur = next
        return cur
    
    def insertByPath(self, id_path, datas):
        space_len = len(id_path) - len(datas)
        if space_len < 0:
            raise ValueError("datas len larger than path len")
        elif space_len > 0:
            spaces = [None] * space_len
            datas = spaces + datas
        return self._updateByPath(id_path, datas)

    def insertById(self, father_id, id, data, force=False):
        father = self.searchById(father_id)
        if father:
            new_node = tNode(id, data)
            father.add(new_node)
            return new_node
        else:
            if force:
                new_node = tNode(id, data)
                self._head.add(new_node)
                new_node.waitFather(father_id)
                return new_node
            else:
                return None
 
    def updataById(self, id, data):
        the = self.searchById(id)
        if the:
            the.updata(data)
            return True
        else:
            return False
 
    def changeFather(self, father, child):
        if not isinstance(father, tNode):
            father_ = self.searchById(father)
            if not father_:
                return False,father
            father = father_
        if not isinstance(child, tNode):
            child_ = self.searchById(child)
            if not child_:
                return False,child
            child = child_
        old_f = child.father()
        if old_f is not None:
            old_f.remove(child)
        father.add(child)
        return True,None
 
    def _checkWait(self, wait_node):
        father_id = wait_node.waitFather()
        ret,err = self.changeFather(father_id, wait_node)
        if ret:
            wait_node.gotWaitFather()
        return  ret
 
    def _updateByPath(self, id_path, datas):
        father_path = id_path[:-1]
        new_id = id_path[-1]
        father = self.searchByPath(father_path)
        if not father:
            father = self._updateByPath(father_path, datas[:-1])
        the = father.go(new_id)
        if the:
            the.updata(datas[-1])
        else:
            the = tNode(new_id, datas[-1])
            father.add(the)
        return the
 
    def _searchById(self, node, id):
        if node.id() == id:
            return node
        for child in node.children():
            if child.id() == id:
                return child
        for child in node.children():
            re = self._searchById(child, id)
            if re: return re
        return None
    
    def dict(self, need_data=True):
        out = {}
        self._dict(self._head, out, need_data)
        return out
    
    def list(self):
        out = []
        self._list(self._head, out)
        return out
            
    def _dict(self, node, out, need_data):
        next_out = {}
        if need_data:
            out[node.id()] = [node.data(), next_out]
        else:
            out[node.id()] = next_out
        for child in node.children():
            self._dict(child, next_out, need_data)
    
    def _list(self, node, out):
        value = {
            "id": node.id(),
            "data": node.data()
        }
        if node.father() is not None:
            value["fid"] = node.father().id()
        else:
            value["fid"] = None
        out.append(value)
        for child in node.children():
            self._list(child, out)

if __name__ == '__main__':
    one = tTree()
#    one.insertByPath([0,1,2,3,4], ['1','2','3','4'])
#    one.insertByPath([0,1,2,3,5], ['5'])
#    one.insertById(0, 7, '-7')
#    one.insertById(0, -1, '-1')
#    one.changeFather(-1, 1)
#    node9 = one.insertById(8, 9, '9', True)
#    node9 = one.insertById(9, 10, '10', True)
#    node9 = one.insertById(11, 12, '12', True)
#    one.checkWait()
#    print one.dict()
#    one.insertById(7, 8, '8')
#    print one.dict()
#    one.checkWait()
#    print one.dict()
#    one.checkWait()
#    print one.dict()
#    print one.searchByPath([0,-1,1,2,3,4]).data()
#    print one.searchById(1).data()
#    print one.list()
    one.insertByPath([0,1,2], ['1','2'])
    one.insertByPath([0,1,3], ['1','3'])
    one.insertById(0, 4, '4')
    one.insertById(0, -1, '-1')
    one.changeFather(-1, 2)
    print one.dict()


