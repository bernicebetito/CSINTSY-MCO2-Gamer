import os, re

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

    def checkPiece(self, piece):
        if [piece[0], piece[1]] in self.human_locations:
            return True
        return False

    def checkMove(self, location):
        if [location[0], location[1]] not in self.human_locations:
            if [location[0], location[1]] not in self.agent_locations:
                if location[0] % 2 == 0:
                    if location[1] % 2 == 0:
                        return True
                    return False
                elif location[1] % 2 == 1:
                    return True
                return False
            return False
        return False

    def updateLocation(self, oldLocation, newLocation):
        self.grid_content[oldLocation[0]][oldLocation[1]] = "     "
        self.grid_content[newLocation[0]][newLocation[1]] = "HUMAN"
        if oldLocation in self.human_locations:
            for i in range(len(self.human_locations)):
                if self.human_locations[i] == oldLocation:
                    self.human_locations[i] = newLocation

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


if __name__ == "__main__":
    game = checkers()
    game.initalizeLocations()

    print("\nWelcome to Checkers!\nPlease Enter [S] to Start...\n")

    key_input = ""
    while key_input.lower() != "s":
        key_input = input()

    game_continue = True
    while game_continue:
        os.system("cls" if os.name == "nt" else "clear")
        game.printBoard()

        print("To exit the game, Enter EXIT\n\n")
        print("\nEnter a Piece and Move in the following format: [Piece Row][Piece Column] [Move Row][Move Column]")
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
                valid_piece = re.match("^[a-zA-Z][1-8] [a-zA-Z][1-8]", user_move)
                if valid_piece:
                    piece_move = user_move[:2]
                    piece = [ord(piece_move[:1]) - 65, int(piece_move[1:]) - 1]

                    user_move = user_move[len(user_move) - 2:]
                    move = [ord(user_move[:1]) - 65, int(user_move[1:]) - 1]
                    if game.checkPiece(piece):
                        if game.checkMove(move):
                            valid_move = True

                if not valid_move:
                    print("\nInvalid Piece and / or Move! Please enter a Valid Piece to Move.\n")
                else:
                    game.updateLocation(piece, move)

    print("\n\nThank you for playing Checkers!")