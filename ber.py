#!/usr/bin/python

import struct, util


class BERException (Exception):
    pass

class BER(object):
    """
    Robey's tiny little attempt at a BER decoder.
    """

    def __init__(self, content=''):
        self.content = content
        self.idx = 0

    def __str__(self):
        return self.content

    def __repr__(self):
        return 'BER(' + repr(self.content) + ')'

    def decode(self):
        return self.decode_next()
    
    def decode_next(self):
        if self.idx >= len(self.content):
            return None
        id = ord(self.content[self.idx])
        self.idx += 1
        if (id & 31) == 31:
            # identifier > 30
            id = 0
            while self.idx < len(self.content):
                t = ord(self.content[self.idx])
                if not (t & 0x80):
                    break
                id = (id << 7) | (t & 0x7f)
                self.idx += 1
        if self.idx >= len(self.content):
            return None
        # now fetch length
        size = ord(self.content[self.idx])
        self.idx += 1
        if size & 0x80:
            # more complimicated...
            # FIXME: theoretically should handle indefinite-length (0x80)
            t = size & 0x7f
            if self.idx + t > len(self.content):
                return None
            size = 0
            while t > 0:
                size = (size << 8) | ord(self.content[self.idx])
                self.idx += 1
                t -= 1
        if self.idx + size > len(self.content):
            # can't fit
            return None
        data = self.content[self.idx : self.idx + size]
        self.idx += size
        # now switch on id
        if id == 0x30:
            # sequence
            return self.decode_sequence(data)
        elif id == 2:
            # int
            return util.inflate_long(data)
        else:
            # 1: boolean (00 false, otherwise true)
            raise BERException('Unknown ber encoding type %d (robey is lazy)' % id)

    def decode_sequence(data):
        out = []
        b = BER(data)
        while 1:
            x = b.decode_next()
            if x == None:
                return out
            out.append(x)
    decode_sequence = staticmethod(decode_sequence)

