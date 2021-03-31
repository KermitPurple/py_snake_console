from dataclasses import dataclass
from colorama import init, Fore, Back, Style, Cursor

@dataclass
class Coord:
    """A class to represent a point in 2D space or a vector in R2"""
    x: int
    y: int

    def __iter__(self):
        yield self.x
        yield self.y

    def __add__(self, other):
        if type(other) is int:
            return Coord(self.x + other, self.y + other)
        elif type(other) is Coord:
            return Coord(self.x + other.x, self.y + other.y)
        else:
            raise TypeError(f'Cannot add {type(other)} and Coord')

    def __sub__(self, other):
        if type(other) is int:
            return Coord(self.x - other, self.y - other)
        elif type(other) is Coord:
            return Coord(self.x - other.x, self.y - other.y)
        else:
            raise TypeError(f'Cannot subtract {type(other)} from Coord')

    def __mul__(self, other):
        if type(other) is int:
            return Coord(self.x * other, self.y * other)
        elif type(other) is Coord:
            return Coord(self.x * other.x, self.y * other.y)
        else:
            raise TypeError(f'Cannot multiply {type(other)} and Coord')

    def __rmul__(self, other):
        return self * other

    def __div__(self, other):
        return self.__floordiv__(self, other)

    def __floordiv__(self, other):
        if type(other) is int:
            return Coord(self.x // other, self.y // other)
        elif type(other) is Coord:
            return Coord(self.x // other.x, self.y // other.y)
        else:
            raise TypeError(f'Cannot divide {type(other)} and Coord')

@dataclass
class ListNode:
    """A class to represent a single node in a linked list"""
    val: any
    next: 'ListNode' = None

    def tail(self) -> 'ListNode':
        n = self
        while n.next:
            n = n.next
        return n

    def push(self, *vals: any):
        for val in vals:
            self.tail().next = ListNode(val)

    def pop(self) -> any:
        n = self
        prev = self
        while n.next:
            prev = n
            n = n.next
        val = n.val
        prev.next = None
        return val

    @staticmethod
    def from_iter(iterator):
        head = ListNode(iterator[0])
        head.push(*iterator[1:])
        return head

    def __iter__(self):
        n = self
        while n:
            yield n.val
            n = n.next

    def __repr__(self):
        s = str(self.val)
        n = self.next
        while n:
            s += ' -> ' + str(n.val)
            n = n.next
        return s


class SnakeGame:
    """A console-based snake application"""
    def __init__(self):
        self.board_size = Coord(50, 50)
        self.snake = ListNode(self.board_size // 2)

    def run(self):
        pass

move_cursor = lambda pos: print(Cursor.POS(*pos),end='')

if __name__ == '__main__': # driver code
    init()
    SnakeGame().run()
