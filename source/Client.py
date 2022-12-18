import sys
import time

import Message as msg
import Agent


class Client(Agent):
    """
        Client Class:
        1. Runs from current process
        2. Polls values from command line arguments
        3. Sends values to all proposers as REQUEST message
    """

    def __init__(self, *args, **kwargs):
        super.__init__(self, role="clients", *args, **kwargs)

    #Start process: Inherited function from Process
    #   Runs REQUEST to proposers
    def run(self):
        #Repeatedly poll for input
        while True:
            #Handle each input
            for value in sys.stdin:
                value = {"value": value.strip()}

                #create and send encodeed request message
                message = msg.Message(phase="REQUEST", data=value)
                self.send((self.ip, self.port), message.encode())
                print(f'REQUEST [{message}] from {self} to all proposers')

                #sleep process before next poll
                time.sleep(.001)