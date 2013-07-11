import simple_go
import unittest


class TestSequenceFunctions(unittest.TestCase):

    def setUp(self):
        self.size = 13
        self.current_board = simple_go.Board(self.size)
        self.board_history = []
        self.move_history = []

    def tearDown(self):
            self.setUp()

    #def test_firstMove(self):
    #        pos = (3, 3)
    #        self.current_board.make_move(pos)
    #        self.assertEqual(self.current_board[pos], BLACK)

    def test_neighbour(self):
            pos = (3, 3)
            pos2 = (3, 4)
            pos3 = (3, 2)
            pos4 = (4, 3)
            pos5 = (2, 3)
            pos6 = (2, 1)
            pos7 = (2, 4)
            pos8 = (4, 2)
            pos9 = (4, 4)
            self.current_board.make_move(pos)
            self.assertEqual(self.current_board.is_neighbour(pos, pos2), True)
            self.assertEqual(self.current_board.is_neighbour(pos, pos3), True)
            self.assertEqual(self.current_board.is_neighbour(pos, pos4), True)
            self.assertEqual(self.current_board.is_neighbour(pos, pos5), True)
            self.assertEqual(self.current_board.is_neighbour(pos, pos6), False)
            self.assertEqual(self.current_board.is_neighbour(pos, pos7), False)
            self.assertEqual(self.current_board.is_neighbour(pos, pos8), False)
            self.assertEqual(self.current_board.is_neighbour(pos, pos9), False)

    def test_liberties(self):
            pos = (3, 3)
            self.current_board.make_move(pos)
            self.assertEqual(self.current_board.liberties(pos), 4)

if __name__ == '__main__':
    unittest.main()


