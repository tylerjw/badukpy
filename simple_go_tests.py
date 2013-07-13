import simple_go
import unittest
from copy import deepcopy


class TestSequenceFunctions(unittest.TestCase):

    def setUp(self):
        self.size = 13
        self.game = simple_go.Game(self.size)
        self.board = simple_go.Board(self.size)

    def tearDown(self):
        self.game = None
        self.board = None

    def test_board_init(self):
        ''' tests __init__ in Board '''
        self.assertEqual(self.board.size, self.size)
        self.assertEqual(self.board.side, simple_go.BLACK)
        self.assertEqual(self.board.captures[simple_go.BLACK], 0)
        self.assertEqual(self.board.captures[simple_go.WHITE], 0)
        self.assertEqual(self.board.groups[simple_go.BLACK], None)
        self.assertEqual(self.board.groups[simple_go.WHITE], None)
        self.assertEqual(self.board.territory_white, 0)
        self.assertEqual(self.board.territory_black, 0)
        for pos in self.board.goban:
            self.assertEqual(self.board.goban[pos], simple_go.EMPTY)
        self.assertEqual(self.board.groups[simple_go.EMPTY], [self.board.goban.keys()])

    def test_eq_ne(self):
        ''' tests __eq__ and __ne__ in Board'''
        board2 = deepcopy(self.board)
        self.assertEqual(self.board, board2)
        board2.make_move((4, 4))
        self.assertNotEqual(self.board, board2)

    def test_iterate_goban(self):
        ''' test iterate_goban in Board '''
        expected = self.size * self.size  # expected value
        test = 0
        for pos in self.board.iterate_goban():
            test += 1
        self.assertEqual(expected, test)

    def test_iterate_neighbour(self):
        ''' tests iterate_neighbour '''
        expected = 2
        test = 0
        for pos in self.board.iterate_neighbour((1, 1)):
            test += 1
        self.assertEqual(expected, test)

    def test_firstMove(self):
        pos = (3, 3)
        board = self.game.make_move(pos)
        self.assertEqual(self.game.current_board.goban[pos], simple_go.BLACK)
        self.assertEqual(board.side, simple_go.WHITE)

    def test_is_neighbour(self):
        pos = (3, 3)
        pos2 = (3, 4)
        pos3 = (3, 2)
        pos4 = (4, 3)
        pos5 = (2, 3)
        pos6 = (2, 1)
        pos7 = (2, 4)
        pos8 = (4, 2)
        pos9 = (4, 4)
        self.game.make_move(pos)
        self.assertEqual(self.board.is_neighbour(pos, pos2), True)
        self.assertEqual(self.board.is_neighbour(pos, pos3), True)
        self.assertEqual(self.board.is_neighbour(pos, pos4), True)
        self.assertEqual(self.board.is_neighbour(pos, pos5), True)
        self.assertEqual(self.board.is_neighbour(pos, pos6), False)
        self.assertEqual(self.board.is_neighbour(pos, pos7), False)
        self.assertEqual(self.board.is_neighbour(pos, pos8), False)
        self.assertEqual(self.board.is_neighbour(pos, pos9), False)

    def test_liberties(self):
        pos = (3, 3)
        self.game.make_move(pos)
        self.assertEqual(self.board.liberties(pos), 4)

    def test_ponnuki(self):
        self.board.side = simple_go.Board(self.size)
        pos = (2, 3)
        pos2 = (3, 2)
        pos3 = (4, 3)
        pos4 = (3, 4)
        self.board.side = simple_go.BLACK
        self.board.make_move(pos, False)
        self.board.make_move(pos2, False)
        self.board.make_move(pos3, False)
        self.board.make_move(pos4, False)
        self.assertEqual(self.board.groups[simple_go.BLACK], [[(2, 3)], [(3, 2)], [(4, 3)], [(3, 4)]])
        self.board.side = simple_go.WHITE
        self.assertEqual(self.board.legal_move((3, 3)), False)
        self.assertEqual(self.board.liberties(pos), 4)
        self.assertEqual(self.board.liberties(pos2), 4)
        self.assertEqual(self.board.liberties(pos3), 4)
        self.assertEqual(self.board.liberties(pos4), 4)

    def test_string_move_functions(self):
        ''' test string/move conversion functions '''
        test = {(1, 1): "A1", (2, 3): "B3", (5, 5): "E5"}
        for pos, string in test.items():
            self.assertEqual(simple_go.move_as_string(pos, self.size), string)
            self.assertEqual(simple_go.string_as_move(string, self.size), pos)

    def test_group_territory(self):
        # test teritory closed
        '''
           ABCDEFGHJKLMN
          +-------------+
        13|.............|13
        12|.............|12
        11|XXXXXXXXXX...|11
        10|X.........X..|10
         9|X.........X..| 9
         8|X.........X..| 8
         7|X.........X..| 7
         6|X.........X..| 6
         5|X.........X..| 5
         4|X.........X..| 4
         3|X.........X..| 3
         2|X.........X..| 2
         1|XXXXXXXXXXX..| 1
          +-------------+
           ABCDEFGHJKLMN
        '''
        for i in range(1, 11):
            self.board.make_move((1, i), False)
            self.board.make_move((i, 11), False)
            self.board.make_move((11, i), False)
            self.board.make_move((i, 1), False)

        #print self.board

        group = self.board.groups[simple_go.BLACK][0]
        self.assertEqual(len(self.board.group_territory(group)), 81)

        # test teritory containing other color with an unconditionally alive group
        '''
           ABCDEFGHJKLMN
          +-------------+
        13|.............|13
        12|.............|12
        11|XXXXXXXXXX...|11
        10|X.........X..|10
         9|X.........X..| 9
         8|X.OOOOO...X..| 8
         7|X.O.O.OO..X..| 7
         6|X.OOOOOO..X..| 6
         5|X.O....O..X..| 5
         4|X.O....O..X..| 4
         3|X.OOOOOO..X..| 3
         2|X.........X..| 2
         1|XXXXXXXXXXX..| 1
          +-------------+
           ABCDEFGHJKLMN
        '''
        self.board.side = simple_go.WHITE

        for i in range(3, 8):
            self.board.make_move((3, i), False)
            self.board.make_move((i, 8), False)
            self.board.make_move((8, i), False)
            self.board.make_move((i, 3), False)
        for i in range(4, 8):
            self.board.make_move((i,6),False)
        self.board.make_move((5,7),False)
        self.board.make_move((7,7),False)

        #print "\nopen\n",self.board

        group = self.board.groups[simple_go.BLACK][0]
        territory = self.board.group_territory(group)
        test = (4,7) not in territory
        self.assertEqual(test, True) #(4,7) - D7 not in Black territory (white eye)

    def test_group_corner(self):
        for i in range(0, 6):
            self.board.make_move((5, i), False)
            self.board.make_move((i, 5), False)
        #print self.board
        group = self.board.groups[simple_go.BLACK][0]
        self.assertEqual(len(self.board.group_territory(group)), 16)

        for i in range(0, 5):
            self.board.make_move((3, i), False)
        group = self.board.groups[simple_go.BLACK][0]
        self.assertEqual(len(self.board.group_territory(group)), 12)

    def test_bent_group(self):
        for i in range(0, 6):
            self.board.make_move((i, 5), False)
        for i in range(0, 3):
            self.board.make_move((3, i), False)
        for i in range(3, 6):
            self.board.make_move((i, 3), False)
            self.board.make_move((6, i), False)

        self.board.side = simple_go.WHITE
        for i in range(4, 8):
            self.board.make_move((i, 2), False)
        self.board.make_move((4, 1), False)
        self.board.make_move((7, 1), False)

        """
           ABCDEFGHJKLMN
          +-------------+
        13|.............|13
        12|.............|12
        11|.............|11
        10|.............|10
         9|.............| 9
         8|.............| 8
         7|.............| 7
         6|.............| 6
         5|XXXXXX.......| 5
         4|.....X.......| 4
         3|..XXXX.......| 3
         2|..XOOOO......| 2
         1|..XO..O......| 1
          +-------------+
           ABCDEFGHJKLMN

        """

        black_group = self.board.groups[simple_go.BLACK][0]
        white_group = self.board.groups[simple_go.WHITE][0]

        self.assertEqual(len(self.board.group_territory(black_group)), 11)
        self.assertEqual(len(self.board.group_territory(white_group)), 2)

if __name__ == '__main__':
    unittest.main()


