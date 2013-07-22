'''
Game Tree for badukpy

'''

EMPTY = "."
BLACK = "X"
WHITE = "O"

colors = [BLACK, WHITE]

other_side = {BLACK: WHITE, WHITE: BLACK}
sgf_side = {BLACK: 'B', WHITE: 'W'}

PASS_MOVE = (-1, -1)

class Node:
    def __init__(self,previous,index,move,side,board_hash,captures):
        self.next = []  #updomming nodes
        self.previous = previous #the node before this one
        if previous:
            self.path = previous.path + [index] #add index in next to path
        else:
            self.path = [index] #a first move
        self.move = move
        self.side = side
        self.board_hash = board_hash # for ko test
        self.captures = captures

class GoGameTree:
    def __init__(self,bp=None,wp=None):
        self.black_placed = bp #stones placed by black on the first move
        self.white_placed = wp #white stones placed
        self.current = None
        self.firsts = [] #first moves, allowing multiple first moves

    def walk(self,root=None):
        ''' if root is none, walks the whole tree,
            otherwise starts at the given root,
            recursive depth tree traverse
        '''
        if root:
            yield root
            for item in root.next:
                self.walk(item)
        else:
            for item in self.firsts:
                self.walk(item)

    def series(self,path):
        '''
        generator for getting nodes in a path
        '''
        cursor = firsts[path[0]]
        yield cursor
        if len(path) > 1:
            for index in path[2:]:
                cursor = cursor.next[index]
                yield cursor
            
    def make_move(move,captures,board_hash):
        ''' make a move if ko test passes
            if ko test fails, return false
            else add move, advance current, and return true
        '''
        #if current is None, first move
        if self.current == None:
            index = len(self.firsts)
            self.current = Node(None,index,BLACK,board_hash,captures)
            self.firsts.append(self.current)
            return True

        #ko test - make sure board hash isn't in current path
        hashes = [node.board_hash for node in self.series(self.cursor.path)]
        if board_hash in hashes:
            return False

        index = len(self.current.next)
        new_node = Node(self.current,index,other_side[self.current.side],
                        board_hash,captures)
        self.current.next.append(new_node)
        self.current = new_node
        return True

    def undo_move(self):
        ''' Undo a move, if current is none (first move) return None '''
        if self.current == None:
            return None
        old = self.current
        self.current = self.current.previous
        return old
        
