# valueIterationAgents.py
# -----------------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


# valueIterationAgents.py
# -----------------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


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
          newvals = self.values.copy()

          for state in self.mdp.getStates():
            if not self.mdp.isTerminal(state):
              actions = self.mdp.getPossibleActions(state)
              bestval = float("-inf")
              for a in actions:
                bestval = max(bestval, self.getQValue(state, a))
                newvals[state] = bestval

          self.values = newvals 

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
        qval = 0

        those = []
        those = self.mdp.getTransitionStatesAndProbs(state, action)

        for nextstate, prob in those:
          reward = self.mdp.getReward(state, action, nextstate)
          qval += prob * (reward + self.discount * self.values[nextstate])

        return qval

    def computeActionFromValues(self, state):
        """
          The policy is the best action in the given state
          according to the values currently stored in self.values.

          You may break ties any way you see fit.  Note that if
          there are no legal actions, which is the case at the
          terminal state, you should return None.
        """

        "*** YOUR CODE HERE ***"
        vals = util.Counter()
        action = None

        for sprime in self.mdp.getPossibleActions(state):
          vals[sprime] = self.computeQValueFromValues(state, sprime)

        return vals.argMax()
        

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
        "***YOUR CODE HERE***"

        vals = util.Counter()
        states = self.mdp.getStates()

        for i in range(self.iterations):
          curr = states[i%len(states)]
          vals = self.values.copy()
          possiblevals = []

          if self.mdp.isTerminal(curr):
            self.values[curr] = 0

          else:
            for action in self.mdp.getPossibleActions(curr):
              temp = 0
              for transition in self.mdp.getTransitionStatesAndProbs(curr, action):
                temp += transition[1] * (self.mdp.getReward(curr, action, transition[0]) + self.discount * vals[transition[0]])
              possiblevals.append(temp)
            self.values[curr] = max(possiblevals)


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
        self.values = collections.defaultdict(float)
        predecessors = {}
        pqueue = util.PriorityQueue()

        states = self.mdp.getStates()
        for state in states:
            self.values[state] = 0

        for s in states:
          predecessors[s] = self.getstatepredecessors(s)

        for s in states:
          if not self.mdp.isTerminal(s):
            highestQ = self.gethighestQValue(s) 
            diff = abs(self.values[s] - highestQ) 
            pqueue.update(s, -diff) 

        for i in range(self.iterations):
          if pqueue.isEmpty():
            return
          state = pqueue.pop()  
          self.values[state] = self.gethighestQValue(state) 
          for p in list(predecessors[state]):
            highestQ = self.gethighestQValue(p) 
            diff = abs(self.values[p] - highestQ)
            if diff > theta:
              pqueue.update(p, -diff) 

    def getstatepredecessors(self, state):

        predecessors = set()

        if not self.mdp.isTerminal(state):
          states = self.mdp.getStates()
          
          for s in states:
            if not self.mdp.isTerminal(s):
              possibleacts = self.mdp.getPossibleActions(s)
              if 'north' in possibleacts:
                transition = self.mdp.getTransitionStatesAndProbs(s, 'north')
                for nextState in transition:
                  if (nextState[0] == state) and (nextState[1] > 0):
                    predecessors.add(s)
              if 'west' in possibleacts:
                transition = self.mdp.getTransitionStatesAndProbs(s, 'west')
                for nextState in transition:
                  if (nextState[0] == state) and (nextState[1] > 0):
                    predecessors.add(s)
              if 'east' in possibleacts:
                transition = self.mdp.getTransitionStatesAndProbs(s, 'east')
                for nextState in transition:
                  if (nextState[0] == state) and (nextState[1] > 0):
                    predecessors.add(s)
              if 'south' in possibleacts:
                transition = self.mdp.getTransitionStatesAndProbs(s, 'south')
                for nextState in transition:
                  if (nextState[0] == state) and (nextState[1] > 0):
                    predecessors.add(s)
         
        return predecessors

    def gethighestQValue(self, state):

        q = float('-inf')
        actions = self.mdp.getPossibleActions(state)

        if len(actions) == 0:
            return None
        for action in actions:
          currQ = 0.0
          transitions = self.mdp.getTransitionStatesAndProbs(state, action)
          for nextState in transitions:
            currQ += nextState[1] * (self.mdp.getReward(state, action, nextState) + self.discount * self.getValue(nextState[0]))
          if currQ > q:
              q = self.computeQValueFromValues(state, action)

        return q



  
    """def runValueIteration(self):
        "*** YOUR CODE HERE ***"

        vals = util.Counter()
        before = []
        states = self.mdp.getStates()

        #compute predecessors of all states
        for state in states:
          preceed = set()
          for s in states:
            for a in self.mdp.getPossibleActions(s):
              for t in self.mdp.getTransitionStatesAndProbs(s, a):
                if t[0] == state:
                  preceed.add(s)
          before.append(preceed)

        #initialize a priority queue
        pqueue = util.PriorityQueue()


        for state in states:
          #for each non-terminal state s.....
          if not self.mdp.isTerminal(state):
      
            maxval = float("-inf")

            #highest q val across all possible actions from s
            for action in self.mdp.getPossibleActions(state):
              maxval = max(maxval, self.getQValue(state, action))

            diff = abs(self.getValue(state) - maxval)

            #push state on pqueue with priority -diff
            pqueue.push(state, -diff)

        




        for i in range(self.iterations):

          if not pqueue.isEmpty():
            
            #pop a state off
            state = pqueue.pop()

            if not self.mdp.isTerminal(state):
              #update s's value if not terminal
              self.values[state] = self.values[state] - self.getValue(state)

            for p in before[i]:
              maxval = float("-inf")
              for a in self.mdp.getPossibleActions(state):
                maxval = max(maxval, self.getQValue(state, a))
              diff = abs(self.getValue(state) - maxval)

              if self.theta < diff:
                pqueue.push(p, -diff)

          else:
            print("here it is")
            return"""
