import cursor, random, time
from enum import Enum
from os import system
from msvcrt import kbhit, getch
from colorama import init, Fore, Back, Style, Cursor, deinit
from dataclasses import dataclass

class Direction(Enum):
    UP = 'w'
    DOWN = 's'
    LEFT = 'a'
    RIGHT = 'd'

OPPOSITE_DIRECTIONS = {
        Direction.UP: Direction.DOWN,
        Direction.DOWN: Direction.UP,
        Direction.LEFT: Direction.RIGHT,
        Direction.RIGHT: Direction.LEFT,
        }

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

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y))

    def clone(self):
        return Coord(*self)

COORD_DIRECTION = {
        Coord(0, -1): Direction.UP,
        Coord(0, 1): Direction.DOWN,
        Coord(-1, 0): Direction.LEFT,
        Coord(1, 0): Direction.RIGHT,
        }

DIRECTION_COORD = {
        Direction.UP: Coord(0, -1),
        Direction.DOWN: Coord(0, 1),
        Direction.LEFT: Coord(-1, 0),
        Direction.RIGHT: Coord(1, 0),
        }

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

    def push_front(self, *vals: [any]) -> 'ListNode':
        for val in vals:
            self = ListNode(val, self)
        return self

    def push(self, *vals: [any]):
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

    def reverse(self) -> 'ListNode':
        n = self
        prev = None
        while n:
            n.next, n, prev = prev, n.next, n
        return prev

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
    move_cursor = lambda self, pos: print(Cursor.POS(*pos),end='')

    def __init__(self):
        self.board_size = Coord(80, 40)
        self.window_size = self.board_to_screen(self.board_size) + Coord(1, 1)
        self.snake = ListNode(self.board_size // 2)
        self.length_to_add = 2
        self.direction = Direction.UP
        self.running = True
        self.fruit = self.get_new_fruit()
        self.score = 0

    def empty_spots(self):
        result = []
        for i in range(self.board_size.y):
            for j in range(self.board_size.x):
                c = Coord(j, i)
                if c not in self.snake:
                    result.append(c)
        return result

    def get_new_fruit(self):
        return random.choice(self.empty_spots())

    def board_to_screen(self, pos):
        pos = Coord(*pos)
        return pos * Coord(2, 1) + Coord(3, 2)

    def setup_window(self):
        system(f'mode con: cols={self.window_size.x} lines={self.window_size.y}')
        print(Back.WHITE + ' ' * self.window_size.x, end = '')
        for _ in range(self.window_size.y - 3):
            print(Back.WHITE + '  '  + Back.BLACK + ' ' * (self.window_size.x - 4) + Back.WHITE + '  ', end = '')
        print(Back.WHITE + ' ' * self.window_size.x + Style.RESET_ALL, end = '')

    def draw_tail_piece(self, pos: Coord):
        self.move_cursor(self.board_to_screen(pos))
        print(Back.BLUE + Fore.LIGHTBLUE_EX + '▒▒' + Style.RESET_ALL)

    def draw_head_piece(self, pos: Coord):
        self.move_cursor(self.board_to_screen(pos))
        print(Back.BLUE + Fore.LIGHTBLUE_EX + 'XX' + Style.RESET_ALL)

    def draw_fruit_piece(self, pos: Coord):
        self.move_cursor(self.board_to_screen(pos))
        print(Back.RED + '  ' + Style.RESET_ALL)

    def erase_piece(self, pos: Coord):
        self.move_cursor(self.board_to_screen(pos))
        print('  ')

    def collide(self, pos: Coord) -> bool:
        return (pos.x < 0 or
                pos.y < 0 or
                pos.x >= self.board_size.x or
                pos.y >= self.board_size.y or
                pos in self.snake)

    def update_score(self):
        self.move_cursor((1, self.window_size.y))
        print(f'Score: {self.score}', end = '')

    def update(self):
        pos = self.snake.val.clone() + DIRECTION_COORD[self.direction]
        if self.collide(pos):
            self.running = False
            return
        elif pos == self.fruit:
            self.fruit = self.get_new_fruit()
            self.score += 1
            self.update_score()
            self.length_to_add += 2
        self.erase_piece(self.snake.tail().val)
        self.snake = self.snake.push_front(pos)
        if self.length_to_add == 0:
            self.snake.pop()
        else:
            self.length_to_add -= 1
        self.draw_fruit_piece(self.fruit)
        self.draw_head_piece(self.snake.val)
        self.draw_tail_piece(self.snake.next.val)

    def keyboard_input(self):
        if not kbhit():
            return
        ch = getch().decode('utf-8').lower()
        if ch in 'wasd':
            d = Direction(ch)
            if self.direction is not OPPOSITE_DIRECTIONS[d]:
                self.direction = d
        elif ch == 'r':
            # TODO: DON'T JUST REVERSE DIRECTION BUT FIND THE CORRECT DIRECTION
            self.direction = OPPOSITE_DIRECTIONS[self.direction]
            self.snake = self.snake.reverse()

    def run(self):
        self.setup_window()
        self.update_score()
        while self.running:
            self.update()
            self.keyboard_input()
            time.sleep(0.1)

if __name__ == '__main__': # driver code
    init()
    cursor.hide()
    try:
        SnakeGame().run()
    finally:
        cursor.show()
        deinit()
