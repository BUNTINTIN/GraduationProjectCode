#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
File: test_binary_tree.py
Author: liuzihang(liuzihang@baidu.com)
Time: 2019-04-04 15:55:28
Descript:测试二叉树
"""
import sys
import json

class Node:
    def __init__(self,item):
        self.item = item
        self.child1 = None
        self.child2 = None
        self.father = None

class Tree:
    def __init__(self):
        self.root = None

    def add(self, item):
        node = Node(item)
        if self.root is None:
            self.root = node
        else:
            q = [self.root]
            father_node = self.root

            while True:
                pop_node = q.pop(0)
                father_node = pop_node
                if pop_node.child1 is None:
                    node.father = father_node
                    pop_node.child1 = node
                    return
                elif pop_node.child2 is None:
                    node.father = father_node
                    pop_node.child2 = node
                    return
                else:
                    q.append(pop_node.child1)
                    q.append(pop_node.child2)

    def traverse(self):  # 层次遍历
        if self.root is None:
            return None
        q = [self.root]
        res = [self.root.item, '(father:None)']
        while q != []:
            pop_node = q.pop(0)
            if pop_node.child1 is not None:
                q.append(pop_node.child1)
                res.append(pop_node.child1.item)
                res.append('(father:' + str(pop_node.child1.father.item) + ')')

            if pop_node.child2 is not None:
                q.append(pop_node.child2)
                res.append(pop_node.child2.item)
                res.append('(father:' + str(pop_node.child1.father.item) + ')')
        return res

    def preorder(self,root):  # 先序遍历
        if root is None:
            return []
        result = [root.item]
        left_item = self.preorder(root.child1)
        right_item = self.preorder(root.child2)
        return result + left_item + right_item

    def inorder(self,root):  # 中序序遍历
        if root is None:
            return []
        result = [root.item]
        left_item = self.inorder(root.child1)
        right_item = self.inorder(root.child2)
        return left_item + result + right_item

    def postorder(self,root):  # 后序遍历
        if root is None:
            return []
        result = [root.item]
        left_item = self.postorder(root.child1)
        right_item = self.postorder(root.child2)
        return left_item + right_item + result

if __name__ == '__main__':
    t = Tree()
    for i in range(10):
        t.add(i)
    print('层序遍历:',t.traverse())
    print('先序遍历:' + json.dumps(t.preorder(t.root)))
    print('中序遍历:',t.inorder(t.root))
    print('后序遍历:',t.postorder(t.root))

