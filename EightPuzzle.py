from queue import Queue
import time
from queue import PriorityQueue
import os
from tabulate import tabulate
import re
import sys


# checks if a move is legal and if so returns the new state
def moveTile(state, direction):
    newState = list(state)
    index = newState.index('0')

    # the direction is meant from the tile that is moved, so the opposite of the direction the blank space is moved to
    if direction == 'DOWN' and index not in [0, 1, 2]:
        newState[index], newState[index - 3] = newState[index - 3], newState[index]

    if direction == 'UP' and index not in [6, 7, 8]:
        newState[index], newState[index + 3] = newState[index + 3], newState[index]

    if direction == 'RIGHT' and index not in [0, 3, 6]:
        newState[index], newState[index - 1] = newState[index - 1], newState[index]

    if direction == 'LEFT' and index not in [2, 5, 8]:
        newState[index], newState[index + 1] = newState[index + 1], newState[index]

    return ''.join(newState)


# prints the current state in the view of an 8-puzzle, also replaces the 0 with an _ for better readability
def printState(state):
    stateToPrint = state.replace('0', '_')
    for i in range(0, 9, 3):
        print(' '.join(stateToPrint[i:i + 3]))


# returns True if puzzle is solvable, False if it is not
def checkForSolvability(state):
    inversions = 0

    checkState = state.replace('0', '')

    for i in range(len(checkState)):
        for j in range(i + 1, len(checkState)):
            if checkState[i] > checkState[j]:
                inversions += 1

    # if the inversions are odd the puzzle is not solvable
    return inversions % 2 == 0


def bfs(startState, goalState):
    visited = set()
    queue = Queue()
    queue.put((startState, ''))
    generatedNodes = 0
    startTime = time.time()

    while not queue.empty():
        currentState, path = queue.get()

        # checks if time exceeded 15 min
        if time.time() - startTime > 900:
            return 'Timed out', '<<??>>', '>15min'

        if currentState == goalState:
            return path, generatedNodes, time.time() - startTime

        if currentState in visited:
            continue

        visited.add(currentState)
        for direction in ['UP', 'DOWN', 'LEFT', 'RIGHT']:
            newState = moveTile(currentState, direction)
            generatedNodes += 1

            # adds state to the queue if it was not already visited
            if newState not in visited:
                newPath = path + direction[0]
                queue.put((newState, newPath))

    return '', 0, 0

def hForMisplacedTiles(currentState, goalState):
    misplacedTiles = 0

    for i in range(len(currentState)):
        if currentState[i] != goalState[i] and currentState[i] != 0:
            misplacedTiles += 1

    return misplacedTiles


def hForManhattanDistance(currentState, goalState):
    manhattanDistance = 0

    for i in range(len(currentState)):
        if currentState[i] == 0:
            continue

        # Get current position of tile
        currentRow = i // 3
        currentCol = i % 3

        # Get goal position of tile
        goalRow = goalState.rfind(currentState[i]) // 3
        goalCol = goalState.rfind(currentState[i]) % 3

        # Calculate the Manhattan distance for the tile PS: abs is used to always receive a positive value
        manhattanDistance = abs(currentRow - goalRow) + abs(currentCol - goalCol)

    return manhattanDistance


# calculates heuristic based on how many of the tiles are in the correct order
def hForCorrectOrder(currentState, goalState):
    correctOrder = 0
    lastTile = -1

    for i in range(len(currentState)):

        if lastTile == -1:
            lastTile = currentState[i]
            continue

        if int(currentState[i]) == int(lastTile) + 1:
            correctOrder += 1

        if currentState[i] != goalState[i] and currentState[i] != 0:
            correctOrder += 1

    return correctOrder


def aSearch(startState, goalState, heuristics):
    visited = set()
    queue = PriorityQueue()
    queue.put((0, startState, '', 0))  # priority, state, path, cost
    generatedNodes = 0
    startTime = time.time()

    while not queue.empty():

        _, currentState, path, cost = queue.get()  # _ because the priority of the current state is not required

        if time.time() - startTime > 900:
            return 'Timed out', '<<??>>', '>15min'

        if currentState == goalState:
            return path, generatedNodes, time.time() - startTime

        if currentState in visited:
            continue

        visited.add(currentState)

        for direction in ['UP', 'DOWN', 'LEFT', 'RIGHT']:
            newState = moveTile(currentState, direction)

            if not newState or newState in visited:
                continue

            generatedNodes += 1
            estimate = 0

            # calculates estimate based on the heuristics selected by the user
            if heuristics == 'manhattan':
                estimate = hForMisplacedTiles(currentState, goalState)

            if heuristics == 'misplaced':
                estimate = hForManhattanDistance(currentState, goalState)

            if heuristics == 'order':
                estimate = hForCorrectOrder(currentState, goalState)

            fn = cost + estimate + 1

            newPath = path + direction[0]
            queue.put((fn, newState, newPath, cost + 1))

    return 'Error: No solution found', generatedNodes, '???'


def dls(startState, goalState, maxDepth):
    visited = set()
    stack = [(startState, '', 0)] # state, path, current depth
    generatedNodes = 0

    while stack:
        currentState, path, currentDepth = stack.pop()
        visited.add(currentState)

        if currentState == goalState:
            return path, generatedNodes, True

        if currentDepth < maxDepth:
            for direction in ['UP', 'DOWN', 'LEFT', 'RIGHT']:
                newState = moveTile(currentState, direction)
                generatedNodes += 1

                if newState in visited:
                    continue

                newPath = path + direction[0]
                stack.append((newState, newPath, currentDepth + 1))

    return '', generatedNodes, False

def iddfs(startState, goalState):
    maxDepth = 1
    startTime = time.time()
    generatedNodes = 0

    while True:
        path, dlsNodes, found = dls(startState, goalState, maxDepth)
        generatedNodes += dlsNodes

        if found:
            return path, generatedNodes, time.time() - startTime

        maxDepth += 1
        if time.time() - startTime > 900:
            return 'Timed out', '<<??>>', '>15min'


def manualInput(goalState):
    startState: str = input("Enter the start state: ").strip().replace('_', '0')

    if not checkForSolvability(startState):
        print("The puzzle is not solvable\n")
        printState(startState)
        return

    algorithm: str = input("Enter the algorithm to use (bfs, ids, misplaced, manhattan or order): ")

    if algorithm not in ['bfs', 'ids', 'misplaced', 'manhattan', 'order']:
        print("Invalid choice of algorithm: ", algorithm)
        return

    if algorithm == 'bfs':
        solution, generatedNodes, endTime = bfs(startState, goalState)
    elif algorithm == 'ids':
        solution, generatedNodes, endTime = iddfs(startState, goalState)
    else:
        solution, generatedNodes, endTime = aSearch(startState, goalState, algorithm)

    # solution, generatedNodes, endTime = bfs(startState, goalState)
    # solution, generatedNodes, endTime = aSearch(startState, goalState, 'order')

    print(f"Total nodes generated: {generatedNodes}")
    print(f"Total time: {endTime}")
    print(f"Solution found in {len(solution)} moves:")
    print(f"{solution}")


def recursiveFolderInput(goalState, path):
    collectedData = []

    averages = [['depth', 'bfs-nodes', 'bfs-time', 'ids-nodes', 'ids-time', 'A*h1-nodes', 'A*h1-time',
                 'A*h2-nodes', 'A*h2-time', 'A*h3-nodes', 'A*h3-time']]

    for subFolder in os.listdir(path):
        subFolder = os.path.join(path, subFolder)

        if os.path.isdir(subFolder):
            algorithmData = {
                'depth': re.sub(r'\D', '', re.sub(r'^.*?[/\\]', '', subFolder)),
                'bfs': {'nodes': [], 'times': []},
                'ids': {'nodes': [], 'times': []},
                'a1': {'nodes': [], 'times': []},
                'a2': {'nodes': [], 'times': []},
                'a3': {'nodes': [], 'times': []},

            }
            for filename in os.listdir(subFolder):
                filePath = os.path.join(subFolder, filename)

                print(f"Processing {filePath}")

                if os.path.isfile(filePath) and filePath.endswith('.txt'):
                    startState = formatFileToState(filePath)

                    if not checkForSolvability(startState):
                        print("The puzzle is not solvable\n")
                        printState(startState)
                        continue

                    bfsSearch = bfs(startState, goalState)
                    if bfsSearch[0] not in ['Timed out', 'Error: No solution found']:
                        algorithmData['bfs']['nodes'].append(bfsSearch[1])
                        algorithmData['bfs']['times'].append(bfsSearch[2] if float(bfsSearch[2]) > 0 else 0.0000000001)

                    idsSearch = iddfs(startState, goalState)
                    if idsSearch[0] not in ['Timed out', 'Error: No solution found']:
                        algorithmData['ids']['nodes'].append(idsSearch[1])
                        algorithmData['ids']['times'].append(idsSearch[2] if float(idsSearch[2]) > 0 else 0.0000000001)

                    aSearchMisplaced = aSearch(startState, goalState, 'misplaced')
                    if aSearchMisplaced[0] not in ['Timed out', 'Error: No solution found']:
                        algorithmData['a1']['nodes'].append(aSearchMisplaced[1])
                        algorithmData['a1']['times'].append(aSearchMisplaced[2] if float(aSearchMisplaced[2]) > 0 else 0.0000000001)

                    aSearchManhattan = aSearch(startState, goalState, 'manhattan')
                    if aSearchManhattan[0] not in ['Timed out', 'Error: No solution found']:
                        algorithmData['a2']['nodes'].append(aSearchManhattan[1])
                        algorithmData['a2']['times'].append(aSearchManhattan[2] if float(aSearchManhattan[2]) > 0 else 0.0000000001)

                    aSearchOrder = aSearch(startState, goalState, 'order')
                    if aSearchOrder[0] not in ['Timed out', 'Error: No solution found']:
                        algorithmData['a3']['nodes'].append(aSearchOrder[1])
                        algorithmData['a3']['times'].append(aSearchOrder[2] if float(aSearchOrder[2]) > 0 else 0.0000000001)

                    # print(algorithmData)

        collectedData.append(algorithmData)

    for data in collectedData:
        averageEntry = [
            data['depth'],
            sum(data['bfs']['nodes'])/(len(data['bfs']['nodes']) if len(data['bfs']['nodes']) > 0 else 1),
            sum(data['bfs']['times']) / (len(data['bfs']['times']) if len(data['bfs']['nodes']) > 0 else 1),
            sum(data['ids']['nodes']) / (len(data['ids']['nodes']) if len(data['ids']['nodes']) > 0 else 1),
            sum(data['ids']['times']) / (len(data['ids']['times']) if len(data['ids']['times']) > 0 else 1),
            sum(data['a1']['nodes']) / (len(data['a1']['nodes']) if len(data['bfs']['nodes']) > 0 else 1),
            sum(data['a1']['times']) / (len(data['a1']['times']) if len(data['bfs']['nodes']) > 0 else 1),
            sum(data['a2']['nodes']) / (len(data['a2']['nodes']) if len(data['bfs']['nodes']) > 0 else 1),
            sum(data['a2']['times']) / (len(data['a2']['times']) if len(data['bfs']['nodes']) > 0 else 1),
            sum(data['a3']['nodes']) / (len(data['a3']['nodes']) if len(data['bfs']['nodes']) > 0 else 1),
            sum(data['a3']['times']) / (len(data['a3']['times']) if len(data['bfs']['nodes']) > 0 else 1),
        ]
        averages.append(averageEntry)

    print(tabulate(averages, headers='firstrow', tablefmt='fancy_grid'))

def formatFileToState(path):
    with open(path, 'r') as file:
        return ''.join(file.read().replace('_', '0').split())


# test-state: 531087264 651482037 867254301 752631480

def main():
    goalState = '123456780'

    if len(sys.argv) < 2:
        print('Usage: python EightPuzzle <runType> <if runType=a: path to folder>')
        return

    if sys.argv[1] == 'm':
        manualInput(goalState)
        return

    if sys.argv[1] == 'a':
        if len(sys.argv) != 3:
            print('Usage: python EightPuzzle <runType> <if runType=a: path to folder>')
            return

        if not os.path.exists(sys.argv[2]):
            print('Not a valid path!')
            return

        recursiveFolderInput(goalState, sys.argv[2])

    # recursiveFolderInput(goalState, 'Part3')


if __name__ == "__main__":
    main()
