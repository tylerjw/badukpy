'''
baduk_gui

gui for badukpy game
'''

from Tkinter import Frame, Canvas
from simple_go import Game, BLACK, WHITE, EMPTY
from copy import deepcopy

draw_color = {BLACK:'black', WHITE:'white'}

class Window(Frame):
    def __init__(self,game,master=None):
        Frame.__init__(self,master) #call superclass constructor
        self.pack(padx=15,pady=15)

        self.game = game
        self.size = self.game.size
        self.line_xy = [50] #for drawing lines
        for i in range(self.size):
            self.line_xy.append(self.line_xy[i]+50)
        self.cir_d = 50  #circle diameter

        self.canvas_hw = 100 + (self.size-1) * 50

        self.stones = {}
        
        self.canvas = Canvas(self,width=self.canvas_hw,height=self.canvas_hw)
        #draw lines
        for i in range(self.size):
            #vertical
            self.canvas.create_line(self.line_xy[i],50,self.line_xy[i],self.canvas_hw-50,width=3)
            #horizontal
            self.canvas.create_line(50,self.line_xy[i],self.canvas_hw-50,self.line_xy[i],width=3)

        self.canvas.pack()

        self.moves_remaining = 20
        self.random_game()
        
    def translate(self,move):
        ''' method for finding the x,y pos to draw a move at x,y(board coords)'''
        return (25 + (move[0]-1)*50,25 + (move[1]-1)*50)
        
    def __draw_stone(self,move,color):
        ''' draws a stone '''
        if color == EMPTY:
            #remove
            self.canvas.delete(str(move))
        else:
            (x,y) = self.translate(move)
            self.canvas.create_oval(x,y,x+50,y+50,fill=draw_color[color],
                                    tags=(str(move),draw_color[color]))

    def __redraw_board(self,board):
        ''' redraw the board '''
        # check for differences between board.goban and self.stones
        for move,color in board.goban.items():
            self.__draw_stone(move,color)
        

    def make_move(self,move):
        board = self.game.make_move(move)
        if board: # will be None if non-legal move
            self.__redraw_board(board)

    def random_game(self):
        if self.moves_remaining == 0:
            return
        else:
            self.moves_remaining -= 1
            move = self.game.generate_move()
            self.make_move(move)
            self.after(100,self.random_game)
                

if __name__ == '__main__':
    size = 5
    g = Game(size)
    Window(g).mainloop()
            
        
