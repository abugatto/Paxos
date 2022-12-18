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

    def __init__(self, address, send, setleader, catchup):
        super.__init__(self)
        self.daemon = True

        #Define functions
        self.send = send
        self.setleader = setleader
        self.catchup = catchup

        #Input message params (pid, ip, port)
        self.address = address

        #define leader
        self.leader = False

        #Define server and client timers
        self.hearbeatInterval = .001
        self.leaderTimer = 2
        self.last = None
        

    '''
        PUBLIC
    '''

    def run(self):
        #check leader timer every .001s
        #   if not heard after 2 seconds then declare leader
        while True:
            time.sleep(self.hearbeatInterval)
            now = time.time()

            #Output heartbeat/election message
            if self.leader:
                print(f"Proposer [{self.address(0)}] is the leader")

                #create and send election message
                message = msg.Message(phase="ELECTION", data = {'pid' : self.address(0)})
                self.send((self.address(1), self.address(2)), message.encode())

            #Check for leader heartbeat every 2 seconds
            if self.last is not None and not self.leader:
                if now - self.last >= 2:
                    self.last = now

                    #Set self to leader and 
                    self.setLeader()
                    self.catchup()

    #Updates leader
    def updateLeader(self, leader):
        self.leader = leader

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
        self.proposersCaughtUp = 0 #another way to track quorum

        #keep track of instance and whether it is updated
        self.instance = -1
        self.isUpdated = False

        #Keep track of leader using daemon thread
        #   daemon polls for leader on defined intervals
        self.leader = True
        address = (
            self.pid, 
            self.network['proposers']['ip'], 
            self.network['proposers']['port']
        )
        self.daemon = LeaderElectionDaemon(
            address, self.send, self.__setLeader, self.__catchupInstanceRequest
        )
        self.daemon.updateLeader(self.leader)

    '''
        PRIVATE
    '''

    #sets self to leader... to be used from daemon
    def __setLeader(self):
        self.leader = True

    #Add state[instance] to state history
    def __updateState(self, instance):
        if instance is not None and instance not in self.states:
            self.states[instance] = {
                "c_rnd": self.pid + 1, 
                "c_val": None, 
                "v": None,
                "v_rnd": 0, 
                "v_val": 0,
                "counter1B": 0, 
                "counter2B": 0
            }

    #Create, print, and send phase 1A message to acceptors
    def __phase1A(self, message):
        #create phase 1A message
        instance = message.instance
        message1A = msg.Message(instance=instance, phase="1A", data = {
            'c_rnd': self.states[instance]['c_rnd']
        })

        #get address of acceptors and send mesage
        address = (
            self.network['acceptors']['ip'], 
            self.network['acceptors']['port']
        )
        self.send(address, message1A.encode())

        #print message
        print(f"Proposer [{self.pid}] sending [{message1A}] to acceptors")

    #Create, print, and send phase 2A message to acceptors
    def __phase2A(self, message):
        instance = message.instance

        #if message round is the same as current round increment counter for 1B
        if self.states[instance]['c_rnd'] == message.data['rnd']:
            self.states[instance]['counter1B'] += 1

        #If message value is greater than max seen value then switch
        if self.states[instance]['v_rnd'] <= message.data['v_rnd']:
            self.states[instance]['v_rnd'] = message.data['v_rnd']
            self.states[instance]['v_val'] = message.data['v_val']

        #check if request quorum has been reached and send 
        if self.states[instance]['counter1B'] >= self.quorum:
            #reset counter
            self.states[instance]['counter1B'] = 0

            #set c_val
            if self.states[instance]['v_val'] == 0:
                self.states[instance]['c_val'] = self.states[instance]['v']
            else:
                self.states[instance]['c_val'] = self.states[instance]['v_val']

            #create phase 2A message
            instance = message.instance
            message2A = msg.Message(instance=instance, phase="2A", data = {
                'c_rnd': self.states[instance]['c_rnd'],
                'c_val': self.states[instance]['c_val']
            })

            #get address of acceptors and send mesage
            address = (
                self.network['acceptors']['ip'], 
                self.network['acceptors']['port']
            )
            self.send(address, message2A.encode())

            #print message
            print(f"Proposer [{self.pid}] sending [{message2A}] to acceptors")

    #Create, print, and send phase decision message to proposers and learners
    def __decide(self, message):
        instance = message.instance

        #if message round is the same as current round increment counter for 2B
        if self.states[instance]['c_rnd'] == message.data['rnd']:
            self.states[instance]['counter2B'] += 1

        #check if request quorum has been reached and send 
        if self.states[instance]['counter2B'] >= self.quorum:
            #reset counter
            self.states[instance]['counter2B'] = 0

            #create phase DECISION message
            instance = message.instance
            encoded = msg.Message(instance=instance, phase="DECISION", data = {
                'c_rnd': self.states[instance]['c_rnd'],
                'c_val': self.states[instance]['c_val']
            }).encode()

            #get address of proposers and send mesage
            address = (
                self.network['proposers']['ip'], 
                self.network['proposers']['port']
            )
            self.send(address, encoded)

            #get address of learners and send mesage
            address = (
                self.network['learners']['ip'], 
                self.network['learners']['port']
            )
            self.send(address, encoded)

            #print message
            print(f"Proposer [{self.pid}] sending [{message}] to proposers and learners")

    #Requests instance from acceptor
    def __catchupInstanceRequest(self):
        #create phase CU_INST_REQ message
        messageCU = msg.Message(phase="CU_INST_REQ", data = {'role': "proposers"})

        #get address of acceptors and send mesage
        address = (
            self.network['acceptors']['ip'], 
            self.network['acceptors']['port']
        )
        self.send(address, messageCU.encode())

        #print message
        print(f"Proposer [{self.pid}] sending [{messageCU}] to acceptors")

    #Handles instance update from acceptors
    def __handleCatchupInstanceUpdate(self, message):
        #Update instance if needed
        if self.instance < message.instance:
            self.instance = message.instance
        
        #If a majority of nodes have caught up then we have reached quorum
        if not self.isUpdated:
            self.proposersCaughtUp += 1
            if self.proposersCaughtUp == self.quorum:
                self.proposersCaughtUp = 0
                self.isUpdated = True
        
        #Checks if any instances are missing from the history and requests them
        for instance in range(0, self.instance + 1):
            if instance != -1 and instance not in self.states:
                #create phase REQUEST message
                messageReq = msg.Message(instance=instance, phase="REQUEST", data=None)

                #get address of proposers and send mesage
                address = (
                    self.network['proposers']['ip'], 
                    self.network['proposers']['port']
                )
                self.send(address, messageReq.encode())

                #print message
                print(f"Proposer [{self.pid}] sending [{messageReq}] to proposers")
            

    #Handle history request from learner
    def __handleCatchupHistoryRequest(self):
        #If valued instance is in states then add value to history
        history = {}
        for instance in self.states:
            if self.states[instance]['c_val'] is not None:
                history[instance] = self.states[instance]['c_val']
            else:
                history[instance] = None

        #Make history message to send to learners
        if len(history) == 0: history = None
        messageCU = msg.Message(phase="CU_HIST_UP", data = {'history': history})

        #get address of learners and send mesage
        address = (
            self.network['learners']['ip'], 
            self.network['learners']['port']
        )
        self.send(address, messageCU.encode())

        #print message
        print(f"Proposer [{self.pid}] sending [{messageCU}] to learners")

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
        self.__catchupInstanceRequest()

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
            #Handles new instance (from client to proposer) 
            instance = 0
            if message.instance is None:
                #Create new instance
                self.instance += 1
                self.__updateState(self.instance)
                instance = self.instance
            else:
                #Handles catch up request (from proposer to proposers)
                instance = message.instance

            #Set current state's value to data['v']
            self.states[instance]['v'] = message.data['v'] 

            #handles instance not being updated
            if not self.isUpdated:
                self.__catchupInstanceRequest()

            #Increment current round, assuming there are max 10 proposers
            self.states[instance]['c_rnd'] += 10

            #If leader then run send requests
            if self.leader and self.isUpdated:
                self.__phase1A(message)
        elif message.phase == "1B":
            #If leader recieves confirmation of request then propose
            if self.leader:
                self.__phase2A(message)
        elif message.phase == "2B":
            #If leader recieves confirmation of proposal then decide
            if self.leader:
                self.__decide(message)
        elif message.phase == "DECISION":
            #If decision is reached then update current round and value
            self.__updateState(message.instance)
            self.states[message.instance]['c_rnd'] = message.data['c_rnd']
            self.states[message.instance]['c_val'] = message.data['c_val']
        elif message.phase == "ELECTION":
            #reset daemon leader timer
            self.daemon.resetTimer()

            #Run leader election
            if message.data['pid'] > self.pid:
                self.leader = False
                self.daemon.updateLeader(self.leader)
        elif message.phase == "CU_INST_UP":
            #If acceptor sends an instance update
            self.__handleCatchupInstanceUpdate(message.instance)
        elif message.phase == "CU_HISTORY_REQ":
            #If learner requests states history from leader
            if self.leader:
                self.__handleCatchupHistoryRequest()