#!/usr/bin/env python3
import sys

import Client
import Proposer
import Acceptor
import Learner

#########################################

#Parses configuration file and returns network dictionary
def get_network(cfgpath):
    network = {}
    with open(cfgpath, 'r') as cfgfile:
        for line in cfgfile:
            (role, host, port) = line.split()
            network[role] = {'ip': host, 'port': int(port)}

    return network

#########################################

if __name__ == '__main__':
    #parse command line arguments
    cfgpath = sys.argv[1]
    role = sys.argv[2]
    id = int(sys.argv[3])

    #create network address dictionary
    network = get_network(cfgpath)
    max_acceptors = 3

    #Start process for requested node
    print(f'Initializing agent: [{role} : {id}]')
    if role == 'acceptor':
        acceptors = network['acceptors']
        acceptor = Acceptor.Acceptor(
            role=role,
            address=(id, acceptors['ip'], acceptors['port']),
            network=network
        )
        
        acceptor.start() #spawns seperate process and kills current
    elif role == 'proposer':
        proposers = network['proposers']
        proposer = Proposer.Proposer(
            role=role,
            address=(id, proposers['ip'], proposers['port']),
            network=network,
            max_acceptors=max_acceptors
        )

        proposer.start()
    elif role == 'learner':
        learners = network['learners']
        learner = Learner.Learner(
            role=role,
            address=(id, learners['ip'], learners['port']),
            network=network
        )

        learner.start()
    elif role == 'client':
        clients = network['clients']
        client = Client.Client(
            role=role,
            address=(id, clients['ip'], clients['port']),
            network=network
        )

        #runs in current process (with commandline input)
        client.run()
