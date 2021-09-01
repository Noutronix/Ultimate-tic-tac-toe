import math
import random as rd
import numpy as np
import csv
import copy
import time
import matplotlib.pyplot as plt


def check(question: str, group: list):

    '''Checks to see if user inputs are valid.'''
    
    while True:
        ans = input(question)
        if ans == "q":
            return ans

        if int(ans) in group:
            return int(ans)
        else:
            print("that square/grid has already been filled.") 


class grid:
    
    def referee(self): 

        '''Checks to see if someone won the game, and if so, who.'''

        original = copy.copy(self.winner)

        if self.winner == 0:
            
            if isinstance(self, large_grid):
                for i in self.board.flat:
                    if i.winner == 0:
                        i.referee()

            #checking to see who won on a large/small board 
            board = copy.copy(self.board) if isinstance(self, small_grid) else np.array([x.winner for x in self.board.flat]).reshape((3, 3))
            
            if isinstance(self, small_grid):
                board1 = copy.deepcopy(board)
                board = np.array([x if x != 3 else 0 for x in self.board.flat]).reshape((3, 3))

            if list(board.flat).count(1)>2 or list(board.flat).count(2)>2 or not any(x==0 for x in board.flat): #more than 2 of either X or O
                for i in range(2): 
                    #for wins/losses
                    if i == 1:
                        board = np.rot90(board) #turns 90 degees on second iteration
                    #regular lines |||
                    diag = np.diagonal(board)
                    if all(x == board[0, 0] for x in board[0]) and board[0, 0] != 0 and board[0, 0] != 3:
                        self.winner = board[0, 0]
                    
                    elif all(x == board[1, 0] for x in board[1]) and board[1, 0] != 0 and board[1, 0] != 3:
                        self.winner = board[1, 0]

                    elif all(x == board[2, 0] for x in board[2]) and board[2, 0] != 0 and board[2, 0] != 3:
                        self.winner = board[2, 0]

                    #diagonal line /
                    elif all(x == diag[0] for x in diag) and diag[0] != 0:
                        self.winner = diag[0]

                if isinstance(self, small_grid): #to see if small boards are tied
                    if self.winner == 0:
                        if not any([x==0 for x in board1.flat]):
                            self.winner = 3

            if isinstance(self, large_grid):
                if self.winner != 1 and self.winner != 2: #if no one won
                    test_grid = small_grid(None, 0)
                    count = 0
                    for num in (1, 2):
                        test_grid.winner = 0
                        test_grid.board = np.array([sb.winner if sb.winner != 0 else num for sb in self.board.flat]).reshape((3, 3))
                        test_grid.referee()
                        if test_grid.winner == 3:
                            count += 1
                    if count == 2:
                        self.winner = 3


        if isinstance(self, small_grid):
            return self.winner
        return original != self.winner
                
                
                                    

class large_grid(grid):
    
    '''A global grid object.'''

    def __init__(self, file_name=None):
        self.winner = 0
        self.board = np.array([small_grid(self, i) for i in range(9)]).reshape(3, 3)
        self.active_grid = None
        if file_name != None:
            self.from_file(file_name)
    
    def from_file(self, file_name): #only for testing
        '''Used to start the game from a certain point.'''
        with open(file_name, "r") as f:
            cf = [x for x in csv.reader(f)]  #file syntax: 9x9 grid plus the starting grid in csv format
            self.active_grid = self.board.flat[int(cf[-1][0])]

            for a in self.board:
                for smb in a:
                    for num1 in range(3):
                        for num2 in range(3):
                            #recreating the file's board 
                            smb.board[num1, num2] = cf[num1+smb.coords[0]*3][num2+smb.coords[1]*3]
    

    def to_file(self, file_name): 
        '''Used to translate the grid object to a readable file.'''
        with open(file_name, "w") as f:
            for large_line in self.board:
                for num in range(3):
                    for sg in large_line:
                        for mark in sg.board[num]:
                            f.write("{}, ".format(mark))
                    f.write("\n")


    
    def add(self, move, player):
        '''Adds a move to the board.'''
        self.board[move[0]].referee()
        if self.board[move[0]].winner == 0:
            self.board[move[0]].board[move[1]] = player
            self.active_grid = self.board[move[1]]
            return self
        else:
            raise AssertionError
    
    def switch(self): #obsolete
        for sb in self.board.flat:
            for num in range(9):
                if sb.board.flat[num] != 0:
                    sb.board.flat[num] = abs(sb.board.flat[num]-2)+1






class small_grid(grid):

    '''A local grid object.'''

    def __init__(self, parent, num):
        self.parent = parent
        self.coords = (num//3, num%3)
        self.possible_moves = []
        self.board = np.array([0 for i in range(9)]).reshape(3, 3)
        self.winner = 0
    
    def moves(self):
        '''Determines the moves a player could make on this specific local board'''
        self.referee()
        if self.winner == 0:
            indexes = np.where(self.board.flat[:]==0)
            self.possible_moves = [[self.coords, (i//3, i%3)] for i in [x.tolist() for x in indexes][0]]
        else:
            self.possible_moves = []
        return self.possible_moves
        



class parent_node:

    '''Starting point for the tree search.'''

    def __init__(self, lg, create=True):
        self.sim_num = 0
        self.wins = 0
        self.successor = None
        self.children = []
        self.lg = lg

        if create:
            if lg.active_grid.moves() != []:
                group = lg.active_grid.possible_moves
            else:
                group = [x for y in lg.board.flat for x in y.moves() if y.winner == 0]
            for i in group:
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

        '''Chooses the best move out of the computer's possible moves.'''
    
        for child in self.children:
            child.MCTS()

        for child in self.children:
            child.MCTS()
            
            child.board.referee()
            if child.board.winner == 2:
                time.sleep(1) # for effect
                v = sorted(self.children, key=lambda x:x.value)
                self.value = [self.wins/self.sim_num, (v[0].value, v[-1].value)]
                return child.move   
        
        num = (30 if len(self.children) < 10 else 45)
        st = time.time()
        count = 0
        while time.time()-st < num:
            count += 1
            child = sorted(self.children, key=lambda x:x.pickrate)[-1]
            child.MCTS()
        print("c:", count, "t:", time.time()-st)
        
        self.successor = sorted(self.children, key=lambda x:x.value)[-1]
        v = sorted(self.successor.children, key=lambda x:x.value)
        self.value = [self.wins/self.sim_num, (v[0].value, v[-1].value)]
        return self.successor.move
    
    def new_parent(self, lg):

        '''Creates a new parent while keeping the relevant nodes from the old one.'''

        for n in self.successor.children:
            if [x for sb in lg.board.flat for x in sb.board.flat] == [x for sb in n.board.board.flat for x in sb.board.flat]:
                pn = parent_node(lg, False)
                if len(n.children) != 0:
                    pn.children = n.children
                    for child in pn.children:
                        child.parent = pn
                else:
                    if lg.active_grid.moves() != []:
                        group = lg.active_grid.possible_moves
                    else:
                        group = [x for y in lg.board.flat for x in y.moves() if y.winner == 0]
                    for i in group:
                        lg_copy = copy.deepcopy(lg)
                        lg_copy.add(i, 2)
                        pn.children.append(node(lg_copy, 2, pn, i))
                pn.sim_num = n.sim_num
                pn.wins = n.wins
                return pn
        pn = parent_node(lg)
        return pn
    


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
        self.best_move = None


    def calibrate(self):
        '''Puts values up to date (most importantly the pickrate).'''
        self.value = self.wins/self.sim_num
        self.pickrate = self.value + math.sqrt(math.log(self.parent.sim_num)/self.sim_num)


    def distribute(self, outcome):

        '''Used for the backpropagation step of Monte Carlo tree search.'''

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

        '''Preforms the first three steps of the Monte Carlo tree search process.'''

        if self.sim_num == 0: #step 3: Simulation
            self.board.referee()
            order = [1, 2] if self.side == 2 else [2, 1] #order changes because it's the opposite player's turn
            count = 1
            nb = copy.deepcopy(self.board)
            
            while nb.winner == 0: # while game is ongoing
                count += 1
                if count == 100:
                    nb.referee()
                    raise ValueError
                
                for num in order: 
                    nb.referee()
                    if nb.winner == 0:
                        if nb.active_grid.winner != 0: #if someone won/tied on active grid
                            group = []
                            
                            for sb in nb.board.flat:
                                for i in sb.moves():
                                    group.append(i)

                        else:
                            group = nb.active_grid.moves() #random square from active_grid
                    
                    else:
                        break

                    move = None
                    
                    b = [x.winner for x in nb.board.flat]
                    if b.count(1) > 1 or b.count(2) > 1:                   
                        for i in group:
                            nb2 = copy.deepcopy(nb)
                            nb2.add(i, num)
                            nb2.referee()
                            if nb2.winner == num:
                                move = i

                    if move == None:
                        move = rd.choice(group)
                        

                    ag_coords = nb.active_grid.coords
                    nb.add(move, num) #automatically changes active_grid
                    
                    if nb.board[ag_coords].referee():
                        nb.referee() #only referee 9x9 grid if someone wins/ties (to be tested/changed)

                    if nb.winner != 0:
                        break
            
            self.distribute(nb.winner)
                            
        else: 
            if self.board.winner == 0:     
                if self.sim_num == 1: #Step 2: Expansion
                    if self.board.active_grid.winner == 0:
                        for i in self.board.active_grid.moves():
                            new_board = copy.deepcopy(self.board)
                            new_board.add(i, abs(self.side-2)+1)
                            self.children.append(node(new_board, abs(self.side-2)+1, self, i)) #creates new child nodes
                        
                    else:
                        for i in [x for y in self.board.board.flat for x in y.moves() if y.winner == 0]:
                            new_board = copy.deepcopy(self.board)
                            new_board.add(i, abs(self.side-2)+1)
                            self.children.append(node(new_board, abs(self.side-2)+1, self, i)) #creates new child nodes
                    
                    if self.children == []:
                        raise ValueError
                #Step 1: Selection
                child = None
                if self.sim_num == 2:
                    for i in self.children:
                        i.board.referee()
                        if i.board.winner == abs(self.side-2)+1:
                            child = i
                            self.best_move = i
                            break
                
                if self.best_move != None and child == None:
                    child = self.best_move

                elif all(x.sim_num > 0 for x in self.children):
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
            start = int([x for x in csv.reader(f)][-1][0])
            lg.active_grid = lg.board.flat[start]

    lg.referee()
    pn = None
    file_mode = check("would you like to play with file mode? (1 for yes and 2 for no): ", [1, 2]) == 1
    difficulty = check("would you like to go first? (1 for yes and 2 for no): ", [1, 2])
    data = []
    rerun = False
    count = 1

    while lg.winner == 0: #until game ends
        if rerun == True or difficulty == 1:
            if lg.active_grid == None:
                tr_grids = [x.coords[0]*3+x.coords[1]+1 for x in lg.board.flat if x.moves() != []]
                player_move1 = check("choose a section of the board (out of 9): ", tr_grids)-1
                lg.active_grid = lg.board.flat[player_move1]

            elif lg.active_grid.winner != 0:
                tr_grids = [x.coords[0]*3+x.coords[1]+1 for x in lg.board.flat if x.moves() != []]
                player_move1 = check("choose a section of the board (out of 9): ", tr_grids)-1
                lg.active_grid = lg.board.flat[player_move1]
                
            tr_moves = [x[1][0]*3+x[1][1]+1 for x in lg.active_grid.moves()]
            player_move = check("choose a square in section {} (out of 9): ".format(lg.active_grid.coords[0]*3+lg.active_grid.coords[1]+1), tr_moves)-1
            
            
            if player_move == "q":
                break
            
            
            lg.add([lg.active_grid.coords, (player_move//3, player_move%3)], 1)
            if file_mode:
                lg.to_file("current_board.csv")

            lg.referee()
            if lg.winner != 0:
                break
            
            if pn == None:
                pn = parent_node(lg)
            else:
                pn = pn.new_parent(lg)
            try:
                cpm = pn.choose()
                exc = False
            except Exception:
                m = lg.active_grid.moves()
                moves = (m if m != [] else [x for y in lg.board.flat for x in y.moves()]) 
                exc = True
                cpm = rd.choice(moves)
            count += 1
            if not exc:
                data.append(100-int(pn.value[0]*100))
            

            print("the computer has played on square no.{} of section no.{}.".format(cpm[1][0]*3+cpm[1][1]+1, cpm[0][0]*3+cpm[0][1]+1))
            lg.add(cpm, 2)
            if file_mode:
                lg.to_file("current_board.csv")

            lg.referee()
        
        else:
            time.sleep(2) #so it looks like it's thinking
            rerun = True
            cpm = rd.choice([x for x in lg.board[1, 1].moves() if x[1] != [1, 1]])
            print("the computer has played on square no.{} of section no.{}.".format(cpm[1][0]*3+cpm[1][1]+1, cpm[0][0]*3+cpm[0][1]+1))
            lg.add(cpm, 2)



    
    plt.plot(data, color="black", label="Player's heuristic score at each turn", marker="o")
    plt.axis([1, len(data)-1, 1, 100])
    plt.ylabel("Heuristic score for player (max: 100 min: 1)")
    plt.xlabel("Player turns")
    plt.suptitle("Heuristic score over the course of the game")
    plt.legend()
    plt.show()

    if lg.winner == 1:
        return "Player wins."
    elif lg.winner == 2:
        return "Computer wins."
    else:
        return "Tie"



print(game())
