# multiAgents.py
# --------------
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


from util import manhattanDistance
from game import Directions
import random, util

from game import Agent

class ReflexAgent(Agent):
    """
    A reflex agent chooses an action at each choice point by examining
    its alternatives via a state evaluation function.

    The code below is provided as a guide.  You are welcome to change
    it in any way you see fit, so long as you don't touch our method
    headers.
    """


    def getAction(self, gameState):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {NORTH, SOUTH, WEST, EAST, STOP}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices) # Pick randomly among the best

        "Add more of your code here if you want to"

        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (newFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        newPos = successorGameState.getPacmanPosition()
        newFood = successorGameState.getFood()
        newGhostStates = successorGameState.getGhostStates()
        newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]

        "*** YOUR CODE HERE ***"

        foodlist = []
        foodlist = newFood.asList()

        #Our motivation: our score will be comprised of the following factors:
        #distance to closest pellet, distance to closest ghost, 
            #remaining food left, and getScore value

        #first lets calculate distance to closest food

        closestfood = -1
        if len(foodlist) == 0:
            closestfood = 0
        else:
            for food in foodlist:
                if closestfood < 0:
                    closestfood = manhattanDistance(food, newPos)
                else:
                    closestfood = min(manhattanDistance(food, newPos), closestfood)

        #now we put a value to that
        #note that we use fractions so that smaller distances have higher priority
        #note that we add one to not divide by zero

        closestfoodvalue = 1.8/(closestfood+1)
        

        #next lets calculate distance to closest ghost (scared or not)

        scared = False
        closestghost = -1
        for ghost in newGhostStates:
            if closestghost < 0:
                closestghost = manhattanDistance(ghost.getPosition(), newPos)
            else:
                if ghost.scaredTimer == 0:
                    scared = False
                else:
                    scared = True
                closestghost = min(manhattanDistance(ghost.getPosition(), newPos), closestghost)

        #value

        if scared == True:
            #we want to go closer, increase value
            closestghostvalue = .8/(closestghost + 1)
        else:
            #we want to run away, decrease value
            closestghostvalue = -2/(closestghost + 1)
        
        #next we want to support states that have fewer pelets left, so the
            #longer the food list, the less preferred it will be

        foodvalue = -len(foodlist)

        return closestfoodvalue + closestghostvalue + foodvalue


def scoreEvaluationFunction(currentGameState):
    """
    This default evaluation function just returns the score of the state.
    The score is the same one displayed in the Pacman GUI.

    This evaluation function is meant for use with adversarial search agents
    (not reflex agents).
    """
    return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):
    """
    This class provides some common elements to all of your
    multi-agent searchers.  Any methods defined here will be available
    to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

    You *do not* need to make any changes here, but you can if you want to
    add functionality to all your adversarial search agents.  Please do not
    remove anything, however.

    Note: this is an abstract class: one that should not be instantiated.  It's
    only partially specified, and designed to be extended.  Agent (game.py)
    is another abstract class.
    """

    def __init__(self, evalFn = 'scoreEvaluationFunction', depth = '2'):
        self.index = 0 # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)

class MinimaxAgent(MultiAgentSearchAgent):
    """
    Your minimax agent (question 2)
    """

    def getAction(self, gameState):
        """
        Returns the minimax action from the current gameState using self.depth
        and self.evaluationFunction.

        Here are some method calls that might be useful when implementing minimax.

        gameState.getLegalActions(agentIndex):
        Returns a list of legal actions for an agent
        agentIndex=0 means Pacman, ghosts are >= 1

        gameState.generateSuccessor(agentIndex, action):
        Returns the successor game state after an agent takes an action

        gameState.getNumAgents():
        Returns the total number of agents in the game

        gameState.isWin():
        Returns whether or not the game state is a winning state

        gameState.isLose():
        Returns whether or not the game state is a losing state
        """
        "*** YOUR CODE HERE ****"

        def minimax(agent, depth, state):

            #check if terminal state
            if depth == self.depth and agent % state.getNumAgents() == 0:
                return self.evaluationFunction(state), None

            #check if next agent is MIN (ghost)
            if agent % state.getNumAgents() != 0:
                return minfunction(agent % state.getNumAgents(), depth, state)

            #if neither then next agent is MAX (pacman)
            else:
                return maxfunction(agent % state.getNumAgents(), depth, state)


        def maxfunction(agent, depth, state):

            allactions = state.getLegalActions(agent)

            if len(allactions) == 0:
                return self.evaluationFunction(state), None

            #initialize v
            v = -float("inf")
            action = None

            #for each successor
            for legal_action in allactions:
                newvalue, newaction = minimax(agent+1, depth+1, state.generateSuccessor(agent, legal_action))
                #v is max
                if newvalue > v:
                    v = newvalue
                    action = legal_action
            #return v
            return v, action

        def minfunction(agent, depth, state):

            allactions = state.getLegalActions(agent)
            
            if len(allactions) == 0:
                return self.evaluationFunction(state), None

            #initialize v
            v = float("inf")
            action = None

            #for each successor
            for legal_action in allactions:

                newvalue, newaction = minimax(agent+1, depth, state.generateSuccessor(agent, legal_action))
                #v is max

                if newvalue < v:
                    v = newvalue
                    action = legal_action
            #return v
            return v, action
     
        return minimax(0,0,gameState)[1]

class AlphaBetaAgent(MultiAgentSearchAgent):
    """
    Your minimax agent with alpha-beta pruning (question 3)
    """

    def getAction(self, gameState):
        """
        Returns the minimax action using self.depth and self.evaluationFunction
        """
        "*** YOUR CODE HERE ***"
        def a_b_minimax(alpha, beta, agent, depth, state):

            #check if terminal state
            if depth == self.depth and agent % state.getNumAgents() == 0:
                return self.evaluationFunction(state), None

            #check if next agent is MIN (ghost)
            if agent % state.getNumAgents() != 0:
                return a_b_minvalue(alpha, beta, agent % state.getNumAgents(), depth, state)

            #if neither then next agent is MAX (pacman)
            else:
                return a_b_maxvalue(alpha, beta, agent % state.getNumAgents(), depth, state)

        def a_b_maxvalue(alpha, beta, agent, depth, state):

            allactions = state.getLegalActions(agent)

            if len(allactions) == 0:
                return self.evaluationFunction(state), None

            #initialize v
            v = -float("inf")
            action = None

            #for each successor
            for legal_action in allactions:
                newvalue, newaction = a_b_minimax(alpha, beta, agent+1, depth+1, state.generateSuccessor(agent, legal_action))
                #v is max
                if newvalue > v:
                    v = newvalue
                    action = legal_action
                #check if v is greater to beta
                if v > beta:
                    return v, action
                alpha = max(alpha, v)
            #return v
            return v, action

        def a_b_minvalue(alpha, beta, agent, depth, state):

            allactions = state.getLegalActions(agent)
            
            if len(allactions) == 0:
                return self.evaluationFunction(state), None

            #initialize v
            v = float("inf")
            action = None

            #for each successor
            for legal_action in allactions:
                newvalue, newaction = a_b_minimax(alpha, beta, agent+1, depth, state.generateSuccessor(agent, legal_action))
                #v is max
                if newvalue < v:
                    v = newvalue
                    action = legal_action
                #check if v is less than alpha
                if v < alpha:
                    return v, action
                beta = min(beta, v)
            #return v
            return v, action


        return a_b_minimax(-float("inf"), float("inf"), 0, 0, gameState)[1]


class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """

    def getAction(self, gameState):
        """
        Returns the expectimax action using self.depth and self.evaluationFunction

        All ghosts should be modeled as choosing uniformly at random from their
        legal moves.
        """
        "*** YOUR CODE HERE ***"
        def expectimax(agent, depth, state):

            #check if terminal state
            if depth == self.depth and agent % state.getNumAgents() == 0:
                return self.evaluationFunction(state), None

            #check if next agent is MIN (ghost)
            if agent % state.getNumAgents() != 0:
                return expectedfunction(agent % state.getNumAgents(), depth, state)

            #if neither then next agent is MAX (pacman)
            else:
                return maxfunction(agent % state.getNumAgents(), depth, state)

        def expectedfunction(agent, depth, state):

            allactions = state.getLegalActions(agent)

            numactions = len(allactions)

            if numactions == 0:
                return self.evaluationFunction(state), None

            #initialize v
            v = 0
            action = None

            for legal_action in allactions:
                v += expectimax(agent+1, depth, state.generateSuccessor(agent, legal_action))[0]

            return (v/numactions), action


        def maxfunction(agent, depth, state):

            allactions = state.getLegalActions(agent)

            if len(allactions) == 0:
                return self.evaluationFunction(state), None

            #initialize v
            v = -float("inf")
            action = None

            #for each successor
            for legal_action in allactions:
                newvalue, newaction = expectimax(agent+1, depth+1, state.generateSuccessor(agent, legal_action))
                #v is max
                if newvalue > v:
                    v = newvalue
                    action = legal_action
            #return v
            return v, action

        return expectimax(0, 0, gameState)[1]

def betterEvaluationFunction(currentGameState):
    """
    Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
    evaluation function (question 5).

    DESCRIPTION: I started with my original evaluation function and instead updated the
    gamestate from successor to current. I added in the value of the current
    game score as well!!

    """
    
    #Defining facets
    newPos = currentGameState.getPacmanPosition()
    newFood = currentGameState.getFood()
    newGhostStates = currentGameState.getGhostStates()
    newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]

    #old function

    foodlist = []
    foodlist = newFood.asList()

     #Our motivation: our score will be comprised of the following factors:
    #distance to closest pellet, distance to closest ghost, 
        #remaining food left, and getScore value

    #first lets calculate distance to closest food

    closestfood = -1
    if len(foodlist) == 0:
        closestfood = 0
    else:
        for food in foodlist:
            if closestfood < 0:
                closestfood = manhattanDistance(food, newPos)
            else:
                closestfood = min(manhattanDistance(food, newPos), closestfood)

    #now we put a value to that
    #note that we use fractions so that smaller distances have higher priority
    #note that we add one to not divide by zero

    closestfoodvalue = 1.8/(closestfood+1)
        

    #next lets calculate distance to closest ghost (scared or not)

    scared = False
    closestghost = -1
    for ghost in newGhostStates:
        if closestghost < 0:
            closestghost = manhattanDistance(ghost.getPosition(), newPos)
        else:
            if ghost.scaredTimer == 0:
                scared = False
            else:
                scared = True
            closestghost = min(manhattanDistance(ghost.getPosition(), newPos), closestghost)

    #value

    if scared == True:
        #we want to go closer, increase value
        closestghostvalue = .8/(closestghost + 1)
    else:
        #we want to run away, decrease value
        closestghostvalue = -2/(closestghost + 1)
        
    #next we want to support states that have fewer pelets left, so the
        #longer the food list, the less preferred it will be

    foodvalue = -len(foodlist)

    score = .7 * currentGameState.getScore()

    return closestfoodvalue + closestghostvalue + foodvalue + score

# Abbreviation
better = betterEvaluationFunction
