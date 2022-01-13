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


class checkers():
    def __init__(self):
        self.grid_content = []

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
        """

    def alphaBeta(self, state):
        self.depthLimit = abs((len(state.agent_locations) - len(state.human_locations))) + 2
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
            state.current_state = copy_state
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
            state.current_state = copy_state
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
            state.current_state = copy_state
            sortMoves.addMove(x, value)

        for a in sortMoves.getMoves():
            copy_state = copy.deepcopy(state.current_state)
            state.updateLocation(a[0], a[1])
            v2 = self.minMoveOrder(state, alpha, beta, depthLimit - 1)
            state.current_state = copy_state

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
            state.current_state = copy_state
            sortMoves.addMove(x, value)

        for a in sortMoves.getMoves():
            copy_state = copy.deepcopy(state.current_state)
            state.updateLocation(a[0], a[1])
            v2 = self.maxMoveOrder(state, alpha, beta, depthLimit - 1)
            state.current_state = copy_state
            if v2 < v:
                v = v2
                beta = min(beta, v)
            if v <= alpha:
                self.minPruning += 1
                return v

        return v


class checkersStates():
    def __init__(self, state):
        self.current_state = state
        self.human_locations = []
        self.agent_locations = []

        for row in range(len(self.current_state)):
            for col in range(len(self.current_state[row])):
                if self.current_state[row][col] == "HUMAN" or self.current_state[row][col] == "KingH":
                    self.human_locations.append([row, col])
                elif self.current_state[row][col] == "AGENT" or self.current_state[row][col] == "KingA":
                    self.agent_locations.append([row, col])

    def getStatistics(self):
        if not self.checkMoves(self.human_locations) and self.checkMoves(self.agent_locations):
            winner = "Agent"
        elif self.checkMoves(self.human_locations) and not self.checkMoves(self.agent_locations):
            winner = "Human"
        elif len(self.human_locations) > len(self.agent_locations):
            winner = "Human"
        elif len(self.human_locations) < len(self.agent_locations):
            winner = "Agent"
        elif len(self.human_locations) == len(self.agent_locations):
            winner = "Draw"
        else:
            winner = "Draw"

        return {"Human": len(self.human_locations), "Agent": len(self.agent_locations), "Winner": winner}

    def updatePieces(self):
        self.human_locations = []
        self.agent_locations = []

        for row in range(len(self.current_state)):
            for col in range(len(self.current_state[row])):
                if self.current_state[row][col] == "HUMAN" or self.current_state[row][col] == "KingH":
                    self.human_locations.append([row, col])
                elif self.current_state[row][col] == "AGENT" or self.current_state[row][col] == "KingA":
                    self.agent_locations.append([row, col])

        self.agent_locations.sort(reverse=True)
        self.human_locations.sort()

    def computeUtility(self):
        kings = 0
        men = 0
        for row in self.current_state:
            kings += row.count("KingA")
            men += row.count("AGENT")
        return ((len(self.agent_locations) - len(self.human_locations)) * 100) + (kings * 50) + (men * 20)

    def computeEvaluation(self):
        kings = 0
        men = 0
        for row in self.current_state:
            kings += row.count("KingA")
            men += row.count("AGENT")
        return ((len(self.agent_locations) - len(self.human_locations)) * 50) + (kings * 25) + (men * 10)

    def checkTerminal(self):
        if not self.checkMoves("HUMAN") and not self.checkMoves("AGENT"):
            return True
        elif len(self.human_locations) == 0 and len(self.agent_locations) == 0:
            return True
        return False

    def checkValidMove(self, piece, location, turn):
        if location[0] < 0 or location[0] > 7 or location[1] < 0 or location[1] > 7:
            return False
        if (piece not in self.human_locations and (turn == "HUMAN" or turn == "KingH")) or (piece not in self.agent_locations and (turn == "AGENT" or turn == "KingA")):
            return False
        if location in self.human_locations or location in self.agent_locations:
            return False
        if (location[0] % 2 == 1 and location[1] % 2 == 0) or (location[0] % 2 == 0 and location[1] % 2 == 1):
            return False

        if turn == "HUMAN":
            if piece[0] - 1 == location[0] and (piece[1] - 1 == location[1] or piece[1] + 1 == location[1]):
                return True
            elif piece[0] - 2 == location[0] and (piece[1] - 2 == location[1] or piece[1] + 2 == location[1]):
                if [piece[0] - 1, piece[1] - 1] in self.agent_locations and [piece[0] - 2, piece[1] - 2] == location:
                    return True
                elif [piece[0] - 1, piece[1] + 1] in self.agent_locations and [piece[0] - 2, piece[1] + 2] == location:
                    return True
                return False
            return False
        elif turn == "AGENT":
            if piece[0] + 1 == location[0] and (piece[1] - 1 == location[1] or piece[1] + 1 == location[1]):
                return True
            elif piece[0] + 2 == location[0] and (piece[1] - 2 == location[1] or piece[1] + 2 == location[1]):
                if [piece[0] + 1, piece[1] - 1] in self.human_locations and [piece[0] + 2, piece[1] - 2] == location:
                    return True
                elif [piece[0] + 1, piece[1] + 1] in self.human_locations and [piece[0] + 2, piece[1] + 2] == location:
                    return True
                return False
            return False
        elif turn == "KingH" or turn == "KingA":
            if piece[0] - 1 == location[0] and (piece[1] - 1 == location[1] or piece[1] + 1 == location[1]):
                return True
            elif piece[0] + 1 == location[0] and (piece[1] - 1 == location[1] or piece[1] + 1 == location[1]):
                return True
            elif (piece[0] - 2 == location[0] or piece[0] + 2 == location[0]) and (piece[1] - 2 == location[1] or piece[1] + 2 == location[1]):
                if turn == "KingH":
                    if [piece[0] - 1, piece[1] - 1] in self.agent_locations and [piece[0] - 2, piece[1] - 2] == location:
                        return True
                    if [piece[0] - 1, piece[1] + 1] in self.agent_locations and [piece[0] - 2,piece[1] + 2] == location:
                        return True
                    if [piece[0] + 1, piece[1] - 1] in self.agent_locations and [piece[0] + 2, piece[1] - 2] == location:
                        return True
                    if [piece[0] + 1, piece[1] + 1] in self.agent_locations and [piece[0] + 2,piece[1] + 2] == location:
                        return True
                else:
                    if [piece[0] - 1, piece[1] - 1] in self.human_locations and [piece[0] - 2, piece[1] - 2] == location:
                        return True
                    if [piece[0] - 1, piece[1] + 1] in self.human_locations and [piece[0] - 2, piece[1] + 2] == location:
                        return True
                    if [piece[0] + 1, piece[1] - 1] in self.human_locations and [piece[0] + 2, piece[1] - 2] == location:
                        return True
                    if [piece[0] + 1, piece[1] + 1] in self.human_locations and [piece[0] + 2, piece[1] + 2] == location:
                        return True
                return False
            return False
        else:
            return False

    def getStates(self, turn):
        moveStates = []
        captureStates = []

        if turn == "HUMAN":
            player_locations = self.human_locations
        else:
            player_locations = self.agent_locations

        for current in player_locations:
            if self.checkValidMove(current, [current[0] - 1, current[1] - 1], self.current_state[current[0]][current[1]]):
                moveStates.append([current, [[current[0] - 1, current[1] - 1]]])
            if self.checkValidMove(current, [current[0] - 1, current[1] + 1], self.current_state[current[0]][current[1]]):
                moveStates.append([current, [[current[0] - 1, current[1] + 1]]])
            if self.checkValidMove(current, [current[0] + 1, current[1] - 1], self.current_state[current[0]][current[1]]):
                moveStates.append([current, [[current[0] + 1, current[1] - 1]]])
            if self.checkValidMove(current, [current[0] + 1, current[1] + 1], self.current_state[current[0]][current[1]]):
                moveStates.append([current, [[current[0] + 1, current[1] + 1]]])

            if self.checkValidMove(current, [current[0] - 2, current[1] - 2], self.current_state[current[0]][current[1]]):
                captureStates.append([current, [[current[0] - 2, current[1] - 2]]])
            if self.checkValidMove(current, [current[0] - 2, current[1] + 2], self.current_state[current[0]][current[1]]):
                captureStates.append([current, [[current[0] - 2, current[1] + 2]]])
            if self.checkValidMove(current, [current[0] + 2, current[1] - 2], self.current_state[current[0]][current[1]]):
                captureStates.append([current, [[current[0] + 2, current[1] - 2]]])
            if self.checkValidMove(current, [current[0] + 2, current[1] + 2], self.current_state[current[0]][current[1]]):
                captureStates.append([current, [[current[0] + 2, current[1] + 2]]])
        if len(captureStates) > 0:
            return "CAPTURE", captureStates
        else:
            return "FORWARD", moveStates

    def getCaptureStates(self, current):
        if self.checkValidMove(current, [current[0] - 2, current[1] - 2], self.current_state[current[0]][current[1]]):
            return "CAPTURE", [current[0] - 2, current[1] - 2]
        if self.checkValidMove(current, [current[0] - 2, current[1] + 2], self.current_state[current[0]][current[1]]):
            return "CAPTURE", [current[0] - 2, current[1] + 2]
        if self.checkValidMove(current, [current[0] + 2, current[1] - 2], self.current_state[current[0]][current[1]]):
            return "CAPTURE", [current[0] + 2, current[1] - 2]
        if self.checkValidMove(current, [current[0] + 2, current[1] + 2], self.current_state[current[0]][current[1]]):
            return "CAPTURE", [current[0] + 2, current[1] + 2]
        return "FORWARD", []

    def checkMoves(self, turn):
        if turn == "HUMAN":
            player_locations = self.human_locations
        else:
            player_locations = self.agent_locations

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

        for currentUpdate in newLocation:
            capturedPiece = False
            capturedLocation = []
            if oldLocation[0] + 2 == currentUpdate[0] and oldLocation[1] + 2 == currentUpdate[1]:
                capturedLocation = [oldLocation[0] + 1, oldLocation[1] + 1]
                capturedPiece = True
            elif oldLocation[0] - 2 == currentUpdate[0] and oldLocation[1] + 2 == currentUpdate[1]:
                capturedLocation = [oldLocation[0] - 1, oldLocation[1] + 1]
                capturedPiece = True
            elif oldLocation[0] + 2 == currentUpdate[0] and oldLocation[1] - 2 == currentUpdate[1]:
                capturedLocation = [oldLocation[0] + 1, oldLocation[1] - 1]
                capturedPiece = True
            elif oldLocation[0] - 2 == currentUpdate[0] and oldLocation[1] - 2 == currentUpdate[1]:
                capturedLocation = [oldLocation[0] - 1, oldLocation[1] - 1]
                capturedPiece = True

            if capturedPiece:
                self.current_state[capturedLocation[0]][capturedLocation[1]] = "     "

            if updatedLocation:
                if self.current_state[oldLocation[0]][oldLocation[1]] == "HUMAN" or self.current_state[oldLocation[0]][oldLocation[1]] == "KingH":
                    if currentUpdate[0] == 0:
                        self.current_state[currentUpdate[0]][currentUpdate[1]] = "KingH"
                    else:
                        self.current_state[currentUpdate[0]][currentUpdate[1]] = self.current_state[oldLocation[0]][oldLocation[1]]
                    self.current_state[oldLocation[0]][oldLocation[1]] = "     "
                elif self.current_state[oldLocation[0]][oldLocation[1]] == "AGENT" or self.current_state[oldLocation[0]][oldLocation[1]] == "KingA":
                    if currentUpdate[0] == 7:
                        self.current_state[currentUpdate[0]][currentUpdate[1]] = "KingA"
                    else:
                        self.current_state[currentUpdate[0]][currentUpdate[1]] = self.current_state[oldLocation[0]][oldLocation[1]]
                    self.current_state[oldLocation[0]][oldLocation[1]] = "     "
                else:
                    updatedLocation = False

            oldLocation = currentUpdate

        self.updatePieces()
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