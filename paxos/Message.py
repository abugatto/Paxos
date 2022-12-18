import json


class Message:
    '''
        Message Class:
        1. Encode and Decode messages from JSONs
        2. Handle all phases of PAXOS
        3. Support for leader elections
        4. Support for catch up
    '''

    def __init__(self, instance=None, phase=None, data=None, message=None):
        #check if message is encoded
        if not message:
            self.instance = instance
            self.phase = phase

            #Convert to dict based on phase request
            #Data is assumed to be dictionary with relevant components
            if self.phase == "REQUEST":
                #Handles new instance (from client to proposer) 
                # and catch up (from proposer to acceptors)
                self.data = {
                    "v": data['v']
                }
            elif self.phase == "1A":
                self.data = {
                    "c_rnd": data['c_rnd']
                }
            elif self.phase == "1B":
                self.data = {
                    "rnd": data['rnd'], 
                    "v_rnd": data['v_rnd'], 
                    "v_val": data['v_val']
                }
            elif self.phase == "2A":
                self.data = {
                    "c_rnd": data['c_rnd'],
                    "c_val": data['c_val']
                }
            elif self.phase == "2B":
                self.data = {
                    "v_rnd": data['v_rnd'],
                    "v_val": data['v_val']
                }
            elif self.phase == "DECISION":
                self.data = {
                    "c_rnd": data['c_rnd'],
                    "v_val": data['v_val']
                }
            elif self.phase == "ELECTION":
                self.data = {
                    "pid": data['pid']
                }
            elif self.phase == "CU_INST_Req":
                self.data = {
                    "role": data['role'] #multiple agents will use this
                }
            elif self.phase == "CU_INST_UP":
                #Update instance
                self.data = None
            elif self.phase == "CU_HISTORY_REQ":
                #No data, just a request
                self.data = None
            elif self.phase == "CU_HISTORY_UP":
                self.data = data['history']
            else:
                print("Error!!! Invalid message type...")
        else:
            #ignore instance, phase, and data inputs since they are in message
            self.decode(message)

    def __str__(self):
        return str((self.instance, self.phase, self.data))

    #Encode message (instance, phase, data) into json
    def encode(self):
        return json.dumps({
            "instance": self.instance, 
            "phase" : self.phase, 
            "data": self.data
        })

    #Decode json into (instance, phase, data)
    def decode(self, message):
        decoded = json.loads(message)

        #load decoded values into message
        self.instance = decoded['instance']
        self.phase = decoded['phase']
        self.data = decoded['data']