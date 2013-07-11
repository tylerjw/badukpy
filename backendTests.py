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

    def test_firstMove(self):
            pos = (3, 3)
            self.current_board.make_move(pos)
            self.assertEqual(self.current_board[pos], BLACK)

    def test_neighbour(self):
            pos = (3, 3)
            pos2 = (3, 4)
            self.current_board.make_move(pos)
            self.assertEqual(self.current_board.is_neighbour(pos, pos2), True)

    def test_liberties(self):
            pos = (3, 3)
            self.current_board.make_move(pos)
            self.assertEqual(self.current_board.liberties(pos), 4)

if __name__ == '__main__':
    unittest.main()


