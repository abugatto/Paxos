import sys
import time
import math

import Message as msg
import Agent


class Acceptor(Agent):
    """
        Acceptor Class:
        1. 
    """

    def __init__(self, *args, **kwargs):
        super.__init__(self, role="acceptors", *args, **kwargs)
        
        #Keep track of states: 
        # instance : {c_rnd, c_val, v, max_v_rnd, max_v_val, quorum1B, quorum2B}
        self.states = {}

        #keep track of instance and whether it is updated
        self.instance = -1

    '''
        PRIVATE
    '''
    
    #Add state[instance] to state history
    def __updateState(self, instance):
        if instance is not None and instance not in self.states:
            self.states[instance] = {
                "rnd": 0, 
                "v_rnd": 0, 
                "v_val": None
            }

    #Create, print, and send phase 1B message to acceptors
    def __phase1B(self, message):
        #If round is greater than the current round then switch and send message
        if self.states[instance]['rnd'] <= message.data['c_rnd']:
            self.states[instance]['rnd'] = message.data['c_rnd']

            #create phase 1B message
            instance = message.instance
            message1B = msg.Message(instance=instance, phase="1B", data = {
                "rnd": self.state[instance]['rnd'], 
                "v_rnd": self.state[instance]['v_rnd'], 
                "v_val": self.state[instance]['v_val']
            })

            #get address of proposers and send mesage
            address = (
                self.network['proposers']['ip'], 
                self.network['proposers']['port']
            )
            self.send(address, message1B.encode())

            #print message
            print(f"Acceptor [{self.pid}] sending [{message1B}] to proposers")

    #Create, print, and send phase 1B message to acceptors
    def __phase2B(self, message):
        #If round is greater than the current round then switch and send message
        if self.states[instance]['rnd'] <= message.data['c_rnd']:
            self.states[instance]['v_rnd'] = message.data['c_rnd']
            self.states[instance]['v_val'] = message.data['c_val']

            #create phase 2B message
            instance = message.instance
            message2B = msg.Message(instance=instance, phase="2B", data = {
                "v_rnd": self.state[instance]['v_rnd'], 
                "v_val": self.state[instance]['v_val']
            })

            #get address of proposers and send mesage
            address = (
                self.network['proposers']['ip'], 
                self.network['proposers']['port']
            )
            self.send(address, message2B.encode())

            #print message
            print(f"Acceptor [{self.pid}] sending [{message2B}] to proposers")

    def __handleCatchupInstanceRequest(self, message):


    '''
        PUBLIC
    '''

    def handleMessage(self, message):
        print(f'Acceptor [{self}] recieves [{message}]')

        #Update state with new instance
        self.__updateState(message.instance)

        #If instance is greater than the current switch
        if message.instance is not None and message.instance > self.instance:
            self.instance = message.instance

        #Handle different message types
        if message.phase == "1A":
            #If the leader sends a request 
            self.__phase1B(message)
        elif message.phase == "2A":
            #If the leader sends a proposal
            self.__phase2B(message)
        elif message.phase == "CU_INST":
            #If a proposer or learner wants an instance update
            self.__handleCatchupInstanceRequest(message)