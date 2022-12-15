from multiprocessing import Process
import sys
import socket
import struct

import util 

class Agent(Process):
    """
        Agent Parent Class:
        1. Acts as specialized process with extra functions common to each
        component of the PAXOS algorithm.
        2. Initializes the I/O sockets at the address
        3. 
    """
    #initialize process from parameters
    def __init__(self, type, address, network):
        super.__init__(self)

        #get type: {Clients, Proposers, Acceptors, Learners}
        self.type = type

        #get address {pid, ip, port}
        self.pid = address[0]
        self.ip = address[1]
        self.port = address[2]

        #dictionary of adresses grouped by type
        #   {Clients: [], Proposers: [], Acceptors: [], Learners: []}
        self.nodes = network

        #Initialize sockets:


    #Start process: Inherited function from Process
    def run(self):

    
    #create a multicast socket listening to the address
    def mcast_receiver(self, hostport):
        #Creates a reciever socket for all incoming UDP messages
        self.recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

        #
        self.recv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.recv_sock.bind(hostport)

        #
        mcast_group = struct.pack("4sl", socket.inet_aton(hostport[0]), socket.INADDR_ANY)
        self.recv_sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mcast_group)

    #Creates a UDP socket for sending outgoing UDP multicast messages
    def mcast_sender(self):
        self.send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        
    def 