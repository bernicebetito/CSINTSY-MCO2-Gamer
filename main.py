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

    def printLocations(self):
        for row in self.grid_content:
            for column in row:
                print(column, end=" ")
            print("\n")

    def printBoard(self):
        print("-" * 80)
        for row in self.grid_content:
            print("         |" * 8, end="\n")
            for column in row:
                print(" ", column, end="  |")
            print("\n         |", end="")
            print("         |" * 7, end="\n")
            print("-" * 80, end="\n")


if __name__ == "__main__":
    game = checkers()
    game.initalizeLocations()
    game.printBoard()