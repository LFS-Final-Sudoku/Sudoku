# Sudoku

Overview: <br />
General:<br />
This project is an analysis of Sudoku solving strategies and how they compare to each other. The strategies we implemented were arbitrarily picking squares to fill guesses into, filling in squares with the fewest possible values first, and filling in squares that are forced to be a particular value before guessing a square with fewest possibilities as before. For each of these strategies, the model backtracks when it reaches a dead end where no moves are legal, undoing guesses until progress can be made by choosing a different guess. This guarantees that any of these strategies will solve any solvable Sudoku board given enough steps, though their efficiency varies greatly.

Visualization:
We had two visualization tools for this project: one for the model and one for plotting results. In our visualizer.py file we have a pygame visualization of a sudoku board. This visualizer loads whatever initial sudoku board is fed in and then you are able to progress forward and see the solving algorithm make a guess as a new entry shows up in red. This progresses and you can watch the solver guess and backtrack until it solves the puzzle. We also have a graphs.py file that generates graphs for visualizing results from the solver and the effects of changing different variables.

Testing: 
Our testing focused on the non-trivial functions, testing with both regular tests and property-based tests. We also included a property-based test that compares the number of steps taken in solving a sudoku with the different heuristics. This test ensures that the trivial solving algorithm that guesses randomly always solves the puzzle in fewer or equal steps than the worst case runtime. It also asserts that the better the heuristic used is, the fewer steps the algorithm takes. Because of the randomness of hypothesis testing, we could only assert upper bounds on the number of steps.  

Scope of Model:
Our model covers traditional sudoku. It can be used on any board that is the size of a perfect square (1x1, 4x4, 9x9, 16x16, etc.). Our model does not cover rule variants or alternative board layouts. Within traditional sudoku, we cover 3 main strategies with the ability to modularly add more. Boards can start with any amount of filled or unfilled squares and can have different limits on steps to solve. 

Did your goals change at all from your proposal? Did you realize anything you planned was unrealistic, or that anything you thought was unrealistic was doable?:
Our goals changed from analyzing runtime on a large scale to analyzing different heuristics for solving on a smaller scale. Even with using z3, fully solving a 9x9 sudoku board with individual steps was a very long process, so we customized certain example boards to show the way different solving strategies made fewer mistakes and solved the board in fewer steps. This ended up being a more interesting approach because we could directly see exactly what each solving algorithm was doing and compare the number of steps. 

We started by trying to use Forge, but quickly realized that we weren’t going to have enough computing power to do any meaningful analysis in Forge. After switching to z3, we were able to get more interesting results! 


Video Link: https://drive.google.com/file/d/1JLvVLamghUMewKITAS6mb2fDtRcf01l-/view?usp=sharing

Collaborators: We did not collaborate on the final project.
