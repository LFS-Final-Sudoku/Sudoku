import time
from sudoku import time_strategy, Sudoku
import matplotlib.pyplot as plt

## Strategy
## 0 = random
## 1 = guess least possibilities

def call_time_strategy(sudoku, guess_strategy, trials, num_unfilled, max_steps_per_trial):
    start = time.time()
    avg_steps = time_strategy(sudoku, guess_strategy, trials, num_unfilled, max_steps_per_trial)
    total_time = time.time() - start
    avg_time = total_time / trials

    return avg_steps, avg_time

def get_sudoku_and_strategy(grid_size, strategy):
    sudoku = Sudoku(grid_size)

    if strategy == 0: guess_strategy = None
    elif strategy == 1: guess_strategy = sudoku.guess_least_possibilities
    else: raise ValueError("Invalid strategy")

    return sudoku, guess_strategy

def plot_data(x, y, x_title, y_title):
    x = [str(item) for item in x]
    plt.bar(x, y)
    plt.xlabel(x_title)
    plt.ylabel(y_title)
    plt.show()

def create_graph_grid_size(grid_size_list, strategy, trials, num_unfilled, max_steps_per_trial):
    avg_steps_list, avg_time_list = [], []
    for grid_size in grid_size_list:
        sudoku, guess_strategy = get_sudoku_and_strategy(grid_size, strategy)
        avg_steps, avg_time = call_time_strategy(sudoku, guess_strategy, trials, num_unfilled, max_steps_per_trial)
        avg_steps_list.append(avg_steps)
        avg_time_list.append(avg_time)

    plot_data(grid_size_list, avg_steps_list, "Grid Size", "Average Steps to Solve")
    plot_data(grid_size_list, avg_time_list, "Grid Size", "Average Time to Solve")


def create_graph_strategy(grid_size, strategy_list, trials, num_unfilled, max_steps_per_trial):
    avg_steps_list, avg_time_list = [], []
    for strategy in strategy_list:
        sudoku, guess_strategy = get_sudoku_and_strategy(grid_size, strategy)
        avg_steps, avg_time = call_time_strategy(sudoku, guess_strategy, trials, num_unfilled, max_steps_per_trial)
        avg_steps_list.append(avg_steps)
        avg_time_list.append(avg_time)

    plot_data(strategy_list, avg_steps_list, "Solve Strategy", "Average Steps to Solve")
    plot_data(strategy_list, avg_time_list, "Solve Strategy", "Average Time to Solve")


def create_graph_num_unfilled(grid_size, strategy, trials, num_unfilled_list, max_steps_per_trial):
    avg_steps_list, avg_time_list = [], []
    for num_unfilled in num_unfilled_list:
        sudoku, guess_strategy = get_sudoku_and_strategy(grid_size, strategy)
        avg_steps, avg_time = call_time_strategy(sudoku, guess_strategy, trials, num_unfilled, max_steps_per_trial)
        avg_steps_list.append(avg_steps)
        avg_time_list.append(avg_time)

    plot_data(num_unfilled_list, avg_steps_list, "Number of Unfilled Squares", "Average Steps to Solve")
    plot_data(num_unfilled_list, avg_time_list, "Number of Unfilled Squares", "Average Time to Solve")

MAX_STEPS = 100
TRIALS = 1
if __name__ == "__main__":
    create_graph_grid_size(grid_size_list=[4,9], strategy=1, trials=TRIALS, num_unfilled=5, max_steps_per_trial=MAX_STEPS)
    create_graph_strategy(grid_size=4, strategy_list=[1,1], trials=TRIALS, num_unfilled=5, max_steps_per_trial=MAX_STEPS)
    create_graph_num_unfilled(grid_size=4, strategy=1, trials=TRIALS, num_unfilled_list=[1,2,3,4,5,6,7,8,9,10], max_steps_per_trial=MAX_STEPS)
