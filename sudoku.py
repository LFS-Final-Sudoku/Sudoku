from z3 import *
from visualizer import visualize
from random import sample, randrange

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
    def __init__(self, N):
        """
        Constructor of this class
        """
        assert int(N ** (1/2)) == N ** (1/2)
        self.N = N # Size of the board
        self.s = Solver()
        self.board_count = 0

    def solve(self, board):
        """
        Returns the solved board if SAT or returns nothing if it is not.
        """
        result = self.s.check()
        if result == sat: return get_grid(self.N, board, self.s.model())
        else:             return None

    def get_mini_section(self, row, col):
        """
        Determine which subgrid a coordinate is in.
        """
        section_size = self.N ** (1/2)
        return (row // section_size) * section_size + (col // section_size)

    def create_board(self, known_cells = [], no_fill = True):
        """
        Generates an empty board and adds wellformedness rules for sudoku.
        """
        self.board_count += 1
        board = {(i, j): Int('{}_{}_{}'.format(self.board_count, i, j)) for i in range(self.N) for j in range(self.N)}

        # Establish board constraints
        for i in range(self.N):
            for j in range(self.N):
                self.s.add(Or(
                    board[(i, j)] == -1,
                    And(board[(i, j)] > 0, board[(i, j)] < self.N + 1)))

        # Establish uniqueness within row, column, and subgrid.
        for i in range(self.N):
            for j in range(self.N):
                for k in range(self.N):
                    for l in range(self.N):
                        if i == k and j == l:
                            continue
                        if i == k or j == l or self.get_mini_section(i, j) == self.get_mini_section(k, l):
                            self.s.add(Or(
                                board[(i, j)] == -1, board[(k, l)] == -1,
                                board[(i, j)] != board[(k, l)]))

        # Insert inputted values
        for r, row in enumerate(known_cells):
            for c, num in enumerate(row):
                num_to_insert = num if num is not None else -1
                if no_fill or num_to_insert != -1:
                    self.s.add(board[(r, c)] == num_to_insert)

        # Create possibilities map
        possibilities = {(i, j): [Bool('{} {}_{}_{}'.format(num, self.board_count, i, j)) for num in range(self.N)] for i in range(self.N) for j in range(self.N)}
        for i in range(self.N):
            for j in range(self.N):
                for num in range(1, self.N + 1):
                    constraints = []
                    for k in range(self.N):
                        for l in range(self.N):
                            if i == k and j == l:
                                continue
                            if i == k or j == l or self.get_mini_section(i, j) == self.get_mini_section(k, l):
                                constraints.append(board[(k, l)] == num)
                    self.s.add(If(
                        Or(constraints),
                        possibilities[(i, j)][num - 1] == False,
                        possibilities[(i, j)][num - 1] == True
                    ))

        #Count possibilities per square
        possibility_counts = {(i, j): Int('counts {}_{}_{}'.format(self.board_count, i, j)) for i in range(self.N) for j in range(self.N)}
        for i in range(self.N):
            for j in range(self.N):
                for count in range(1, self.N + 1):
                    self.s.add(Implies(
                        PbEq([(var, 1) for var in possibilities[(i, j)]], count),
                        possibility_counts[(i, j)] == count
                    ))
                            
        return board, possibility_counts, possibilities
        
    def generate_solved_board(self, known_cells = []):
        """
        Generates a solved board.
        """
        board, *_ = self.create_board(known_cells, False)
        for r in range(self.N):
            for c in range(self.N):
                self.s.add(board[(r, c)] != -1)
        return self.solve(board)

    def guess_cell(self, pre, post, *_):
        """
        Takes a guess for one cell on the grid.
        """
        constraints = []
        for i in range(self.N):
            for j in range(self.N):
                self.s.add(Implies(pre[(i, j)] != -1, pre[(i, j)] == post[(i, j)]))
                constraints.append(pre[(i, j)] != post[(i, j)])
        # Constraint enforcing that exactly one square has changed
        self.s.add(PbEq([(x,1) for x in constraints], 1))

    def get_guess_least_possibilties_constraint(self, pre, post, possibility_counts):
        constraints = []
        # Variable to store minimum possibilities count among blank spaces
        min_possibilities = Int(f"min_possibilities {self.board_count}")
        for i in range(self.N):
            for j in range(self.N):
                # Enforce that the minimum is the smallest possibility count of unfilled squares
                constraints.append(Implies(pre[(i, j)] == -1, min_possibilities <= possibility_counts[(i, j)]))
                # Either the cell doesn't change or its possibility count is the minimum
                constraints.append(Or(
                    pre[(i, j)] == post[(i, j)],
                    possibility_counts[(i, j)] == min_possibilities,
                ))
        return And(constraints)

    def guess_least_possibilities(self, pre, post, possibility_counts, *_):
        """
        Find a cell with the least number of possible options and begin guessing there.
        """
        self.guess_cell(pre, post) # Exactly one blank cell must be filled
        self.s.add(self.get_guess_least_possibilties_constraint(pre, post, possibility_counts))
    
    def guess_forced(self, pre, post, possibility_counts, possibilities):
        self.guess_cell(pre, post) # Exactly one blank cell must be filled
        can_guess_forced_condition = [] # Stores conditions for each square that are true iff. that square is forced
        then_constraints = [] # Constraints to apply if a square is forced.
        # If no square is forced, guess square with lowest possibility count.
        else_constraint = self.get_guess_least_possibilties_constraint(pre, post, possibility_counts)
        
        for i in range(self.N):
            for j in range(self.N):
                cell_section = self.get_mini_section(i, j) 
                for num_index, is_possible_var in enumerate(possibilities[(i, j)]):
                    row_possibilities = []
                    col_possibilities = []
                    section_possibilities = []
                    for k in range(self.N):
                        # Get constraints corresponding with whether number is possible elsewhere in row
                        if k != j:
                            unfilled_and_possible = And(
                                pre[(i, k)] == -1,
                                possibilities[(i, k)][num_index]
                            )
                            row_possibilities.append(unfilled_and_possible)
                        # Get constraints corresponding with whether number is possible elsewhere in column
                        if k != i:
                            unfilled_and_possible = And(
                                pre[(k, j)] == -1,
                                possibilities[(k, j)][num_index]
                            )
                            col_possibilities.append(unfilled_and_possible)
                        # Get constraints corresponding with whether number is possible elsewhere in section
                        for l in range(self.N):
                            if (i != k or j != l) and cell_section == self.get_mini_section(k, l):
                                unfilled_and_possible = And(
                                    pre[(k, l)] == -1,
                                    possibilities[(k, l)][num_index]
                                )
                                section_possibilities.append(unfilled_and_possible)
                    
                    # The current square is forced to be number n if it is unfilled, can legally be n, 
                    # and either its row, col, or section has no other square that can be n.
                    forced_condition = And(
                        pre[(i, j)] == -1,
                        is_possible_var,
                        Or(
                            Not(Or(row_possibilities)),
                            Not(Or(col_possibilities)),
                            Not(Or(section_possibilities))
                        )
                    )
                    can_guess_forced_condition.append(forced_condition)

                    # If there is a square that is forced, non-forced numbers should not be filled in.
                    then_constraint = Implies(
                        And(pre[(i, j)] == -1, Not(forced_condition)),
                        post[(i, j)] != num_index + 1
                    )
                    then_constraints.append(then_constraint)

        # If any square is forced, apply then_constraints to require a forced square to change;
        # otherwise guess a square with lowest possibility count.
        guess_forced_equation = If(
            Or(can_guess_forced_condition),
            And(then_constraints),
            else_constraint
        )
        self.s.add(guess_forced_equation)


    def possible_values(self, row, col, post):
        """
        Recursively count the number of possible values for a cell.
        """
        # Base case: if UNSAT, return 0
        if self.solve(post) is None:
            return 0

        value = post[(row, col)]

        # Push so that we can (temporarily) add a constraint
        self.s.push()
        # Add the constraint that the value is actually different
        self.s.add(post[(row, col)] != value)
        # Count how many possibilities there are that are different from the value we recorded
        count = self.possible_values(row, col, post)
        # Remove the temporary constraint
        self.s.pop()
        return count + 1

def remove_values(board, num_to_remove):
    """
    Removes random values from a solved sudoku board to generate an unsolved board.
    """
    board_copy = [row.copy() for row in board]
    filled_locations = []
    for r, row in enumerate(board_copy):
        for c, val in enumerate(row):
            if val != -1:
                filled_locations.append((r, c))
    to_remove = sample(filled_locations, min(num_to_remove, len(filled_locations)))
    for r, c in to_remove:
        board_copy[r][c] = -1
    return board_copy

def generate_random_starting_board(N, num_unfilled):
    """
    Generates a random starting board of size N with num_unfilled empty squares.
    """
    sudoku = Sudoku(N)
    random_row = sample(range(1, N + 1), N)
    known_cells = [[-1 for _ in range(N)] for _ in range(N)]
    known_cells[randrange(0, N)] = random_row
    board = sudoku.generate_solved_board(known_cells)
    return remove_values(board, num_unfilled)

def get_board_difference(board1, board2):
    """
    Finds the location of difference in two boards.
    """
    for r, (row1, row2) in enumerate(zip(board1, board2)):
        for c, (val1, val2) in enumerate(zip(row1, row2)):
            if val1 != val2:
                return (r, c)

def apply_strategy(sudoku, initial, guess_strategy, guesses=[], constraint_map=[], steps=0, max_steps=60, use_visualizer=True):
    """
    Applies a Sudoku solving strategy.
    """
    sudoku.s.reset()
    pre, pre_possibility_counts, pre_possibilities= sudoku.create_board(initial)
    pre_board = sudoku.solve(pre)
    if pre_board is None:
        print("terminated with no solution") # Initial board breaks sudoku rules.
        return None
    if not any([-1 in row for row in pre_board]):
        print("terminated by solving")
        return steps # Board already solved
    post, *_ = sudoku.create_board()

    # Add any constraints banning failed guessed values of squares
    for _, r, c, bad_value in constraint_map:
        sudoku.s.add(post[(r, c)] != bad_value)

    steps += 1
    if steps > max_steps:
        print("out of steps")
        return steps
    guess_strategy(pre, post, pre_possibility_counts, pre_possibilities)
    post_board = sudoku.solve(post)

    if use_visualizer:
        visualize(pre_board)

    while post_board is not None:
        pre_board = sudoku.solve(pre)
        difference = get_board_difference(pre_board, post_board)

        if use_visualizer:
            visualize(post_board, [difference])

        if not any([-1 in row for row in post_board]):
            print("terminated by solving")
            return steps # board solved

        guesses.append((difference, post_board[difference[0]][difference[1]]))
        pre, pre_possibility_counts, _ = sudoku.create_board(post_board)
        post, *_ = sudoku.create_board()
        steps += 1
        if steps > max_steps:
            print("out of steps")
            return steps
        guess_strategy(pre, post, pre_possibility_counts, pre_possibilities)
        post_board = sudoku.solve(post)

    # Dead end reached if while loop terminates, so backtrack
    if len(guesses) == 0:
        print("terminated with no solution")
        return None # Cannot backtrack, so no solution
    (last_r, last_c), last_guess = guesses.pop()

    # Remove no longer relevant constraints
    while constraint_map and len(guesses) < constraint_map[-1][0]:
        constraint_map.pop()

    # Add constraint banning the last guessed value for that square
    constraint_map.append((len(guesses), last_r, last_c, last_guess))

    # Remove last guess and try to proceed again
    pre_board[last_r][last_c] = -1
    return apply_strategy(sudoku, pre_board, guess_strategy, guesses, constraint_map, steps, max_steps, use_visualizer)

def time_strategy(sudoku, guess_strategy, trials, num_unfilled, max_steps_per_trial):
    """
    Generates random boards and counts the number of steps needed to solve, returning an average timesteps to solve.
    """
    trial_steps = []
    while len(trial_steps) < trials:
        board = generate_random_starting_board(sudoku.N, num_unfilled)
        steps_taken = apply_strategy(sudoku, board, guess_strategy, max_steps=max_steps_per_trial, use_visualizer=False)
        trial_steps.append(steps_taken)
        print(f"Trial {len(trial_steps)}: {steps_taken}")
    return sum(trial_steps) / trials

if __name__ == "__main__":
    # guess_least_possibilities makes incorrect first guess, guess_forced solves perfectly.
    game_data_example = [
        [6, 5, None, 1, None, 3, None, None, 7],
        [7, None, 3, 5, 2, 4, None, None, 1],
        [None, None, 4, 6, 7, None, 5, 2, 3],
        [9, 3, 7, None, None, None, 6, 8, None],
        [None, None, 5, 8, 3, 6, None, 7, 9],
        [None, None, 6, None, None, 7, None, None, None],
        [5, 7, None, None, 1, None, 2, None, 6],
        [4, 6, 1, None, None, 2, 7, None, 5],
        [None, None, None, 7, 6, None, None, 1, 8]
        ]

    #one from solved example
    # game_data_example = [[5, None, 7, 6, 9, 8, 2, 3, 4], [2, 8, 9, 1, 3, 4, 7, 5, 6], [3, 4, 6, 2, 7, 5, 8, 9, 1], [6, 7, 2, 8, 4, 9, 3, 1, 5], [1, 3, 8, 5, 2, 6, 9, 4, 7], [9, 5, 4, 7, 1, 3, 6, 8, 2], [4, 9, 5, 3, 6, 2, 1, 7, 8], [7, 2, 3, 4, 8, 1, 5, 6, 9], [8, 6, 1, 9, 5, 7, 4, 2, 3]]

    # backtracking example
    # game_data_example = [[5, 1, 7, 6, None, 8, 2, None, 4], [2, 8, 9, 1, None, None, 7, 5, 6], [3, 4, 6, 2, 7, 5, 8, 9, 1], [6, 7, 2, 8, 4, 9, 3, 1, 5], [1, 3, 8, 5, 2, 6, 9, 4, 7], [9, 5, 4, 7, 1, 3, 6, 8, 2], [4, 9, 5, 3, 6, 2, 1, 7, 8], [7, 2, 3, 4, 8, 1, 5, 6, 9], [8, 6, 1, 9, 5, 7, 4, 2, 3]]

    sudoku = Sudoku(9)
    print(apply_strategy(sudoku, game_data_example, sudoku.guess_forced)) 

    # sudoku = Sudoku(9)
    # average_steps = time_strategy(sudoku, sudoku.guess_least_possibilities, 5, 18, 100)
    # print(f"Average steps: {average_steps}")

    # sudoku = Sudoku(4)
    # apply_strategy(sudoku, generate_random_starting_board(4, 5), sudoku.guess_least_possibilities)