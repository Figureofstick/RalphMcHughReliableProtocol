
# The packet class is really just a structure to hold four values:
# acknum - acknowledgement number
# seqnum - sequence number
# payload - a message (string of characters)
# checksum - a checksum provided by the user
#
# This class gives no guidance on how to allocate sequence numbers
# or compute checksums, instead the caller is expected to set these
# fields appropriately for their implementation. The simulator
# uses the values of these fields to print information.

class Packet:
    def __init__(self):
        self.acknum = None
        self.seqnum = None
        self.payload = None
        self.checksum = None

    def __repr__(self):
        return f'Packet(acknum={self.acknum}, seqnum={self.seqnum}, checksum={self.checksum}, payload={self.payload})'
    
    def __str__(self):
        return self.__repr__()
