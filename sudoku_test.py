from sudoku import *
from hypothesis import given, strategies as st, settings, event

# test that the created board is follows all sudoku rules. 
def test_create_board(sudoku):
    board_created = sudoku.create_board()
    
    for i in range(sudoku.N):
            for j in range(sudoku.N):
                for k in range(sudoku.N):
                    for l in range(sudoku.N):
                        if i == k and j == l:
                            continue
                        if i == k or j == l or sudoku.get_mini_section(i, j) == sudoku.get_mini_section(k, l):
                            # a cell is empty or filled with correct constraints
                            assert (
                                board_created[0][(i, j)] == -1, board_created[0][(k, l)] == -1 or
                                board_created[0][(i, j)] != board_created[0][(k, l)])


# test that a solved board is fully filled and follows all the rules
def test_generate_solved_board(sudoku):
    board_solved = sudoku.generate_solved_board()
    for i in range(sudoku.N):
            for j in range(sudoku.N):
                for k in range(sudoku.N):
                    for l in range(sudoku.N):
                        if i == k and j == l:
                            assert (board_solved[i][j] == board_solved[k][l])
                        elif i == k or j == l or sudoku.get_mini_section(i, j) == sudoku.get_mini_section(k, l):
                            assert (
                                board_solved[i][j]  != board_solved[k][l])
                            assert (board_solved[i][j]!= -1)
                            assert (board_solved[k][l]!= -1)


SUDOKU_BOARD_SIZE = 4
SUDOKU_SQUARE_COUNT = SUDOKU_BOARD_SIZE*SUDOKU_BOARD_SIZE

# property based test that ensures the correct number of values are removed
random_ints = st.integers(0, SUDOKU_BOARD_SIZE)
@given(random_ints)
@settings(deadline=None, max_examples=10)
def test_remove_values(sudoku, random_int):
    solved_board = sudoku.generate_solved_board()
    removed_board = remove_values(solved_board, random_int)

    difference_count = 0
    for i in range(sudoku.N):
            for j in range(sudoku.N):
                if solved_board[i][j] != removed_board[i][j]:
                    difference_count = difference_count +1 
    
    assert (difference_count == random_int)

#sudoku_row = st.lists(st.integers(min_value= 1,max_value= SUDOKU_BOARD_SIZE+1), 
       #               min_size =SUDOKU_BOARD_SIZE, max_size = SUDOKU_BOARD_SIZE, unique = True) 



#property based test than ensures random starting board has the correct number of blanks
random_ints = st.integers(0, SUDOKU_SQUARE_COUNT)
@given(random_ints)
@settings(deadline=None, max_examples=20)
def test_generate_random_starting_board(sudoku, random_int):
    start_board = generate_random_starting_board(sudoku.N, random_int)
    blank_count = 0
    for i in range(sudoku.N):
            for j in range(sudoku.N):
                if start_board[i][j] == -1:
                    blank_count = blank_count +1 
    assert (blank_count == random_int)

# property based test for comparting strategy steps
num_unfilled_random = st.integers(0, SUDOKU_SQUARE_COUNT)
@given(num_unfilled_random )
@settings(deadline=None, max_examples=20)
def test_time_strategy(sudoku, num_unfilled_random):
     # number of filled squares on starting board
     num_filled = SUDOKU_SQUARE_COUNT - num_unfilled_random
     # number of steps for 1 sudoku game with guess_cell strategy
     steps_guess_cell = time_strategy(sudoku, sudoku.guess_cell, 1, num_unfilled_random, 1)
     # number of steps for 1 sudoku game with guess_least_possible strategy
     steps_guess_least_possibilities = time_strategy(sudoku, sudoku.guess_least_possibilities, 1, num_unfilled_random, 1)

     # creates an upper bound for solving based on worst case running time 
     assert (steps_guess_cell <= SUDOKU_BOARD_SIZE**(SUDOKU_SQUARE_COUNT -num_filled))
     # asserts that guess_least_possilities takes fewer or equal steps as guess_cell
     assert (steps_guess_least_possibilities <= steps_guess_cell)

    
if __name__ == "__main__":
    sudoku = Sudoku(4)
    
    test_create_board(sudoku)
    test_generate_solved_board(sudoku)
    test_remove_values(sudoku)
    test_generate_random_starting_board(sudoku)
    test_time_strategy(sudoku)
    print("All Tests Passed!")

   