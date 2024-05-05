from z3 import *
from visualizer import main

def get_grid(N, L, model):
    """Consumes `N` (size of the board), `L` (dict mapping indices to z3 variables), `model` (z3 model)
    and returns a grid"""

    return [[int(str(model.evaluate(L[i, j]))) for j in range(N)] for i in range(N)]

def print_grid(grid):
    """Pretty-print the grid"""

    if grid is None:
        print("No solution!")
        return

    for row in grid:
        for col in row:
            print(col if col != -1 else "_", end=" ")
        print()

class Sudoku(object):
    def __init__(self, N, game_data):
        """Constructor of this class"""

        self.N = N
        self.game_data = game_data

        # Solver
        self.s = Solver()

        self.board_count = 0

    def solve(self, board):
        result = self.s.check()
        if result == sat:
            return get_grid(self.N, board, self.s.model())
        else:
            return None
    
    def get_3x3_section(self, row, col):
        return (row // 3) * 3 + (col // 3)
    
    def create_board(self, known_cells = [], no_fill = True):
        self.board_count += 1
        board = {(i, j): Int('{}_{}_{}'.format(self.board_count, i, j)) for i in range(self.N) for j in range(self.N)}
        
        # Establish board constraints
        for i in range(self.N):
            for j in range(self.N):
                self.s.add(Or(
                    board[(i, j)] == -1, 
                    And(board[(i, j)] > 0, board[(i, j)] < self.N + 1)))

        for i in range(self.N):
            for j in range(self.N):
                for k in range(self.N):
                    for l in range(self.N):
                        if i == k and j == l:
                            continue
                        if i == k or j == l or self.get_3x3_section(i, j) == self.get_3x3_section(k, l):
                            self.s.add(Or(
                                board[(i, j)] == -1, board[(k, l)] == -1, 
                                board[(i, j)] != board[(k, l)]))

        # Insert inputted values
        for r, row in enumerate(known_cells):
            for c, num in enumerate(row):
                num_to_insert = num if num is not None else -1
                if no_fill or num_to_insert != -1:
                    self.s.add(board[(r, c)] == num_to_insert)

        return board
        
    def generate_solved_board(self, known_cells = []):
        board = self.create_board(known_cells, False)
        for r in range(self.N):
            for c in range(self.N):
                self.s.add(board[(r, c)] != -1)
        return self.solve(board)

    def guess_cell(self, pre, post):
        constraints = []
        for i in range(self.N):
            for j in range(self.N):
                self.s.add(Implies(pre[(i, j)] != -1, pre[(i, j)] == post[(i, j)]))
                constraints.append(pre[(i, j)] != post[(i, j)])
        # Constraint enforcing that exactly one square has changed
        self.s.add(PbEq([(x,1) for x in constraints], 1))

    # should return the count as well as the row, col so guess_cell can be constrained to
    # row call with highest count 
    # def possible_values(self, pre, post, row, col, constraints, constraint_list):
    #     count = 0
       
    #     if sudoku.solve(post) is None:
    #         return 0
        
    #     else:

    #         constraint_list.append(post[(row, col)])
    #         print(constraint_list)
    #         self.s.push()
    #         for value in constraint_list:
    #             constraints.append(post[(row, col)] != value)
    #         self.s.pop()
    #         return 1 + sudoku.possible_values(pre, post, row, col, constraints, constraint_list)
        

    def possible_values(self, row, col, post):
        # Base case: check if it is UNSAT, and if so, return 0
        if sudoku.solve(post) is None:
            return 0
            
        # Otherwise, read the value in the model at this row and column
        model = self.s.model()
        # This assumes that `self.variables` maps (row, col) -> Z3 var
        # I totally made this up; use whatever dictionary/list you are using to store the Z3 vars
        value = post[(row, col)]
        
        # Push so that we can (temporarily) add a constraint
        self.s.push()
        # Add the constraint that the value is actually different
        self.s.add(post[(row, col)] != value)
        # Count how many possibilities there are that are different from the value we recorded
        count = self.possible_values(row, col, post)
        # Remove the temporary constraint
        self.s.pop()
        
        # Return 1 + count since `count` does not include the solution we found
        return count + 1
        
    
    def guess_cell(self, pre, post):
        constraints = []
        for i in range(self.N):
            for j in range(self.N):
                self.s.add(Implies(pre[(i, j)] != -1, pre[(i, j)] == post[(i, j)]))
                constraints.append(pre[(i, j)] != post[(i, j)])
                print(sudoku.possible_values(i,j, post))
               
        # Constraint enforcing that exactly one square has changed
        self.s.add(PbEq([(x,1) for x in constraints], 1))


def get_board_difference(board1, board2):
    for r, (row1, row2) in enumerate(zip(board1, board2)):
        for c, (val1, val2) in enumerate(zip(row1, row2)):
            if val1 != val2:
                return (r, c)

def apply_strategy(sudoku, initial, guesses=[], constraint_map=[]): #add fill in strategy parameter later
    sudoku.s.reset()
    pre = sudoku.create_board(initial)
    pre_board = sudoku.solve(pre)
    if not any([-1 in row for row in pre_board]):
        print("terminated by solving")
        return steps # Board already solved
    post = sudoku.create_board()

    # Add any constraints banning failed guessed values of squares
    for _, r, c, bad_value in constraint_map:
        sudoku.s.add(post[(r, c)] != bad_value)

    steps = 1
    sudoku.guess_cell(pre, post)
    post_board = sudoku.solve(post)
    main(pre_board)
    while post_board is not None:
        pre_board = sudoku.solve(pre)
        difference = get_board_difference(pre_board, post_board)
        main(post_board, [difference])
        if not any([-1 in row for row in post_board]):
            print("terminated by solving")
            return steps # board solved
        guesses.append((difference, post_board[difference[0]][difference[1]]))
        pre = sudoku.create_board(post_board)
        post = sudoku.create_board()
        steps += 1
        sudoku.guess_cell(pre, post)
        post_board = sudoku.solve(post)

    # Dead end reached if while loop terminates, so backtrack
    if len(guesses) == 0:
        print("terminated with no solution")
        return steps # Cannot backtrack, so no solution
    (last_r, last_c), last_guess = guesses.pop()
    # Remove no longer relevant constraints
    while constraint_map and len(guesses) < constraint_map[-1][0]:
        constraint_map.pop() 
    # Add constraint banning the last guessed value for that square 
    constraint_map.append((len(guesses), last_r, last_c, last_guess))
    # Remove last guess and try to proceed again
    pre_board[last_r][last_c] = -1
    return steps + apply_strategy(sudoku, pre_board, guesses, constraint_map)
    


if __name__ == "__main__":
    game_data_example = [
        [1, None, None, None, None, None, 8, None, None],
        [None, None, 4, 2, None, None, None, None, 7],
        [None, 3, None, None, None, None, None, None, 9],
        [None, 9, None, None, 6, 7, None, None, None],
        [None, None, None, None, 5, 1, None, None, 2],
        [6, None, None, 9, None, None, None, 1, None],
        [None, None, 8, 5, None, None, None, None, None],
        [None, None, 6, None, None, None, None, None, None],
        [None, 7, None, None, None, 3, 1, 9, None]
    ]

    #one from solved example
    # game_data_example = [[5, None, 7, 6, 9, 8, 2, 3, 4], [2, 8, 9, 1, 3, 4, 7, 5, 6], [3, 4, 6, 2, 7, 5, 8, 9, 1], [6, 7, 2, 8, 4, 9, 3, 1, 5], [1, 3, 8, 5, 2, 6, 9, 4, 7], [9, 5, 4, 7, 1, 3, 6, 8, 2], [4, 9, 5, 3, 6, 2, 1, 7, 8], [7, 2, 3, 4, 8, 1, 5, 6, 9], [8, 6, 1, 9, 5, 7, 4, 2, 3]]
    
    # backtracking example
    game_data_example = [[5, 1, 7, 6, 9, 8, 2, None, 4], [2, 8, 9, 1, None, None, 7, None, 6], [3, 4, 6, 2, 7, 5, 8, 9, 1], [6, 7, 2, 8, 4, 9, 3, 1, 5], [1, 3, 8, 5, 2, 6, 9, 4, 7], [9, 5, 4, 7, 1, 3, 6, 8, 2], [4, 9, 5, 3, 6, 2, 1, 7, 8], [7, 2, 3, 4, 8, 1, 5, 6, 9], [8, 6, 1, 9, 5, 7, 4, 2, 3]]

    sudoku = Sudoku(9, game_data_example)

    steps_taken = apply_strategy(sudoku, game_data_example)
    print(f"Steps: {steps_taken}")