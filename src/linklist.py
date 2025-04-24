#------------------------------------------------
# name: linklist.py
# author: taster
# date: 2025-04-24 17:32:07 星期四
# id: d819b8d0125c2f0c4cdeadfb20c556f1
# description: 双向链表类
#------------------------------------------------

class Node:
    def __init__(self, value, front=None, tail=None):
        self.value = value
        self.front = front
        self.next = tail

class DoubleLink:
    def __init__(self):
        self.head = None
        self.tail = self.head

    def append(self, value):
        if self.head is None:
            self.head = Node(value)
            self.tail = self.head
            return
        tmpNode = Node(value, self.tail)
        self.tail.next = tmpNode
        self.tail = self.tail.next

    def current_state(self):
        if self.tail:
            return self.tail.value
        return None

    def next_state(self):
        if self.tail and self.tail.next:
            return self.tail.next.value
        return None

    def previous_state(self):
        if self.tail and self.tail.front:
            return self.tail.front.value
        return None

    def move_next(self):
        if self.tail and self.tail.next:
            self.tail = self.tail.next

    def move_previous(self):
        if self.tail and self.tail.front:
            self.tail = self.tail.front

    def clear(self):
        """清空，回到最初状态"""
        if self.head:
            self.head.next = None
