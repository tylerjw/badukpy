'''
For use with make_pickle to verify new changes
    do not break working functionality.
'''

from cPickle import load
from simple_go import Game, move_as_string

verbose = False

if __name__ == '__main__':
    fd = open('test_data.pkl', 'rb')
    g = load(fd)
    fd.close()
    print "data loaded"

    num_tests = len(g.board_history)
    results = 0

    print "size:",g.size
    print "moves:",num_tests
    print "#######################################"

    test = Game(g.size)
    for i,move in enumerate(g.move_history):
        test.make_move(move)
        if (i+1 < len(g.board_history)):
            test_board = g.board_history[i+1]
        else:
            test_board = g.current_board
        
        if test_board == test.current_board:
            results += 1
        else:
            print "#######################################"
            print "fail"

        if verbose:
            print "test board",test_board
            print "current board",test.current_board
            print "#######################################"
        else:
            print '.',

    print "\n\nOut of {0} tests".format(num_tests)
    print "Pass {0}".format(results)
    print "Fail {0}".format(num_tests - results)
        
    
