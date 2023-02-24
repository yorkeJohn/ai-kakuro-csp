'''
Author: John Yorke
CSCI 3482 - Artificial Intelligence - Saint Mary's University
'''

from typing import Dict, List, Set, Optional
from copy import deepcopy
from collections import deque

class KakuroConstraint:
    '''
    A class representing a Kakuro constraint where unique variables must sum to a specified value.
    '''
    def __init__(self, variables: List[tuple], sum: int) -> None:
        '''
        Params:
            variables (list): Variables included in the constraint.
            sum (int): Required sum.
        '''
        self.variables: List[tuple] = variables
        self.sum: int = sum

    def is_satisfied(self, assignment: Dict[tuple, int]) -> bool:
        '''
        Tests if the constraint is satisfied.
        
        Params:
            assignment (dict): Current assignment.
        Returns:
            bool: True if the constraint is satisfied, False otherwise.
        '''
        values: List[int] = [assignment[v] for v in self.variables if v in assignment]
        if not len(set(values)) == len(values): # alldiff constraint
            return False
        if not all(v in assignment.keys() for v in self.variables):
           return True
        return sum(values) == self.sum # sum constraint
    
class KakuroCSP:
    '''
    A class representing a Kakuro puzzle as a CSP (Constraint Satisfaction Problem).
    '''
    def __init__(self, variables: List[tuple], constraints: List[KakuroConstraint], options: Dict[str, bool]) -> None:
        '''
        Params:
            variables (list): Variables each representing a grid position in the format (row, col), 1-indexed.
            constraints (list): Constraints each representing a required sum for variables.
            options (dict): Algorithm options.
        '''
        self.variables: List[tuple] = variables
        self.domains: Dict[tuple, List[int]] = {v:list(range(1, 10)) for v in self.variables}
        self.constraints: Dict[tuple, List[KakuroConstraint]] = {v:[c for c in constraints if v in c.variables] 
                                                                 for v in self.variables}
        self.options: Dict[str, bool] = options
        self.steps: int = 0
        self.unassigned: List[tuple] = self.variables.copy()

        self.node_consistency()
        self.ac_3({})

    def is_consistent(self, variable: tuple, assignment: Dict[tuple, int]) -> bool:
        '''
        Tests if a variable is consistent in the assignment.

        Params:
            variable (tuple): Variable to test consistency against.
            assignment (dict): Current assignment.
        Returns:
            bool: True if consistent, False otherwise.
        '''
        for constraint in self.constraints[variable]:
            if not constraint.is_satisfied(assignment):
                return False
        return True
    
    def node_consistency(self) -> bool:
        '''
        Node Consistency algorithm for domain pruning. Does nothing if nc=false.

        Returns:
            bool: True if consistency is established, False otherwise.
        '''
        if not self.options['nc']:
            return True
        
        for variable in self.variables:
            min_sum: int = min(c.sum for c in self.constraints[variable])
            min_vars: int = min(len(c.variables) for c in self.constraints[variable])
            self.domains[variable] = list(filter(lambda value: value <= min_sum - min_vars + 1, self.domains[variable]))

            if not self.domains[variable]:
                return False
        return True

    def get_neighbours(self, variable: tuple) -> List[tuple]:
        '''
        Gets all unassigned neighbours of a variable.

        Params:
            variable (tuple): Variable to get neighbours.
        Returns:
            list: A list of neighbour variables.
        '''
        return [u for u in self.unassigned if u in 
                [v for c in self.constraints[variable] for v in c.variables] 
                and u != variable]

    def forward_check(self, variable: tuple, assignment: Dict[tuple, int]) -> bool:
        '''
        Forward Checking algorithm for constraint propogation. Does nothing if fc=false.

        Params:
            variable (tuple): Variable to forward check neighbours.
            assignment (dict): Current assignment.
        Returns:
            bool: True if consistency is established, False otherwise.
        '''
        if not self.options['fc']:
            return True
        
        for neighbour in self.get_neighbours(variable):
            for value in self.domains[neighbour].copy(): 

                if not self.is_consistent(variable, {**assignment, neighbour: value}):
                    self.domains[neighbour].remove(value)

                    if not self.domains[neighbour]:
                        return False
        return True
    
    def get_arcs(self) -> Set[tuple[tuple, tuple]]:
        '''
        Gets all arcs in the unassigned variables of the CSP.

        Returns:
            list: A list of all arcs.
        '''
        return {(v1, v2) for constraints in self.constraints.values()
                for c in constraints for v1 in c.variables for v2 in c.variables 
                if v1 != v2 and v2 in self.unassigned}

    def ac_3(self, assignment: Dict[tuple, int]) -> bool:
        '''
        AC-3 (Arc Consistency 3) algorithm for constraint propagation. Does nothing if ac3=false.

        Params:
            assignment (dict): Current assignment.
        Returns:
            bool: True if consistency is established, False otherwise.
        '''
        if not self.options['ac3']:
            return True

        queue = deque(self.get_arcs())
        while queue:
            xi, xj = queue.popleft()
            if self.revise(xi, xj, assignment.copy()):
                if not self.domains[xi]:
                    return False
                for constraint in self.constraints[xi]:   
                    for xk in constraint.variables:
                        if xk != xj:
                            queue.append((xk, xi))
        return True

    def revise(self, xi: tuple, xj: tuple, assignment: Dict[tuple, int]) -> bool:
        '''
        Remove inconsistent values from domain of xi.

        Params:
            xi (tuple): Variable.
            xj (tuple): Variable.
            assignment (dict): Current assignment.
        Returns:
            bool: True if domain of xi is revised, False otherwise.
        '''       
        revised = False
        for vi in self.domains[xi].copy():
            assignment[xi] = vi
            if not any(constraint.is_satisfied({**assignment, xj: vj}) 
                       for constraint in self.constraints[xi] 
                       if xj in constraint.variables 
                       for vj in self.domains[xj]):
                self.domains[xi].remove(vi)
                revised = True
        return revised
    
    def mac(self, assignment: Dict[tuple, int]) -> bool:
        '''
        MAC (Maintaining Arc Consistency) extension of AC-3. Does nothing if mac=false.

        Params:
            assignment (dict): Current assignment.
        Returns:
            bool: True if consistency is established, False otherwise.
        '''
        if not self.options['mac']:
            return True
        return self.ac_3(assignment)
    
    def select_variable(self) -> tuple:
        '''
        Selects an unassigned variable.
        Uses MRV (Minimum Remaining Value) heuristic if mrv=true, first variable otherwise.

        Returns:
            tuple: A variable.
        '''
        if not self.options['mrv']:
            return self.unassigned[0]
        return min(self.unassigned, key=lambda var: len(self.domains[var]))
        '''
        Degree Heuristic:
            return min(self.unassigned, key=lambda var: sum([len(c.variables) for c in self.constraints[var]]))
        Random:
            return random.choice(self.unassigned)
        '''
    
    def order_domain(self, variable: tuple, assignment: Dict[tuple, int]) -> List[int]:
        '''
        Gets the ordered domain of a variable.
        Uses LCV (Least Constraining Value) heuristic if lcv=true, does nothing otherwise.

        Params:
            variable (tuple): Variable to get domain.
            assignment (dict): Current assignment.
        Returns:
            list: An ordered domain.
        '''
        if not self.options['lcv']:
            return self.domains[variable]
        return sorted(self.domains[variable], key=lambda value: self.count_conflicts(value, variable, assignment))
    
    def count_conflicts(self, value: int, variable: tuple, assignment: Dict[tuple, int]) -> int:
        '''
        Counts the neighbour conflicts when a value is assigned to a variable.

        Params:
            value (int): Value to test.
            variable (tuple): Variable to assign.
            assignment (dict): Current assignment.
        Returns:
            int: The number of conflicts.
        '''
        conflicts: int = 0
        for neighbour in self.get_neighbours(variable):
            for n_value in self.domains[neighbour]: 
                if not self.is_consistent(neighbour, {**assignment, neighbour: n_value, variable: value}):
                    conflicts+= 1
        return conflicts

    def search(self, assignment: Dict[tuple, int] = {}) -> Optional[Dict[tuple, int]]:
        '''
        Backtracking Search algorithm.

        Params:
            assignment (dict): Current assignment.
        Returns:
            optional: A solution if one exists.
        '''
        if len(assignment) == len(self.variables):
            return assignment # if all variables are assigned, the solution is found

        self.unassigned = [v for v in self.variables if v not in assignment]
        variable: tuple = self.select_variable()

        for value in self.order_domain(variable, assignment):
            self.steps += 1 # count a step each time a variable is tested
            last_domains: Dict[tuple, List[int]] = deepcopy(self.domains)

            new_assignment: Dict[tuple, int] = {**assignment, variable: value}
            if self.is_consistent(variable, new_assignment):
                if self.forward_check(variable, new_assignment) and self.mac(new_assignment):
                    result: Optional[Dict[tuple, int]] = self.search(new_assignment)
                    # if a result is found, return it
                    if result:
                        return result

            # if we are using FC or MAC, restore domains when we backtrack
            if self.options['fc'] or self.options['mac']:
                self.domains = deepcopy(last_domains)
        return None
