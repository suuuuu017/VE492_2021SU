import mdp, util

from learningAgents import ValueEstimationAgent
import collections

class ValueIterationAgent(ValueEstimationAgent):
    """
        * Please read learningAgents.py before reading this.*

        A ValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs value iteration
        for a given number of iterations using the supplied
        discount factor.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 100):
        """
          Your value iteration agent should take an mdp on
          construction, run the indicated number of iterations
          and then act according to the resulting policy.

          Some useful mdp methods you will use:
              mdp.getStates()
              mdp.getPossibleActions(state)
              mdp.getTransitionStatesAndProbs(state, action)
              mdp.getReward(state, action, nextState)
              mdp.isTerminal(state)
        """
        self.mdp = mdp
        self.discount = discount
        self.iterations = iterations
        self.values = util.Counter() # A Counter is a dict with default 0
        self.runValueIteration()

    def runValueIteration(self):
        # Write value iteration code here
        "*** YOUR CODE HERE ***"
        for i in range(self.iterations):
            newValue = self.values.copy()
            for state in self.mdp.getStates():
                bestAction = self.computeActionFromValues(state)
                if not self.mdp.isTerminal(state):
                    newValue[state] = self.computeQValueFromValues(state, bestAction)
            self.values = newValue


    def getValue(self, state):
        """
          Return the value of the state (computed in __init__).
        """
        return self.values[state]


    def computeQValueFromValues(self, state, action):
        """
          Compute the Q-value of action in state from the
          value function stored in self.values.
        """
        "*** YOUR CODE HERE ***"
        probList = self.mdp.getTransitionStatesAndProbs(state, action)
        QVal = 0
        for nextState, prob in probList:
            QVal = prob * (self.mdp.getReward(state, action, nextState) + self.discount * self.values[nextState]) + QVal
        return QVal

    def computeActionFromValues(self, state):
        """
          The policy is the best action in the given state
          according to the values currently stored in self.values.

          You may break ties any way you see fit.  Note that if
          there are no legal actions, which is the case at the
          terminal state, you should return None.
        """
        "*** YOUR CODE HERE ***"
        actionList = self.mdp.getPossibleActions(state)
        if self.mdp.isTerminal(state):
            return None
        valueList = util.Counter()
        for action in actionList:
            val = 0
            probList = self.mdp.getTransitionStatesAndProbs(state, action)
            for nextState, prob in probList:
                # print(val)
                val = prob * (self.mdp.getReward(state, action, nextState) + self.discount * self.values[nextState]) + val
            valueList[action] = val
        valueList.sortedKeys()
        bestAction = valueList.argMax()
        return bestAction

    def getPolicy(self, state):
        return self.computeActionFromValues(state)

    def getAction(self, state):
        "Returns the policy at the state (no exploration)."
        return self.computeActionFromValues(state)

    def getQValue(self, state, action):
        return self.computeQValueFromValues(state, action)

class AsynchronousValueIterationAgent(ValueIterationAgent):
    """
        * Please read learningAgents.py before reading this.*

        An AsynchronousValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs cyclic value iteration
        for a given number of iterations using the supplied
        discount factor.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 1000):
        """
          Your cyclic value iteration agent should take an mdp on
          construction, run the indicated number of iterations,
          and then act according to the resulting policy. Each iteration
          updates the value of only one state, which cycles through
          the states list. If the chosen state is terminal, nothing
          happens in that iteration.

          Some useful mdp methods you will use:
              mdp.getStates()
              mdp.getPossibleActions(state)
              mdp.getTransitionStatesAndProbs(state, action)
              mdp.getReward(state)
              mdp.isTerminal(state)
        """
        ValueIterationAgent.__init__(self, mdp, discount, iterations)

    def runValueIteration(self):
        "*** YOUR CODE HERE ***"
        for i in range(self.iterations):
            newValue = self.values.copy()
            stateNum = len(self.mdp.getStates())
            state = self.mdp.getStates()[i % stateNum]
            bestAction = self.computeActionFromValues(state)
            if not self.mdp.isTerminal(state):
                newValue[state] = self.computeQValueFromValues(state, bestAction)
            self.values = newValue

class PrioritizedSweepingValueIterationAgent(AsynchronousValueIterationAgent):
    """
        * Please read learningAgents.py before reading this.*

        A PrioritizedSweepingValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs prioritized sweeping value iteration
        for a given number of iterations using the supplied parameters.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 100, theta = 1e-5):
        """
          Your prioritized sweeping value iteration agent should take an mdp on
          construction, run the indicated number of iterations,
          and then act according to the resulting policy.
        """
        self.theta = theta
        ValueIterationAgent.__init__(self, mdp, discount, iterations)

    def runValueIteration(self):
        "*** YOUR CODE HERE ***"
        predlist = util.Counter()
        for state in self.mdp.getStates():
            if self.mdp.isTerminal(state):
                continue
            actionList = self.mdp.getPossibleActions(state)
            for action in actionList:
                probList = self.mdp.getTransitionStatesAndProbs(state, action)
                for nextState, prob in probList:
                    if prob:
                        if nextState in predlist.keys():
                            predlist[nextState].add(state)
                        else:
                            predlist[nextState] = set()
                            predlist[nextState].add(state)

        priority = util.PriorityQueue()
        for state in self.mdp.getStates():
            if self.mdp.isTerminal(state):
                continue
            stateVal = self.getValue(state)
            actionList = self.mdp.getPossibleActions(state)
            QvalList = []
            for action in actionList:
                Qval = self.computeQValueFromValues(state, action)
                QvalList.append(Qval)
            highestQval = max(QvalList)
            diff = abs(stateVal - highestQval)
            priority.push(state, -diff)

        for i in range(self.iterations):
            if priority.isEmpty():
                break
            s = priority.pop()
            if not self.mdp.isTerminal(s):
                bestAction = self.computeActionFromValues(s)
                if bestAction:
                    self.values[s] = self.computeQValueFromValues(s, bestAction)
            for pred in predlist[s]:
                stateVal = self.getValue(pred)
                actionList = self.mdp.getPossibleActions(pred)
                QvalList = []
                for action in actionList:
                    Qval = self.computeQValueFromValues(pred, action)
                    QvalList.append(Qval)
                highestQval = max(QvalList)
                diff = abs(stateVal - highestQval)
                if diff > self.theta:
                    priority.update(pred, -diff)