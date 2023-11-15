"""This defines the network entities, Entity is the abstact description of
an Entity where EntityA and EntityB are concrete classes that must be modified
for this assignment"""

from abc import ABC, abstractmethod
import inspect
import packet

class Entity(ABC):
    """Abstract concept of an Entity"""

    def __init__(self, sim):
        self.sim = sim

    @abstractmethod
    def output(self, message):
        """called from layer5 when a message is ready to be sent by the application"""

    @abstractmethod
    def input(self, packet):
        """called from layer 3, when a packet arrives for layer 4"""

    @abstractmethod
    def timerinterrupt(self):
        """called when timer goes off"""

    @abstractmethod
    def starttimer(self, increment):
        """Provided: call this function to start your timer"""

    @abstractmethod
    def stoptimer(self):
        """Provided: call this function to stop your timer"""

    def tolayer5(self, data):
        """Provided: call this function when you have data ready for layer5"""

    def tolayer3(self, packet):
        """Provided: call this function to send a layer3 packet"""


class EntityA(Entity):
    """Concrete implementaion of EntityA. This entity will receive messages
    from layer5 and must ensure they make it to layer3 reliably"""

    def __init__(self, sim):
        super().__init__(sim)
        print(f"{self.__class__.__name__}.{inspect.currentframe().f_code.co_name} called.")

        EntityA.NextSeqNum = 0 # seq number iterable 
        EntityA.SendBase = 0 # base of acknowledged packets
        EntityA.pktInAir = False

        EntityA.backupPkt = list() # a "stream" of the packets 
        EntityA.lastPktSent = None 

        

    def output(self, message):
        """Called when layer5 wants to introduce new data into the stream"""
        print(f"{self.__class__.__name__}.{inspect.currentframe().f_code.co_name} called.")
        
        #create TCP segment
        pkt = packet.Packet()
        pkt.payload = message 
        pkt.seqnum = self.NextSeqNum
        pkt.acknum = pkt.seqnum + len(message)
        pkt.checksum = pkt.seqnum + pkt.acknum + ord(message[0])
      

        self.NextSeqNum += len(message) # iterate the seq num
        self.backupPkt.append(pkt)
        # if there isn't anything in transit, start transit
        if(not self.pktInAir):
            
            self.pktInAir = True # there is something in transit
            self.lastPktSent = self.backupPkt.pop(0) # current pkt in transit
            self.starttimer(10)
            self.tolayer3(pkt)
        
        

        
        
        

    def input(self, packet):
        """Called when the network has a packet for this entity"""
        print(f"{self.__class__.__name__}.{inspect.currentframe().f_code.co_name} called.")
        
        # correct next ack is recieved 
        # it matches the sendBase and it isn't corrupt
        if((packet.acknum == (self.SendBase + len(packet.payload))) == (packet.checksum == (packet.acknum + packet.seqnum + ord(packet.payload[0])))):
            self.stoptimer()
            self.pktInAir = False
            self.SendBase += len(packet.payload) # iterate the sendbase 
            
            if(len(self.backupPkt) > 0):
                self.starttimer(10) # start the timer because there are still packets in needed to go through
                self.lastPktSent = self.backupPkt.pop(0)
                self.pktInAir = True
                self.tolayer3(self.lastPktSent)
            
                
        # packet was corrupted, try sending it again
        else:
            
            self.starttimer(10)
            self.tolayer3(self.lastPktSent) # call the last backupPkt


        

        

    def timerinterrupt(self):
        """called when your timer has expired"""
        print(f"{self.__class__.__name__}.{inspect.currentframe().f_code.co_name} called.")
        #timer timeout
        
        self.pktInAir = True
        self.starttimer(10)
        self.tolayer3(self.lastPktSent) 
        

    # From here down are functions you may call that interact with the simulator.
    # You should not need to modify these functions.

    def starttimer(self, increment):
        """Provided: call this function to start your timer"""
        self.sim.starttimer(self, increment)

    def stoptimer(self):
        """Provided: call this function to stop your timer"""
        self.sim.stoptimer(self)

    def tolayer5(self, data):
        """Provided: call this function when you have data ready for layer5"""
        self.sim.tolayer5(self, data)

    def tolayer3(self, packet):
        """Provided: call this function to send a layer3 packet"""
        self.sim.tolayer3(self, packet)

    def __str__(self):
        return "EntityA"

    def __repr__(self):
        return self.__str__()


class EntityB(Entity):
    def __init__(self, sim):
        super().__init__(sim)

         
        EntityB.lastAck = 0 # the last seq correctly acknowledged
        EntityB.lastPktRcvd = packet.Packet() # the last packet correctly recieved
        
        print(f"{self.__class__.__name__}.{inspect.currentframe().f_code.co_name} called.")

    def output(self, message):
        print(f"{self.__class__.__name__}.{inspect.currentframe().f_code.co_name} called.")
        # TODO add some code
        pass

    # Called when the network has a packet for this entity
    def input(self, packet):
        print(f"{self.__class__.__name__}.{inspect.currentframe().f_code.co_name} called.")
        
        # first off, is this packet legit
        if((packet.seqnum + ord(packet.payload[0]) + packet.acknum) == packet.checksum):
            # is this the next packet I am looking for
            if(self.lastAck == packet.seqnum):

                self.lastAck += len(packet.payload) 
                self.tolayer5(packet.payload) 
                self.tolayer3(packet)
                    

        
        else:
            # negative implies Nack
            packet.acknum = -1
            self.tolayer3(packet)
        
        

        
        
        
    def timerinterrupt(self):
        print(f"{self.__class__.__name__}.{inspect.currentframe().f_code.co_name} called.")
        pass

    def starttimer(self, increment):
        """Provided: call this function to start your timer"""
        self.sim.starttimer(self, increment)

    def stoptimer(self):
        """Provided: call this function to stop your timer"""
        self.sim.stoptimer(self)

    def tolayer5(self, data):
        """Provided: call this function when you have data ready for layer5"""
        self.sim.tolayer5(self, data)

    def tolayer3(self, packet):
        """Provided: call this function to send a layer3 packet"""
        self.sim.tolayer3(self, packet)

    def __str__(self):
        return "EntityB"

    def __repr__(self):
        return self.__str__()