return_approach_level = 0
branch = 0
GivenPred = True
IfPred = True
import ast
from copy import deepcopy
fitness_vector = []

def levensthein_distance(str1: str, str2: str) -> int:
    """
    Calculates the Levenshtein distance between two strings
    Input type: str1: str, str2: str
    Output type: int
    """
    if len(str2) == 0:
        return len(str1)
    elif len(str1) == 0:
        return len(str2)
    elif str1[0] == str2[0]:
        return levensthein_distance(str1[1:], str2[1:])
    else:
        return 1 + min([levensthein_distance(str1[1:], str2), levensthein_distance(str1, str2[1:0]), levensthein_distance(str1[1:], str2[1:])])

def evaluate_fitness_for_other_types(stmt):
    """
    Given the stmt, evaluates the fitness function:
    Such as isinstance(x, myClass()) returns 1
    """
    pass

def evaluate_fitness(left, right, op, flag):
    global GivenPred
    global IfPred
    global return_approach_level
    GivenPred = flag
    return_approach_level -= 1
    global branch
    op_result = True
    K = 1
    match op:
        case '!=':
            branch = -abs(left - right)
            op_result = left != right
        case '==':
            if isinstance(left, str) and isinstance(right, str):
                branch = levensthein_distance(left, right)
            else:
                branch = abs(left - right)
            op_result = left == right
        case '>':
            branch = right - left + K
            op_result = left > right
        case '<':
            branch = left - right + K
            op_result = left < right
        case 'in':
            branch = min([abs(left - right_elem) for right_elem in right])
            op_result = left in right
        case 'not in':
            branch = min([-abs(left - right_elem) for right_elem in right])
            op_result = left not in right
    equality_ops = ['=', '!=', 'in', 'not in']
    branch = branch if flag else -branch + 2 * K if op not in equality_ops else -branch
    branch = normalize_branch(branch)
    IfPred = op_result
    return op_result

def normalize_branch(branch):
    return 1 - 1.001 ** (-clip(branch))

def clip(branch_distance):
    """
    To keep the search space within 5000, -5000
    Note: For given test cases, clip function were not used.
    """
    if branch_distance > 5000:
        return 5000
    elif branch_distance < -5000:
        return -5000
    else:
        return branch_distance

def foo(x, y, z):
    if x > 10:
        if y == 'somestring':
            return 10
    elif x == 2:
        if z < 10:
            return 12
        else:
            return 9
    else:
        return 9

def foo_1(x, y, z):
    global return_approach_level
    return_approach_level = 0
    if evaluate_fitness(x, 10, '>', True):
        if evaluate_fitness(y, 'somestring', '==', True):
            return 10
    elif x == 2:
        if z < 10:
            return 12
        else:
            return 9
    else:
        return 9
foo_1(11, 'somestring', 5)
fitness_vector.append(return_approach_level + branch)

def foo_2(x, y, z):
    global return_approach_level
    return_approach_level = 0
    if evaluate_fitness(x, 10, '>', True):
        if evaluate_fitness(y, 'somestring', '==', False):
            return 10
    elif x == 2:
        if z < 10:
            return 12
        else:
            return 9
    else:
        return 9
foo_2(11, 'somestring', 5)
fitness_vector.append(return_approach_level + branch)

def foo_3(x, y, z):
    global return_approach_level
    return_approach_level = 0
    if evaluate_fitness(x, 10, '>', False):
        if y == 'somestring':
            return 10
    elif evaluate_fitness(x, 2, '==', True):
        if evaluate_fitness(z, 10, '<', True):
            return 12
        else:
            return 9
    else:
        return 9
foo_3(11, 'somestring', 5)
fitness_vector.append(return_approach_level + branch)

def foo_4(x, y, z):
    global return_approach_level
    return_approach_level = 0
    if evaluate_fitness(x, 10, '>', False):
        if y == 'somestring':
            return 10
    elif evaluate_fitness(x, 2, '==', True):
        if evaluate_fitness(z, 10, '<', False):
            return 12
        else:
            return 9
    else:
        return 9
foo_4(11, 'somestring', 5)
fitness_vector.append(return_approach_level + branch)

def foo_5(x, y, z):
    global return_approach_level
    return_approach_level = 0
    if evaluate_fitness(x, 10, '>', False):
        if y == 'somestring':
            return 10
    elif evaluate_fitness(x, 2, '==', False):
        if z < 10:
            return 12
        else:
            return 9
    else:
        return 9
foo_5(11, 'somestring', 5)
fitness_vector.append(return_approach_level + branch)