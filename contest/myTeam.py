# myTeam.py
# ---------------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

from captureAgents import CaptureAgent
import distanceCalculator
import random, time, util
from game import Directions
import game
from util import nearestPoint

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'ExpectimaxAgent', second = 'BustersAgent'):
  """
  This function should return a list of two agents that will form the
  team, initialized using firstIndex and secondIndex as their agent
  index numbers.  isRed is True if the red team is being created, and
  will be False if the blue team is being created.

  As a potentially helpful development aid, this function can take
  additional string-valued keyword arguments ("first" and "second" are
  such arguments in the case of this function), which will come from
  the --redOpts and --blueOpts command-line arguments to capture.py.
  For the nightly contest, however, your team will be created without
  any extra arguments, so you should make sure that the default
  behavior is what you want for the nightly contest.
  """
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########
class ExpectimaxAgent(CaptureAgent):

  def registerInitialState(self, gameState):
    """
    This method handles the initial setup of the
    agent to populate useful fields (such as what team
    we're on).

    A distanceCalculator instance caches the maze distances
    between each pair of positions, so your agents can use:
    self.distancer.getDistance(p1, p2)
    """
    self.red = gameState.isOnRedTeam(self.index)
    self.distancer = distanceCalculator.Distancer(gameState.data.layout)

    # comment this out to forgo maze distance computation and use manhattan distances
    self.distancer.getMazeDistances()

    import __main__
    if '_display' in dir(__main__):
      self.display = __main__._display

    # record the pushback status and reinvasion location
    self.offense = False
    self.targetPos = None

    # save some reused variables
    self.w = gameState.getWalls().width
    self.h = gameState.getWalls().height

  def chooseAction(self, gameState):
    """
      Returns the minimax action from the current gameState using self.depth
      and self.evaluationFunction.
    """
    "*** YOUR CODE HERE ***"
    start = time.time()
    actions = gameState.getLegalActions(self.index)
    actions.remove('Stop')

    # if pushed back, pick another way to invade
    if gameState.getAgentPosition(self.index) == gameState.getInitialAgentPosition(self.index):
      self.offense = False
    if gameState.getAgentState(self.index).isPacman:
      self.offense = True
    elif self.offense:
      print('Oops! Gotta find another way around.')
      self.offense = False
      myPos = gameState.getAgentPosition(self.index)
      self.targetPos = (myPos[0], random.choice(range(self.h)))
      while gameState.hasWall(self.targetPos[0], self.targetPos[1]):
        self.targetPos = (myPos[0], random.choice(range(self.h)))
      print('New location to invade!', self.targetPos)

    if self.targetPos:
      myPos = gameState.getAgentPosition(self.index)
      if myPos != self.targetPos:
        # don't cross the boarder
        print('Moving to target location..')
        for action in actions:
          if gameState.generateSuccessor(self.index, action).getAgentState(self.index).isPacman:
            actions.remove(action)
        actions_dist = {action: self.getMazeDistance(myPos, self.targetPos) for action in actions}
        return min(actions_dist, key=actions_dist.get)
      else:
        print('Arrived new location!')
        self.targetPos = None

    enemies = {i: gameState.getAgentState(i) for i in self.getOpponents(gameState)}
    self.ghosts = [i for i, enemy in enemies.items() if not enemy.isPacman]
    self.depth = 2
    
    actions_val = {action: self.minValue(gameState.generateSuccessor(self.index, action), 0, 0)
                    for action in actions}
    max_val = max(actions_val.values())
    best_actions = [action for action, val in actions_val.items() if val == max_val]
    print 'eval time for offense agent: %.4f' % (time.time() - start)

    return random.choice(best_actions)

  def maxValue(self, gameState, level):
    if level == self.depth or gameState.isOver():
        return self.evaluationFunction(gameState)

    actions = gameState.getLegalActions(self.index)
    actions.remove('Stop')

    return max(self.minValue(gameState.generateSuccessor(self.index, action), 0, level) for action in actions)

  def minValue(self, gameState, ghost_id, level):
    if level == self.depth or gameState.isOver():
        return self.evaluationFunction(gameState)

    # invisible
    ghostPos = gameState.getAgentPosition(self.ghosts[ghost_id])
    if not ghostPos or self.getMazeDistance(ghostPos, gameState.getAgentState(self.index).getPosition()) > 3:
      if ghost_id < len(self.ghosts)-1:
        return self.minValue(gameState, ghost_id+1, level)
      else:
        return self.maxValue(gameState, level+1)
    # visible!
    else:
      actions = gameState.getLegalActions(self.ghosts[ghost_id])
      if ghost_id < len(self.ghosts)-1:
        return sum(self.minValue(
            gameState.generateSuccessor(self.ghosts[ghost_id], action), ghost_id+1, level) for action in actions)/len(actions)
      else:
        return sum(self.maxValue(
            gameState.generateSuccessor(self.ghosts[ghost_id], action), level+1) for action in actions)/len(actions)

  def evaluationFunction(self, gameState):
    features = self.getFeatures(gameState)
    weights = self.getWeights(gameState)
    return features * weights

  def getFeatures(self, gameState):
    features = util.Counter()
    successor = gameState
    if successor.isOver():
      features['successorScore'] = 1000
      return features
    features['successorScore'] = self.getScore(successor)
    myPos = successor.getAgentState(self.index).getPosition()
    atHome = bool(not successor.getAgentState(self.index).isPacman)

    # Compute distance to the nearest food or capsule
    foodList = self.getFood(successor).asList()
    if foodList:
      features['distanceToFood'] = min([self.getMazeDistance(myPos, food) for food in foodList])

    # be careful about the ghosts!
    for i in self.ghosts:
      # check if it's close
      dist = successor.getAgentPosition(i)
      if dist and dist < 3 and not atHome and not successor.getAgentState(i).scaredTimer:
        features['DangerCloseGhost'+str(i)] = 1000
        # get caught!
        if not dist:
          features['DangerCloseGhost'+str(i)] = -1000

    return features

  def getWeights(self, gameState):
    w = {'successorScore': 1000, 'distanceToFood': -10}
    for i in self.ghosts:
      w['DangerCloseGhost'+str(i)] = 10
    return w

class BustersAgent(CaptureAgent):
    
  def registerInitialState(self, gameState):
    "Initial setups"
    self.red = gameState.isOnRedTeam(self.index)
    self.distancer = distanceCalculator.Distancer(gameState.data.layout)
    self.distancer.getMazeDistances()

    import __main__
    if '_display' in dir(__main__):
      self.display = __main__._display

    self.inferenceModules = None
    self.firstMove = True

    # save some reused variables
    self.w = gameState.getWalls().width
    self.h = gameState.getWalls().height

  def getAction(self, gameState):
    "Updates beliefs, then chooses an action based on updated beliefs."
    self.start = time.time()
    self.observationHistory.append(gameState)
    myState = gameState.getAgentState(self.index)
    myPos = myState.getPosition()
    if myPos != nearestPoint(myPos):
      # We're halfway from one position to the next
      return gameState.getLegalActions(self.index)[0]

    enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
    self.invaders = [a for a in enemies if a.isPacman]
    # when no invaders, move around the boarder
    if not self.invaders:
      self.inferenceModules = None
      return self.moveAtBoarder(gameState)
    # have invaders, use particle filter to track
    else:
      # initialize if no inference
      if not self.inferenceModules:
        print('Initialize tracker')
        self.inferenceModules = JointParticleFilter(gameState, self.index, self.invaders)
      if not self.firstMove: self.inferenceModules.elapseTime(gameState)
      self.firstMove = False
      self.inferenceModules.observeState(gameState)
      self.ghostBeliefs = self.inferenceModules.getBeliefDistribution()
      #self.displayDistributionsOverPositions(self.ghostBeliefs)
    return self.chooseAction(gameState)

  def chooseAction(self, gameState):
    pacmanPosition = gameState.getAgentState(self.index).getPosition()
    legal = gameState.getLegalActions(self.index)
    legal.remove(Directions.STOP)

    # don't cross the boarder
    for action in legal:
      if gameState.generateSuccessor(self.index, action).getAgentState(self.index).isPacman:
        legal.remove(action)

    ghostsPos = []
    for i in range(len(self.invaders)):
      # can see the invader, update the belief
      if self.invaders[i].getPosition():
        ghostsPos.append(self.invaders[i].getPosition())
        self.inferenceModules.updatePosition(self.invaders[i].getPosition(), i)
      # cannot see..
      else:
        ghostsPos.append(max(self.ghostBeliefs[i], key=self.ghostBeliefs[i].get))

    # get the closest ghost position
    ghostsDist = {ghostPosition: self.getMazeDistance(pacmanPosition, ghostPosition)
                  for ghostPosition in ghostsPos}
    closestGhostPos = min(ghostsDist, key=ghostsDist.get)

    # return the action that minimizes the distance or maximize if scared
    closestGhostDist = {action: self.getMazeDistance(game.Actions.getSuccessor(pacmanPosition, action), closestGhostPos) for action in legal}
    if gameState.getAgentState(self.index).scaredTimer:
      maxValue = max(closestGhostDist.values())
      bestActions = [a for a, v in closestGhostDist.items() if v == maxValue]
    else:
      minValue = min(closestGhostDist.values())
      bestActions = [a for a, v in closestGhostDist.items() if v == minValue]
    print 'eval time for defense agent(buster mode): %.4f' % (time.time() - self.start)

    return random.choice(bestActions)

  def moveAtBoarder(self, gameState):
    actions = gameState.getLegalActions(self.index)
    actions.remove(Directions.STOP)

    if self.red:
      loc = [(x,y) for x, y in zip([self.w/2-2]*3, range(self.h/2-1,self.h/2+2))]
    else:
      loc = [(x,y) for x, y in zip([self.w/2+2]*3, range(self.h/2-1,self.h/2+2))]

    x, y = random.choice(loc)
    while gameState.hasWall(x, y):
      x, y = random.choice(loc)
    pos = tuple([x, y])
    myPos = gameState.getAgentState(self.index).getPosition()
    values = [self.getMazeDistance(pos, game.Actions.getSuccessor(myPos,a)) for a in actions]
    minValue = min(values)
    bestActions = [a for a, v in zip(actions, values) if v == minValue]
    print 'eval time for defense agent(move at boarder): %.4f' % (time.time() - self.start)

    return random.choice(bestActions)

class JointParticleFilter:

  def __init__(self, gameState, index, invaders):
    self.legalPositions = [p for p in gameState.getWalls().asList(False)]
    self.walls = gameState.getWalls()
    self.invaders = invaders
    self.index = index
    self.numInvaders = len(invaders)
    self.numParticles = 100*self.numInvaders

    self.ghostAgents = invaders
    self.particles = [tuple(random.choice(self.legalPositions) for _ in range(self.numInvaders)) for _ in range(self.numParticles)]

  def updatePosition(self, pos, ghost_id):
    'saw the invader, update the beliefs'
    updatedParticles = []
    for particle in self.particles:
      part = list(particle)
      part[ghost_id] = pos
      updatedParticles.append(tuple(part))

    self.particles = updatedParticles

  def elapseTime(self, gameState):
    newParticles = []
    for oldParticle in self.particles:
      newParticle = list(oldParticle) # A list of ghost positions
      newParticle = tuple(random.choice(game.Actions.getLegalNeighbors(pos, self.walls)) for pos in newParticle)
      newParticles.append(newParticle)
    self.particles = newParticles
  
  def observeState(self, gameState):
    pacmanPosition = gameState.getAgentState(self.index).getPosition()
    noisyDistances = gameState.getAgentDistances()

    weights = util.Counter()
    for p in self.particles:
      t = 1
      for i in range(self.numInvaders):
        dist = util.manhattanDistance(p[i], pacmanPosition)
        t *= gameState.getDistanceProb(dist, noisyDistances[i])
      weights[p] += t

    if not any(weights.values()):
      self.particles = [tuple(random.choice(self.legalPositions) for _ in range(self.numInvaders)) for _ in range(self.numParticles)]
      return None

    weights.normalize()
    # resample
    self.particles = [util.sample(weights) for _ in range(self.numParticles)]
  
  def getBeliefDistribution(self):
    jointDistribution = util.Counter()
    for part in self.particles: jointDistribution[part] += 1
    jointDistribution.normalize()
    # marginalize the belief over each invader
    dist = []
    for ghostIdx in range(self.numInvaders):
      dist.append(util.Counter())
      for t, prob in jointDistribution.items():
        dist[-1][t[ghostIdx]] += prob
    return dist
