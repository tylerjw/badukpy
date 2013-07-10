'''
For building the pickle file for unit test comparasons

'''

from cPickle import dump
from simple_go import Game

verbose = False
size = 9
moves = 50

if __name__ == '__main__':
    size = size
    g = Game(size)
    print "size:",size
    print "moves:",moves
    for i in range(moves):
        move = g.generate_move()
        g.make_move(move)
        if verbose:
            print g.current_board
        else:
            print '.',

    fd = open('test_data.pkl', 'wb')
    dump(g, fd, -1)
    fd.close()
    print "\nGame pickled"
