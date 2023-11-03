# ******************************************************************
#   ALTERNATING BIT AND GO-BACK-N NETWORK EMULATOR: VERSION 1.1  J.F.Kurose
#
#   This code should be used for PA2, unidirectional or bidirectional
#   data transfer protocols (from A to B. Bidirectional transfer of data
#   is for extra credit and is not required).  Network properties:
#   - one way network delay averages five time units (longer if there
#   are other messages in the channel for GBN), but can be larger
#   - packets can be corrupted (either the header or the data portion)
#   or lost, according to user-defined probabilities
#   - packets will be delivered in the order in which they were sent
#   (although some can be lost).
# *********************************************************************

import argparse
import random
import copy

from entity import EntityA, EntityB

MSGLEN = 20


class Event:
    def __init__(self, time, entity, etype):
        self.time = time
        self.entity = entity
        self.etype = etype

    @staticmethod
    def sorter(event):
        """Sort events base on time"""
        return event.time

    TIMER_INTERRUPT = 0
    FROM_LAYER5 = 1
    FROM_LAYER3 = 2


class TimerEvent(Event):
    def __init__(self, entity, time):
        super(TimerEvent, self).__init__(entity, time, Event.TIMER_INTERRUPT)

    def __repr__(self):
        return f"TimerEvent({self.time}, {self.entity})"

    def __str__(self):
        return self.__repr__()


class FromLayer5Event(Event):
    def __init__(self, entity, time):
        super(FromLayer5Event, self).__init__(entity, time, Event.FROM_LAYER5)

    def __repr__(self):
        return f"FromLayer5({self.time}, {self.entity})"

    def __str__(self):
        return f"FromLayer5({self.time}, {self.entity})"


class FromLayer3Event(Event):
    def __init__(self, entity, time, packet):
        super(FromLayer3Event, self).__init__(entity, time, Event.FROM_LAYER3)
        self.packet = packet

    def __repr__(self):
        return f"FromLayer3({self.time}, {self.entity}, {self.packet})"

    def __str__(self):
        return f"FromLayer3({self.time}, {self.entity}, {self.packet})"


class Simulator:
    def __init__(
        self, bidirectional, trace, seed, nmessages, corruptprob, lossprob, lambdat
    ):
        self.bidirectional = bidirectional
        self.trace = trace
        random.seed(seed)
        self.nsim = 0
        self.nsimmax = nmessages
        self.corruptprob = corruptprob
        self.lossprob = lossprob
        self.lambdat = lambdat

        self.evlist = []

        self.ntolayer3 = 0
        self.nlost = 0
        self.ncorrupt = 0
        self.time = 0.0
        self.entity_a = EntityA(self)
        self.entity_b = EntityB(self)
        self.generate_next_arrival()

    def run(self):
        """Run the simulation"""

        while len(self.evlist) > 0:
            e = self.evlist.pop(0)
            if self.trace >= 2:
                print(f"{e}")

            # update time to next event time
            self.time = e.time

            if isinstance(e, FromLayer5Event):
                # set up future arrival
                if self.nsim < self.nsimmax:
                    self.generate_next_arrival()

                    # fill in msg to give with string of same letter
                    msg2give = chr(ord("A") + (self.nsim % 26)) * MSGLEN
                    if self.trace > 2:
                        print(f"          MAINLOOP: data given to student: {msg2give}")
                    e.entity.output(msg2give)
                    self.nsim += 1

            elif isinstance(e, TimerEvent):
                e.entity.timerinterrupt()

            elif isinstance(e, FromLayer3Event):
                pkt2give = copy.deepcopy(e.packet)

                # deliver packet to appropriate entity
                e.entity.input(pkt2give)

            else:
                assert False, f"invalid event {e}"

        print(f" Simulator terminated at time {self.time}")
        print(f" after sending {self.nsim} from layer5")

    def generate_next_arrival(self):
        # x is uniform on [0,2*lambda]
        # having mean of lambda
        time = self.time + self.lambdat * random.random() * 2.0

        if self.trace > 2:
            print("          GENERATE NEXT ARRIVAL: creating new arrival")

        if self.bidirectional and random.random() >= 0.5:
            event = FromLayer5Event(time, self.entity_b)
        else:
            event = FromLayer5Event(time, self.entity_a)

        self.insertevent(event)

    def insertevent(self, event):
        """Insert an event into the queue of events"""
        if self.trace > 2:
            print(f"            INSERTEVENT: future event: {repr(event)}")
        self.evlist.append(event)
        self.evlist.sort(key=Event.sorter)
        self.showevlist()

    def showevlist(self):
        print("eventlist")
        print("-------------------------")
        for i in self.evlist:
            print(repr(i))
        print("-------------------------")


    def starttimer(self, entity, increment):
        """Called by student code to start a timer"""

        if self.trace > 2:
            print(f"          START TIMER: starting timer at {self.time}")

        # be nice: check to see if timer is already started, if so, then warn
        for i in self.evlist:
            if isinstance(i, TimerEvent) and i.entity == entity:
                print("Warning: attempt to start a timer that is already started")
                return

        event = TimerEvent(self.time + increment, entity)
        self.insertevent(event)

    def stoptimer(self, entity):
        """called by students routine to cancel a previously-started timer"""

        if self.trace > 2:
            print(f"          STOP TIMER: stopping timer at {self.time}")

        for i in self.evlist:
            if isinstance(i, TimerEvent) and i.entity == entity:
                self.evlist.remove(i)
                return
        print("Warning: unable to cancel your timer. It wasn't running.")

    def printevlist(self):
        """display the current event list, in order"""
        print("--------------")
        print("Event List Follows:")
        for event in self.evlist:
            print(f"{event}")
        print("--------------")

    def tolayer5(self, entity, message):
        """Receive some data for layer5"""
        if self.trace > 2:
            print(f"          TOLAYER5: data received from {entity}: {message}")

    def tolayer3(self, entity, packet):
        """Take a packet from the user and send it through our media
        where it might be lost or corrupted"""
        self.ntolayer3 += 1

        if entity == self.entity_a:
            otherentity = self.entity_b
        else:
            otherentity = self.entity_a

        # simulate losses:
        if random.random() < self.lossprob:
            self.nlost += 1
            if self.trace > 0:
                print("          TOLAYER3: packet being lost\n")
            return

        # make a copy of the packet student just gave me since he/she may decide
        # to do something with the packet after we return back to him/her
        mypkt = copy.deepcopy(packet)
        if self.trace > 2:
            print(f"          TOLAYER3: {repr(mypkt)}")

        # create future event for arrival of packet at the other side

        # compute the arrival time of packet at the other end.
        # medium can not reorder, so make sure packet arrives
        # between 1 and 10 time units after the latest arrival time
        # of packets currently in the medium on their way to the
        # destination
        lasttime = self.time
        for i in self.evlist:
            if isinstance(i, FromLayer3Event) and otherentity == i.entity:
                lasttime = i.time

        lasttime = lasttime + 1.0 + 9.0 * random.random()

        event = FromLayer3Event(lasttime, otherentity, mypkt)

        if random.random() < self.corruptprob:
            # simulate corruption:
            self.ncorrupt += 1
            how = random.random()
            if how < 0.75:
                # corrupt payload
                mypkt.payload = "Z" + mypkt.payload[1:]
            elif how < 0.875:
                mypkt.seqnum = 999999
            else:
                mypkt.acknum = 999999

            if self.trace > 0:
                print("          TOLAYER3: packet being corrupted")

        if self.trace > 2:
            print("          TOLAYER3: scheduling arrival on other side")

        self.insertevent(event)


def main():
    """Kick things off: parse the arguments, build a simulation, run it"""
    parser = argparse.ArgumentParser(description="network simulator")
    parser.add_argument(
        "--bidirectional",
        action="store_true",
        help="extra credit bidirectional simulation",
    )
    parser.add_argument(
        "--trace", default=3, type=int, help="set the trace level (0-3)"
    )
    parser.add_argument("--seed", default=0, type=int, help="set random seed")
    parser.add_argument(
        "--messages",
        default=10,
        type=int,
        help="maximum number of messages to simulate",
    )
    parser.add_argument(
        "--corruptprob",
        default=0.0,
        type=float,
        help="corruption probability (0.0 - 1.0)",
    )
    parser.add_argument(
        "--lossprob", default=0.0, type=float, help="packet loss probaility (0.0 - 1.0)"
    )
    parser.add_argument("--lambda", default=1, type=float, help="packet arrival rate")
    args = parser.parse_args()
    assert args.messages >= 0
    assert args.lossprob >= 0.0 and args.lossprob <= 1.0
    assert args.corruptprob >= 0.0 and args.corruptprob <= 1.0
    assert args.__dict__["lambda"] > 0.0

    sim = Simulator(
        args.bidirectional,
        args.trace,
        args.seed,
        args.messages,
        args.corruptprob,
        args.lossprob,
        args.__dict__["lambda"],
    )
    sim.run()


if __name__ == "__main__":
    main()
