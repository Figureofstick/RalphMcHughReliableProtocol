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

        # Initialize anything you need here

    def output(self, message):
        """Called when layer5 wants to introduce new data into the stream"""
        print(f"{self.__class__.__name__}.{inspect.currentframe().f_code.co_name} called.")
        # TODO add some code

        pkt = packet.Packet()
        pkt.payload = message
        self.tolayer3(pkt)

    def input(self, packet):
        """Called when the network has a packet for this entity"""
        print(f"{self.__class__.__name__}.{inspect.currentframe().f_code.co_name} called.")
        # TODO add some code

    def timerinterrupt(self):
        """called when your timer has expired"""
        print(f"{self.__class__.__name__}.{inspect.currentframe().f_code.co_name} called.")

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

        # Initialize anything you need here
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
        self.tolayer5(packet.payload)

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
