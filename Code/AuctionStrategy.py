
bidders_purpose_mixed_strategy = {}


def evaluate_purpose(player_id, numberbidders, wincondition, artists, rd, itemsinauction, winnerarray):
    purpose_score = {}
    if player_id in winnerarray:
        purpose = itemsinauction[winnerarray.index(player_id)]
        for art in artist:
            if art == purpose:
            purpose_score[art] = 1.0
            else:
            purpose_score[art] = 0.0

    else:
        least_win_round = 2*numberbidders+1
        art_count = {}
        for art in artist:
            art_count[art] = 0
            purpose_score[art] = 0.0

        inital_score = len(itemsinauction) - rd - 1
        sum_score = 0.0
        for i in range(rd, len(itemsinauction)):
            item = itemsinauction[i]
            if art_count[item] <= least_win_round:
                purpose_score[item] += inital_score - i
                inital_score += inital_score - i
            else:
                search_flag = 0
                for art in artists:
                if art_count[art] == least_win_round:
                    search_flag += 1

                if search_flag == len(artists):
                    break

        for art in artists:
            purpose_score[art] = purpose_score[art]/sum_score

    return purpose_score


single_round_winrate = 0.0


def simulate_prob_tree(prob, prob_bid_count, index):


def fiction_play(numberbidders, wincondition, artists, values, rd, itemsinauction, winnerarray, winneramount, mybidderid, players, standings, winnerpays):
    for i in range(numberbidders):
        if palyer[i] != mybidderid:
            bidders_purpose_mixed_strategy[palyer[i]] = evaluate_purpose(
                palyer[i], numberbidders, wincondition, artists, rd, itemsinauction, winnerarray)


def worst_case_best_respond_strategy(numberbidders, wincondition, artists, values, rd, itemsinauction, winnerarray, winneramount, mybidderid, players, standings, winnerpays):
    if rd == 0:
    fiction_play(numberbidders, wincondition, artists, values, rd, itemsinauction,
                 winnerarray, winneramount, mybidderid, players, standings, winnerpays)
