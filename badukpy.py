'''
baduk_gui

gui for badukpy game
'''

from Tkinter import Frame, Canvas
from simple_go import Game,BLACK,WHITE,EMPTY,PASS_MOVE,move_as_string
from copy import deepcopy

draw_color = {BLACK:'black', WHITE:'white'}

class Window(Frame):
    def __init__(self,game,canvas_hw,master=None):
        Frame.__init__(self,master) #call superclass constructor
        self.pack(padx=15,pady=15)
        
        self.game = game
        self.size = self.game.size
        self.canvas_hw = canvas_hw
        self.cir_d = self.canvas_hw/(self.size+1)  #circle diameter
        self.line_xy = [self.cir_d] #for drawing lines
        for i in range(self.size):
            self.line_xy.append(self.line_xy[i]+self.cir_d)

        self.stones = {}
        
        self.canvas = Canvas(self,width=self.canvas_hw,height=self.canvas_hw)
        #draw lines
        for i in range(self.size):
            #vertical
            self.canvas.create_line(self.line_xy[i],self.cir_d,self.line_xy[i],self.canvas_hw-self.cir_d,width=3)
            #horizontal
            self.canvas.create_line(self.cir_d,self.line_xy[i],self.canvas_hw-self.cir_d,self.line_xy[i],width=3)

        self.canvas.grid(row=0,column=0,sticky='w')

        move = self.game.generate_move()
        self.make_move(move)
        self.canvas.bind('<Button-1>', self.mousepress)

    def mousepress(self,event):
        x = ((event.x - self.cir_d/2) / self.cir_d) + 1
        y = ((event.y - self.cir_d/2) / self.cir_d) + 1
        move = (x,y)
        #test if move is valid
        if ((0 < x < (1+self.size)) and (0 < y < (1+self.size)) and
            self.game.legal_move(move)):
            self.make_move(move)
            move = self.game.generate_move()
            self.make_move(move)
            print "(black,white): ", g.score()
        
    def translate(self,move):
        ''' method for finding the x,y pos to draw a move at x,y(board coords)'''
        return ((self.cir_d/2) + (move[0]-1)*self.cir_d,(self.cir_d/2) + (move[1]-1)*self.cir_d)
        
    def __draw_stone(self,move,color):
        ''' draws a stone '''
        if color == EMPTY:
            #remove
            self.canvas.delete(str(move))
        else:
            if not self.canvas.find_withtag(str(move)):
                (x,y) = self.translate(move)
                self.canvas.create_oval(x,y,x+self.cir_d,y+self.cir_d,fill=draw_color[color],
                                        tags=(str(move),draw_color[color]))

    def __redraw_board(self,board):
        ''' redraw the board '''
        # check for differences between board.goban and self.stones
        for move,color in board.goban.items():
            self.__draw_stone(move,color)
        

    def make_move(self,move):
        board = self.game.make_move(move)
        if board and move != PASS_MOVE: # will be None if non-legal move
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
    size = 9
    g = Game(size)
    Window(g,600).mainloop()
            
        
