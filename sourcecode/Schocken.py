"""
class representing the game, instances with console
"""


class SchockenGame:

    def __init__(self):
        print("Enter number of Players: ")

        self.__number_of_players = 0
        while self.__number_of_players == 0:
            no_players = input()
            if not no_players.isnumeric() or int(no_players) <= 0:
                print("Not a valid Number, try again...")
            else:
                self.__number_of_players = int(no_players)

        self.__list_of_players = []
        for i in range(1, self.__number_of_players + 1):
            print(f"Enter name for player {i}: ")
            p = Player(str(input()))
            self.__list_of_players.append(p)
        self.__number_of_cups = 13
        self.__number_of_halves = 2
        self.__currently_cups_middle = self.__number_of_cups

    def start_game(self):

        for i in range(0, self.__number_of_halves):
            print(f"Started half {i + 1}")
            self.__play_half(False)

        # get final players
        final_players = list()
        print("following players are in final: ")
        for p in self.__list_of_players:
            if not p.half_lost:
                p.in_game = False
            else:
                print(f"{p.name}")
                final_players.append(p)

        # check if final is necessary
        # if only one final player -> finish game
        if len(final_players) <= 1:
            print(f"{final_players[0].name} lost the game")
        else:  # play final
            print(f"Started final")
            self.__play_half(True)
            looser = self.__list_of_players[0]  # first player is the looser cause of the rotating
            print(f"{looser.name} lost the game")
        # reset after game
        self.__reset_after_game()

    def __play_half(self, is_final: bool):
        # play phase 1
        phase_result = "running"
        while phase_result == "running":
            phase_result = self.__play_phase_1()
        # check for schock-out or single player gets all cups
        if phase_result == "cancelled_half":
            self.__reset_after_half()
            return
        # set in game to false for all players with no cups after phase 1
        if not is_final:
            print("Following players leaves the half: ")
            for p in self.__list_of_players:
                if p.cups == 0:
                    p.in_game = False
                    print(f"{p.name}")

        # play phase 2
        phase_result = "running"
        while phase_result == "running":
            phase_result = self.__play_phase_2()

        self.__reset_after_half()

    def __play_phase_1(self):
        best, worst = self.__play_round()
        # check for "Schock-out"
        if best.current_throw.get_rank() == 5:
            worst.half_lost = True
            # also rotate players globally
            self.__list_of_players = rotate(self.__list_of_players, self.__list_of_players.index(worst))
            print(f"{best.name} throws schock-out!!!")
            print(f"{worst.name} lost half.")
            return "cancelled_half"
        # check if there are enough cups
        subtracted_cups = best.current_throw.get_cup_score() if best.current_throw.get_cup_score() <= self.__currently_cups_middle else self.__currently_cups_middle
        # substrate cups from the "middle"
        self.__currently_cups_middle -= subtracted_cups
        # add cups to looser
        worst.cups += subtracted_cups
        # also rotate players globally
        self.__list_of_players = rotate(self.__list_of_players, self.__list_of_players.index(worst))
        print(f"{best.name} throws best throw with: {best.current_throw}")
        print(f"{worst.name} got {subtracted_cups} cups.")
        print(f"Remaining cups in middle: {self.__currently_cups_middle}")
        # check if there are any cups in middle
        # if not, finish phase 1
        if self.__currently_cups_middle == 0:
            if worst.cups == self.__number_of_cups:
                print(f"{worst.name} got all cups and lost half.")
                worst.half_lost = True
                return "cancelled_half"
            else:
                return "cancelled"
        else:
            return "running"

    def __play_phase_2(self):
        best, worst = self.__play_round()
        # check for "Schock-out"
        if best.current_throw.get_rank() == 5:
            worst.half_lost = True
            # also rotate players globally
            self.__list_of_players = rotate(self.__list_of_players, self.__list_of_players.index(worst))
            print(f"{best.name} throws schock-out!!!")
            print(f"{worst.name} lost half.")
            return "cancelled_half"

        subtracted_cups = best.current_throw.get_cup_score() if best.current_throw.get_cup_score() <= best.cups else best.cups
        #  subtract cups from best
        best.cups -= subtracted_cups
        #  add cups to worst
        worst.cups += subtracted_cups
        # Shuffle list so the looser starts the next
        self.__list_of_players = rotate(self.__list_of_players, self.__list_of_players.index(worst))

        print(f"{best.name} throws best throw with: {best.current_throw}")
        print(f"{worst.name} got {subtracted_cups} cups from {best.name}.")
        print(f"Remaining cups in middle: {self.__currently_cups_middle}")
        # check if best has no cups -> delete from list
        if best.cups == 0:
            print(f"{best.name} has no cups anymore and left the half.")
            best.in_game = False
        # check if worst has all cups -> cancel phase 2
        if worst.cups == self.__number_of_cups:
            print(f"{worst.name} lost half")
            worst.half_lost = True
            return "cancelled"
        else:
            return "running"

    def __play_round(self):
        currently_worst_player = None
        currently_best_player = None
        # enter throw for each player
        for p in self.__list_of_players:
            # check if player in game
            if not p.in_game:  # if not, take next player
                continue
            # enter throw for current player
            print(f"enter throw for {p}: ")
            # validate throw entry
            entry = ""
            while entry == "":
                temp = str(input())
                if throw_entry_valid(temp):
                    entry = temp
                else:
                    print("Not a valid throw! try again...")
            #  save throw to player
            p.set_current_throw(int(entry[0]), int(entry[1]), int(entry[2]))
            # set first player best and worst
            if currently_best_player is None and currently_worst_player is None:
                currently_best_player = p
                currently_worst_player = p
            # check if it is currently the best throw
            elif not p.current_throw.is_lower(currently_best_player.current_throw):
                currently_best_player = p
            # check if it is currently the worst throw
            elif p.current_throw.is_lower(currently_worst_player.current_throw):
                currently_worst_player = p

        return currently_best_player, currently_worst_player

    def __reset_after_half(self):
        # reset cups middle
        self.__currently_cups_middle = self.__number_of_cups
        # reset cups of players
        for p in self.__list_of_players:
            p.in_game = True
            p.cups = 0

    def __reset_after_game(self):
        # reset cups middle
        self.__currently_cups_middle = self.__number_of_cups
        # reset cups of players
        for p in self.__list_of_players:
            p.in_game = True
            p.cups = 0
            p.half_lost = False
            p.current_throw = None


"""
Class representing a player
"""


class Player:

    def __init__(self, p_name: str):
        self.name = p_name
        self.cups = 0
        self.in_game = True
        self.half_lost = False
        self.current_throw: Throw = None

    def set_current_throw(self, w1: int, w2: int, w3: int):
        self.current_throw = Throw(w1, w2, w3)

    def __repr__(self):
        return f'Name: {self.name}; current cups: {self.cups}'


"""
Class representing a dice throw of a player
"""


class Throw:
    def __init__(self, t1: int, t2: int, t3: int):
        # check if dice values are between 1 and 6
        if t1 not in range(1, 7) or t2 not in range(1, 7) or t3 not in range(1, 7):
            raise Exception("Error: Invalid dice value")
        self.dice_value_list = sorted([t1, t2, t3], reverse=True)

    def get_cup_score(self):
        w1 = self.dice_value_list[0]
        w2 = self.dice_value_list[1]
        w3 = self.dice_value_list[2]
        # "Schock-out"
        if w1 == w2 == w3 == 1:
            return 13
        # "Schock-x"
        elif w2 == w3 == 1:
            return w1
        # "Admiral"
        elif w1 == w2 == w3:
            return 3
        # "Strasse"
        elif w2 == w1 - 1 and w3 == w2 - 1:
            return 2
        # "einfacher Wurf"
        else:
            return 1

    def get_rank(self):
        w1 = self.dice_value_list[0]
        w2 = self.dice_value_list[1]
        w3 = self.dice_value_list[2]
        # "Schock-out"
        if w1 == w2 == w3 == 1:
            return 5
        # "Schock-x"
        elif w2 == w3 == 1:
            return 4
        # "Admiral"
        elif w1 == w2 == w3:
            return 3
        # "Strasse"
        elif w2 == w1 - 1 and w3 == w2 - 1:
            return 2
        # "einfacher Wurf"
        else:
            return 1

    def is_lower(self, previous_throw):
        if not type(previous_throw) is Throw:
            raise Exception("Error: previous_throw is not of type Throw")
        # check rank
        if self.get_rank() != previous_throw.get_rank():
            return self.get_rank() < previous_throw.get_rank()
        # check first dice
        elif self.dice_value_list[0] != previous_throw.dice_value_list[0]:
            return self.dice_value_list[0] < previous_throw.dice_value_list[0]
        # check second dice
        elif self.dice_value_list[1] != previous_throw.dice_value_list[1]:
            return self.dice_value_list[1] < previous_throw.dice_value_list[1]
        # check third dice; if throws are completely equal, the current throw is lower than the previous one
        else:
            return self.dice_value_list[2] <= previous_throw.dice_value_list[2]

    def __repr__(self):
        return f"{self.dice_value_list[0]}-{self.dice_value_list[1]}-{self.dice_value_list[2]}"


# Helper


def throw_entry_valid(entry: str):
    if not len(entry) == 3:
        return False
    for e in entry:
        if not e.isdigit or int(e) not in range(1, 7):
            return False
    return True


def rotate(l: list, n: int):
    return l[n:] + l[:n]


# Test Region


s = SchockenGame()
playing = True
while playing:
    s.start_game()
    print("For playing another round enter 'y'")
    if not str(input()) == "y":
        playing = False
