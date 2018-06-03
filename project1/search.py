import util

class SearchProblem:
    """
    This class outlines the structure of a search problem, but doesn't implement
    any of the methods (in object-oriented terminology: an abstract class).

    You do not need to change anything in this class, ever.
    """

    def getStartState(self):
        """
        Returns the start state for the search problem
        """
        util.raiseNotDefined()

    def isGoalState(self, state):
        """
          state: Search state

        Returns True if and only if the state is a valid goal state
        """
        util.raiseNotDefined()

    def getSuccessors(self, state):
        """
          state: Search state

        For a given state, this should return a list of triples,
        (successor, action, stepCost), where 'successor' is a
        successor to the current state, 'action' is the action
        required to get there, and 'stepCost' is the incremental
        cost of expanding to that successor
        """
        util.raiseNotDefined()

    def getCostOfActions(self, actions):
        """
         actions: A list of actions to take

        This method returns the total cost of a particular sequence of actions.  The sequence must
        be composed of legal moves
        """
        util.raiseNotDefined()


def tinyMazeSearch(problem):
    """
    Returns a sequence of moves that solves tinyMaze.  For any other
    maze, the sequence of moves will be incorrect, so only use this for tinyMaze
    """
    from game import Directions
    s = Directions.SOUTH
    w = Directions.WEST
    return  [s,s,w,s,w,w,s,w]

def depthFirstSearch(problem):
    """
    Search the deepest nodes in the search tree first
    [2nd Edition: p 75, 3rd Edition: p 87]

    Your search algorithm needs to return a list of actions that reaches
    the goal.  Make sure to implement a graph search algorithm
    [2nd Edition: Fig. 3.18, 3rd Edition: Fig 3.7].

    To get started, you might want to try some of these simple commands to
    understand the search problem that is being passed in:

    print "Start:", problem.getStartState()
    print "Is the start a goal?", problem.isGoalState(problem.getStartState())
    print "Start's successors:", problem.getSuccessors(problem.getStartState())
    """
    "*** YOUR CODE HERE ***"
    # initialize frontier using initial state of problem
    current_state = problem.getStartState()
    frontier = util.Stack()
    frontier.push(current_state)

    # initialize explored set to be empty
    explored_set = []

    # a dictionary to save how to get to certain states from initial state
    actions_list = {current_state:[]}

    # loop while we still have unexplored nodes
    while not frontier.isEmpty():

        # choose a leaf node and remove it from frontier
        leaf_node = frontier.pop()

        # return the solution if it is the goal state
        if problem.isGoalState(leaf_node):
            return actions_list[leaf_node]

        # add the node to explored set
        explored_set.append(leaf_node)

        # expand the chosen node
        # and add to the frontier if not in frontier and explored set
        for successor in problem.getSuccessors(leaf_node):
            child, action, _ = successor
            if child not in explored_set and child not in frontier.list:
                frontier.push(child)
                actions_list[child] = actions_list[leaf_node] + [action]
    else:
        # search through all but still can't find a solution -> failed!
        return 'failure'


def breadthFirstSearch(problem):
    """
    Search the shallowest nodes in the search tree first.
    [2nd Edition: p 73, 3rd Edition: p 82]
    """
    "*** YOUR CODE HERE ***"
    # initialize frontier using initial state of problem
    current_state = problem.getStartState()
    frontier = util.Queue()
    frontier.push(current_state)

    # initialize explored set to be empty
    explored_set = []

    # a dictionary to save how to get to certain states from initial state
    actions_list = {current_state:[]}

    # loop while we still have unexplored nodes
    while not frontier.isEmpty():

        # choose a leaf node and remove it from frontier
        leaf_node = frontier.pop()

        # add the node to explored set
        explored_set.append(leaf_node)

        # expand the chosen node
        # and add to the frontier if not in frontier and explored set
        for successor in problem.getSuccessors(leaf_node):
            child, action, _ = successor
            if child not in explored_set and child not in frontier.list:
                # return the solution if it is the goal state
                if problem.isGoalState(child):
                    return actions_list[leaf_node] + [action]
                frontier.push(child)
                actions_list[child] = actions_list[leaf_node] + [action]
    else:
        # search through all but still can't find a solution -> failed!
        return 'failure'

def uniformCostSearch(problem):
    "Search the node of least total cost first. "
    "*** YOUR CODE HERE ***"
    # initialize frontier using initial state of problem
    current_state = problem.getStartState()
    frontier = util.PriorityQueue()
    frontier.push(current_state, 0)

    # initialize explored set to be empty
    explored_set = []

    # a dictionary to save how to get to certain states from initial state
    actions_list = {current_state:[]}

    # loop while we still have unexplored nodes
    while not frontier.isEmpty():

        # choose a leaf node and remove it from frontier
        leaf_node = frontier.pop()

        # return the solution if it is the goal state
        if problem.isGoalState(leaf_node):
            return actions_list[leaf_node]

        # add the node to explored set
        explored_set.append(leaf_node)

        # expand the chosen node
        # and add to the frontier if not in frontier and explored set
        for successor in problem.getSuccessors(leaf_node):
            child, action, cost = successor
            if child not in explored_set and child not in frontier.heap:
                actions_list[child] = actions_list[leaf_node] + [action]
                frontier.push(child, problem.getCostOfActions(actions_list[child]))
    else:
        # search through all but still can't find a solution -> failed!
        return 'failure'

def nullHeuristic(state, problem=None):
    """
    A heuristic function estimates the cost from the current state to the nearest
    goal in the provided SearchProblem.  This heuristic is trivial.
    """
    return 0

def aStarSearch(problem, heuristic=nullHeuristic):
    "Search the node that has the lowest combined cost and heuristic first."
    "*** YOUR CODE HERE ***"
    # initialize frontier using initial state of problem
    current_state = problem.getStartState()
    frontier = util.PriorityQueue()
    frontier.push(current_state, 0)

    # initialize explored set to be empty
    explored_set = set()

    # a dictionary to save how to get to certain states from initial state
    actions_list = {current_state:[]}

    # loop while we still have unexplored nodes
    while not frontier.isEmpty():

        # choose a leaf node and remove it from frontier
        leaf_node = frontier.pop()

        # return the solution if it is the goal state
        if problem.isGoalState(leaf_node):
            return actions_list[leaf_node]

        # add the node to explored set
        explored_set.add(leaf_node)

        # expand the chosen node
        # and add to the frontier if not in frontier and explored set
        # replace the node in frontier if current node has lower cost
        for successor in problem.getSuccessors(leaf_node):
            child, action, cost = successor
            if frontier.heap:
                vals, keys = zip(*frontier.heap)
                frontier_node = {key: val for key, val in zip(keys, vals)}
            else:
                frontier_node = []
            if child not in explored_set and child not in frontier_node:
                actions_list[child] = actions_list[leaf_node] + [action]
                c = problem.getCostOfActions(actions_list[child])+heuristic(child, problem)
                frontier.push(child, c)
            elif child in frontier_node:
                new_c = problem.getCostOfActions(actions_list[leaf_node]+[action])+heuristic(child, problem)
                if new_c < frontier_node[child]:
                    frontier.heap.remove((frontier_node[child],child))
                    frontier.push(child, new_c)
                    actions_list[child] = actions_list[leaf_node] + [action]
    else:
        # search through all but still can't find a solution -> failed!
        return 'failure'

astar = aStarSearch
bfs = breadthFirstSearch
dfs = depthFirstSearch
ucs = uniformCostSearch