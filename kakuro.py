'''
Author: John Yorke
CSCI 3482 - Artificial Intelligence - Saint Mary's University
'''

from typing import Dict, List, Any, Optional
from kakuro_csp import KakuroCSP, KakuroConstraint
import json

if __name__ == '__main__':
    '''
    Main method.
    Reads in a Kakuro config file and solves the puzzle as a CSP.
    '''
    config_filename: str = 'given_8x8.txt' # specify config file
    config: Dict[str, Any] = {}

    '''
    Support for JSON or TXT configs. 
    See the '/config' directory to view or edit config files
    '''
    with open(f'config/{config_filename}', 'r') as config_file:
        if config_filename.endswith('.json'): # load json file
            config = json.load(config_file)
        else: # read in text file
            lines = config_file.read().splitlines()
            config['options'] = {k.lower(): v == 'true' for k, v in (l.split('=') for l in lines[:6])}
            config['rows'], config['cols'] = map(int, [l.split('=')[1] for l in lines[6:8]])
            config['board'] = [l.split(',') for l in lines[8:8+config['rows']]]
            config['constraints'] = [{'row': int(r),'col': int(c),'sum': int(s),'type': t} 
                                     for r, c, s, t in (l.split(',') for l in lines[9+config['rows']:])]
    
    options: Dict[str, bool] = config['options']
    board: List[List[str]] = config['board']

    variables: List[tuple] = [(i+1, j+1) for i, row in enumerate(board) for j, cell in enumerate(row) if cell == '0']

    constraints: List[KakuroConstraint] = []
    for constraint in config['constraints']:
        row, col, rows, cols = constraint['row'], constraint['col'], config['rows'], config['cols']
        c_variables: List[tuple] = []
        match constraint['type']:
            case 'h':
                end: int = next((j for j in range(col+1, cols+1) if board[row-1][j-1] == '#'), cols+1)
                c_variables = [(row, j) for j in range(col+1, end)]
            case 'v':
                end: int = next((i for i in range(row+1, rows+1) if board[i-1][col-1] == '#'), rows+1)
                c_variables = [(i, col) for i in range(row+1, end)]
        constraints.append(KakuroConstraint(c_variables, constraint['sum']))

    kakuro: KakuroCSP = KakuroCSP(variables, constraints, options)

    solution: Optional[Dict[tuple, int]] = kakuro.search()

    '''
    Report the solution if it exists.
    See the '/out' directory to view the last solution.
    '''
    solution_str: str = f'Options: {options}\nSolution: {solution}\nSteps: {kakuro.steps}\n\n'

    if solution:
        solution_str += '\n'.join([','.join([str(solution[(i+1, j+1)]) if (i+1, j+1) in solution else cell 
                                             for j, cell in enumerate(row)]) for i, row in enumerate(board)])

    with open('out/solution.txt', 'w') as out_file:
            out_file.write(solution_str)
    print(solution_str)
