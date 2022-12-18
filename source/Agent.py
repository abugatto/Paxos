from multiprocessing import Process
import socket
import struct

import Message as msg

class Agent(Process):
    """
        Agent Parent Class:
        1. Acts as specialized process with extra functions common to each
        component of the PAXOS algorithm.
        2. Initializes the I/O sockets at the address
        3. Inherits self.run() from Process (called in new process from start())
        4. Has a virtual Update State function for each phase of Paxos
    """

    #initialize process parameters
    def __init__(self, role, address, network):
        super.__init__(self)

        #get role: {Clients, Proposers, Acceptors, Learners}
        self.role = role

        #get address {pid, ip, port}
        self.pid = address(0)
        self.ip = address(1)
        self.port = address(2)

        #dictionary of adresses grouped by role
        #   {Clients: [], Proposers: [], Acceptors: [], Learners: []}
        self.nodes = network

        #Initialize sockets:
        self.maxbuf = 2**16
        self.__initServer()
        self.__initClient()

    '''
        PRIVATE
    '''

    #create a multicast socket listening to the address
    def __initServer(self):
        #Creates a reciever socket for all incoming UDP messages
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

        # Set some options to make it multicast-friendly
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        mcast_group = struct.pack("4sl", socket.inet_aton(self.ip), socket.INADDR_ANY)
        self.server.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mcast_group)

    #Creates a UDP socket for sending outgoing UDP multicast messages
    def __initClient(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

    '''
        PUBLIC
    '''

    #Return string of (role, pid, ip, port) for identification in command line
    def __str__(self):
        return str((self.role, self.address(0), self.address(1), self.address(1)))

    #Start process: Inherited function from Process
    #   runs for all processes and initializes socket communication
    def run(self):
        #Initialize server at (ip, port)
        self.server.bind((self.ip, self.port)) #because AF_INET family
        print(f'Agent [{self}] listening for messages...')

        #Handle all incoming messages
        while True:
            #Recieve and decode message
            message = self.recieve()

            #Handle decoded message from client
            self.handleMessage(message)

    #Virtual function for components
    def updateState(self, instance):
        pass

    #Send message from client: address = (ip, port)
    def send(self, address, message):
        return self.client.sendto(message, address)
    
    #Recieve and decode message from client
    def recieve(self):
        #recieve message with max buffersize
        message_enc, _ = self.server.recvfrom(self.maxbuf)

        #Decode message -> MessageObject
        return msg.Message(message=message_enc)

    #Recieve message from external clients
    def handleMessage(self, message):
        pass