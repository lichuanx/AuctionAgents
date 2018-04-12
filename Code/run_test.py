from multiprocessing import Process
from AuctionClient import AuctionClient
from AuctionServer import AuctionServer
from TestClient import TestClient
import time

HOST = "localhost"
ports = 8060
numbidders = 3
numtest = 1
neededtowin = 0
itemtypes = ['Picasso', 'Van_Gogh', 'Rembrandt', 'Da_Vinci']
#numitems = {'Picasso': 10, 'Van_Gogh' : 10, 'Rembrandt' : 10, 'Da_Vinci' : 10}
numitems = {}
auction_size = 200
budget = 1000
values = {'Picasso': 1, 'Van_Gogh' : 5, 'Rembrandt' : 10, 'Da_Vinci' : 20}
announce_order = True
winner_pays = 0

args = (HOST, ports, numbidders, neededtowin, itemtypes, numitems, auction_size, budget, values, announce_order, winner_pays
, )

verbose = False


def run_auction(host, ports, numbidders, neededtowin, itemtypes, numitems, auction_size, budget, values, announce_order, winner_pays):
    auctionroom = AuctionServer(host=host, ports=ports, numbidders=numbidders, neededtowin=neededtowin,
    itemtypes=itemtypes, numitems=numitems, auction_size=auction_size, budget=budget, values=values, announce_order=announce_order, winner_pays=winner_pays)
    auctionroom.announce_auction()
    auctionroom.run_auction()


def run_client(port, bidderid, verbose, test):
    if test:
        bidbot =TestClient(port=port, mybidderid=bidderid, verbose=verbose)
    else:
        bidbot = AuctionClient(port=port, mybidderid=bidderid, verbose=verbose)
    bidbot.play_auction()


if __name__=='__main__':
     print("Starting AuctionServer")
     auctionserver = Process(target = run_auction, args = args)
     auctionserver.start()
     time.sleep(2)
     bidbots = []
     for i in range(numbidders):
         p = ports + i
         if i < numtest:
             name = "Test" + str(i+1)
         else:
             name = "Bidbot" + str(i+1-numtest)
         print("Starting AuctionClient on port %d with name %s" % (p, name))
         b = Process(target = run_client, args = (p, name, verbose, i < numtest))
         bidbots.append(b)
         b.start()
         time.sleep(1)