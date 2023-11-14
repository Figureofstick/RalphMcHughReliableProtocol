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
        EntityA.pktsNotYetAckd = False

        EntityA.backupPkt = list() # a "stream" of the packets 
        EntityA.backupPktIndex = 0 # this is essentially the sendbase value but instead of increasing by 16
        # it increases by one each time

    def output(self, message):
        """Called when layer5 wants to introduce new data into the stream"""
        print(f"{self.__class__.__name__}.{inspect.currentframe().f_code.co_name} called.")
        
        #create TCP segment
        pkt = packet.Packet()
        pkt.payload = message 
        pkt.seqnum = self.NextSeqNum
        pkt.checksum = ord("Z") - ord(message[0]) # the checksum works by getting the sum of the ASCII values
        # the ascii on the other side should add up to ascii Z or 90

        self.NextSeqNum += len(message) # iterate the seq num
        # if(timer not running) start timer
        self.starttimer
        # save packet if it needs to be re-sent
        self.backupPkt.append(pkt)
        # pass segment to Layer 3
        self.tolayer3(pkt)

        
        
        

    def input(self, packet):
        """Called when the network has a packet for this entity"""
        print(f"{self.__class__.__name__}.{inspect.currentframe().f_code.co_name} called.")
        # TODO add some code
        # correct next ack is recieved 
        if(packet.acknum == self.SendBase):
            self.SendBase += len(packet.payload) # iterate the sendbase 
            self.backupPktIndex += 1 # iterate the backupPktIndex
            self.stoptimer # stop the timer
        # packet was corrupted, try sending it again
        if(packet.acknum < 0):
            self.starttimer
            self.tolayer3(self.backupPkt[self.backupPktIndex]) # call the last backupPkt


        

        

    def timerinterrupt(self):
        """called when your timer has expired"""
        print(f"{self.__class__.__name__}.{inspect.currentframe().f_code.co_name} called.")
        #timer timeout
        #retransmit not yet acked segment with smallest sequence number
        self.starttimer
        self.tolayer3(self.backupPkt[self.backupPktIndex]) # call the last backupPkt
        # self.pktsNotYetAckd = False
        #start timer

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

         
        EntityB.lastAck = 0 # the last packet correctly acknowledged
        print(f"{self.__class__.__name__}.{inspect.currentframe().f_code.co_name} called.")

    # Called when layer5 wants to introduce new data into the stream
    # For EntityB, this function does not need to be filled in unless
    # you're doing the extra credit, bidirectional part of the assignment
    def output(self, message):
        print(f"{self.__class__.__name__}.{inspect.currentframe().f_code.co_name} called.")
        # TODO add some code
        pass

    # Called when the network has a packet for this entity
    def input(self, packet):
        print(f"{self.__class__.__name__}.{inspect.currentframe().f_code.co_name} called.")
        # TODO add some code
        # check checksum, does the message and the checksum add up to capital Z?
        if(packet.checksum + ord(packet.payload[0]) == ord("Z")):
            # checksum passed
            # if this is the correct next packet
            # otherwise I will do nothing
            if(self.lastAck == packet.seqnum):

                
                packet.acknum = packet.seqnum + len(packet.payload) # make the acknowledgement packet
                self.lastAck = packet.acknum # update the last correctly acknowledged packet
                self.tolayer5(packet.payload) # give the correct payload to the application

                # send the ack back to EntityA
                self.tolayer3(packet)
            
        # that last packet was corrupted
        # I need it again
        else:
            # negative implies Nack
            packet.acknum = -1
            self.tolayer3(packet)
        
        

        
        
        

    # called when your timer has expired
    def timerinterrupt(self):
        print(f"{self.__class__.__name__}.{inspect.currentframe().f_code.co_name} called.")
        pass

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
        return "EntityB"

    def __repr__(self):
        return self.__str__()
