import sys
import time
import math

import Message as msg
import Agent


class Learner(Agent):
    """
        Learner Class:
        1. 
    """

    def __init__(self, *args, **kwargs):
        super.__init__(self, role="learners", *args, **kwargs)
        
        #Keep track of states: 
        # instance : {c_rnd, c_val, v, max_v_rnd, max_v_val, quorum1B, quorum2B}
        self.states = {}
        self.instance = -1

        #Control variables for printing conscensus values
        self.printable = True
        self.lastInstance = -1

    '''
        PRIVATE
    '''

    #Update state store at instance
    def __updateState(self, instance):
        if instance not in self.states:
            self.states[instance] = {'v': None}

    #request current instance from acceptors
    def __catchupInstanceRequest(self):
        #create phase 2B message
        messageCU = msg.Message(phase="CU_INST_REQ", data = {'role': "learners"})

        #get address of acceptors and send mesage
        address = (
            self.network['acceptors']['ip'], 
            self.network['acceptors']['port']
        )
        self.send(address, messageCU.encode())

        #print message
        print(f"Learner [{self.pid}] sending [{messageCU}] to acceptors")

    #Check and update history if needed
    def __catchupHistoryRequest(self):
        #Checks if any instances are missing from the history
        for instance in range(0, self.instance + 1):
            if instance != -1 and instance not in self.states:
                self.printable = False
                break
        
        #If not printable request history from proposers
        if self.printable:
            for instance in range(self.lastInstance + 1, len(self.states)):
                v = self.states[instance]['v']
                if instance in self.states and v is not None:
                    print(f'Instance [{instance}]: {v}')
            
            #update lastInstance
            self.lastInstance = len(self.states)-1
        else:
            #create phase 2B message
            messageCU = msg.Message(phase="CU_HIST_REQ")

            #get address of proposers and send mesage
            address = (
                self.network['proposers']['ip'], 
                self.network['proposers']['port']
            )
            self.send(address, messageCU.encode())

            #print message
            print(f"Learner [{self.pid}] sending [{messageCU}] to proposers")

    #Updates instance from acceptor CU_INST_UP message
    def __handleCatchupInstanceUpdate(self, message):
        #if instance is greater than sent instance update
        if self.instance < message.instance:
            #update instance
            self.instance = message.instance

            #If learner just spawned request history
            if self.instance == -1:
                self.__catchupHistoryRequest()

    #Updates History from leader
    def __handleCatchupHistoryUpdate(self, message):
        history = message['history']

        #if history not empty 
        if history is not None:
            #if new instance is included then update
            newinstance =len(history) - 1
            if self.instance < newinstance:
                self.instance = newinstance

            #Add all new instances from history to states
            for instance in history:
                if instance not in self.states or self.states[instance]['v'] is None:
                    self.states[instance] = {'v': history[instance]}

        #Print
        for instance in range(self.lastInstance + 1, len(self.states)):
            v = self.states[instance]['v']
            if instance in self.states and v is not None:
                print(f'Instance [{instance}]: {v}')
            
        #update lastInstance
        self.lastInstance = len(self.states)-1

    '''
        PUBLIC
    '''

    def run(self):
        #bind server 
        self.server.bind((self.ip, self.port))
        print(f'Learner [{self}] listening for messages...')

        #Catch up if spawned in the middle of a paxos run
        #   sends update request to acceptors
        self.__catchupInstanceRequest()

        #Handle all incoming messages
        while True:
            #Recieve and decode message
            message = self.recieve()

            #Handle decoded message from client
            self.handleMessage(message)

    #handle incoming messages
    def handleMessage(self, message):
        print(f'Learner [{self}] recieves [{message}]')

        #handle message types
        if message.phase == "DECISION":
            #If instance is greater than the current switch
            if message.instance is not None and message.instance > self.instance:
                self.instance = message.instance

            #Update state and allow new values to be printed
            self.__updateState(self.instance)
            self.states[self.instance]['v'] = message.data['v_val']
            self.printable = True

            #Check and update history if needed
            self.__catchupHistoryRequest()
        elif message.phase == "CU_INST_UP":
            #if acceptors return for instance update
            #request missing instances from proposers if needed
            self.__handleCatchupInstanceUpdate(message)
        elif message.phase == "CU_HISTORY_UP":
            #If the leader sends the history
            self.__handleCatchupHistoryUpdate(message)
