from threading import Thread
import sys
import time
import math

import Message as msg
import Agent

########################################################################

class LeaderElectionDaemon(Thread):
    """
        Leader Election Daemon Class:
        1. 
    """

    def __init__(self, send, catchup):
        super.__init__(self)
        self.daemon = True

        #Define server and client timers
        self.last = time.time()
        

    '''
        PUBLIC
    '''

    def run(self):
        #check leader timer every .001s
        #   if not heard after 2 seconds then declare leader

        #send leader heartbeat every second


    #Updates leader timer
    #If timer ends leader is presumed dead and election is initiated
    def resetTimer(self):
        self.last = time.time()

########################################################################

class Proposer(Agent):
    """
        Proposer Class:
        1. Maintains multi-paxos state machine 
        2. Elects and polls leader
        3. 
    """

    def __init__(self, acceptors, *args, **kwargs):
        super.__init__(self, role="proposers", *args, **kwargs)
        
        #Keep track of states: 
        # instance : {c_rnd, c_val, v, max_v_rnd, max_v_val, quorum1B, quorum2B}
        self.states = {}

        #for quorum calculation
        self.quorum = math.ceil((acceptors + 1) / 2)

        #keep track of instance and whether it is updated
        self.instance = -1
        self.isUpdated = False

        #Keep track of leader using daemon thread
        #   daemon polls for leader on defined intervals
        self.leader = True
        self.daemon = LeaderElectionDaemon(self.send, self.__catchup)

    '''
        PRIVATE
    '''

    #If leader is dead declare yourself leader
    def __newLeaderCallback(self, timer):
        if timer

    def __updateState(self, instance):


    def __phase1A(self, ):


    def __phase1B(self, ):


    def __phase2A(self, ):


    def __phase2B(self, ):


    def __decide(self, ):


    def __catchupInstance(self):


    def __catchupDecisiom(self, instance):


    def __catchupHistory(self):


    '''
        PUBLIC
    '''

    #Initiates leader daemon, initiates server, catches up instance
    # and handles new messages
    def run(self):
        #if leader election daemon isn't running start it
        if not self.daemon.is_alive(): self.daemon.start()

        #bind server 
        self.server.bind((self.ip, self.port))
        print(f'Proposer [{self}] listening for messages...')

        #Catch up if spawned in the middle of a paxos run
        self.__catchup()

        #Handle all incoming messages
        while True:
            #Recieve and decode message
            message = self.recieve()

            #Handle decoded message from client
            self.handleMessage(message)

    #Handles each incoming message 
    def handleMessage(self, message):
        print(f'Proposer [{self}] recieves [{message}]')

        #Update state with instance if not stored
        self.__updateState(message.instance)

        #Handle different types of messages
        if message.phase == "REQUEST":

        elif message.phase == "1B":
            
        elif message.phase == "2B":
            
        elif message.phase == "DECISION":
            
        elif message.phase == "ELECTION":
            #reset daemon leader timer
            self.daemon.resetTimer()

            #Run leader election
            if message.data['pid'] > self.pid:
                self.leader = False
        elif message.phase == "CU_INST":
            
        elif message.phase == "CU_LEARN":
