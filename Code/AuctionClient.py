import socket
import random
import math


def evaluate_sequence(numberbidders, wincondition, artists, rd, itemsinauction, potential_competitors):
    purpose_score = {}
    least_win_round = wincondition
    art_count = {}
    for art in artists:
        art_count[art] = 0
        purpose_score[art] = 0.0

    sum_score = 0
    inital_score = len(itemsinauction) - rd - 1
    for i in range(rd, len(itemsinauction)):
        item = itemsinauction[i]
        rate = 1/(potential_competitors[item]+1)
        if art_count[item] < least_win_round:
            art_count[item] += 1
        elif art_count[item] == least_win_round:
            purpose_score[item] += (inital_score)*math.pow(rate, (i-rd+1))
            sum_score += (inital_score)*math.pow(rate, (i-rd+1))
        else:
            search_flag = 0
            for art in artists:
                if art_count[art] == least_win_round:
                    search_flag += 1

            if search_flag == len(artists):
                break

    for art in artists:
        purpose_score[art] = purpose_score[art]/sum_score

    print(least_win_round)
    return purpose_score


def evaluate_purpose(players, artists, itemsinauction, winnerarray, mybidderid):
    purpose_score = {}
    for art in artists:
        purpose_score[art] = 0.0

    for player_id in players:
        if player_id != mybidderid:
            if player_id in winnerarray:
                purpose = itemsinauction[winnerarray.index(player_id)]
                for art in artists:
                    if art == purpose:
                        purpose_score[art] += 1.0
                    else:
                        purpose_score[art] += 0.0
            else:
                for art in artists:
                    purpose_score[art] += 1.0

    return purpose_score


def best_next_sequence_strategy(numberbidders, wincondition, artists, values, rd, itemsinauction, winnerarray, winneramount, mybidderid, players, standings, winnerpays):
    curr_item = itemsinauction[rd]

    if mybidderid in winnerarray:
        best_choice = itemsinauction[winnerarray.index(mybidderid)]
        if best_choice == curr_item and standings[mybidderid][best_choice] == (wincondition-1):
            return standings[mybidderid]['money']
        elif best_choice == curr_item and standings[mybidderid][best_choice] > 0:
            return math.floor(standings[mybidderid]['money']/(wincondition-standings[mybidderid][best_choice]))
        else:
            return 0
    else:

        potential_competitors = evaluate_purpose(
            players, artists, itemsinauction, winnerarray, mybidderid)

        sequence_priority = evaluate_sequence(
            numberbidders, wincondition, artists, rd, itemsinauction, potential_competitors)

        max_prob = 0.0
        for art in sequence_priority:
            if sequence_priority[art] > max_prob:
                best_choice = art
                max_prob = sequence_priority[art]

        print(sequence_priority)
        if best_choice == curr_item:
            return math.floor(standings[mybidderid]['money']/wincondition)

        else:
            return 0


def second_highest_valuation_strategy(numberbidders, wincondition, artists, values, rd, itemsinauction, winnerarray, winneramount, mybidderid, players, standings, winnerpays):
    curr_item = itemsinauction[rd]

    my_valuation = math.ceil(
        standings[mybidderid]["money"]/(wincondition-standings[mybidderid][curr_item]))

    other_max_valuation = 0
    other_min_valuation = -1
    for player in players:
        if player != mybidderid:
            private_va = math.floor(
                standings[player]["money"]/(wincondition-standings[player][curr_item]))
            if private_va > other_max_valuation:
                other_max_valuation = private_va
            if other_min_valuation < 0:
                other_min_valuation = private_va
            elif private_va < other_min_valuation:
                other_min_valuation = private_va

    if my_valuation >= other_max_valuation:
        if wincondition-standings[mybidderid][curr_item] == 1:
            return standings[mybidderid]["money"]
        else:
            return other_max_valuation
    elif other_min_valuation*(wincondition-standings[mybidderid][curr_item]) < standings[mybidderid]["money"]:
        return other_min_valuation
    else:
        return int(standings[mybidderid]["money"]/10)


def first_price_highest_value_strategy(numberbidders, wincondition, artists, values, rd, itemsinauction, winnerarray, winneramount, mybidderid, players, standings, winnerpays):
    curr_item = itemsinauction[rd]

    initial_budget = standings[mybidderid]["money"]

    total_score = 0
    half_total_score = 0
    for art in artists:
        total_score += artists[art]*values[art]

    half_total_score = total_score/2

    remain_score = total_score
    for i in range(0, rd):
        remain_score -= values[itemsinauction[i]]
    
    already_gain_score = 0
    for art in artists:
      already_gain_score += standings[mybidderid][art]*values[art]

    money_per_score = initial_budget/(half_total_score-already_gain_score)
    
    print(initial_budget)
    players_private_values = {}
    if remain_score > half_total_score:
        return int(values[curr_item]*money_per_score)
    else:
        for player in players:
            wanted_score = half_total_score
            gained_score = 0
            for art in artists:
                gained_score += standings[player][art]*values[art]
            wanted_score = wanted_score - gained_score
            players_private_values[player] = standings[player]["money"] / wanted_score 
        
        second_highest = 0
        my_valuation = 0
        for player in players:
          if player == mybidderid:
            my_valuation = players_private_values[player]
          elif players_private_values[player] > second_highest:
            second_highest = players_private_values[player]

          if my_valuation >= second_highest:
            return int(values[curr_item]*second_highest+1)
          else:
            return int(values[curr_item]*my_valuation)

def always_pay_my_valua_strategy(numberbidders, wincondition, artists, values, rd, itemsinauction, winnerarray, winneramount, mybidderid, players, standings, winnerpays):
    curr_item = itemsinauction[rd]
    initial_budget = standings[mybidderid]["money"]

    total_score = 0
    half_total_score = 0
    for art in artists:
        total_score += artists[art]*values[art]

    half_total_score = total_score/2

    remain_score = total_score
    for i in range(0, rd):
        remain_score -= values[itemsinauction[i]]
    
    already_gain_score = 0
    for art in artists:
      already_gain_score += standings[mybidderid][art]*values[art]
    if already_gain_score > half_total_score:
      return int(initial_budget*random.random()+1)
    money_per_score = 0
    if remain_score < half_total_score-already_gain_score:
        money_per_score = initial_budget/remain_score
    else:
        money_per_score = initial_budget/(half_total_score-already_gain_score)
    return int(values[curr_item]*money_per_score)


class AuctionClient(object):
    """A client for bidding with the AucionRoom"""

    def __init__(self, host="localhost", port=8020, mybidderid=None, verbose=False):
        self.verbose = verbose
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        forbidden_chars = set(""" '".,;:{}[]()""")
        if mybidderid:
            if len(mybidderid) == 0 or any((c in forbidden_chars) for c in mybidderid):
                print(
                    """mybidderid cannot contain spaces or any of the following: '".,;:{}[]()!""")
                raise ValueError
            self.mybidderid = mybidderid
        else:
            # this is the only thing that distinguishes the clients
            self.mybidderid = raw_input("Input team / player name : ").strip()
            while len(self.mybidderid) == 0 or any((c in forbidden_chars) for c in self.mybidderid):
                self.mybidderid = raw_input(
                    """You input an empty string or included a space  or one of these '".,;:{}[]() in your name which is not allowed (_ or / are all allowed)\n for example Emil_And_Nischal is okay\nInput team / player name: """).strip()
        self.sock.send(self.mybidderid.encode("utf-8"))

        data = self.sock.recv(5024).decode('utf_8')
        x = data.split(" ")
        if self.verbose:
            print("Have received response of %s" % ' '.join(x))
        if(x[0] != "Not" and len(data) != 0):
            self.numberbidders = int(x[0])
            if self.verbose:
                print("Number of bidders: %d" % self.numberbidders)
            self.numtypes = int(x[1])
            if self.verbose:
                print("Number of types: %d" % self.numtypes)
            self.numitems = int(x[2])
            if self.verbose:
                print("Items in auction: %d" % self.numitems)
            self.maxbudget = int(x[3])
            if self.verbose:
                print("Budget: %d" % self.maxbudget)
            self.neededtowin = int(x[4])
            if self.verbose:
                print("Needed to win: %d" % self.neededtowin)
            self.order_known = "True" == x[5]
            if self.verbose:
                print("Order known: %s" % self.order_known)
            self.auctionlist = []
            self.winnerpays = int(x[6])
            if self.verbose:
                print("Winner pays: %d" % self.winnerpays)
            self.values = {}
            self.artists = {}
            order_start = 7
            if self.neededtowin > 0:
                self.values = None
                for i in range(7, 7+(self.numtypes*2), 2):
                    self.artists[x[i]] = int(x[i+1])
                    order_start += 2
                if self.verbose:
                    print("Item types: %s" % str(self.artists))
            else:
                for i in range(7, 7+(self.numtypes*3), 3):
                    self.artists[x[i]] = int(x[i+1])
                    self.values[x[i]] = int(x[i+2])
                    order_start += 3
                if self.verbose:
                    print("Item types: %s" % str(self.artists))
                    print("Values: %s" % str(self.values))

            if self.order_known:
                for i in range(order_start, order_start+self.numitems):
                    self.auctionlist.append(x[i])
                if self.verbose:
                    print("Auction order: %s" % str(self.auctionlist))

        self.sock.send('connected '.encode("utf-8"))

        data = self.sock.recv(5024).decode('utf_8')
        x = data.split(" ")
        if x[0] != 'players':
            print("Did not receive list of players!")
            raise IOError
        if len(x) != self.numberbidders + 2:
            print("Length of list of players received does not match numberbidders!")
            raise IOError
        if self.verbose:
            print("List of players: %s" % str(' '.join(x[1:])))

        self.players = []

        for player in range(1, self.numberbidders + 1):
            self.players.append(x[player])

        self.sock.send('ready '.encode("utf-8"))

        self.standings = {name: {artist: 0 for artist in self.artists}
                          for name in self.players}
        for name in self.players:
            self.standings[name]["money"] = self.maxbudget

    def play_auction(self):
        winnerarray = []
        winneramount = []
        done = False
        while not done:
            data = self.sock.recv(5024).decode('utf_8')
            x = data.split(" ")
            if x[0] != "done":
                if x[0] == "selling":
                    currentitem = x[1]
                    if not self.order_known:
                        self.auctionlist.append(currentitem)
                    if self.verbose:
                        print("Item on sale is %s" % currentitem)
                    bid = self.determinebid(self.numberbidders, self.neededtowin, self.artists, self.values, len(
                        winnerarray), self.auctionlist, winnerarray, winneramount, self.mybidderid, self.players, self.standings, self.winnerpays)
                    if self.verbose:
                        print("Bidding: %d" % bid)
                    self.sock.send(str(bid).encode("utf-8"))
                    data = self.sock.recv(5024).decode('utf_8')
                    x = data.split(" ")
                    if x[0] == "draw":
                        winnerarray.append(None)
                        winneramount.append(0)
                    if x[0] == "winner":
                        winnerarray.append(x[1])
                        winneramount.append(int(x[3]))
                        self.standings[x[1]][currentitem] += 1
                        self.standings[x[1]]["money"] -= int(x[3])
            else:
                done = True
                if self.verbose:
                    if self.mybidderid in x[1:-1]:
                        print("I won! Hooray!")
                    else:
                        print("Well, better luck next time...")
        self.sock.close()

    def determinebid(self, numberbidders, wincondition, artists, values, rd, itemsinauction, winnerarray, winneramount, mybidderid, players, standings, winnerpays):
        '''You have all the variables and lists you could need in the arguments of the function,
        these will always be updated and relevant, so all you have to do is use them.
        Write code to make your bot do a lot of smart stuff to beat all the other bots. Good luck,
        and may the games begin!'''

        '''
        numberbidders is an integer displaying the amount of people playing the auction game.

        wincondition is an integer. A postiive integer means that whoever gets that amount of a single type
        of item wins, whilst 0 means each itemtype will have a value and the winner will be whoever accumulates the
        highest total value before all items are auctioned or everyone runs out of funds.

        artists will be a dict of the different item types as keys with the total number of that type on auction as elements.

        values will be a dict of the item types as keys and the type value if wincondition == 0. Else value == None.

        rd is the current round in 0 based indexing.

        itemsinauction is a list where at index "rd" the item in that round is being sold is displayed. Note that it will either be as long as the sum of all the number of the items (as in "artists") in which case the full auction order is pre-announced and known, or len(itemsinauction) == rd+1, in which case it only holds the past and current items, the next item to be auctioned is unknown.

        winnerarray is a list where at index "rd" the winner of the item sold in that round is displayed.

        winneramount is a list where at index "rd" the amount of money paid for the item sold in that round is displayed.

        example: I will now construct a sentence that would be correct if you substituted the outputs of the lists:
        In round 5 winnerarray[4] bought itemsinauction[4] for winneramount[4] pounds/dollars/money unit.

        mybidderid is your name: if you want to reference yourself use that.

        players is a lists containing all the names of the current players.

        standings is a set of nested dictionaries (standings is a dictionary that for each person has another dictionary
        associated with them). standings[name][artist] will return how many paintings "artist" the player "name" currently has.
        standings[name]['money'] (remember quotes for string, important!) returns how much money the player "name" has left.

            standings[mybidderid] is the information about you.
            I.e., standings[mybidderid]['money'] is the budget you have left.

        winnerpays is an integer representing which bid the highest bidder pays. If 0, the highest bidder pays their own bid,
        but if 1, the highest bidder instead pays the second highest bid (and if 2 the third highest, ect....). Note though that if you win, you always pay at least 1 (even if the second-highest was 0).

        Don't change any of these values, or you might confuse your bot! Just use them to determine your bid.
        You can also access any of the object variables defined in the constructor (though again don't change these!), or declare your own to save state between determinebid calls if you so wish.

        determinebid should return your bid as an integer. Note that if it exceeds your current budget (standings[mybidderid]['money']), the auction server will simply set it to your current budget.

        Good luck!
        '''

        # Game 1: First to buy wincondition of any artist wins, highest bidder pays own bid, auction order known.
        if (wincondition > 0) and (winnerpays == 0) and self.order_known:
            return self.first_bidding_strategy(numberbidders, wincondition, artists, values, rd, itemsinauction, winnerarray, winneramount, mybidderid, players, standings, winnerpays)

        # Game 2: First to buy wincondition of any artist wins, highest bidder pays own bid, auction order not known.
        if (wincondition > 0) and (winnerpays == 0) and not self.order_known:
            return self.second_bidding_strategy(numberbidders, wincondition, artists, values, rd, itemsinauction, winnerarray, winneramount, mybidderid, players, standings, winnerpays)

        # Game 3: Highest total value wins, highest bidder pays own bid, auction order known.
        if (wincondition == 0) and (winnerpays == 0) and self.order_known:
            return self.third_bidding_strategy(numberbidders, wincondition, artists, values, rd, itemsinauction, winnerarray, winneramount, mybidderid, players, standings, winnerpays)

        # Game 4: Highest total value wins, highest bidder pays second highest bid, auction order known.
        if (wincondition == 0) and (winnerpays == 1) and self.order_known:
            return self.fourth_bidding_strategy(numberbidders, wincondition, artists, values, rd, itemsinauction, winnerarray, winneramount, mybidderid, players, standings, winnerpays)

        # Though you will only be assessed on these four cases, feel free to try your hand at others!
        # Otherwise, this just returns a random bid.
        return self.random_bid(standings[mybidderid]['money'])

    def random_bid(self, budget):
        """Returns a random bid between 1 and left over budget."""
        return int(budget*random.random()+1)

    def first_bidding_strategy(self, numberbidders, wincondition, artists, values, rd, itemsinauction, winnerarray, winneramount, mybidderid, players, standings, winnerpays):
        """Game 1: First to buy wincondition of any artist wins, highest bidder pays own bid, auction order known."""

        # Currently just returns a random bid
        price = best_next_squence_strategy(numberbidders, wincondition, artists, values, rd,
                                           itemsinauction, winnerarray, winneramount, mybidderid, players, standings, winnerpays)
        curr_item = itemsinauction[rd]
        print("myrobot offer: ", curr_item, price)
        return price

    def second_bidding_strategy(self, numberbidders, wincondition, artists, values, rd, itemsinauction, winnerarray, winneramount, mybidderid, players, standings, winnerpays):
        """Game 2: First to buy wincondition of any artist wins, highest bidder pays own bid, auction order not known."""

        price = second_highest_valuation_strategy(numberbidders, wincondition, artists, values, rd,
                                                  itemsinauction, winnerarray, winneramount, mybidderid, players, standings, winnerpays)
        curr_item = itemsinauction[rd]
        print("myrobot offer: ", curr_item, price)
        return price

    def third_bidding_strategy(self, numberbidders, wincondition, artists, values, rd, itemsinauction, winnerarray, winneramount, mybidderid, players, standings, winnerpays):
        """Game 3: Highest total value wins, highest bidder pays own bid, auction order known."""
        price = first_price_highest_value_strategy(numberbidders, wincondition, artists, values, rd, itemsinauction, winnerarray, winneramount, mybidderid, players, standings, winnerpays)
        curr_item = itemsinauction[rd]
        print("myrobot offer: ", curr_item, price)
        return price

    def fourth_bidding_strategy(self, numberbidders, wincondition, artists, values, rd, itemsinauction, winnerarray, winneramount, mybidderid, players, standings, winnerpays):
        """Game 4: Highest total value wins, highest bidder pays second highest bid, auction order known."""

        price = always_pay_my_valua_strategy(numberbidders, wincondition, artists, values, rd, itemsinauction, winnerarray, winneramount, mybidderid, players, standings, winnerpays)
        curr_item = itemsinauction[rd]
        print("myrobot offer: ", curr_item, price, standings[mybidderid]["money"])
        return price
