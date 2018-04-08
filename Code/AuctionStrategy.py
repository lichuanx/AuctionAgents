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


if __name__ == '__main__':
    xx = calculate_expectation(0.5, 4)
    print(xx)
