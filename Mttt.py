import math
import multiprocessing as mp
import random as rd
import numpy as np
import csv
import copy
import time


def check(question: str, group: list):
    #to make sure an input doesnt break the game
    while True:
        ans = int(input(question))
        if ans in group:
            return ans
        else:
            print("that square/grid has already been filled.") 


class grid:
    
    def referee(self): #broken :sadge:

        original = copy.copy(self.winner)

        if self.winner == 0:
            
            if isinstance(self, large_grid):
                for i in self.board.flat:
                    if i.winner == 0:
                        i.referee()

            #checking to see who won on a large/small board

            board = copy.copy(self.board) if isinstance(self, small_grid) else np.array([x.winner for x in self.board.flat]).reshape((3, 3))

            if list(board.flat).count(1)>2 or list(board.flat).count(2)>2: #more than 2 of either X or O
                for i in range(2): 
                    #for wins/losses
                    l = board.T if i else board #turns 90 degees on second iteration
                    #regular lines |||
                    if all(x == l[0, 0] for x in l[0]) and l[0, 0] != 0 and l[0, 0] != 3:
                        self.winner = l[0, 0]
                    
                    elif all(x == l[1, 0] for x in l[1]) and l[1, 0] != 0 and l[1, 0] != 3:
                        self.winner = l[1, 0]

                    elif all(x == l[2, 0] for x in l[2]) and l[2, 0] != 0 and l[2, 0] != 3:
                        self.winner = l[2, 0]

                    #diagonal line /
                    elif all(x == l.diagonal()[0] for x in l.diagonal()) and l.diagonal()[0] != 0:
                        self.winner = l.diagonal()[0]

                if isinstance(self, small_grid): #to see if small boards are tied
                    if self.winner == 0:
                        if not any([x==0 for x in self.board.flat]):
                            self.winner = 3

            if isinstance(self, large_grid):
                if self.winner != 1 and self.winner != 2: #if no one won
                    test_grid = grid()
                    test_grid.winner = 0
                    for num in (1, 2):
                        test_grid.board = np.array([x if x != 0 else num for x in self.board.flat]).reshape((3, 3))
                        test_grid.referee()
                        if test_grid.winner == 3:
                            self.winner = 3
                            break


        if isinstance(self, small_grid):
            return self.winner
        return original != self.winner
                
                
                                    

class large_grid(grid):
    def __init__(self):
        self.winner = 0
        self.board = np.array([small_grid(self, i) for i in range(9)]).reshape(3, 3)
        self.active_grid = self.board[1, 1]
    
    def from_file(self, file_name): 
        #used to start the game from a certain point
        with open(file_name, "r") as f:
            cf = [x for x in csv.reader(f)]  #file syntax: 9x9 grid plus the starting grid in csv format
            self.active_grid = self.board.flat[int(cf[-1][0])-1]

            for a in self.board:
                for smb in a:
                    for num1 in range(3):
                        for num2 in range(3):
                            #recreating the file's board 
                            smb.board[num1, num2] = cf[num1+smb.coords[0]*3][num2+smb.coords[1]*3]
    

    def to_file(self, file_name):

        with open(file_name, "w") as f:
            for large_line in self.board:
                for num in range(3):
                    for sg in large_line:
                        for mark in sg.board[num]:
                            f.write("{}, ".format(mark))
                    f.write("\n")


    
    def add(self, move, player):
        self.board[move[0]].board[move[1]] = player
        self.active_grid = self.board[move[1]]
        return self




class small_grid(grid):
    def __init__(self, parent, num):
        self.parent = parent
        self.coords = (num//3, num%3)
        self.possible_moves = []
        self.board = np.array([0 for i in range(9)]).reshape(3, 3)
        self.winner = 0
    
    def moves(self):
        #moves a player could make on this small board
        indexes = np.where(self.board.flat[:]==0)
        self.possible_moves = [[self.coords, (i//3, i%3)] for i in [x.tolist() for x in indexes][0]]
        return self.possible_moves
        



class parent_node:
    def __init__(self, lg):
        self.sim_num = 0
        self.wins = 0
        
        self.children = []

        for i in lg.active_grid.moves():
            lg_copy = copy.deepcopy(lg)
            lg_copy.add(i, 2)
            self.children.append(node(lg_copy, 2, self, i))
        
    def distribute(self, outcome):
        if outcome == 2:
            self.wins += 1
        elif outcome == 3:
            self.wins += 0.5
        self.sim_num += 1

    def choose(self):
        for child in self.children:
            child.MCTS()
        
        for i in range(300):
            child = sorted(self.children, key=lambda x:x.pickrate)[-1]
            child.MCTS()
        
        self.value = self.wins/self.sim_num

        return sorted(self.children, key=lambda x:x.value)[-1].move


        



class node:
    def __init__(self, board, side, parent, move):
        #node that can be reused over and over
        self.wins = 0
        self.move = move
        self.sim_num = 0
        self.parent = parent
        self.pickrate = 0 
        self.value = 0
        self.board = board
        self.children = []
        self.side = side


    def calibrate(self):
        #puts values up to date (most importantly the pickrate)
        self.value = self.wins/self.sim_num
        self.pickrate = self.value + math.sqrt(math.log(self.parent.sim_num)/self.sim_num)**1/2 #1/2 == c


    def distribute(self, outcome):
        if outcome == 2: #computer wins
            if self.side == 2:
                self.wins += 1
        elif outcome == 3: #tie
            self.wins += 0.5
        elif self.side == 1:
            self.wins += 1

        self.sim_num += 1
        
        self.parent.distribute(outcome)


    def MCTS(self):

        if self.sim_num == 0: #random choices
            self.board.referee()
            order = [1, 2] if self.side == 2 else [2, 1] #order changes because it's the opposite player's turn
            c = 1
            nb = copy.deepcopy(self.board)
            
            while nb.winner == 0: # while game is ongoing
                c += 1
                if c == 100:
                    raise ValueError
                
                for num in order: 
                    nb.active_grid.referee()
                    if nb.active_grid.winner != 0: #if someone won/tied on active grid
                        move = None
                        for sb in sorted(nb.board.flat, key=lambda x:rd.random()):
                            if sb.winner == 0:
                                sb.referee()
                                if sb.winner == 0:
                                    move = rd.choice(sb.moves()) #random square in 9x9 grid (if active_grid is full)
                                    break

                        if move == None:
                            nb.referee()
                            break

                    else:
                        move = rd.choice(nb.active_grid.moves()) #random square from active_grid

                    ag_coords = nb.active_grid.coords
                    nb.add(move, num) #automatically changes active_grid
                    
                    if nb.board[ag_coords].referee():
                        nb.referee() #only referee 9x9 grid if someone wins/ties (to be tested/changed)

                    if nb.winner != 0:
                        break
            
            self.distribute(nb.winner)
                            
        else: 
            if self.board.winner == 0:     
                if self.sim_num == 1:
                    if self.board.active_grid.winner == 0:
                        for i in self.board.active_grid.moves():
                            new_board = copy.deepcopy(self.board.add(i, abs(self.side-2)+1))
                            self.children.append(node(new_board, abs(self.side-2)+1, self, None)) #creates new child nodes
                    else:
                        for i in [x for y in self.board.board.flat for x in y.moves() if y.winner == 0]:
                            new_board = copy.deepcopy(self.board.add(i, abs(self.side-2)+1))
                            self.children.append(node(new_board, abs(self.side-2)+1, self, None)) #creates new child nodes

                if all(x.sim_num > 0 for x in self.children):
                    for child in self.children:
                        child.calibrate()
                    child = sorted(self.children, key=lambda x:x.pickrate)[-1]
                else:
                    child = rd.choice([x for x in self.children if x.sim_num == 0])
                child.MCTS()
            
            else:
                self.distribute(self.board.winner)

        self.calibrate()


def game(file_name=None):
    
    lg = large_grid()
    if file_name != None:
        #if the game starts from a specific time
        lg.from_file(file_name)
        with open(file_name, "r") as f:
            start = int([x for x in csv.reader(f)][-1][0])-1
            lg.active_grid = lg.board.flat[start]

    for sg in lg.board.flat:
        sg.referee()
    lg.referee()


    while lg.winner == 0: #until game ends
        
        if lg.active_grid.winner != 0:
            tr_grids = [x[0][0]*3+x[0][1] for x in lg.board.flat if x.moves() != []]
            player_move1 = check("choose a section of the board (out of 9):", tr_grids)-1
            lg.active_grid = lg.board.flat[player_move1]
        
        tr_moves = [x[1][0]*3+x[1]+1 for x in lg.active_grid.moves()]
        player_move = check("choose a square in section {} (out of 9):".format(lg.active_grid.coords[0]*3+lg.active_grid.coords[1]), tr_moves)-1
        lg.add([lg.active_grid.coords, (player_move//3, player_move%3)], 1)

        cpm = parent_node(lg).choose()
        print("the computer has played on square no.{} of section no.{}.".format(cpm[1][0]*3+cpm[1][0]+1, cpm[0][0]*3+cpm[0][1]+1))
        lg.active_grid.add(cpm, 2)
        
        lg.referee()
    
    else:
        print("game has already finished!")
    
    if lg.winner == 1:
        return "X"
    elif lg.winner == 2:
        return "O"
    else:
        return "Tie"

def test():
    lg = large_grid()
    c = 0
    lg.referee()
    while True:
        c+=1
        if c > 42:
            print(lg.winner)
            raise ValueError
        
        if lg.active_grid.winner == 0:
            lg.add(rd.choice(lg.active_grid.moves()), 1)
        else:
            lg.add(rd.choice([y for x in lg.board.flat for y in x.moves() if x.winner == 0]), 1)
        lg.referee()
        if lg.winner != 0:
            break
        print("start")
        start_time = time.time()
        lg.add(parent_node(lg).choose(), 2)
        print(time.time()-start_time)

        lg.to_file("Mttt_inputs.csv")
        lg.referee()
        if lg.winner != 0:
            break

    print(lg.winner)

test()
    


#things to do:
# - learn about multithreading
# - create the MCTS algotithm
# - make the algorithm take a certain time or how long the player takes to act
# - use multithreading to make ^ happen and distribute load to other cpus
# - make it play against a player that chooses randomly to see what the best pickrate is