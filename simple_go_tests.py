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
        self.assertEqual(self.board.size,self.size)
        self.assertEqual(self.board.side,simple_go.BLACK)
        self.assertEqual(self.board.captures[simple_go.BLACK],0)
        self.assertEqual(self.board.captures[simple_go.WHITE],0)
        self.assertEqual(self.board.groups[simple_go.BLACK],None)
        self.assertEqual(self.board.groups[simple_go.WHITE],None)
        self.assertEqual(self.board.territory_white,0)
        self.assertEqual(self.board.territory_black,0)
        for pos in self.board.goban:
            self.assertEqual(self.board.goban[pos],simple_go.EMPTY)
        self.assertEqual(self.board.groups[simple_go.EMPTY],[self.board.goban.keys()])

    def test_eq_ne(self):
        ''' tests __eq__ and __ne__ in Board'''
        board2 = deepcopy(self.board)
        self.assertEqual(self.board,board2)
        board2.make_move((4,4))
        self.assertNotEqual(self.board,board2)

    def test_iterate_goban(self):
        ''' test iterate_goban in Board '''
        expected = self.size*self.size #expected value
        test = 0
        for pos in self.board.iterate_goban():
            test += 1
        self.assertEqual(expected,test)

    def test_iterate_neighbour(self):
        ''' tests iterate_neighbour '''
        expected = 2
        test = 0
        for pos in self.board.iterate_neighbour((1,1)):
            test += 1
        self.assertEqual(expected,test)

    def test_firstMove(self):
        pos = (3, 3)
        self.game.make_move(pos)
        self.assertEqual(self.game.current_board.goban[pos], simple_go.BLACK)

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

    def test_string_move_functions(self):
        ''' test string/move conversion functions '''
        test = {(1,1):"A1", (2,3):"B3", (5,5):"E5"}
        for pos,string in test.items():
            self.assertEqual(simple_go.move_as_string(pos,self.size),string)
            self.assertEqual(simple_go.string_as_move(string,self.size),pos)

if __name__ == '__main__':
    unittest.main()


