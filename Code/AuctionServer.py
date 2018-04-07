import socket
import random
import select
import time

class AuctionServer(object):
    def __init__(self, host="localhost", ports=8020, numbidders=2, neededtowin=3, itemtypes=['Picasso', 'Van_Gogh', 'Rembrandt', 'Da_Vinci'], numitems={}, auction_size=200, budget=1000, values={}, announce_order=True, winner_pays=0):
        self.host = host
        self.numbidders = numbidders
        if type(ports) == int:
            self.ports = [i+ports for i in range(numbidders)]
        else:
            self.ports = ports
        sockets = []

        if len(self.ports) != self.numbidders:
            print("Need same number of ports as bidders!")
            raise ValueError

        self.neededtowin = neededtowin
        self.itemtypes = itemtypes
        self.numitems = numitems
        self.auction_size = auction_size
        self.budget = budget
        self.values = values
        self.announce_order = announce_order
        self.winner_pays = winner_pays

        if not self.numitems:
            if self.auction_size <= 0:
                print("Please give a positive auction_size when not manually setting numitems!")
                raise ValueError
            self.numitems = {i : 0 for i in self.itemtypes}
        else:
            if set(itemtypes) != set(numitems.keys()):
                print("Need keys of numitems to match itemtypes!")
                raise ValueError
            if self.auction_size != 0:
                print("Please set auction size to 0 when manually setting numitems!")
                raise ValueError

        if not self.values and self.neededtowin <= 0:
            print("Please give a positive needed to win, or set values!")
            raise ValueError

        if self.neededtowin <= 0 and (set(self.values.keys()) != set(itemtypes)):
            print ("Please give a postive neededtowin or set values for all itemtypes!")
            raise ValueError

        if self.winner_pays >= self.numbidders:
            print ("Please set winner_pays to be less than numbidders!")
            raise ValueError

        if self.auction_size == 0:
            for i in self.numitems:
                self.auction_size += self.numitems[i]

        for i in range(numbidders):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind((self.host, self.ports[i]))
            sockets.append(sock)

        self.conns = []
        for sock in sockets:
            sock.listen(1)
            conn, addr = sock.accept()
            self.conns.append(conn)
            #print ("Address:", addr)


        self.auctionlist = []

        to_auction = [i for i in self.numitems.keys() if self.numitems[i] > 0]
        sellingcount = 0

        if len(to_auction) == 0:
            while(sellingcount < self.auction_size):
              x = self.itemtypes[int((len(self.itemtypes))*random.random())]
              self.auctionlist.append(x)
              self.numitems[x] += 1
              sellingcount += 1
        else:
            numselling = {i : 0 for i in self.itemtypes}
            while(sellingcount < self.auction_size):
              x = to_auction[int((len(to_auction))*random.random())]
              self.auctionlist.append(x)
              numselling[x] += 1
              if numselling[x] == self.numitems[x]:
                  to_auction.remove(x)
              sellingcount += 1

    def announce_auction(self):
        listtosend = str(self.numbidders) + ' ' + str(len(self.itemtypes)) + ' ' + str(self.auction_size) + ' ' + str(self.budget) + ' ' + str(self.neededtowin) + ' ' + str(self.announce_order) + ' ' + str(self.winner_pays) + ' '

        if self.values and self.neededtowin <= 0:
            for i, v in self.values.items():
                listtosend += str(i) + ' ' + str(self.numitems[i]) + ' ' + str(v) + ' '
        else:
            for i in self.itemtypes:
                listtosend += str(i) + ' ' + str(self.numitems[i]) + ' '

        if self.announce_order:
            listtosend += ' '.join(self.auctionlist)

        self.bidderids = []
        self.porttobidders = {}
        for conn in self.conns:
            socks,write_ready,exceptready = select.select([conn],[conn],[])
            for s in socks:
                data = s.recv(1024).decode('utf_8')
                indata = data.split(" ")
                if indata[0] in self.bidderids:
                    print("Already have a bidder called %s, please ensure all biddierids are unique!" % indata[0])
                    raise ValueError
                #print s.getpeername()
                self.porttobidders[s.getpeername()] = indata[0]
                self.bidderids.append(indata[0])
                print("%s has joined the game" % indata[0])
                s.send(listtosend.encode("utf-8"))

        for conn in self.conns:
            read_ready,socks,exceptready = select.select([conn],[conn],[])
            stringtosend = 'players '
            for name in self.bidderids:
              stringtosend += name + ' '
            for s in socks:
                data = s.recv(1024).decode('utf_8')
                if data != 'connected ':
                    print("Did not receive connect signal from %s" % self.porttobidders[s.getpeername()])
                    raise IOError
                s.send(stringtosend.encode("utf-8"))

        for conn in self.conns:
            socks,write_ready,exceptready = select.select([conn],[],[])
            for s in socks:
                data = s.recv(1024).decode('utf_8')
                if data != 'ready ':
                    print("Did not receive ready signal from %s" % self.porttobidders[s.getpeername()])
                    raise IOError

        print("Everyone has joined and is ready, let's go!")
        time.sleep(3)
        self.standings = {name: {artist : 0 for artist in self.itemtypes} for name in self.bidderids}
        for name in self.bidderids:
            self.standings[name]["money"] = self.budget

    def run_auction(self):
        current_round = 0
        done = False
        won = None
        while not done:
            if current_round >= self.auction_size:
                done = True
                break
            bids = {}
            currentitem = self.auctionlist[current_round]
            print("Selling %s" % currentitem)
            for conn in self.conns:
                inputready,socks,exceptready = select.select([],[conn],[])
                stringtosend = 'selling ' + currentitem + ' '
                for s in socks:
                    s.send(stringtosend.encode("utf-8"))
            for conn in self.conns:
                socks,outputready,exceptready = select.select([conn],[],[])
                for s in socks:
                    data = s.recv(1024).decode('utf_8')
                    indata = data.split(" ")
                    attempted_bid = int(indata[0])
                    pname = self.porttobidders[s.getpeername()]
                    if attempted_bid > self.standings[pname]["money"]:
                        attempted_bid = self.standings[pname]["money"]
                    bids[pname] = attempted_bid
            #print(bids)
            sorted_bids = list(bids.items())
            sorted_bids.sort(key=lambda x : x[1],reverse=True)
            time.sleep(2)
            winners = [p for p in sorted_bids if p[1] == sorted_bids[0][1]]
            if winners[0][1] == 0:
                for conn in self.conns:
                    inputready,socks,exceptready = select.select([],[conn],[])
                    stringtosend = 'draw '
                    for s in socks:
                        s.send(stringtosend.encode("utf-8"))
                current_round += 1
                continue
            winner = random.choice(winners)[0]
            payment = sorted_bids[self.winner_pays][1]
            if payment <= 0:
                payment = 1
            print("%s wins the %s, and pays %d" % (winner, currentitem, payment))
            self.standings[winner][currentitem] += 1
            self.standings[winner]["money"] -= payment
            for conn in self.conns:
                inputready,socks,exceptready = select.select([],[conn],[])
                stringtosend = 'winner ' + winner + ' pays ' + str(payment) + ' '
                for s in socks:
                    s.send(stringtosend.encode("utf-8"))
            current_round += 1
            out_of_cash = True
            if self.neededtowin > 0:
                if self.standings[winner][currentitem] >= self.neededtowin:
                    won = winner
                    print("%s has won with %d %s!" % (winner, self.standings[winner][currentitem], currentitem))
                    done = True
            for name in self.bidderids:
                if not done:
                    if self.standings[name]["money"] > 0:
                        out_of_cash = False
                        break
            if not done and out_of_cash:
                print("Everyone's out of cash! Game over!")
                done = True

        time.sleep(2)
        if self.neededtowin == 0:
            player_values = {}
            for name in self.standings:
                player_values[name] = 0
                for artist in self.values:
                    player_values[name] += (self.standings[name][artist] * self.values[artist])
            sorted_values = list(player_values.items())
            sorted_values.sort(key=lambda x : x[1],reverse=True)
            winners = [p for p in sorted_values if p[1] == sorted_values[0][1]]
            won = []
            for winner in winners:
                print("%s has won with %d total value!" % winner)
                won.append(winner[0])

            # max_value = sorted_values[0][1]
            # for p in sorted_values:
            #     if p[1] == max_value:
            #         winners.append((p[0],p[1],standings[p[0]]["money"]))
            #     else:
            #         break
            # winners.sort(key=lambda x : x[2], reverse=True)
            # print("%s has won with %d total value and %d money left!" % winners[0])
            # won = winners[0][0]
        if won == None:
            won = "Nobody"
            print("Nobody managed to win, oh dear....")
        for conn in self.conns:
            inputready,socks,exceptready = select.select([],[conn],[])
            stringtosend = 'done '
            if type(won) == str:
                stringtosend += won + ' wins '
            if type(won) == list:
                stringtosend += ' '.join(won) + ' wins'
            for s in socks:
                s.send(stringtosend.encode("utf-8"))

        time.sleep(2)
        for conn in self.conns:
            conn.close()
