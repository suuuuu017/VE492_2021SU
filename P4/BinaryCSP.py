# Hint: from collections import deque
from Interface import *
from collections import deque


# = = = = = = = QUESTION 1  = = = = = = = #


def consistent(assignment, csp, var, value):
    """
    Checks if a value assigned to a variable is consistent with all binary constraints in a problem.
    Do not assign value to var.
    Only check if this value would be consistent or not.
    If the other variable for a constraint is not assigned,
    then the new value is consistent with the constraint.

    Args:
        assignment (Assignment): the partial assignment
        csp (ConstraintSatisfactionProblem): the problem definition
        var (string): the variable that would be assigned
        value (value): the value that would be assigned to the variable
    Returns:
        boolean
        True if the value would be consistent with all currently assigned values, False otherwise
    """
    # TODO: Question 1
    for constraint in csp.binaryConstraints:
        if constraint.affects(var):
            var2 = constraint.otherVariable(var)
            if assignment.isAssigned(var2):
                value2 = assignment.assignedValues[var2]
                if not constraint.isSatisfied(value, value2):
                    return False
    return True
    #why it is true for others

    raise_undefined_error()


def recursiveBacktracking(assignment, csp, orderValuesMethod, selectVariableMethod, inferenceMethod):
    """
    Recursive backtracking algorithm.
    A new assignment should not be created.
    The assignment passed in should have its domains updated with inferences.
    In the case that a recursive call returns failure or a variable assignment is incorrect,
    the inferences made along the way should be reversed.
    See maintainArcConsistency and forwardChecking for the format of inferences.

    Examples of the functions to be passed in:
    orderValuesMethod: orderValues, leastConstrainingValuesHeuristic
    selectVariableMethod: chooseFirstVariable, minimumRemainingValuesHeuristic
    inferenceMethod: noInferences, maintainArcConsistency, forwardChecking

    Args:
        assignment (Assignment): a partial assignment to expand upon
        csp (ConstraintSatisfactionProblem): the problem definition
        orderValuesMethod (function<assignment, csp, variable> returns list<value>):
            a function to decide the next value to try
        selectVariableMethod (function<assignment, csp> returns variable):
            a function to decide which variable to assign next
        inferenceMethod (function<assignment, csp, variable, value> returns set<variable, value>):
            a function to specify what type of inferences to use
    Returns:
        Assignment
        A completed and consistent assignment. None if no solution exists.
    """
    # TODO: Question 1
    # print(assignment)
    if assignment.isComplete():
        return assignment
    # import pdb; pdb.set_trace()
    var = selectVariableMethod(assignment, csp)
    if not var:
        return None
    # where is the selectVariableMetho defined?
    inferences = set([])
    for val in orderValuesMethod(assignment, csp, var):
        # import pdb;
        # pdb.set_trace()
        if consistent(assignment, csp, var, val):
            assignment.assignedValues[var] = val
            #what if use AC3 the inferenceMethod call still right?
            inferences = inferenceMethod(assignment, csp, var, val)
            if inferences is not None:
                result = recursiveBacktracking(assignment, csp, orderValuesMethod, selectVariableMethod, inferenceMethod)
                # import pdb; pdb.set_trace()
                if result is not None:
                    return result
                # for inference in inferences:
                    # assignment.assignedValues[inference[0]].remove(inference[1])
        assignment.assignedValues[var] = None
        if inferences:
            for inference in inferences:
                assignment.varDomains[inference[0]].add(inference[1])
    return None

    raise_undefined_error()


def eliminateUnaryConstraints(assignment, csp):
    """
    Uses unary constraints to eleminate values from an assignment.

    Args:
        assignment (Assignment): a partial assignment to expand upon
        csp (ConstraintSatisfactionProblem): the problem definition
    Returns:
        Assignment
        An assignment with domains restricted by unary constraints. None if no solution exists.
    """
    domains = assignment.varDomains
    for var in domains:
        for constraint in (c for c in csp.unaryConstraints if c.affects(var)):
            for value in (v for v in list(domains[var]) if not constraint.isSatisfied(v)):
                domains[var].remove(value)
                # Failure due to invalid assignment
                if len(domains[var]) == 0:
                    return None
    return assignment


def chooseFirstVariable(assignment, csp):
    """
    Trivial method for choosing the next variable to assign.
    Uses no heuristics.
    """
    for var in csp.varDomains:
        if not assignment.isAssigned(var):
            return var


# = = = = = = = QUESTION 2  = = = = = = = #


def minimumRemainingValuesHeuristic(assignment, csp):
    """
    Selects the next variable to try to give a value to in an assignment.
    Uses minimum remaining values heuristic to pick a variable. Use degree heuristic for breaking ties.

    Args:
        assignment (Assignment): the partial assignment to expand
        csp (ConstraintSatisfactionProblem): the problem description
    Returns:
        the next variable to assign
    """
    nextVar = None
    domains = assignment.varDomains

    # TODO: Question 2
    min = float('inf')
    maxDegree = -1 * float('inf')
    for var in domains:
        if not assignment.isAssigned(var):
            if len(domains[var]) < min:
                nextVar = var
                min = len(domains[var])
                maxDegree = degreeHeuristics(var, assignment, csp)
            if len(domains[var]) == min:
                if degreeHeuristics(var, assignment, csp) > maxDegree:
                    nextVar = var
                    maxDegree = degreeHeuristics(var, assignment, csp)
    return nextVar
    raise_undefined_error()

def degreeHeuristics(var, assignment, csp):
    count = 0
    for rest in csp.binaryConstraints:
        if not assignment.isAssigned(rest.otherVariable(var)) and rest.affects(var):
            count = count + 1
    return count


def orderValues(assignment, csp, var):
    """
    Trivial method for ordering values to assign.
    Uses no heuristics.
    """
    return list(assignment.varDomains[var])


# = = = = = = = QUESTION 3  = = = = = = = #

def takeSecond(elem):
    return elem[1]
def takeFirst(elem):
    return elem[0]

def leastConstrainingValuesHeuristic(assignment, csp, var):
    """
    Creates an ordered list of the remaining values left for a given variable.
    Values should be attempted in the order returned.
    The least constraining value should be at the front of the list.

    Args:
        assignment (Assignment): the partial assignment to expand
        csp (ConstraintSatisfactionProblem): the problem description
        var (string): the variable to be assigned the values
    Returns:
        list<values>
        a list of the possible values ordered by the least constraining value heuristic
    """
    # TODO: Question 3
    valList = []
    for val in assignment.varDomains[var]:
        count = 0
        constraints = [cons for cons in csp.binaryConstraints]
        for constraint in constraints:
            if constraint.affects(var):
                otherVar = constraint.otherVariable(var)
                for otherVal in assignment.varDomains[otherVar]:
                    if not constraint.isSatisfied(val, otherVal):
                        count = count + 1
        valList.append((val, count))
    valList.sort(key = takeSecond)

    return [takeFirst(elem) for elem in valList]
    raise_undefined_error()


def noInferences(assignment, csp, var, value):
    """
    Trivial method for making no inferences.
    """
    return set([])


# = = = = = = = QUESTION 4  = = = = = = = #


def forwardChecking(assignment, csp, var, value):
    """
    Implements the forward checking algorithm.
    Each inference should take the form of (variable, value)
    where the value is being removed from the domain of variable.
    This format is important so that the inferences can be reversed
    if they result in a conflicting partial assignment.
    If the algorithm reveals an inconsistency,
    any inferences made should be reversed before ending the function.

    Args:
        assignment (Assignment): the partial assignment to expand
        csp (ConstraintSatisfactionProblem): the problem description
        var (string): the variable that has just been assigned a value
        value (string): the value that has just been assigned
    Returns:
        set< tuple<variable, value> >
        the inferences made in this call or None if inconsistent assignment
    """
    inferences = set([])

    # TODO: Question 4
    constraints = [cons for cons in csp.binaryConstraints]
    for constraint in constraints:
        if constraint.affects(var):
            otherVar = constraint.otherVariable(var)
            # for otherVal in assignment.varDomains[otherVar]:
            if value in assignment.varDomains[otherVar]:
                # if not constraint.isSatisfied(value, otherVal):
                if len(assignment.varDomains[otherVar]) > 1:
                    inferences.add((otherVar, value))
                    assignment.varDomains[otherVar].remove(value)
                else:
                    for inference in inferences:
                        assignment.varDomains[inference[0]].add(inference[1])
                    return None
    return inferences
    raise_undefined_error()


# = = = = = = = QUESTION 5  = = = = = = = #


def revise(assignment, csp, var1, var2, constraint):
    """
    Helper function to maintainArcConsistency and AC3.
    Remove values from var2 domain if constraint cannot be satisfied.
    Each inference should take the form of (variable, value)
    where the value is being removed from the domain of variable.
    This format is important so that the inferences can be reversed
    if they result in a conflicting partial assignment.
    If the algorithm reveals an inconsistency,
    any inferences made should be reversed before ending the function.

    Args:
        assignment (Assignment): the partial assignment to expand
        csp (ConstraintSatisfactionProblem): the problem description
        var1 (string): the variable with consistent values
        var2 (string): the variable that should have inconsistent values removed
        constraint (BinaryConstraint): the constraint connecting var1 and var2
    Returns:
        set<tuple<variable, value>>
        the inferences made in this call or None if inconsistent assignment
    """
    inferences = set([])

    # TODO: Question 5
    for value2 in assignment.varDomains[var2]:
        flag = False
        for value1 in assignment.varDomains[var1]:
            if constraint.isSatisfied(value1, value2):
                flag = True
                break
        if not flag:
            inferences.add((var2, value2))
    if len(inferences) == len(assignment.varDomains[var2]):
        return None
    for inference in inferences:
        assignment.varDomains[inference[0]].remove(inference[1])
    return inferences

    raise_undefined_error()


def maintainArcConsistency(assignment, csp, var, value):
    """
    Implements the maintaining arc consistency algorithm.
    Inferences take the form of (variable, value)
    where the value is being removed from the domain of variable.
    This format is important so that the inferences can be reversed
    if they result in a conflicting partial assignment.
    If the algorithm reveals an inconsistency,
    and inferences made should be reversed before ending the function.

    Args:
        assignment (Assignment): the partial assignment to expand
        csp (ConstraintSatisfactionProblem): the problem description
        var (string): the variable that has just been assigned a value
        value (string): the value that has just been assigned
    Returns:
        set<<variable, value>>
        the inferences made in this call or None if inconsistent assignment
    """
    inferences = set([])
    domains = assignment.varDomains

    queue = deque()

    constraints = [cons for cons in csp.binaryConstraints]
    for constraint in constraints:
        if constraint.affects(var):
            Xj = constraint.otherVariable(var)
            if not assignment.isAssigned(Xj):
                queue.append((var, Xj, constraint))

    while len(queue) > 0:
        var1, var2, con = queue.pop()
        inferencesNew = revise(assignment, csp, var1, var2, con)
        if inferencesNew is None:
            for inference in inferences:
                assignment.varDomains[inference[0]].add(inference[1])
            return None
        elif len(inferencesNew) > 0:
            constraints = [cons for cons in csp.binaryConstraints]
            for constraint in constraints:
                if constraint.affects(var2):
                    Xk = constraint.otherVariable(var2)
                    if not assignment.isAssigned(Xk):
                        queue.append((var2, Xk, constraint))
            inferences = inferences.union(inferencesNew)
    return inferences


    # TODO: Question 5
    #  Hint: implement revise first and use it as a helper function"""
    raise_undefined_error()


# = = = = = = = QUESTION 6  = = = = = = = #


def AC3(assignment, csp):
    """
    AC3 algorithm for constraint propagation.
    Used as a pre-processing step to reduce the problem
    before running recursive backtracking.

    Args:
        assignment (Assignment): the partial assignment to expand
        csp (ConstraintSatisfactionProblem): the problem description
    Returns:
        Assignment
        the updated assignment after inferences are made or None if an inconsistent assignment
    """
    inferences = set([])
    domains = csp.varDomains

    queue = deque()

    for Xi in domains:
        constraints = [cons for cons in csp.binaryConstraints]
        for constraint in constraints:
            if constraint.affects(Xi):
                Xj = constraint.otherVariable(Xi)
                queue.append((Xi, Xj, constraint))

    while len(queue) > 0:
        Xi, Xj, constraint = queue.pop()
        inferencesNew = revise(assignment, csp, Xi, Xj, constraint)
        if inferencesNew is None:
            for inference in inferences:
                assignment.varDomains[inference[0]].add(inference[1])
            return None
        elif len(inferencesNew) > 0:
            constraints = [cons for cons in csp.binaryConstraints]
            for constraint in constraints:
                if constraint.affects(Xj):
                    Xk = constraint.otherVariable(Xj)
                    if not assignment.isAssigned(Xk):
                        queue.append((Xj, Xk, constraint))
            inferences = inferences.union(inferencesNew)
    return assignment




    # TODO: Question 6
    #  Hint: implement revise first and use it as a helper function"""
    raise_undefined_error()


def solve(csp, orderValuesMethod=leastConstrainingValuesHeuristic,
          selectVariableMethod=minimumRemainingValuesHeuristic,
          inferenceMethod=forwardChecking, useAC3=True):
    """
    Solves a binary constraint satisfaction problem.

    Args:
        csp (ConstraintSatisfactionProblem): a CSP to be solved
        orderValuesMethod (function): a function to decide the next value to try
        selectVariableMethod (function): a function to decide which variable to assign next
        inferenceMethod (function): a function to specify what type of inferences to use
        useAC3 (boolean): specifies whether to use the AC3 pre-processing step or not
    Returns:
        dictionary<string, value>
        A map from variables to their assigned values. None if no solution exists.
    """
    assignment = Assignment(csp)

    assignment = eliminateUnaryConstraints(assignment, csp)
    if assignment is None:
        return assignment

    if useAC3:
        assignment = AC3(assignment, csp)
        if assignment is None:
            return assignment

    assignment = recursiveBacktracking(assignment, csp, orderValuesMethod, selectVariableMethod, inferenceMethod)
    if assignment is None:
        return assignment

    return assignment.extractSolution()
