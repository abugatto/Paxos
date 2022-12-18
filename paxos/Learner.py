import sys
import time
import math

import Message 
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


    def __catchupInstanceRequest(self):



    def __catchupHistoryRequest(self):



    def __handleCatchupInstanceUpdate(self, message):



    def __handleCatchupHistoryUpdate(self, message):


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
        elif message.phase == "CU_INST":
            #if acceptors return for instance update
            #request missing instances from proposers if needed
            self.__handleCatchupInstanceUpdate(message)
        elif message.phase == "CU_HISTORY":
            #If the leader sends the history
            self.__handleCatchupHistoryUpdate(message)
