# 2048_ai
# puzzle.py

import sys
import copy
import re
import time
import copy

VALID_TILES = [2, 4, 8, 16, 32, 64, 128, 256, 512, 2048]

start_time = time.time()

#Tree class to structure tree of game moves
#board: board configuration of move
#big_tile: biggest tile at this move
#curr_spawn: current spawn index at this move
#moves: list of strings, of move directions leading up to this move
#level: level of tree node 
#next_move: list of tree nodes for next valid moves
class Tree(object):
    def __init__(self, board, big_tile, curr_spawn, level):
        #board configuration for this move
        self.board = copy.deepcopy(board)
        #biggest tile at this move
        self.big_tile = big_tile
        #current spawn index at this move
        self.curr_spawn = curr_spawn
        #list of moves leading up to this move
        self.moves = []
        #list of tree nodes for next valid moves
        self.next_move = []
        #integer level of node in tree
        self.level = level

#main driver function
def main():
    f = open(sys.argv[1], 'r')
    #file = f.read()
    board = []
    dim = []
    spawn = []
    moves = []
    win = False
    moves = []
    for i, line in enumerate(f):
        row = [int(n) for n in line.split()]
        if i==0:
            goal = row[0]
            if goal not in VALID_TILES:
                solution([], start_time, [])
        elif i==1:
            dim = row
            if len(dim) != 2:
                solution([], start_time, [])
        elif i==2:
            spawn = row
            if spawn == []:
                #no spawn tiles
                solution([], start_time, [])
        elif i>2:
            board.append(row)

    #moves = generate_moves(board, dim, big_tile, spawn, curr_spawn)
    win, board, moves = play(board, dim, spawn, goal)

    if win:
        solution(board, start_time, moves)
    else:
        #print("No more moves")
        solution([], start_time, [])

#print_board(): prints the board configuration from the 2d list passed in
#prints a 2d matrix with spaces
def print_board(board):
    for row in board:
        for tile in row:
            print(tile, end=" ")
        print()

#play(): master function to 'play' the game/puzzle
#board: current board configuration
#dim: dimensions of the board
#spawn: list of spawn values
#goal: goal tile to win game
#returns win(if won game), board(the ending board configuration), moves(the ending list of moves)
def play(board, dim, spawn, goal):
    #setup the game board
    big_tile = 0
    big_tile = find_biggest_tile(board, big_tile)
    curr_spawn = 0
    moves = []
    win = False
    
    #check if goal is already on the board
    for row in board:
        for tile in row:
            if tile == goal:
                win = True
    if not win:
        win, board, moves = iddfts(board, dim, big_tile, goal, spawn, curr_spawn)

    return win, board, moves

#finds largest tile value on board 
#board: current board setup
#big_tile: value of biggest tile on board
#returns big_tile(biggest tile on board)
def find_biggest_tile(board, big_tile):
    #iterates over entire board, looking for largest tile value
    for row in board:
        for i in row:
            if i > big_tile:
                big_tile = i
    return big_tile

#spawn_tile(): after a valid move, new tile will be spawned
#board: current board set up
#dim: board dimensions
#spawn: list of spawn value pattern
#curr_spawn: index of the current spawn value in pattern
#returns spawn_board(new board configurations after spawn), new_spawn(spawn index value)
def spawn_tile(board, dim, spawn, curr_spawn):
    height = dim[1]
    width = dim[0]
    new_spawn = curr_spawn
    spawn_board = copy.deepcopy(board)

    if curr_spawn >= len(spawn):
        curr_spawn = 0
    #top left
    if spawn_board[0][0] == 0:
        spawn_board[0][0] = spawn[curr_spawn]
    #top right
    elif spawn_board[0][width-1] == 0:
        spawn_board[0][width-1] = spawn[curr_spawn]
    #bottom right
    elif spawn_board[height-1][width-1] == 0:
        spawn_board[height-1][width-1] = spawn[curr_spawn]
    #bottom left
    elif spawn_board[height-1][0] == 0:
        spawn_board[height-1][0] = spawn[curr_spawn]
    #else no new spawn
    else:
        #counteract the spawn increment in iddfts
        new_spawn -= 1
    return spawn_board, new_spawn

#generate_level(): creates stack of tree level based on the previous level
#stack: list that contains the nodes of previous tree level
#dim: dimensions of board
#spawn: list of spawn values
#curr_spawn: index of current spawn tile
#returns next_level(list of the next level of tree nodes), if won, board, moves
def generate_level(stack, goal, dim, spawn, curr_spawn):
    level_stack = copy.copy(stack)
    next_level = []
    board = [[]]
    moves = []

    while level_stack:
        node = level_stack.pop()
        prev_moves = copy.copy(node.moves)
        # print("current board")
        # print_board(node.board)
        possible_moves = list(generate_valid_moves(
            node.board, dim, node.big_tile, spawn, node.curr_spawn))
        if possible_moves == []:
            #no possible moves from here, game over
            return next_level,False,board,moves

        for move in possible_moves:
            # print("move " + move[3])
            # print_board(move[0])
            #create new node from current node move and add to stack
            #add newest move direction to current node's move directions
            #Tree(current move board, current move's biggest tile, current move's spawn index, list of moves)
            next_node = Tree(move[0], move[1], move[2]+1)
            next_node.moves = copy.copy(prev_moves)
            next_node.moves.append(move[3])

            if next_node.big_tile == goal:
                    board = copy.deepcopy(next_node.board)
                    moves = next_node.moves
                    return next_level, True, next_node.board, next_node.moves

            node.next_move.append(next_node)
            next_level.append(next_node)

    return next_level, False, board, moves

#iddfts(): iterative-deepening, depth-first search algorithm
#board: current configuration of the board
#dim: dimenions of the board
#big_tile: current biggest tile value
#goal: goal tile value
#spawn:  list of spawn values
#curr_spawn: index of current spawn tile
#returns win(if won), board(ending board configuration), moves(list of move directions to get to end)
def iddfts(board, dim, big_tile, goal, spawn, curr_spawn):
    win = False
    level = 1
    root = Tree(board, big_tile, curr_spawn, 0)
    new_board = copy.deepcopy(board)
    node = root
    #stack of stacks by level in tree
    stack = []
    stack.append(root)
    #already checked if goal tile was on board(at root) in parent function play()
    while not win:
        #reset stack
        stack = []
        stack.append(root)
        #NEW SUBMISSION CODE
        #This is more of a true IDDFTS alorithm that is working. Not fully optimized, but works.
        #print(level)
        while stack:
            node = stack.pop()
            prev_moves = copy.copy(node.moves)
            # print("current board")
            # print_board(node.board)
            possible_moves = list(generate_valid_moves(
                node.board, dim, node.big_tile, spawn, node.curr_spawn))
            if possible_moves == []:
                #no possible moves from here, game over
                win = False
                return win, board, moves

            for move in possible_moves:
                # print("move " + move[3])
                # print_board(move[0])
                #create new node from current node move and add to stack
                #add newest move direction to current node's move directions
                #Tree(current move board, current move's biggest tile, current move's spawn index, list of moves)
                next_node = Tree(move[0], move[1], move[2]+1, node.level+1)
                next_node.moves = copy.copy(prev_moves)
                next_node.moves.append(move[3])
                node.next_move.append(next_node)

                if next_node.big_tile == goal:
                    win = True
                    board = copy.deepcopy(next_node.board)
                    moves = next_node.moves
                    return win, board, moves
                elif next_node.level < level:
                    #add node to stack, more levels to look at
                    stack.append(next_node)
                else:
                    #if node at max depth level, cannot invesitgate this part of tree further
                    #do not add to stack
                    continue
        #if goal tile not found in stack, increase depth level
        level += 1

        #PREVIOUS SUBMISSION CODE
        #Not a true IDDFTS, so I went back and redid it correctly. Kept this code here to compare against new algorithm
        # #Decided to loop through each level of the tree as it grows and search for goal tile
        # #Checks the biggest tile values at the lowest level, builds upon previous stacks in
        # #hope to speed up search process. Still calculates depth-first, just separates stack into levels
        # while(depth <= level):
        #     #generate stack of next level moves
        #     level_stack, win, board, moves = generate_level(stack[len(stack)-1], goal, dim, spawn, curr_spawn)
        #     if level_stack == [] and board == [[]] and moves == []:
        #         win = False
        #     if win:
        #         return win, board, moves
        #     else:
        #         #add list to list of levels
        #         next_level = copy.copy(level_stack)
        #         stack.append(next_level)
        #         #increase depth to continue search for goal tile
        #         depth += 1
        # #increase level to search move tree for goal tile
        # level += 1
    return win, board, moves

#from hw1, fix later?
#breadth-first search algorithm
#returns if won, ending board configuration, string of move directions to get to end
def bfs(board, dim, big_tile, spawn, goal, moves):
    #queue of each move's board, move direction, new big tile
    queue = []
    # move: (board, move_direction, big_tile)
    tried = []
    solution_board = []
    solution = []
    win = False
    solution_moves = []
    move_dirs = ''
    curr_spawn = 0
    #moves = [(move_dirs, board, big_tile)]
    #generate intial 4 moves
    #states = [[direction, board, big_tile, dirs]]
    states, curr_spawn = generate_moves(board, dim, big_tile, move_dirs, spawn, curr_spawn)
    curr_spawn = 0
    start_move = (states, board, big_tile)
    curr_spawn = 0
    new_board = copy.deepcopy(board)
    #traverse
    queue.append(start_move)
    solution.append(start_move)
    
    while queue:
        move = queue.pop(0)
        tried.append(move)

        if len(move[0]) == 0:
            #no more possible moves
            win = False
            return win, board, solution_moves
        else:
            #at least one possible move
            #move = [states, board, big_tile]
            #possible_move = states
            #states = [[direction, board, big_tile]]
            #for each possible move in the generated states, 
            # choose the one that has a tile equivalent to the goal,
            # otherwise add to queue the next possible steps from that state
            for possible_move in move[0]:
                #check win
                        if possible_move[2] == goal:
                            solution_board = copy.deepcopy(possible_move[1])
                            board = copy.deepcopy(solution_board)
                            solution_moves = possible_move[0]
                            best_move = copy.deepcopy(possible_move)
                            solution.append(best_move)
                            win = True
                            return win, board, solution_moves
                        elif possible_move not in tried:
                            #generate next possible moves from current state
                            next_board = copy.deepcopy(possible_move[1])
                            #next_board, curr_spawn = spawn_tile(next_board, dim, spawn, curr_spawn)
                            big_tile = possible_move[2]
                            next_states, curr_spawn = generate_moves(next_board, dim, big_tile, possible_move[0], spawn, curr_spawn)
                            next_possible_move = (next_states, move_dirs, next_board, big_tile)
                            #add next possible moves to the queue
                            queue.append(next_possible_move)

                        tried.append(possible_move)
            
    return win, board, solution_moves

#shift_tiles(): shift tiles in direction of move, combining tiles if they are the same
#board: current board set up(2d list)
#dim: list of dimensions of the board([width, height])
#start: where to begin the shift(0)
#end: when to end the shift(width, height)
#rotate: how many rotations to shift in the left direction(0-3)
#returns board_shift(board configuration after shifting and combining tiles), new_big(newest biggest tile)
def shift_tiles(board, start, end, rotate, big_tile):
    board_shift = copy.deepcopy(board)
    new_big = big_tile

    #goal is to have board in postion so can shift horizontally then flip
    #rotate board for vertical shift
    for r in range(rotate):
        board_rotate = [list(r) for r in list(zip(*board_shift[::-1]))]
        board_shift = copy.deepcopy(board_rotate)
    for row in board_shift:
        #combine tiles
        #will only combine tiles if they are same value, right next to each other, or separated by 0's
        i=0
        j=i+1
        while (i < end-1 and j <=end-1):
            tile = row[i]
            next_tile = row[j]
            if tile !=0 and tile == next_tile:
                #combine
                row[i] = tile + row[j]
                #check is new tile is bigger than current biggest tile
                combine = row[i]
                if combine > new_big:
                    new_big = combine
                #replace other tile with 0
                row[j] = 0
                #increment
                i += 1
                j = i + 1
            elif next_tile == 0:
                #shift next cursor over
                j += 1
            else:
                #increment, shift cursor over
                i += 1
                j = i + 1

        #shift tiles
        for tile in range(start, end):
            #only shift tiles when there is space to shift(0 in place)
            if row[tile] == 0:
                #if at the end of the shift, make last tile 0
                if tile == end:
                    row[end] = 0
                else:
                    #shift tiles
                    next_tile = tile
                    count = 0
                    while (next_tile < end-1 and row[next_tile] == 0):
                        count += 1
                        #will increment next_tile
                        next_tile += 1
                    #will add count value
                    row[tile] = row[tile+count]
                    row[tile+count] = 0

    #rotate board back
    for r in range(rotate):
        board_rotate = [list(r) for r in list(zip(*board_shift))[::-1]]
        board_shift = copy.deepcopy(board_rotate)

    return board_shift, new_big

#generate_move(): generates board configuration based on input for a certain type of move
#board: current board set up(2d list)
#dim: list of dimensions of board([width, height])
#big_tile: current biggest tile value(integer of base 2)
#start: start of row for shift(0)
#end: end of row for shift(width, height)
#rotate: how many rotations to shift in left position(0-3)
#returns board_move(new board configuration after move), new_big(biggest tile value after the move)
def generate_move(board, dim, big_tile, start, end, rotate):
    board_move = copy.deepcopy(board)
    new_big = big_tile
    #shift tiles
    board_move, new_big = shift_tiles(board_move, start, end, rotate, big_tile)
    return board_move, new_big

#generates_valid_moves(): generates all valid possible moves from current state
#board: current board state
#dim: board dimensions
#big_tile: biggest tile on the board
#spawn: list of spawn tile value pattern
#curr_spawn: current spawn value index from previous state
#returns states(list of all valid states)
#states: [[board_move, new_big, new_spawn, direction]]
def generate_valid_moves(board, dim, big_tile, spawn, curr_spawn):
    board_move = copy.deepcopy(board)
    move_spawn = curr_spawn
    #list of each valid move: (board setup, big_tile, current spawn index, direction letter)
    states = []
    new_big = big_tile
    width = dim[0]
    height = dim[1]

    #left shift
    #parameters(board, dimension, start at 0, end at width, no rotate)
    board_move, new_big = generate_move(board_move, dim, big_tile, 0, width, 0)
    if valid_move(board, board_move, dim):
        valid_state = copy.deepcopy(board_move)
        valid_state, new_spawn = spawn_tile(valid_state, dim, spawn, move_spawn)
        # print("Left Shift")
        # print_board(valid_state)
        states.append((valid_state, new_big, new_spawn, 'L'))

    #right shift
    board_move = copy.deepcopy(board)
    #parameters(board, dimension, start at 0, end at width, rotate 2x)
    board_move, new_big = generate_move(board_move, dim, big_tile, 0, width, 2)
    if valid_move(board, board_move, dim):
        valid_state = copy.deepcopy(board_move)
        valid_state, new_spawn = spawn_tile(valid_state, dim, spawn, move_spawn)
        # print("Right Shift")
        # print_board(valid_state)
        states.append((valid_state, new_big, new_spawn, 'R'))

    #down shift
    board_move = copy.deepcopy(board)
    #parameters(board, dimension, start at 0, end at height, rotate 1x)
    board_move, new_big = generate_move(board_move, dim, big_tile, 0, height, 1)
    if valid_move(board, board_move, dim):
        valid_state = copy.deepcopy(board_move)
        valid_state, new_spawn = spawn_tile(valid_state, dim, spawn, move_spawn)
        # print("Down Shift")
        # print_board(valid_state)
        states.append((valid_state, new_big, new_spawn, 'D'))

    #up shift
    board_move = copy.deepcopy(board)
    #parameters(board, dimension, start at 0, end at height, rotate 3x)
    board_move, new_big = generate_move(board_move, dim, big_tile, 0, height, 3)
    if valid_move(board, board_move, dim):
        valid_state = copy.deepcopy(board_move)
        valid_state, new_spawn = spawn_tile(valid_state, dim, spawn, move_spawn)
        # print("Up Shift")
        # print_board(valid_state)
        states.append((valid_state, new_big, new_spawn, 'U'))
    
    return states

#valid_move(): determines if current board configuration is a valid move by checking if any changes were made to the board
#board: current board confu=iguration
#board-move: board configuration after possible move
#dim: dimensions of the board
#returns if move is valid
def valid_move(board, board_move, dim):
    valid = False
    length = dim[0]
    height = dim[1]
    i=0
    #iterates through boards, checking to see if any values differ
    #if at least one value differs, then the move is valid
    while i < height:
        j=0
        while j < length:
            if ((board[i][j] == 0 and board_move[i][j] == 0) or (board[i][j] != board_move[i][j])):
                valid = True
                break
            j += 1
        if valid:
            break
        i += 1
    return valid

#solution(): prints out solution to screen and in solution text file
#board: solution board configuration
#start_time: the time at which the runtime of the program started
#moves: list of move directions to get the goal tile
def solution(board, start_time, moves):
    time_elapsed = int((time.time()-start_time)*100000)
    move_count = len(moves)
    #print to screen
    print(time_elapsed)
    print(move_count)
    for move in moves:
        print(move, end='')
    print()
    print_board(board)
    #send to output file
    solution = open("solution.txt", "w")
    solution.write(str(time_elapsed) + "\n")
    solution.write(str(move_count) + "\n")
    for move in moves:
        solution.write(str(move))
    solution.write("\n")
    for row in board:
        for tile in row:
            solution.write(str(tile) + " ")
        solution.write("\n")

if __name__ == "__main__":
    main()
