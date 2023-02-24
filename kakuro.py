'''
Author: John Yorke
CSCI 3482 - Artificial Intelligence - Saint Mary's University
'''

from typing import Dict, List, Optional
from kakuro_csp import KakuroCSP, KakuroConstraint
import json

if __name__ == '__main__':
    '''
    Main method.
    Reads in a Kakuro config file and solves the puzzle as a CSP.
    '''
    config_file: str = 'given_5x5.json'
    config: Dict[str, str] = json.load(open(f'config/{config_file}', 'r'))
    
    options: Dict[str, bool] = config['options']

    rows: int = config['rows']
    cols: int = config['cols']
    board: List[List[str]] = config['board']

    variables: List[tuple] = [(i+1, j+1) for i, row in enumerate(board) for j, cell in enumerate(row) if cell == '0']

    constraints: List[KakuroConstraint] = []
    for constraint in config['constraints']:
        row: int = constraint['row']
        col: int = constraint['col']
        match constraint['type']:
            case 'h':
                end: int = next((j for j in range(col+1, cols+1) if board[row-1][j-1] == '#'), cols+1)
                c_variables: List[tuple] = [(row, j) for j in range(col+1, end)]
            case 'v':
                end = next((i for i in range(row+1, rows+1) if board[i-1][col-1] == '#'), rows+1)
                c_variables: List[tuple] = [(i, col) for i in range(row+1, end)]
        constraints.append(KakuroConstraint(c_variables, constraint['sum']))

    kakuro: KakuroCSP = KakuroCSP(variables, constraints, options)

    solution: Optional[Dict[tuple, int]] = kakuro.bt_search()

    # report the solution
    solution_str: str = f'Options: {options}\nSolution: {solution}\nSteps: {kakuro.steps}\n\n'

    if solution:
        solution_str += '\n'.join([','.join([str(solution[(i+1, j+1)]) if (i+1, j+1) in solution else cell 
                                             for j, cell in enumerate(row)]) for i, row in enumerate(board)])

    with open('out/solution.txt', 'w') as out_file:
            out_file.write(solution_str)
    print(solution_str)
