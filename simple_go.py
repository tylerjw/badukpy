#Simple Go playing program
#Goals are:
#1) Easy to understand:
#   If fully understanding GnuGo could be considered advanced,
#   then this should be beginner level Go playing program
#   Main focus is in understanding code, not in fancy stuff.
#   It should illustrate Go concepts using simple code.
#2) Plays enough well to get solid rating at KGS
#3) Small
#4) License should be GPL compatible: probably multiple licenses.

#Why at Senseis?
#Goal is to illustrate Go programming and not to code another "GnuGo".
#Senseis looks like good place to co-operatively write text and 
#create diagrams to illustrate algorithms.
#So main focus is in explaining code.
#Also possibility is to crosslink between concepts and documented code.


import re, string, time, random, sys
from types import *
from math import sqrt
from copy import deepcopy

EMPTY = "."
BLACK = "X"
WHITE = "O"

colors = [BLACK, WHITE]

other_side = {BLACK: WHITE, WHITE: BLACK}

PASS_MOVE = (-1, -1)

x_coords_string = "ABCDEFGHJKLMNOPQRSTUVXYZ"

def move_as_string(move, board_size):
    """convert move tuple to string
          example: (2, 3) -> B3
    """
    if move==PASS_MOVE: return "PASS"
    x, y = move
    return x_coords_string[x-1] + str(y)

def string_as_move(m, size):
    """convert string to move tuple
          example: B3 -> (2, 3)
    """
    if m=="PASS": return PASS_MOVE
    x = string.find(x_coords_string, m[0]) + 1
    y = int(m[1:])
    return x,y

class Board:
    def __init__(self, size):
        """Initialize board:
              argument: size
        """
        self.size = size
        self.side = BLACK #side to move
        self.captures = {} #number of stones captured
        self.captures[WHITE] = 0
        self.captures[BLACK] = 0
        self.groups = {}
        self.groups[WHITE] = None
        self.groups[BLACK] = None
        
        self.territory_white = 0
        self.territory_black = 0

        self.goban = {} #actual board
        #Create and initialize board as empty size*size
        for pos in self.iterate_goban():
            self.goban[pos] = EMPTY
        #empty groups
        self.groups[EMPTY] = [self.goban.keys()]

    def __eq__(left, right):
        if (left.captures == right.captures and
            left.groups == right.groups and
            left.goban == right.goban):
            return True
        return False

    def __ne__(left, right):
        if not left.__eq__(right):
            return True
        return False

    def iterate_goban(self):
        """This goes trough all positions in goban
              Example usage: see above __init__ method
        """
        for x in range(1, self.size+1):
            for y in range(1, self.size+1):
                yield x, y

    def iterate_neighbour(self, pos):
        """This goes trough all neighbour positions:
              down, up, left, right
              Example usage: see legal_move method
        """
        x, y = pos
        for x2,y2 in ((x,y-1), (x,y+1), (x-1,y), (x+1,y)):
            if 1<=x2<=self.size and 1<=y2<=self.size:
                yield (x2, y2)

    def get_pos_list(self, side):
        """This goes through all positions in goban
            and returns a list of positions of the given side
        """
        output = []
        for pos in self.iterate_goban():
            if self.goban[pos] == side:
                output.append(pos)
        return output

    def print_groups(self, groups):
        """Converts the list of list chains to string format
        """
        if not groups:
            return None
        output = []
        for group in groups:
            output.append(self.print_group(group))
        return output

    def print_group(self, group):
        line = []
        for point in group:
            line.append(move_as_string(point, self.size))
        return line

    def key(self):
        """This returns unique key for board.
              Returns board as string.
              Key can be used for example in super-ko detection
        """
        stones = []
        for pos in self.iterate_goban():
            stones.append(self.goban[pos])
        return string.join(stones, "")

    def change_side(self):
        self.side = other_side[self.side]

    def legal_move(self, move):
        """Test whether given move is legal.
              Returns truth value.

              Returns false if play would result in suicide
        """
        if move==PASS_MOVE:
            return True
        if move not in self.goban: return False
        if self.goban[move]!=EMPTY: return False
        for pos in self.iterate_neighbour(move): # prevent suicide
            # neighboor is empty
            if self.goban[pos]==EMPTY: return True
            # neighboor is own chain, check that chain has more that one liberty (prevent suicide)
            if self.goban[pos]==self.side and self.liberties(pos)>1: return True
            # neighboor is opponent, and they only have one liberty = capture
            if self.goban[pos]==other_side[self.side] and self.liberties(pos)==1: return True
        return False

    def calculate_territory(self):
        """
            Calculate territory for both colors.
            To calculate actual score see Game class
        """
        liberty_pos_white = []
        liberty_pos_black = []
        
        for group in self.groups[WHITE]:
            liberty_pos_white.append(liberties_group(group))
            
        for group in self.groups[BLACK]:
            liberty_pos_black.append(liberties_group(group))
            
        for pos in liberty_pos_white:
            if pos in liberty_pos_black:
                liberty_pos_white.remove(pos)
                liberty_pos_black.remove(pos)
                
        self.territory_white = liberty_pos_white.length
        self.territory_black = liberty_pos_black.length

    def liberties(self, pos):
        """Count liberties for group at given position.
              Returns number of liberties.
              This is simple flood algorith tha keeps track of stones and empty intersections visited.
              pos_list keeps track of stones we need to visit.
              pos_list starts with argument pos.
              We go trough each stone in pos_list.
              First we check whether we have already seen this position and skip it if it so.
              Then we go trough each neighbour intersection skipping those we have already seen.
              If intersection is empty we add to liberty_count and mark this as visited.
              If intersection belongs to same group we add it to stones to go trough (pos_list).
              If it gets added more than once that is not problem because we as first step skip stones already seen.
              It would be more complex to check for duplicates now: we would need to check both seen_pos and pos_list.
              TODO: add senseis diagram illustrating algorithm.
        """
        seen_pos = {}
        liberty_count = 0
        group_color = self.goban[pos]
        pos_list = [pos]
        while pos_list:
            pos2 = pos_list.pop()
            if pos2 in seen_pos: continue
            seen_pos[pos2] = True
            for pos3 in self.iterate_neighbour(pos2):
                if pos3 in seen_pos: continue
                if self.goban[pos3]==EMPTY:
                    liberty_count = liberty_count + 1
                    seen_pos[pos3] = True
                    continue
                if self.goban[pos3]==group_color:
                    pos_list.append(pos3)
        return liberty_count

    def group(self, pos):
        '''Find the group that pos exists in
        '''
        for g in self.groups[self.goban[pos]]:
            if pos in g:
                return g
        return None

    def liberties_pos(self, pos):
        '''Find liberties given a pos attached to a group
        '''
        color = self.goban[pos]
        group = self.group(pos)
        if group:
            return self.liberties_group(group)
        return None

    def liberties_group(self, group):
        '''Find liberties given group(list of points)
        '''
        liberties = {}
        for pos in group:
            for neighbour in self.iterate_neighbour(pos):
                if self.goban[neighbour] == EMPTY:
                    liberties[neighbour] = True
        return liberties.keys()

    

    def is_vital(self, group, empty_group):
        '''Find empty groups that neighbor the given group
        Vital: All empty points are also liberties to the chain.
        '''
        liberties = self.liberties_group(group)
        for pos in empty_group:
            if pos not in liberties:
                return False
        return True

    def get_alive(self, color):
        '''
        Initially, let X be the set of Black chains, and let R be the
        set of Black-enclosed regions of X. We perform the following
        two steps repeatedly:

        1.Remove from X all Black chains with less than two vital
        Black-enclosed regions in R.
        2.Remove from R all Black-enclosed regions with a surrounding
        stone in a chain not in X. 

        We stop the algorithm when either step fails to remove any item.
        The resultant set X is then the desired set of unconditionally
        alive Black chains.
        '''

        repeat = True
        X = deepcopy(self.groups[color])
        X_flat = []
        for group in X:
            for pos in group:
                X_flat.append(pos)
                
        R = deepcopy(self.groups[EMPTY])
        while repeat:
            repeat = False
            X_rem = []
            for i,group in enumerate(X):
                vital = 0
                for region in R:
                    if self.is_vital(group,region):
                        vital += 1
                if vital < 2:
                    repeat = True
                    X_rem.append(i)
                    for pos in group:
                        X_flat.remove(pos)
            X_rem.reverse()
            for i in X_rem:
                X.pop(i)
            R_rem = []
            for i,region in enumerate(R):
                for pos in region:
                    flag = False
                    for nei in self.iterate_neighbour(pos):
                        if self.goban[nei] != EMPTY and (nei not in X_flat):
                            #the other color is a neighbour or a point not in X of the same color
                            repeat = True
                            flat = True
                            if i not in R_rem:
                                R_rem.append(i)
                            break
                    if flag: break
            R_rem.reverse()
            for i in R_rem:
                R.pop(i)

            if (len(X) == 0):
                repeat = False
                
        return X
                

    def remove_group(self,  pos):
        """Recursively remove given group from board and updating capture counts.
              First we remove this stone and then recursively call ourself to remove neighbour stones.
        """
        remove_color = self.goban[pos]
        self.goban[pos] = EMPTY
        self.captures[remove_color] = self.captures[remove_color] + 1
        for pos2 in self.iterate_neighbour(pos):
            if self.goban[pos2] == remove_color:
                self.remove_group(pos2)

    def __update_groups(self, move):
        ''' utility function for updating groups lists
            Assert: move already made (not EMPTY)

        1. If there are no groups for given side just create a new group
        and assign the point.
        2. Look at all neighbors of move and see if it connects to an
        existing group, if so add to that group.
        3. Test to see if this move combined groups, if so combine the
        groups
        4. If move did not join existing group, create new group with
        move
        5. Remove the position from the empty group it is in and note the
        index of that group
        6. If the position removed was the last one to be removed from the
        group, delete the group and be done
        7. There could be up to 4 empty groups broken off by playing a
        stone, check to see if neighbors of move are in the empty group
        just played into, and if so create new temporary groups with each
        of them.
        8. Going point by point until all points find a home check to see
        if they neighbor any point in a given group
        9. If they neighbor points in two groups those groups get combined
        10. If the resulting list of temporary groups has more than 1
        group, pop off the old empty group and add the new split ones
        '''
        # is this the first move
        if self.groups[self.side] == None:
            self.groups[self.side] = [[move]]
        else:
            # update group lists
            groups = []
            # Does this move connect to an existing group
            for neighbour in self.iterate_neighbour(move):
                for i, group in enumerate(self.groups[self.side]):
                    if neighbour in group:
                        if(len(groups)==0): #only add to the first one
                            group.append(move)
                        if i not in groups: #prevent multiple additions
                            groups.append(i)
            # Was not found
            if len(groups) == 0:
                self.groups[self.side].append([move])
            # Found in multiple groups
            elif len(groups) > 1:
                groups.sort() #order the groups
                remove = sorted(groups[1:],reverse=True) #create a list of lists to move
                for i in remove:
                    self.groups[self.side][groups[0]] += self.groups[self.side][i]
                    self.groups[self.side].pop(i)

        # empty group manipulation
        groups = []
        # remove from empty group
        index = 0
        done = False
        for i,group in enumerate(self.groups[EMPTY]):
            if move in group:
                group.remove(move)
                index = i
                if len(group)==0: #last item in group
                    self.groups[EMPTY].pop(i)
                    done = True
                break
        if not done:
            original = deepcopy(self.groups[EMPTY][index])
            for neighbour in self.iterate_neighbour(move):
                if neighbour in original:
                    groups.append([neighbour])
                    original.remove(neighbour)
            while len(original)>0:
                for pos in original:
                    found = []
                    for i,group in enumerate(groups):
                        for item in group:
                            if self.is_neighbour(item,pos):
                                if len(found)<1:
                                    group.append(pos)
                                    original.remove(pos)
                                if i not in found: #don't double add... results in double remove
                                    found.append(i)
                    if len(found) > 1: #combine groups
                        found.sort() #order the groups
                        remove = sorted(found[1:],reverse=True) #create a list of lists to move
                        for i in remove:
                            groups[found[0]] += groups[i]
                            groups.pop(i)

            if(len(groups)>1):
                #out with the old, in with the new
                self.groups[EMPTY].pop(index)
                for g in groups:
                    self.groups[EMPTY].append(g)
                
    def is_neighbour(self,pos1,pos2):
        '''Utility function for testing if one function is a neighbour of another.
        '''
        for n in self.iterate_neighbour(pos1):
            if n == pos2:
                return True
        return False

    def make_move(self, move):
        """Make move given in argument.
              Returns move or None if illegl.
              First we check given move for legality.
              Then we make move and remove captured opponent groups if there are any.

              Keeps track of groups lists
        """
        if move==PASS_MOVE:
            self.change_side()
            return move
        if self.legal_move(move):
            self.goban[move] = self.side #make move

            # update groups
            self.__update_groups(move)

            # check if a group was captured and needs to be removed
            remove_color = other_side[self.side]
            for pos in self.iterate_neighbour(move):
                if self.goban[pos]==remove_color and self.liberties(pos)==0:
                    self.remove_group(pos)
                    # remove from groups list
                    for i,group in enumerate(self.groups[remove_color]):
                        if pos in group:
                            temp = self.groups[remove_color].pop(i)
                            # if a group is removed, it should be addedd as an empty group.
                            self.groups[EMPTY].append(temp) 
                            break
                    
            self.change_side() # change side
            return move
        return None

    def put_stone(self, pos, color):
        """
            Might need this to handle handicap stones and have make_move-like methods
            handle more complex tasks (de-coupling between make a move and the whole logic behind it)
        """
        self.goban[pos] = color

    def __str__(self):
        """Convert position to string suitable for printing to screen.
              Returns board as string.
        """
        s = self.side + " to move:\n"
        s = s + "Captured stones: "
        s = s + "White: " + str(self.captures[WHITE])
        s = s + " Black: " + str(self.captures[BLACK]) + "\n"
        s = s + "Groups: \n"
        s = s + "Black: " + str(self.print_groups(self.groups[BLACK])) + '\n'
        s = s + "White: " + str(self.print_groups(self.groups[WHITE])) + '\n'
        s = s + "Empty: " + str(self.print_groups(self.groups[EMPTY])) + '\n'
        board_x_coords = "   " + x_coords_string[:self.size]
        s = s + board_x_coords + "\n"
        s = s + "  +" + "-"*self.size + "+\n"
        for y in range(self.size, 0, -1):
            if y < 10:
                board_y_coord = " " + str(y)
            else:
                board_y_coord = str(y)
            line = board_y_coord + "|"
            for x in range(1, self.size+1):
                line = line + self.goban[x,y]
            s = s + line + "|" + board_y_coord + "\n"
        s = s + "  +" + "-"*self.size + "+\n"
        s = s + board_x_coords + "\n"
        return s

class Game:
    def __init__(self, size):
        """Initialize game:
           argument: size
        """
        self.size = size
        self.current_board = Board(size)
        #past boards and moves
        self.board_history = []
        self.move_history = []
        #for super-ko detection
        self.position_seen = {}
        self.position_seen[self.current_board.key()] = True
        
        #TODO: handle komi?
        self.komi = 6.5

    def make_move_in_new_board(self, move):
        """This is utility method.
              This does not check legality.
              It returns move in copied board and also key of new board
        """
        new_board = deepcopy(self.current_board)
        new_board.make_move(move)
        board_key = new_board.key()
        return new_board, board_key

    def legal_move(self, move):
        """check whether move is legal
              return truth value
              first check move legality on current board
              then check for repetition (situational super-ko)
        """
        if move==PASS_MOVE:
            return True
        if not self.current_board.legal_move(move): return False
        new_board, board_key = self.make_move_in_new_board(move)
        if board_key in self.position_seen: return False
        return True

    def make_move(self, move):
        """make given move and return new board
              or return None if move is illegal
              First check move legality.
              Then make move and update history.
        """
        if not self.legal_move(move): return None
        new_board, board_key = self.make_move_in_new_board(move)
        self.move_history.append(move)
        self.board_history.append(self.current_board)
        if move!=PASS_MOVE:
            self.position_seen[board_key] = True
        self.current_board = new_board
        return new_board

    def undo_move(self):
        """undo latest move and return current board
              or return None if at beginning.
              Update repetition history and make previous position current.
        """
        if not self.move_history: return None
        last_move = self.move_history.pop()
        if last_move!=PASS_MOVE:
            del self.position_seen[self.current_board.key()]
        self.current_board = self.board_history.pop()
        return self.current_board

    def calculate_score(self):
        Board.calculate_territory()
        Board.territory_white = Board.territory_white + self.komi

    def list_moves(self):
        """return all legal moves including pass move
        """
        all_moves = [PASS_MOVE]
        for move in self.current_board.iterate_goban():
            if self.legal_move(move):
                all_moves.append(move)
        return all_moves

    def select_random_move(self):
        """return randomly selected move from all legal moves
        """
        return random.choice(self.list_moves())

    def generate_move(self):
        """generate move using random move generator
        """
        return self.select_random_move()


def main():
    size = 5
    g = Game(size)
    while True:
        move = g.generate_move()
        g.make_move(move)
        print move_as_string(move, g.size)
        print g.current_board
        #if last 2 moves are pass moves: exit loop
        if len(g.move_history)>=2 and \
           g.move_history[-1]==PASS_MOVE and \
           g.move_history[-2]==PASS_MOVE:
            break
        
def grouping_test():
    size = 5
    g = Game(size)
    for i in range(20):
        move = g.generate_move()
        g.make_move(move)
        print move_as_string(move, g.size)
        print g.current_board

def life_test():
    size = 5
    g = Game(size)
    black = ['A5','A4','B4','C4','C5','D4','E4']
    white = ['A2','B2','B1','C2','D2','E2','E3']
    moves = []
    for i in range(7):
        moves.append(string_as_move(black[i], g.size))
        moves.append(string_as_move(white[i], g.size))

    for m in moves:
        g.make_move(m)
        print g.current_board

    print "Unconditionally Alive:"
    print "Black: ",g.current_board.print_groups(g.current_board.get_alive(BLACK))
    print "White: ",g.current_board.print_groups(g.current_board.get_alive(WHITE))
        
    
if __name__=="__main__":
    life_test()

