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
from math import sqrt
from copy import deepcopy
from sgflib import Collection,GameTree,Node,SGFParser,Property
from gametree import GoGameTree

EMPTY = "."
BLACK = "X"
WHITE = "O"

colors = [BLACK, WHITE]

other_side = {BLACK: WHITE, WHITE: BLACK}
sgf_side = {BLACK: 'B', WHITE: 'W'}

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

def move_to_sgf(m):
    if m == PASS_MOVE:
        return ''
    sgf = string.ascii_lowercase[m[0]-1] + string.ascii_lowercase[m[1]-1]
    return sgf

def sgf_to_move(sgf):
    if sgf == '':
        return PASS_MOVE
    move = (string.ascii_lowercase.index(sgf[0]), string.ascii_lowercase.index(sgf[1]))
    return move

def game_from_sgf(sgfdata, game_number=0):
    col = SGFParser(sgfdata).parse()
    cur = col.cursor(game_number)
    size = int(cur.node['SZ'][0])
    game = Game(size)

    #build moves list -- if it isn't in order in the file, bad things happen
    add_black = []
    add_white = []
    moves = []
    while 1:
        if cur.node.has_key('AB'):
            add_black += map(sgf_to_move, cur.node['AB'])
        elif cur.node.has_key('AW'):
            add_white += map(sfg_to_move, cur.node['AW'])
        elif cur.node.has_key('B'):
            moves.append(sgf_to_move(cur.node['B'][0]))
        elif cur.node.has_key('W'):
            moves.append(sgf_to_move(cur.node['W'][0]))
        if cur.atEnd: break
        cur.next()

    #add black and white (setup positions)
    if add_black:
        game.add_black(add_black)
    if add_white:
        game.add_white(add_white)

    #move the game along
    for move in moves:
        game.make_move(move)

    return game

class Board:
    def __init__(self, size):
        """Initialize board:
              argument: size
        """
        self.size = size
        self.side = BLACK  # side to move
        self.captures = {}  # number of stones captured
        self.captures[WHITE] = 0
        self.captures[BLACK] = 0
        self.groups = {}
        self.groups[WHITE] = None
        self.groups[BLACK] = None

        self.territory_white = 0
        self.territory_black = 0

        self.goban = {}  # actual board
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
        for x in range(1, self.size + 1):
            for y in range(1, self.size + 1):
                yield x, y

    def iterate_neighbour(self, pos):
        """This goes trough all neighbour positions:
              down, up, left, right
              Example usage: see legal_move method
        """
        x, y = pos
        for x2, y2 in ((x, y - 1), (x, y + 1), (x - 1, y), (x + 1, y)):
            if 1 <= x2 <= self.size and 1 <= y2 <= self.size:
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
        stones = [self.goban[pos] for pos in self.iterate_goban()]
        return string.join(stones, "")

    def hash_new_move(self, move):
        '''For ko test, does not have the overhead of make move
        '''
        test_board = deepcopy(self.goban)
        test_board[move] = self.side
        stones = [test_board[pos] for pos in self.iterate_goban()]
        key = string.join(stones, "")
        return key

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
            if self.goban[pos]==EMPTY:
                return True
            # neighboor is own chain, check that chain has more that one liberty (prevent suicide)
            if self.goban[pos]==self.side and self.liberties(pos)>1: return True
            # neighboor is opponent, and they only have one liberty = capture
            if self.goban[pos]==other_side[self.side] and self.liberties(pos)==1:
                return True
        return False

    def flatten(self, groups):
        '''for flattening groups'''
        flat = []
        for group in groups:
            for pos in group:
                if pos not in flat:
                    flat.append(pos)

        return flat

    def group_territory(self, group):
        """
        Calculate the territory that each group encloses. This assumes dead stones
        were already removed from the board
        """
        result = []

        opposite_side = other_side[self.goban[group[0]]]

        xs = [x[0] for x in group]
        ys = [y[1] for y in group]

        leftMost = min(xs)
        rightMost = max(xs)
        upMost = max(ys)
        downMost = min(ys)

        maxes = (leftMost, rightMost, upMost, downMost)

        for i in range(leftMost, rightMost):
            enemy_stones_y = [ePos for ePos in [(i, x) for x in range(downMost, upMost)] if self.goban[ePos] == opposite_side]
            for k in range(downMost, upMost):
                thisPos = (i, k)
                if self.goban[thisPos] != EMPTY:
                    continue
                enemy_stones_x = [ePos for ePos in [(x, k) for x in range(leftMost, rightMost)] if self.goban[ePos] == opposite_side]
                enemy_stones = enemy_stones_x + enemy_stones_y

                if enemy_stones != []:
                    e_xs = [x[0] for x in enemy_stones]
                    e_ys = [y[1] for y in enemy_stones]
                    e_maxes = (min(e_xs), max(e_xs), max(e_ys), min(e_ys))
                    thisPos_in_enemy_group = self.check_relative_stone_position(thisPos, enemy_stones, e_maxes)
                else:
                    thisPos_in_enemy_group = False

                thisPos_in_group = self.check_relative_stone_position(thisPos, group, maxes)

                if thisPos_in_group and not thisPos_in_enemy_group:
                    result.append(thisPos)

        return result

    def check_relative_stone_position(self, pos, group, maxes):
            inside_x_right = False
            inside_x_left = False
            inside_y_up = False
            inside_y_down = False

            for stone in group:
                if stone[0] == pos[0]:
                    if stone[1] > pos[1] or maxes[2] == self.size:
                        inside_y_up = True
                    if stone[1] < pos[1] or maxes[3] == 1:
                        inside_y_down = True
                if stone[1] == pos[1]:
                    if stone[0] < pos[0] or maxes[0] == 1:
                        inside_x_left = True
                    if stone[0] > pos[0] or maxes[1] == self.size:
                        inside_x_right = True
            return inside_x_right and inside_x_left and inside_y_up and inside_y_down

    def count_territory(self):
        """
            Calculate territory for both colors.
            To calculate actual score see Game class

            Japanese Counting
            1. the number of empty points your stones surround and
            2. the number of your opponent's stones you've captured
            (both during the game, and dead stones on the board at the end)
        """
        liberties_white = []
        liberties_black = []

        if self.groups[WHITE]:
            for group in self.groups[WHITE]:
                liberties_white += self.group_territory(group)
            self.territory_white = len(set(liberties_white))
        if self.groups[BLACK]:
            for group in self.groups[BLACK]:
                liberties_black += self.group_territory(group)
            self.territory_black = len(set(liberties_black))

        self.territory_white += self.captures[BLACK]
        self.territory_black += self.captures[WHITE]

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

    def undo_move(self, move, captures):
        '''
        undo a move
        --
        remove from goban
        remove from group
        restore captures to board
        restore captures to groups
        change sides
        '''
        self.goban[move] = EMPTY
        for group in self.groups[self.side]:
            if move in group:
                group.remove(move)
                break
        if len(captures) > 0:
            for pos in captures:
                self.goban[pos] = other_side[self.side]
            self.groups[other_side[self.side]].append(captures)
        self.side = other_side[self.side]

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
                    if len(groups) == 1:
                        done = True
                        break
                if done: break

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

    def make_move(self, move, change_sides=True):
        """Make move given in argument.
              Returns move or None if illegl.
              First we check given move for legality.
              Then we make move and remove captured opponent groups if there are any.

              Keeps track of groups lists
        """
        captures = []
        if move==PASS_MOVE:
            if change_sides: self.change_side()
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
                            captures = self.groups[remove_color].pop(i)
                            # if a group is removed, it should be addedd as an empty group.
                            self.groups[EMPTY].append(captures)
                            break

            if change_sides: self.change_side() # change side
            return captures
        return None

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
        self.sgf_game_tree = GameTree()
        self.sgf_game_tree.append(Node([Property('FF',['4']), #file format
                          Property('SZ',[str(self.size)]),#board size
                          Property('AP',['BadukPy'])])) #comment
        self.cur = self.sgf_game_tree.cursor()
        #past boards and moves
        self.board_history = []  #not used
        #for super-ko detection
        self.position_seen = {}
        self.position_seen[self.current_board.key()] = True

        #game tree
        self.game_tree = GoGameTree()

        #TODO: handle komi?
        self.komi = 6.5

    def add_white(self, moves):
        for move in moves:
            self.current_board.goban[move] = WHITE
        self.game_tree.white_placed = moves
        self.cur.add_white(map(move_to_sgf,moves))

    def add_black(self, moves):
        for move in moves:
            self.current_board.goban[move] = BLACK
        self.game_tree.black_placed = moves
        self.cur.add_black(map(move_to_sgf,moves))

    def make_move(self, move):
        """make given move and return new board
              or return None if move is illegal
              First check move legality.
              Then make move and update history.
        """
        if not self.current_board.legal_move(move): return None
        board_key = self.current_board.hash_new_move(move) #for ko test
        #add to game tree
        if not self.game_tree.make_move(move, board_key): return None
        #update sgf_game_tree
        self.cur.make_move(move_to_sgf(move),sgf_side[self.current_board.side])
        
        if move!=PASS_MOVE:
            self.position_seen[board_key] = True
        captures = self.current_board.make_move(move) #make the move
        self.game_tree.set_captures(captures)
        return self.current_board

    def undo_move(self):
        """undo latest move and return current board
              or return None if at beginning.
              Update repetition history and make previous position current.
        """
        move = self.game_tree.undo_move()
        if not move: return None

        #update game tree
        self.cur.undo_moves()
        
        captures = self.game_tree.get_captures()
        self.current_board.undo_move(move, captures)
        
        return self.current_board

    def score(self):
        ''' Get the current score
        '''
        self.current_board.count_territory()
        self.current_board.territory_white += self.komi

        return (self.current_board.territory_black, self.current_board.territory_white)

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

    def __str__(self):
        ''' print sfg string '''
        return str(self.sgf_game_tree)

    def move_history(self, distance):
        ''' returns a move in the history of the current game
            uses sgf_game_tree
            distance is a positive number,
            1 last move
            2 move before last
            ...
        '''
        if distance < 1:
            #bad input
            return None
        cur = self.gametree.cursor()
        #transverse to the end
        while not cur.atEnd:
            cur.next()

        for i in range(distance):
            cur.previous()

        move = None
        if cur.node.has_key('W'):
            move = sgf_to_move(cur.node['W'][0])
        elif cur.node.has_key('B'):
            move = sgf_to_move(cur.node['W'][0])

        return move


def main():
    size = 5
    g = Game(size)
    while True:
        move = g.generate_move()
        g.make_move(move)
        print move_as_string(move, g.size)
        print g.current_board
        #if last 2 moves are pass moves: exit loop
        if len(g.board_history)>=2 and \
           g.move_history(1)==PASS_MOVE and \
           g.move_history(2)==PASS_MOVE:
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

    score = g.score()
    print "Score"
    print "Black: ",score[0]
    print "White: ",score[1]

def sgf_test():
    sgffile = open('sgf/qjzm1-103.sgf', 'r')
    sgfdata = sgffile.read()
    sgffile.close()
    g = game_from_sgf(sgfdata, 0)
    print g.sgf_game_tree

    savef = open('save.sgf', 'w')
    savef.write(str(g))
    savef.close()

if __name__=="__main__":
    sgf_test()
