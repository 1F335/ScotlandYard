#!/bin/python3

import random
import copy
from .player import Player


class Game:
    def __init__(self, mr_x, detectives):
        self.detectives_ai = detectives
        self.mr_x_ai = mr_x
        self.boardmap = {}
        self.x_history = []
        self.detectives = []
        self.x = None
        self.load_board()
        self.round = 1
        self.turn = 0
        self.reveal_rounds = [3, 8, 13, 18, 24]

        startTickets = {"taxi": 10, "bus": 8, "underground": 4}

        startLocs = []
        with open("start_locations.txt", "r") as f:
            for line in f:
                startLocs.append(int(line.strip()))
        random.shuffle(startLocs)

        self.x = Player({"taxi": 100, "bus": 100, "underground": 100, "black": 5, "2x": 2}, startLocs[0], "X")

        names = ["A", "B", "C", "D", "E"]

        for n in range(len(names)):
            self.detectives.append(Player(dict(startTickets), startLocs[n + 1], names[n]))

        self.players = [self.x] + self.detectives.copy()

    def next_turn(self, is_player_move=False):
        turn = self.turn
        self.turn += 1


        if turn <= 0:
            # Mr. X's turn
            if (is_player_move):
                move = is_player_move
            else:
                move = self.mr_x_ai.play_move(copy.deepcopy(self.x), copy.deepcopy(self.detectives),
                                          copy.deepcopy(self.x_history))

            if move[0] == "2x":
                self.x.tickets["2x"] -= 1
                if self.x.tickets["2x"] < 0:
                    raise RuntimeError(
                        "Mr X: stop trying to be special - it isn't working.  attempted to use too many 2x tickets")
                self.perform_move(self.x, move[2])
                self.x_history.append((self.x.pos if self.round in self.reveal_rounds else None, move[2][1]))
                self.perform_move(self.x, move[3])
                self.x_history.append((self.x.pos if self.round in self.reveal_rounds else None, move[3][1]))
            else:
                self.perform_move(self.x, move)
                self.x_history.append((self.x.pos if self.round in self.reveal_rounds else None, move[1]))

            print("X Ledger is updated to ", self.x_history)

        else:
            # Detective's turn
            detective = self.detectives[turn - 1]

            if self.cant_move(detective):
                print("Detective {} can't move!".format(detective.name))
            else:
                if is_player_move:
                    move = is_player_move
                else:
                    move = self.detectives_ai.play_move(copy.deepcopy(detective), copy.deepcopy(self.detectives),
                                                copy.deepcopy(self.x_history))
                self.perform_move(detective, move)

        self.is_game_over()

        if self.turn >= 6:
            self.turn = 0
            self.round += 1

    def next_round(self):
        for i in range(6):
            self.next_turn()

    def perform_move(self, player, move):
        # check for legality of move
        if move[0] not in self.boardmap[player.pos][move[1]]:
            raise RuntimeError("{}: What kinda move is that??? move from {} to {} via {} ticket is illegal"
                               .format(player.name, player.pos, move[0], move[1]))
        if player is not self.x and any(move[0] == plr.pos for plr in self.detectives):
            raise RuntimeError(
                    "{}: This node ain't big enough for the both of us! node {} has two people".format(player.name, move[0]))
        player.pos = move[0]
        transport = move[1]
        player.tickets[transport] -= 1
        if player.tickets[transport] < 0:
            raise RuntimeError(
                "{} used a {} ticket they didn't have!".format(player.name, transport))

        print("{} moved to {} using {}".format(player.name, move[0], move[1]))

    def cant_move(self, player):
        for ticket in player.tickets.keys():
            if player.tickets[ticket] > 0 and ticket in self.boardmap[player.pos]:
                return False
        return True

    def is_game_over(self):
        detectives_win = any(self.x.pos == plr.pos for plr in self.detectives)
        x_wins = all(self.cant_move(plr) for plr in self.detectives)
        if detectives_win:
            print("The detectives win!")
            exit()
        if x_wins:
            print("Mr X wins!")
            exit()

    def load_board(self):
        with open("board_data.txt", "r") as f:
            for line in f:
                data = [a.strip() for a in line.split("|")]
                entry = {}
                if len(data) > 1 and data[1] != '':
                    entry["taxi"] = [int(a.strip()) for a in data[1].split(" ")]
                if len(data) > 2 and data[2] != '':
                    entry["bus"] = [int(a.strip()) for a in data[2].split(" ")]
                if len(data) > 3 and data[3] != '':
                    entry["underground"] = [int(a.strip()) for a in data[3].split(" ")]

                black_ticket = []
                for key in entry.keys():
                    black_ticket += entry[key]

                entry["black"] = black_ticket

                if len(data) > 4:
                    entry["black"] += [int(a.strip()) for a in data[4].split(' ')]

                if len(data) > 0:
                    self.boardmap[int(data[0])] = entry

