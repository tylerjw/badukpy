from gametree import GoGameTree
import unittest

class TestSequenceFunctions(unittest.TestCase):

    def setUp(self):
        self.gametree = GoGameTree()

    def testTreeInit(self):
        self.assertEqual(self.gametree.black_placed, None)
        self.assertEqual(self.gametree.white_placed, None)
        self.assertEqual(self.gametree.current, None)
        self.assertEqual(self.gametree.firsts, [])

    def testEmptyWalk(self):
        nodes = list(self.gametree.walk())
        self.assertEqual(nodes, [])

    def testEmptyUndo(self):
        self.assertEqual(self.gametree.undo_move(), None)

if __name__ == '__main__':
    unittest.main()
