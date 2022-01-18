import math, os, time, random, copy


class SortMoves():
    def __init__(self, moveSize):
        self.sortedMoves = [[0, 0] for _ in range(moveSize)]
        self.sizeSorted = 0

    def addMove(self, move, value):
        index = self.sizeSorted
        if index > 0:
            while index and self.sortedMoves[index - 1][1] > value:
                index -= 1
                if index > 0:
                    self.sortedMoves[index] = self.sortedMoves[index - 1]
        self.sortedMoves[index] = [move, value]
        self.sizeSorted += 1

    def getMoves(self):
        ordered = []
        self.sortedMoves = list(filter(([0, 0]).__ne__, self.sortedMoves))
        for x in self.sortedMoves:
            ordered.append(x[0])
        return ordered


class TranspositionTable():
    def __init__(self):
        self.moveOrderCache = {}
        self.indexTable = [[[random.getrandbits(32)] * 2 for _ in range(8)] for _ in range(8)]

    def computeHash(self, board):
        self.keyHash = 0
        for x in range(8):
            for y in range(8):
                if board[x][y] == "HUMAN" or board[x][y] == "KingH":
                    self.keyHash ^= self.indexTable[x][y][0]
                elif board[x][y] == "AGENT" or board[x][y] == "KingA":
                    self.keyHash ^= self.indexTable[x][y][1]
        return self.keyHash

    def findIndex(self, position):
        index = self.indexTable.index(position)
        return self.keyHash ^ index

    def insertValue(self, key, value, bound):
        move_values = {"value": value, "bound": bound}
        self.moveOrderCache[key] = move_values

    def getValue(self, key):
        if key in self.moveOrderCache:
            return self.moveOrderCache[key]
        return False


class checkers():
    def __init__(self):
        self.grid_content = []
        self.cache = TranspositionTable()

    def initializeGrid(self):
        for row in range(8):
            row_content = []
            for column in range(8):
                if row % 2 == 0:
                    comparison = 1
                else:
                    comparison = 0
                if column % 2 == comparison:
                    row_content.append("     ")
                else:
                    if row <= 2:
                        row_content.append("AGENT")
                    elif 5 <= row <= 7:
                        row_content.append("HUMAN")
                    else:
                        row_content.append("     ")
            self.grid_content.append(row_content)

    def tempGrid(self):
        for row in range(8):
            row_content = []
            for column in range(8):
                row_content.append("     ")
            self.grid_content.append(row_content)
        self.grid_content[0][4] = "AGENT"
        self.grid_content[1][3] = "HUMAN"
        self.grid_content[3][1] = "HUMAN"
        self.grid_content[3][3] = "HUMAN"
        self.grid_content[3][5] = "HUMAN"
        self.grid_content[5][1] = "HUMAN"
        self.grid_content[5][3] = "HUMAN"
        self.grid_content[5][5] = "HUMAN"

    def gameContinue(self):
        state = checkersStates(self.grid_content)
        state.printBoard()
        return state.checkMoves("HUMAN") and state.checkMoves("AGENT")

    def endGame(self):
        state = checkersStates(self.grid_content)
        return state.getStatistics()

    def getPossibleMoves(self, turn):
        copy_state = copy.deepcopy(self.grid_content)
        states = checkersStates(self.grid_content)
        possible_states = states.getStates(turn)
        self.grid_content = copy_state
        return possible_states

    def humanTurn(self, oldLocation, newLocation):
        state = checkersStates(self.grid_content)
        updatedLocation = state.updateLocation(oldLocation, newLocation)
        if updatedLocation:
            self.grid_content = state.current_state

        return updatedLocation

    def agentTurn(self):
        state = checkersStates(self.grid_content)
        copy_state = copy.deepcopy(self.grid_content)
        # """
        agent_type, agent_move = self.alphaBeta(state)
        self.grid_content = copy_state
        state.current_state = copy_state
        print(agent_move)
        input()
        state.updateLocation(agent_move[0], agent_move[1])
        self.grid_content = state.current_state
        """
        typeMove, possible_states = state.getStates("AGENT")
        self.grid_content = copy_state
        agent_move = possible_states[random.randrange(len(possible_states))]
        print(agent_move)
        state.updateLocation(agent_move[0], agent_move[1])
        self.grid_content = state.current_state
        # """

    def alphaBeta(self, state):
        human_pieces = 0
        agent_pieces = 0
        for row in range(len(self.grid_content)):
            for col in range(len(self.grid_content[row])):
                if self.grid_content[row][col] == "HUMAN" or self.grid_content[row][col] == "KingH":
                    human_pieces += 1
                elif self.grid_content[row][col] == "AGENT" or self.grid_content[row][col] == "KingA":
                    agent_pieces += 1

        self.depthLimit = abs((agent_pieces - human_pieces)) + 2
        self.numNodes = 0
        self.maxPruning = 0
        self.minPruning = 0
        self.agent_move_type = ""
        self.agent_move = []

        # v = self.maxValue(state, -math.inf, math.inf, self.depthLimit)
        v = self.maxMoveOrder(state, -math.inf, math.inf, self.depthLimit)

        print("v: ", str(v))
        print("nodes: ", self.numNodes)
        print("max pruning: ", self.maxPruning)
        print("min pruning: ", self.minPruning)

        return self.agent_move_type, self.agent_move

    def maxValue(self, state, alpha, beta, depthLimit):
        if state.checkTerminal():
            return state.computeUtility()
        if depthLimit == 0:
            return state.computeEvaluation()

        self.numNodes += 1

        v = -math.inf
        typeMove, possibleMoves = state.getStates("AGENT")
        for a in possibleMoves:
            copy_state = copy.deepcopy(state.current_state)
            state.updateLocation(a[0], a[1])
            v2 = self.minValue(state, alpha, beta, depthLimit - 1)
            state.current_state = copy.deepcopy(copy_state)
            if v2 > v:
                v = v2
                alpha = max(alpha, v)
                if depthLimit == self.depthLimit:
                    self.agent_move = a
                    self.agent_move_type = typeMove
            if v >= beta:
                self.maxPruning += 1
                return v

        return v

    def minValue(self, state, alpha, beta, depthLimit):
        if state.checkTerminal():
            return state.computeUtility()
        if depthLimit == 0:
            return state.computeEvaluation()

        self.numNodes += 1

        v = math.inf
        typeMove, possibleMoves = state.getStates("HUMAN")
        for a in possibleMoves:
            copy_state = copy.deepcopy(state.current_state)
            state.updateLocation(a[0], a[1])
            v2 = self.maxValue(state, alpha, beta, depthLimit - 1)
            state.current_state = copy.deepcopy(copy_state)
            if v2 < v:
                v = v2
                beta = min(beta, v)
            if v <= alpha:
                self.minPruning += 1
                return v

        return v

    def maxMoveOrder(self, state, alpha, beta, depthLimit):
        if state.checkTerminal():
            return state.computeUtility()
        if depthLimit == 0:
            return state.computeEvaluation()

        self.numNodes += 1

        v = -math.inf
        typeMove, possibleMoves = state.getStates("AGENT")

        sortMoves = SortMoves(len(possibleMoves))
        for x in possibleMoves:
            copy_state = copy.deepcopy(state.current_state)
            state.updateLocation(x[0], x[1])
            if state.checkTerminal():
                value = state.computeUtility()
            else:
                value = state.computeEvaluation()
            state.current_state = copy.deepcopy(copy_state)
            sortMoves.addMove(x, value)

        for a in sortMoves.getMoves():
            copy_state = copy.deepcopy(state.current_state)
            state.updateLocation(a[0], a[1])

            tuple_grid = []
            for row in state.current_state:
                tuple_grid.append(tuple(row))
            tuple_grid = tuple(tuple_grid)

            # """
            if hash(tuple_grid) in self.cache.moveOrderCache:
                cacheValue = self.cache.getValue(hash(tuple_grid))
                if cacheValue["bound"] == "UPPER":
                    beta = min(beta, cacheValue["value"])
                elif cacheValue["bound"] == "LOWER":
                    alpha = min(alpha, cacheValue["value"])
                elif cacheValue["bound"] == "EXACT":
                    """
                    self.agent_move = a
                    self.agent_move_type = typeMove
                    print("EXACT\tcacheValue:\t", cacheValue, "\ta:\t", a)
                    state.current_state = copy.deepcopy(copy_state)
                    return cacheValue["value"]
                    """
                    v2 = cacheValue["value"]

                if alpha >= beta:
                    """
                    self.agent_move = a
                    self.agent_move_type = typeMove
                    print("alpha >= beta\talpha:\t", alpha,"\tbeta:\t", beta,"\tcacheValue:\t", cacheValue, "\ta:\t", a)
                    state.current_state = copy.deepcopy(copy_state)
                    return cacheValue["value"]
                    """
                    v2 = cacheValue["value"]
                else:
                    v2 = self.minMoveOrder(state, alpha, beta, depthLimit - 1)
                    state.current_state = copy.deepcopy(copy_state)
            # """
            else:
                v2 = self.minMoveOrder(state, alpha, beta, depthLimit - 1)
                state.current_state = copy.deepcopy(copy_state)

            if v2 > v:
                v = v2
                alpha = max(alpha, v)
                if depthLimit == self.depthLimit:
                    self.agent_move = a
                    self.agent_move_type = typeMove
            if v >= beta:
                self.maxPruning += 1
                return v

            if v2 <= alpha:
                bound = "UPPER"
            elif v2 >= beta:
                bound = "LOWER"
            else:
                bound = "EXACT"
            self.cache.insertValue(hash(tuple_grid), v, bound)

        return v

    def minMoveOrder(self, state, alpha, beta, depthLimit):
        if state.checkTerminal():
            return state.computeUtility()
        if depthLimit == 0:
            return state.computeEvaluation()

        self.numNodes += 1

        v = math.inf
        typeMove, possibleMoves = state.getStates("HUMAN")

        sortMoves = SortMoves(len(possibleMoves))
        for x in possibleMoves:
            copy_state = copy.deepcopy(state.current_state)
            state.updateLocation(x[0], x[1])
            if state.checkTerminal():
                value = state.computeUtility()
            else:
                value = state.computeEvaluation()
            state.current_state = copy.deepcopy(copy_state)
            sortMoves.addMove(x, value)

        for a in sortMoves.getMoves():
            copy_state = copy.deepcopy(state.current_state)
            state.updateLocation(a[0], a[1])

            tuple_grid = []
            for row in state.current_state:
                tuple_grid.append(tuple(row))
            tuple_grid = tuple(tuple_grid)

            # """
            if hash(tuple_grid) in self.cache.moveOrderCache:
                cacheValue = self.cache.getValue(hash(tuple_grid))
                if cacheValue["bound"] == "UPPER":
                    beta = min(beta, cacheValue["value"])
                elif cacheValue["bound"] == "LOWER":
                    alpha = min(alpha, cacheValue["value"])
                elif cacheValue["bound"] == "EXACT":
                    """
                    state.current_state = copy.deepcopy(copy_state)
                    return cacheValue["value"]
                    """
                    v2 = cacheValue["value"]

                if alpha >= beta:
                    """
                    state.current_state = copy.deepcopy(copy_state)
                    return cacheValue["value"]
                    """
                    v2 = cacheValue["value"]
                else:
                    v2 = self.maxMoveOrder(state, alpha, beta, depthLimit - 1)
                    state.current_state = copy.deepcopy(copy_state)
            # """
            else:
                v2 = self.maxMoveOrder(state, alpha, beta, depthLimit - 1)
                state.current_state = copy.deepcopy(copy_state)

            if v2 < v:
                v = v2
                beta = min(beta, v)
            if v <= alpha:
                self.minPruning += 1
                return v

            if v2 <= alpha:
                bound = "UPPER"
            elif v2 >= beta:
                bound = "LOWER"
            else:
                bound = "EXACT"
            self.cache.insertValue(hash(tuple_grid), v, bound)

        return v


class checkersStates():
    def __init__(self, state):
        self.current_state = state

    def getStatistics(self):
        human_pieces = 0
        agent_pieces = 0
        for row in range(len(self.current_state)):
            for col in range(len(self.current_state[row])):
                if self.current_state[row][col] == "HUMAN" or self.current_state[row][col] == "KingH":
                    human_pieces += 1
                elif self.current_state[row][col] == "AGENT" or self.current_state[row][col] == "KingA":
                    agent_pieces += 1

        if not self.checkMoves("HUMAN") and self.checkMoves("AGENT"):
            winner = "Agent"
        elif self.checkMoves("HUMAN") and not self.checkMoves("AGENT"):
            winner = "Human"
        elif human_pieces > agent_pieces:
            winner = "Human"
        elif human_pieces < agent_pieces:
            winner = "Agent"
        else:
            winner = "Draw"

        return {"Human": human_pieces, "Agent": agent_pieces, "Winner": winner}

    def computeUtility(self):
        kings = 0
        men = 0
        for row in self.current_state:
            kings += row.count("KingA")
            men += row.count("AGENT")

        human_pieces = 0
        agent_pieces = 0
        for row in range(len(self.current_state)):
            for col in range(len(self.current_state[row])):
                if self.current_state[row][col] == "HUMAN" or self.current_state[row][col] == "KingH":
                    human_pieces += 1
                elif self.current_state[row][col] == "AGENT" or self.current_state[row][col] == "KingA":
                    agent_pieces += 1

        return ((agent_pieces - human_pieces) * 100) + (kings * 50) + (men * 20)

    def computeEvaluation(self):
        kings = 0
        men = 0
        for row in self.current_state:
            kings += row.count("KingA")
            men += row.count("AGENT")

        human_pieces = 0
        agent_pieces = 0
        for row in range(len(self.current_state)):
            for col in range(len(self.current_state[row])):
                if self.current_state[row][col] == "HUMAN" or self.current_state[row][col] == "KingH":
                    human_pieces += 1
                elif self.current_state[row][col] == "AGENT" or self.current_state[row][col] == "KingA":
                    agent_pieces += 1

        return ((agent_pieces - human_pieces) * 50) + (kings * 25) + (men * 10)

    def checkTerminal(self):
        human_pieces = 0
        agent_pieces = 0
        for row in range(len(self.current_state)):
            for col in range(len(self.current_state[row])):
                if self.current_state[row][col] == "HUMAN" or self.current_state[row][col] == "KingH":
                    human_pieces += 1
                elif self.current_state[row][col] == "AGENT" or self.current_state[row][col] == "KingA":
                    agent_pieces += 1

        if not self.checkMoves("HUMAN") and not self.checkMoves("AGENT"):
            return True
        elif human_pieces == 0 or agent_pieces == 0:
            return True
        return False

    def checkValidMove(self, piece, location, turn):
        agent_pieces = ("AGENT", "KingA")
        human_pieces = ("HUMAN", "KingH")

        if location[0] < 0 or location[0] > 7 or location[1] < 0 or location[1] > 7:
            return False
        if piece[0] < 0 or piece[0] > 7 or piece[1] < 0 or piece[1] > 7:
            return False
        if (location[0] % 2 == 1 and location[1] % 2 == 0) or (location[0] % 2 == 0 and location[1] % 2 == 1):
            return False
        if (piece[0] % 2 == 1 and piece[1] % 2 == 0) or (piece[0] % 2 == 0 and piece[1] % 2 == 1):
            return False
        if self.current_state[piece[0]][piece[1]] not in human_pieces and (turn == "HUMAN" or turn == "KingH"):
            return False
        if self.current_state[piece[0]][piece[1]] not in agent_pieces and (turn == "AGENT" or turn == "KingA"):
            return False
        if self.current_state[location[0]][location[1]] != "     ":
            return False

        if turn == "HUMAN":
            if piece[0] - 1 == location[0] and (piece[1] - 1 == location[1] or piece[1] + 1 == location[1]):
                return True
            elif piece[0] - 2 == location[0] and (piece[1] - 2 == location[1] or piece[1] + 2 == location[1]):
                if 0 <= piece[0] - 1 <= 7 and 0 <= piece[1] - 1 <= 7:
                    if self.current_state[piece[0] - 1][piece[1] - 1] in agent_pieces and [piece[0] - 2, piece[1] - 2] == location:
                        return True
                if 0 <= piece[0] - 1 <= 7 and 0 <= piece[1] + 1 <= 7:
                    if self.current_state[piece[0] - 1][piece[1] + 1] in agent_pieces and [piece[0] - 2, piece[1] + 2] == location:
                        return True
                return False
            return False
        elif turn == "AGENT":
            if piece[0] + 1 == location[0] and (piece[1] - 1 == location[1] or piece[1] + 1 == location[1]):
                return True
            elif piece[0] + 2 == location[0] and (piece[1] - 2 == location[1] or piece[1] + 2 == location[1]):
                if 0 <= piece[0] + 1 <= 7 and 0 <= piece[1] - 1 <= 7:
                    if self.current_state[piece[0] + 1][piece[1] - 1] in human_pieces and [piece[0] + 2, piece[1] - 2] == location:
                        return True
                if 0 <= piece[0] + 1 <= 7 and 0 <= piece[1] + 1 <= 7:
                    if self.current_state[piece[0] + 1][piece[1] + 1] in human_pieces and [piece[0] + 2, piece[1] + 2] == location:
                        return True
                return False
            return False
        elif turn == "KingH" or turn == "KingA":
            if piece[0] - 1 == location[0] and (piece[1] - 1 == location[1] or piece[1] + 1 == location[1]):
                return True
            elif piece[0] + 1 == location[0] and (piece[1] - 1 == location[1] or piece[1] + 1 == location[1]):
                return True
            elif (piece[0] - 2 == location[0] or piece[0] + 2 == location[0]) and (piece[1] - 2 == location[1] or piece[1] + 2 == location[1]):
                valid_one = 0 <= piece[0] - 1 <= 7 and 0 <= piece[1] - 1 <= 7
                valid_two = 0 <= piece[0] - 1 <= 7 and 0 <= piece[1] + 1 <= 7
                valid_three = 0 <= piece[0] + 1 <= 7 and 0 <= piece[1] - 1 <= 7
                valid_four = 0 <= piece[0] + 1 <= 7 and 0 <= piece[1] + 1 <= 7
                if turn == "KingH":
                    if valid_one:
                        if self.current_state[piece[0] - 1][piece[1] - 1] in agent_pieces and [piece[0] - 2, piece[1] - 2] == location:
                            return True
                    if valid_two:
                        if self.current_state[piece[0] - 1][piece[1] + 1] in agent_pieces and [piece[0] - 2,piece[1] + 2] == location:
                            return True
                    if valid_three:
                        if self.current_state[piece[0] + 1][piece[1] - 1] in agent_pieces and [piece[0] + 2, piece[1] - 2] == location:
                            return True
                    if valid_four:
                        if self.current_state[piece[0] + 1][piece[1] + 1] in agent_pieces and [piece[0] + 2,piece[1] + 2] == location:
                            return True
                else:
                    if valid_one:
                        if self.current_state[piece[0] - 1][piece[1] - 1] in human_pieces and [piece[0] - 2, piece[1] - 2] == location:
                            return True
                    if valid_two:
                        if self.current_state[piece[0] - 1][piece[1] + 1] in human_pieces and [piece[0] - 2, piece[1] + 2] == location:
                            return True
                    if valid_three:
                        if self.current_state[piece[0] + 1][piece[1] - 1] in human_pieces and [piece[0] + 2, piece[1] - 2] == location:
                            return True
                    if valid_four:
                        if self.current_state[piece[0] + 1][piece[1] + 1] in human_pieces and [piece[0] + 2, piece[1] + 2] == location:
                            return True
                return False
            return False
        else:
            return False

    def getStates(self, turn):
        moveStates = []
        captureStates = []
        player_locations = []

        for row in range(len(self.current_state)):
            for col in range(len(self.current_state[row])):
                if turn == "HUMAN" and (self.current_state[row][col] == "HUMAN" or self.current_state[row][col] == "KingH"):
                    player_locations.append([row, col])
                elif turn != "HUMAN" and (self.current_state[row][col] == "AGENT" or self.current_state[row][col] == "KingA"):
                    player_locations.append([row, col])

        if turn == "HUMAN":
            player_locations.sort()
        else:
            player_locations.sort(reverse=True)

        for current in player_locations:
            if self.checkValidMove(current, [current[0] - 1, current[1] - 1], self.current_state[current[0]][current[1]]):
                moveStates.append([tuple(current), [(current[0] - 1, current[1] - 1)]])
            if self.checkValidMove(current, [current[0] - 1, current[1] + 1], self.current_state[current[0]][current[1]]):
                moveStates.append([tuple(current), [(current[0] - 1, current[1] + 1)]])
            if self.checkValidMove(current, [current[0] + 1, current[1] - 1], self.current_state[current[0]][current[1]]):
                moveStates.append([tuple(current), [(current[0] + 1, current[1] - 1)]])
            if self.checkValidMove(current, [current[0] + 1, current[1] + 1], self.current_state[current[0]][current[1]]):
                moveStates.append([tuple(current), [(current[0] + 1, current[1] + 1)]])

            copy_state = copy.deepcopy(self.current_state)
            capture_dirs = [(-2, -2), (-2, 2), (2, -2), (2, 2)]

            for curr_dir in capture_dirs:
                if self.checkValidMove(current, [current[0] + curr_dir[0], current[1] + curr_dir[1]], self.current_state[current[0]][current[1]]):
                    curr_move = "CAPTURE"
                    captures = [[current[0] + curr_dir[0], current[1] + curr_dir[1]]]
                    old_piece = [current[0] + curr_dir[0], current[1] + curr_dir[1]]
                    other_options = []
                    curr_other = 0

                    self.updateLocation(current, [[current[0] + curr_dir[0], current[1] + curr_dir[1]]])
                    while curr_move == "CAPTURE":
                        curr_move, next_move = self.getCaptureStates(old_piece)
                        if curr_move == "CAPTURE":
                            if len(next_move) > 1:
                                for x in next_move:
                                    other_options.append(captures + [x])
                                curr_other += 1
                            self.updateLocation(old_piece, [next_move[0]])
                            captures.append(next_move[0])
                            old_piece = next_move[0]
                        elif curr_other < len(other_options):
                            captureStates.append([current, captures])
                            self.current_state = copy.deepcopy(copy_state)
                            self.updateLocation(current, other_options[curr_other])
                            captures = other_options[curr_other]
                            curr_move = "CAPTURE"
                            old_piece = other_options[curr_other][len(other_options[curr_other]) - 1]
                            curr_other += 1

                    self.current_state = copy.deepcopy(copy_state)
                    captureStates.append([current, captures])
        if len(captureStates) > 0:
            possibleCaptures = []
            for x in captureStates:
                move_content = [tuple(x[0])]
                locs = []
                for y in x[1]:
                    locs.append(tuple(y))
                move_content.append(locs)
                possibleCaptures.append(move_content)

            for x in range(len(possibleCaptures)):
                possibleCaptures[x][1] = tuple(possibleCaptures[x][1])
                possibleCaptures[x] = tuple(possibleCaptures[x])

            return "CAPTURE", possibleCaptures
        else:
            for x in range(len(moveStates)):
                moveStates[x][1] = tuple(moveStates[x][1])
                moveStates[x] = tuple(moveStates[x])
            return "FORWARD", moveStates

    def getCaptureStates(self, current):
        curr_move = "FORWARD"
        captures = []
        if self.checkValidMove(current, [current[0] - 2, current[1] - 2], self.current_state[current[0]][current[1]]):
            curr_move = "CAPTURE"
            captures.append([current[0] - 2, current[1] - 2])
        if self.checkValidMove(current, [current[0] - 2, current[1] + 2], self.current_state[current[0]][current[1]]):
            curr_move = "CAPTURE"
            captures.append([current[0] - 2, current[1] + 2])
        if self.checkValidMove(current, [current[0] + 2, current[1] - 2], self.current_state[current[0]][current[1]]):
            curr_move = "CAPTURE"
            captures.append([current[0] + 2, current[1] - 2])
        if self.checkValidMove(current, [current[0] + 2, current[1] + 2], self.current_state[current[0]][current[1]]):
            curr_move = "CAPTURE"
            captures.append([current[0] + 2, current[1] + 2])

        return curr_move, captures

    def checkMoves(self, turn):
        player_locations = []

        for row in range(len(self.current_state)):
            for col in range(len(self.current_state[row])):
                if turn == "HUMAN" and (self.current_state[row][col] == "HUMAN" or self.current_state[row][col] == "KingH"):
                    player_locations.append([row, col])
                elif turn != "HUMAN" and (self.current_state[row][col] == "AGENT" or self.current_state[row][col] == "KingA"):
                    player_locations.append([row, col])

        for current in player_locations:
            if self.checkValidMove(current, [current[0] - 1, current[1] - 1], self.current_state[current[0]][current[1]]):
                return True
            if self.checkValidMove(current, [current[0] - 1, current[1] + 1], self.current_state[current[0]][current[1]]):
                return True
            if self.checkValidMove(current, [current[0] + 1, current[1] - 1], self.current_state[current[0]][current[1]]):
                return True
            if self.checkValidMove(current, [current[0] + 1, current[1] + 1], self.current_state[current[0]][current[1]]):
                return True
            if self.checkValidMove(current, [current[0] - 2, current[1] - 2], self.current_state[current[0]][current[1]]):
                return True
            if self.checkValidMove(current, [current[0] + 2, current[1] - 2], self.current_state[current[0]][current[1]]):
                return True
            if self.checkValidMove(current, [current[0] - 2, current[1] + 2], self.current_state[current[0]][current[1]]):
                return True
            if self.checkValidMove(current, [current[0] + 2, current[1] + 2], self.current_state[current[0]][current[1]]):
                return True

        return False

    def updateLocation(self, oldLocation, newLocation):
        updatedLocation = True

        old = oldLocation
        for currentUpdate in newLocation:
            capturedPiece = False
            capturedLocation = []
            if old[0] + 2 == currentUpdate[0] and old[1] + 2 == currentUpdate[1]:
                capturedLocation = [old[0] + 1, old[1] + 1]
                capturedPiece = True
            elif old[0] - 2 == currentUpdate[0] and old[1] + 2 == currentUpdate[1]:
                capturedLocation = [old[0] - 1, old[1] + 1]
                capturedPiece = True
            elif old[0] + 2 == currentUpdate[0] and old[1] - 2 == currentUpdate[1]:
                capturedLocation = [old[0] + 1, old[1] - 1]
                capturedPiece = True
            elif old[0] - 2 == currentUpdate[0] and old[1] - 2 == currentUpdate[1]:
                capturedLocation = [old[0] - 1, old[1] - 1]
                capturedPiece = True

            if capturedPiece:
                self.current_state[capturedLocation[0]][capturedLocation[1]] = "     "

            if updatedLocation:
                if self.current_state[old[0]][old[1]] == "HUMAN" or self.current_state[old[0]][old[1]] == "KingH":
                    if currentUpdate[0] == 0:
                        self.current_state[currentUpdate[0]][currentUpdate[1]] = "KingH"
                    else:
                        self.current_state[currentUpdate[0]][currentUpdate[1]] = self.current_state[old[0]][old[1]]
                    self.current_state[old[0]][old[1]] = "     "
                elif self.current_state[old[0]][old[1]] == "AGENT" or self.current_state[old[0]][old[1]] == "KingA":
                    if currentUpdate[0] == 7:
                        self.current_state[currentUpdate[0]][currentUpdate[1]] = "KingA"
                    else:
                        self.current_state[currentUpdate[0]][currentUpdate[1]] = self.current_state[old[0]][old[1]]
                    self.current_state[old[0]][old[1]] = "     "
                else:
                    updatedLocation = False

            old = currentUpdate

        return updatedLocation

    def printBoard(self):
        print("-" * 90)
        for i in range(-1, 8):
            if i >= 0:
                print("   ", i + 1, " ", end="  |")
            else:
                print("         |", end="")
        print()
        print("-" * 90)
        row_ctr = 65
        for row in self.current_state:
            print("         |" * 9, end="\n")
            print("   ", chr(row_ctr), "   |", end="")
            for column in row:
                print(" ", column, end="  |")
            print("\n         |", end="")
            print("         |" * 8, end="\n")
            print("-" * 90, end="\n")
            row_ctr += 1


if __name__ == "__main__":
    game = checkers()
    game.initializeGrid()

    print("\nWelcome to Checkers!\nPlease Enter [S] to Start...\n")

    key_input = ""
    while key_input.lower() != "s":
        key_input = input()
        if key_input.lower() != "s":
            print("Invalid Key! Please Enter [S] to Start...\n")

    # os.system("cls" if os.name == "nt" else "clear")
    game_continue = True
    human_turn = False
    while game_continue:
        os.system("cls" if os.name == "nt" else "clear")

        if game.gameContinue():
            if human_turn:
                print("To exit the game, Enter [EXIT]\n\n")
                print("\nEnter the Option Number of the Piece in the following format: [Option Number]\n\n")

                typeMove, possibleMoves = game.getPossibleMoves("HUMAN")
                possibleMoves.sort()
                print("\t", typeMove, " MOVES")
                print("[#]  PIECE  |  MOVES")
                for curr_piece in range(len(possibleMoves)):
                    piece_formatted = chr(possibleMoves[curr_piece][0][0] + 65) + str(possibleMoves[curr_piece][0][1] + 1)
                    print("[{}]    {:<2}   | ".format(curr_piece + 1, piece_formatted), end="")

                    for curr_move in possibleMoves[curr_piece][1]:
                        move_formatted = chr(curr_move[0] + 65) + str(curr_move[1] + 1)
                        print("   {:<2} ".format(move_formatted), end="")
                    print()
                print()

                user_move = ""
                valid_move = False
                while not valid_move:
                    user_move = input()

                    if user_move.lower() == "exit":
                        game_continue = False
                        valid_move = True
                    else:
                        piece = []
                        move = []
                        valid_piece = str(user_move).isdigit()
                        if valid_piece and 0 < int(user_move) <= len(possibleMoves):
                            piece = possibleMoves[int(user_move) - 1][0]
                            move = possibleMoves[int(user_move) - 1][1]

                            if not game.humanTurn(piece, move):
                                human_turn = True
                                valid_move = False
                                print("\n2 Invalid Option Number! Please enter a Valid Option Number.\n")
                            else:
                                human_turn = False
                                valid_move = True
                        else:
                            print("Possible Moves Len: ", len(possibleMoves))
                            human_turn = True
                            valid_move = False
                            print("\n1 Invalid Option Number! Please enter a Valid Option Number.\n")
            else:
                print("\nAgent's Turn...\n")
                time.sleep(1)
                game.agentTurn()
                time.sleep(2)
                human_turn = True
        else:
            game_continue = False

    print("\n\n")
    print("=" * 90, end="\n")
    print(" " * 38, " GAME ENDED ", " " * 38)
    print("=" * 90, end="\n")

    gameStats = game.endGame()
    print("\n\n")
    print("-" * 38, " STATISTICS ", "-" * 38, end="\n")
    print("Number of Agent Pieces Remaining: ", gameStats["Agent"])
    print("Number of Human Pieces Remaining: ", gameStats["Human"], end="\n\n")

    if gameStats["Winner"] != "Draw":
        winner = " " + gameStats["Winner"] + " won! "
    else:
        winner = " " + gameStats["Winner"] + " between Agent and Human! "
    print(" " * int((90 - len(winner)) / 2), winner, " " * int((90 - len(winner)) / 2))
    print("-" * 90, end="\n\n")

    print(" " * 29, "Thank you for playing Checkers!", " " * 30)