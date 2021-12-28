import os, time, random

class checkers():
    def __init__(self):
        self.human_locations = []
        self.agent_locations = []
        self.grid_content = []

    def initalizeLocations(self):
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
                        self.agent_locations.append([row, column])
                    elif 5 <= row <= 7:
                        row_content.append("HUMAN")
                        self.human_locations.append([row, column])
                    else:
                        row_content.append("     ")
            self.grid_content.append(row_content)

    def getStatistics(self):
        state = checkersStates(self.grid_content, self.human_locations, self.agent_locations)
        if not state.checkMoves(self.human_locations) and state.checkMoves(self.agent_locations):
            winner = "Agent"
        elif state.checkMoves(self.human_locations) and not state.checkMoves(self.agent_locations):
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

        for row in range(len(self.grid_content)):
            for col in range(len(self.grid_content[row])):
                if self.grid_content[row][col] == "HUMAN" or self.grid_content[row][col] == "KingH":
                    self.human_locations.append([row, col])
                elif self.grid_content[row][col] == "AGENT" or self.grid_content[row][col] == "KingA":
                    self.agent_locations.append([row, col])

    def gameContinue(self):
        self.updatePieces()
        game_state = checkersStates(self.grid_content, self.human_locations, self.agent_locations)
        return game_state.checkMoves(self.human_locations) and game_state.checkMoves(self.agent_locations)

    def getPossibleMoves(self, turn):
        states = checkersStates(self.grid_content, self.human_locations, self.agent_locations)
        if turn == "HUMAN":
            return states.getStates(self.human_locations)
        else:
            return states.getStates(self.agent_locations)

    def humanTurn(self, oldLocation, newLocation):
        state = checkersStates(self.grid_content, self.human_locations, self.agent_locations)
        print("\n\n")
        self.printLocations()
        print("\n\n")
        updatedGrid, updatedLocation = state.updateLocation(self.grid_content, oldLocation, newLocation)
        if updatedLocation:
            self.grid_content = updatedGrid

        return updatedLocation

    def agentTurn(self):
        state = checkersStates(self.grid_content, self.human_locations, self.agent_locations)
        typeMove, moves = state.getStates(self.agent_locations)
        agent_move = moves[random.randrange(len(moves))]
        print(agent_move)
        updatedGrid, updatedLocation = state.updateLocation(self.grid_content, agent_move[0], agent_move[1])
        if updatedLocation:
            self.grid_content = updatedGrid

    def printLocations(self):
        for row in self.grid_content:
            for column in row:
                print(column, end=" ")
            print("\n")

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
        for row in self.grid_content:
            print("         |" * 9, end="\n")
            print("   ", chr(row_ctr), "   |", end="")
            for column in row:
                print(" ", column, end="  |")
            print("\n         |", end="")
            print("         |" * 8, end="\n")
            print("-" * 90, end="\n")
            row_ctr += 1


class checkersStates():
    def __init__(self, state, human, agent):
        self.current_state = state
        self.human_locations = human
        self.agent_locations = agent

    def checkValidMove(self, piece, location, turn):
        """

        If new location is within range (0 - 7)
        If old location is occupied
        If new location is occupied by any human / agent pieces
        If new location is on correct tile (both even and both odd)

        If HUMAN or AGENT piece is moving forward one square diagonally
        If HUMAN or AGENT piece is capturing opponent's piece/s by moving forward / backward more than one square diagonally
        If KingH or KingA piece is moving forward one square diagonally
        If KingH or KingA piece is capturing opponent's piece/s by moving forward / backward more than one square diagonally

        """
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
                    print("--: ", self.agent_locations)
                    return True
                elif [piece[0] - 1, piece[1] + 1] in self.agent_locations and [piece[0] - 2, piece[1] + 2] == location:
                    print("-+: ", self.agent_locations)
                    return True
                return False
            return False
        elif turn == "AGENT":
            if piece[0] + 1 == location[0] and (piece[1] - 1 == location[1] or piece[1] + 1 == location[1]):
                return True
            elif piece[0] + 2 == location[0] and (piece[1] - 2 == location[1] or piece[1] + 2 == location[1]):
                if [piece[0] + 1, piece[1] - 1] in self.human_locations and [piece[0] + 2, piece[1] - 2] == location:
                    print("+-: ", self.human_locations)
                    return True
                elif [piece[0] + 1, piece[1] + 1] in self.human_locations and [piece[0] + 2, piece[1] + 2] == location:
                    print("++: ", self.human_locations)
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

    def getStates(self, player_locations):
        moveStates = []
        captureStates = []
        for current in player_locations:
            print("current: ", current)
            if self.checkValidMove(current, [current[0] - 1, current[1] - 1], self.current_state[current[0]][current[1]]):
                moveStates.append([current, [[current[0] - 1, current[1] - 1]]])
            if self.checkValidMove(current, [current[0] - 1, current[1] + 1], self.current_state[current[0]][current[1]]):
                moveStates.append([current, [[current[0] - 1, current[1] + 1]]])
            if self.checkValidMove(current, [current[0] + 1, current[1] - 1], self.current_state[current[0]][current[1]]):
                moveStates.append([current, [[current[0] + 1, current[1] - 1]]])
            if self.checkValidMove(current, [current[0] + 1, current[1] + 1], self.current_state[current[0]][current[1]]):
                moveStates.append([current, [[current[0] + 1, current[1] + 1]]])

            if self.checkValidMove(current, [current[0] - 2, current[1] - 2], self.current_state[current[0]][current[1]]):
                print("-- true")
                captureStates.append([current, [[current[0] - 2, current[1] - 2]]])
            if self.checkValidMove(current, [current[0] - 2, current[1] + 2], self.current_state[current[0]][current[1]]):
                print("-+ true")
                captureStates.append([current, [[current[0] - 2, current[1] + 2]]])
            if self.checkValidMove(current, [current[0] + 2, current[1] - 2], self.current_state[current[0]][current[1]]):
                print("+- true")
                captureStates.append([current, [[current[0] + 2, current[1] - 2]]])
            if self.checkValidMove(current, [current[0] + 2, current[1] + 2], self.current_state[current[0]][current[1]]):
                print("++ true")
                captureStates.append([current, [[current[0] + 2, current[1] + 2]]])
            # print("CAPTURE LOCATIONS: ",self.getCaptureStates(self.current_state, current))
        if len(captureStates) > 0:
            input()
            return "CAPTURE", captureStates
        else:
            input()
            return "FORWARD", moveStates

    def getCaptureStates(self, board, oldLocation):
        captureLocations = []
        current = oldLocation

        if self.checkValidMove(current, [current[0] - 2, current[1] - 2], board[current[0]][current[1]]):
            newBoard, updatedLocation = self.updateLocation(board, current, [[current[0] - 2, current[1] - 2]])
            current = [current[0] - 2, current[1] - 2]
            self.getCaptureStates(newBoard, current)
            captureLocations.append([current[0] - 2, current[1] - 2])
        if self.checkValidMove(current, [current[0] - 2, current[1] + 2], board[current[0]][current[1]]):
            newBoard, updatedLocation = self.updateLocation(board, current, [[current[0] - 2, current[1] + 2]])
            current = [current[0] - 2, current[1] + 2]
            self.getCaptureStates(newBoard, current)
            captureLocations.append([current[0] - 2, current[1] + 2])
        if self.checkValidMove(current, [current[0] + 2, current[1] - 2], board[current[0]][current[1]]):
            newBoard, updatedLocation = self.updateLocation(board, current, [[current[0] + 2, current[1] - 2]])
            current = [current[0] + 2, current[1] - 2]
            self.getCaptureStates(newBoard, current)
            captureLocations.append([current[0] + 2, current[1] - 2])
        if self.checkValidMove(current, [current[0] + 2, current[1] + 2], board[current[0]][current[1]]):
            newBoard, updatedLocation = self.updateLocation(board, current, [[current[0] + 2, current[1] + 2]])
            current = [current[0] + 2, current[1] + 2]
            self.getCaptureStates(newBoard, current)
            captureLocations.append([current[0] + 2, current[1] + 2])

        return captureLocations

    def checkMoves(self, player_locations):
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

    def updateLocation(self, board, oldLocation, newLocation):
        updatedLocation = True
        capturedPiece = False
        capturedLocation = []

        old = oldLocation
        new = newLocation
        for currentUpdate in new:
            print("old: ", old)
            print("currentUpdate: ", currentUpdate)
            print("before board[old[0]][old[1]]: ", board[old[0]][old[1]])
            if old[0] + 2 == currentUpdate[0] and old[1] + 2 == currentUpdate[1]:
                print("1")
                capturedLocation = [old[0] + 1, old[1] + 1]
                capturedPiece = True
            elif old[0] - 2 == currentUpdate[0] and old[1] + 2 == currentUpdate[1]:
                print("2")
                capturedLocation = [old[0] - 1, old[1] + 1]
                capturedPiece = True
            elif old[0] + 2 == currentUpdate[0] and old[1] - 2 == currentUpdate[1]:
                print("3")
                capturedLocation = [old[0] + 1, old[1] - 1]
                capturedPiece = True
            elif old[0] - 2 == currentUpdate[0] and old[1] - 2 == currentUpdate[1]:
                print("4")
                capturedLocation = [old[0] - 1, old[1] - 1]
                capturedPiece = True

            """
            if capturedPiece:
                if capturedLocation in self.human_locations:
                    self.human_locations.remove([capturedLocation[0], capturedLocation[1]])
                    board[capturedLocation[0]][capturedLocation[1]] = "     "
                elif capturedLocation in self.agent_locations:
                    self.agent_locations.remove([capturedLocation[0], capturedLocation[1]])
                    board[capturedLocation[0]][capturedLocation[1]] = "     "
                else:
                    updatedLocation = False
            """
            if capturedPiece:
                print("5")
                board[capturedLocation[0]][capturedLocation[1]] = "     "

            if updatedLocation:
                print("6")
                print("after board[old[0]][old[1]]: ", board[old[0]][old[1]])
                if board[old[0]][old[1]] == "HUMAN" or board[old[0]][old[1]] == "KingH":
                    print("7")
                    if currentUpdate[0] == 0:
                        print("8")
                        board[currentUpdate[0]][currentUpdate[1]] = "KingH"
                    else:
                        print("9")
                        board[currentUpdate[0]][currentUpdate[1]] = board[old[0]][old[1]]
                    board[old[0]][old[1]] = "     "
                elif board[old[0]][old[1]] == "AGENT" or board[old[0]][old[1]] == "KingA":
                    print("10")
                    if currentUpdate[0] == 7:
                        print("11")
                        board[currentUpdate[0]][currentUpdate[1]] = "KingA"
                    else:
                        print("12")
                        board[currentUpdate[0]][currentUpdate[1]] = board[old[0]][old[1]]
                    board[old[0]][old[1]] = "     "
                else:
                    print("13")
                    updatedLocation = False

            old = currentUpdate

        return board, updatedLocation


if __name__ == "__main__":
    game = checkers()
    game.initalizeLocations()

    print("\nWelcome to Checkers!\nPlease Enter [S] to Start...\n")

    key_input = ""
    while key_input.lower() != "s":
        key_input = input()

    game_continue = True
    human_turn = False
    while game_continue:
        os.system("cls" if os.name == "nt" else "clear")
        game.printBoard()

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

    gameStats = game.getStatistics()
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