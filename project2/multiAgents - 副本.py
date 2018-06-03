# multiAgents.py
# --------------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

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
    some Directions.X for some X in the set {North, South, West, East, Stop}
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
    # stop moving, bad!
    if action == 'Stop':
        return -10000
    successorGameState = currentGameState.generatePacmanSuccessor(action)
    newPos = successorGameState.getPacmanPosition()
    newFood = successorGameState.getFood()
    newGhostStates = successorGameState.getGhostStates()
    #newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]
    "*** YOUR CODE HERE ***"
    foods = newFood.asList()
    # if foods are empty
    if not foods:
        return 10000
    # let see if there's capsules
    if successorGameState.getCapsules():
        distance = min(manhattanDistance(newPos, cap)
                for cap in successorGameState.getCapsules())
    else:
        # if no capsules, look for the closest food
        distance = min(manhattanDistance(newPos, food) for food in foods)
    # if right on the food/capsule, it's a good thing
    if not distance:
        score = 100
    else:
        score = 1.0/distance

    # few foods, better
    score -= len(foods)**2
    
    # see how far the ghosts are
    for ghostState in newGhostStates:
        distance = manhattanDistance(newPos, ghostState.getPosition())
        # if get caught, bad!
        if not distance:
            return -10000
        # eat up the ghosts as fast as possible after eating capsules
        if ghostState.scaredTimer:
            if ghostState.scaredTimer == 40:
                return 10000
            score -= 100*distance
        # only count if ghosts are close
        elif distance < 5:
            score += 2*distance
    return score

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
  def maxValue(self, gameState, level):
    if level == self.depth or gameState.isWin() or gameState.isLose():
        return self.evaluationFunction(gameState)

    actions = gameState.getLegalActions(0)
    actions.remove('Stop')
    action_val = []
    for ghost_id in range(1,gameState.getNumAgents()):
        action_val.extend(self.minValue(gameState.generateSuccessor(0, action),
                                 ghost_id, level) for action in actions)
    print action_val
    return max(action_val)

  def minValue(self, gameState, ghost_id, level):
    if level == self.depth or gameState.isWin() or gameState.isLose():
        return self.evaluationFunction(gameState)

    actions = gameState.getLegalActions(ghost_id)
    return min(self.maxValue(
        gameState.generateSuccessor(ghost_id, action), level+1) for action in actions)

  def getAction(self, gameState):
    """
      Returns the minimax action from the current gameState using self.depth
      and self.evaluationFunction.

      Here are some method calls that might be useful when implementing minimax.

      gameState.getLegalActions(agentIndex):
        Returns a list of legal actions for an agent
        agentIndex=0 means Pacman, ghosts are >= 1

      Directions.STOP:
        The stop direction, which is always legal

      gameState.generateSuccessor(agentIndex, action):
        Returns the successor game state after an agent takes an action

      gameState.getNumAgents():
        Returns the total number of agents in the game
    """
    "*** YOUR CODE HERE ***"
    actions_val = []
    actions = gameState.getLegalActions(0)
    if 'Stop' in actions:
        actions.remove('Stop')
    for ghost_id in range(1,gameState.getNumAgents()):
        actions_val.extend((action,self.minValue(
            gameState.generateSuccessor(0, action), ghost_id, 0))
             for action in actions)
    print actions_val
    print max(actions_val, key=lambda x: x[1])[1]
    return max(actions_val, key=lambda x: x[1])[0]

class AlphaBetaAgent(MultiAgentSearchAgent):
  """
    Your minimax agent with alpha-beta pruning (question 3)
  """
  def maxValue(self, gameState, level, a, b):
    if level == self.depth:
        return self.evaluationFunction(gameState)

    actions = gameState.getLegalActions(0)
    if not actions:
        return self.evaluationFunction(gameState)
    if 'Stop' in actions:
        actions.remove('Stop')

    v = float('-inf')
    for ghost_id in range(1,gameState.getNumAgents()):
        for action in actions:
            v = max(v, self.minValue(
                    gameState.generateSuccessor(0, action), ghost_id, level, a, b))
            if v >= b:
                return v
            a = max(a, v)
    return v

  def minValue(self, gameState, ghost_id, level, a, b):
    if level == self.depth:
        return self.evaluationFunction(gameState)

    actions = gameState.getLegalActions(ghost_id)
    if not actions:
        return self.evaluationFunction(gameState)
    if 'Stop' in actions:
        actions.remove('Stop')

    v = float('inf')
    for action in actions:
        v = min(v, self.maxValue(
                gameState.generateSuccessor(ghost_id, action), level+1, a, b))
        if v <= a:
            return v
        b = min(b, v)
    return v

  def getAction(self, gameState):
    """
      Returns the minimax action using self.depth and self.evaluationFunction
    """
    "*** YOUR CODE HERE ***"
    actions = gameState.getLegalActions(0)
    if not actions:
        return self.evaluationFunction(gameState)
    if 'Stop' in actions:
        actions.remove('Stop')

    v = float('-inf')
    act = None
    a = float('-inf'); b = float('inf')
    for ghost_id in range(1,gameState.getNumAgents()):
        for action in actions:
            val = self.minValue(
                gameState.generateSuccessor(0, action), ghost_id, 0, a, b)
            if val > v:
                v = val
                act = action
            a = max(a, v)
    print v
    return act

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
    util.raiseNotDefined()

def betterEvaluationFunction(currentGameState):
  """
    Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
    evaluation function (question 5).

    DESCRIPTION: <write something here so we know what you did>
  """
  "*** YOUR CODE HERE ***"
  util.raiseNotDefined()

# Abbreviation
better = betterEvaluationFunction

class ContestAgent(MultiAgentSearchAgent):
  """
    Your agent for the mini-contest
  """

  def getAction(self, gameState):
    """
      Returns an action.  You can use any method you want and search to any depth you want.
      Just remember that the mini-contest is timed, so you have to trade off speed and computation.

      Ghosts don't behave randomly anymore, but they aren't perfect either -- they'll usually
      just make a beeline straight towards Pacman (or away from him if they're scared!)
    """
    "*** YOUR CODE HERE ***"
    util.raiseNotDefined()

