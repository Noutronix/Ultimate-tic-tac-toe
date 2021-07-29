Hello, this is a program that is designed to play the two-player pen-and-paper game 
named Ultimate Tic-Tac-Toe. This readme will first cover the rules of the game, how to use
the python program and finally what went into the creation of the program itself.

Rules:

Here is an excerpt from the Wikipedia article about Ultimate tic tac toe:

"Each small 3 × 3 tic-tac-toe board is referred to as a local board, and the larger 3 × 3 board is referred to as the global board.
The game starts with X playing wherever they want in any of the 81 empty spots. This move "sends" their opponent to its relative location. 
For example, if X played in the top right square of their local board, then O needs to play next in the local board at the top right 
of the global board. O can then play in any one of the nine available spots in that local board, each move sending X to a different local board.
If a move is played so that it is to win a local board by the rules of normal tic-tac-toe, then the entire 
local board is marked as a victory for the player in the global board. Once a local board is won by a player or it is filled 
completely, no more moves may be played in that board. If a player is sent to such a board, then that player may play in any other board. [...].
Game play ends when either a player wins the global board or there are no legal moves remaining, in which case the game is a draw."
(from https://en.wikipedia.org/wiki/Ultimate_tic-tac-toe)



How to use the program:
- Run the program.
- Input text boxes will start to appear.
- When it asks if you want to play with file mode, it means that all moves will appear on a file named
  "current_board.csv", with the "1"s being the player's moves, the "2"s being the program's moves and "0"s being empty spaces.
- If playing with file mode, make sure not to edit "current_board.csv".
- When the input box asks for a number between 1 and 9, it refers to an area on a local or global board, and the numbers are 
  attributed to a specific part of the board like so:

1 2 3

4 5 6

7 8 9 

- When you input your move or when the program outputs its move, write it down on a piece of paper (unless if you are playing with file mode).
- If you would like to end the game prematurely you may do so by inputting 'q'.


The creation process/features:

To create this program, I used a concept called "Monte Carlo Tree Search", which is essentially a method of finding the best move a player can make
when a game has no built-in heuristic system or static evaluation function (such as chess or checkers). If you would like to know more about it, I would reccomend checking out 
its Wikipedia page: https://en.wikipedia.org/wiki/Monte_Carlo_tree_search. The program makes use of OOP to create the nodes that make up the search
tree and to create the board itself. It also displays a Matplotlib graphic that shows the "heuristic" score of the player's moves once the game ends. 


Sources:
- https://en.wikipedia.org/wiki/Ultimate_tic-tac-toe
- https://en.wikipedia.org/wiki/Monte_Carlo_tree_search


Thank you for reading.
