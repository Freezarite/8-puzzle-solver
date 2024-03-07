# Eight Puzzle Solver
by Markus Roth

## Overview
This Python project is my submission for the first lab in the course COM S 472 at Iowa State University.
It implements various algorithms to solve the famous Eight Puzzle Game.

### Algorithms used:
1. BFS
2. IDDSF (increasing its depth by 1 on every fail)
3. A* (using 3 different heuristics)

### Heuristics used:
1. Misplaced tiles Heuristics (checks for in-place tiles)
2. Manhattan distance
3. Order (my own little heuristics, checks for the order of the tiles and if they are in-place)

## Requirements
To run this project, Python 3 is required.

## Usage
The program can be run in two modes. A manual one, which asks the user for a puzzle input and then returns the solution,
and additionally some stats including time taken and the nodes generated.

### Manual-Run
``python EightPuzzle m``  
After running the program like this it's going to ask for the start state and the preferred algorithm as console inputs.

### Automated-Run
``python EightPuzzle a <path-to-input>``  
As an input a folder containing sub-folders with puzzles is required. The program will go through the folders recursively
and run all the algorithms for all the puzzles. Finally, a table is generated showing the statistics for the different algorithms runs
in the different folders.  
An example folder is provided as "Part3"

### Additional Information
For additional information you can view the "Lab1 8-puzzle.pdf" which is the assignments' description.