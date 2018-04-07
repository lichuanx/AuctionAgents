from AuctionServer import AuctionServer

host = "localhost"
ports = 8020
numbidders = 2
neededtowin = 3
itemtypes = ['Picasso', 'Van_Gogh', 'Rembrandt', 'Da_Vinci']
#numitems = {'Picasso': 50, 'Van_Gogh' : 40, 'Rembrandt' : 30, 'Da_Vinci' : 10}
numitems = {}
auction_size = 200
budget = 1000
values = {'Picasso': 1, 'Van_Gogh' : 5, 'Rembrandt' : 10, 'Da_Vinci' : 20}
announce_order = True
winner_pays = 0

auctionroom = AuctionServer(host=host, ports=ports, numbidders=numbidders, neededtowin=neededtowin,
itemtypes=itemtypes, numitems=numitems, auction_size=auction_size, budget=budget, values=values, announce_order=announce_order, winner_pays=winner_pays)

auctionroom.announce_auction()

auctionroom.run_auction()
