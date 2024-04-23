from z3 import *

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
            print(col, end=" ")
        print()

class Sudoku(object):
    def __init__(self, N, game_data):
        """Constructor of this class"""

        self.N = N
        self.game_data = game_data

        # Solver
        self.s = Solver()

        # Grid Variables
        self.L = {(i, j): Int('var_{}_{}'.format(i, j)) for i in range(N) for j in range(N)}


    def get_3x3_section(self, row, col):
        start_row = (row // 3) * 3
        start_col = (col // 3) * 3
        section = []
        for i in range(start_row, start_row + 3):
            section.append(self.L[(i,start_col)]) 
            section.append(self.L[(i,start_col +1)])
            section.append(self.L[(i,start_col +2)])
        return section

    def solve(self):

        # EDIT HERE: PART 1 CONSTRAINTS
        # Here, `self.N` is the size of the board, and `self.game_data` is the game data
        # Feel free to use `self.s.push()` and `self.s.pop()` across `solve` and `check_multiple`
        # to reset constraints if you don't want to reuse them in `check_multiple`

        for i in range(self.N):
            for j in range(self.N):
                self.s.add(self.L[(i, j)] >0)
                self.s.add(self.L[(i, j)] <self.N+1)

        # constraining rows
        for row in range(self.N):
            for i in range(self.N):
                for j in range(self.N):
                    if (i !=j):
                        self.s.add(self.L[(row, i)] != self.L[(row, j)])

        # constraining cols
        for col in range(self.N):
            for i in range(self.N):
                for j in range(self.N):
                    if (i !=j):
                        self.s.add(self.L[(i, col)] != self.L[(j, col)])

        # constraining sections
        # this could probably be cut down time-wise
        for i in range(self.N):
            for j in range(self.N):
                for k in range(self.N):
                    for l in range(self.N):
                        if (i!=k or j!=l):
                            if (self.get_3x3_section(i, j) ==
                                self.get_3x3_section(k, l)):
                                self.s.add(self.L[(i, j)] != self.L[(k, l)])



        # Check for PART 1
        result = self.s.check()
        if result == sat:
            return get_grid(self.N, self.L, self.s.model())
        else:
            return None


    def check_multiple(self, ans):
        """PART 2"""

        # EDIT HERE: PART 2 CONSTRAINTS
        # Here, `self.N` is the size of the board, and `self.game_data` is the game data
        # Feel free to use `self.s.push()` and `self.s.pop()` across `solve` and `check_multiple`
        # to reset constraints if you don't want to reuse them in `check_multiple`
       
        self.s.add(ans != solve())
        # Check for PART 2
        result = self.s.check()
        return result == sat

if __name__ == "__main__":
    game_data_example = [
      [[' ' for _ in range(9)] for _ in range(9)]
    ]

    sudoku = Sudoku(9, game_data_example)
    
    # PART 1
    ans = sudoku.solve()
    print_grid(ans)

    # PART 2
    #print(kenken.check_multiple(ans))