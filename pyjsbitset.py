#PyjsBitset - Copyright (C) 2013 James Garnon

#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#PyjsBitset version 0.5
#Project Site: http://gatc.ca

import math
from pyjsarray import PyUint8Array, PyUint16Array, PyUint32Array


class BitSet:

    """
    BitSet provides a bitset object to use in a Python-to-JavaScript application. It uses the PyUint8Array implementation of the JavaScript Uint8Array 8-bit typedarray. BitSet16 and BitSet32 stores data in the PyUint16Array (16-bit) and PyUint32Array (32-bit) that implement the Uint16Array and Uint32Array typedarray. The BitSet will dynamically expand to hold the bits required, an optional width argument define number of bits the BitSet instance will initially hold.  
    """

    __bit = 8
    __bitmask = None
    __typedarray = PyUint8Array

    def __init__(self, width=None):
        if not BitSet.__bitmask:
            BitSet.__bitmask = dict([(BitSet.__bit-i-1,1<<i) for i in range(BitSet.__bit-1,-1,-1)])
        if width:
            self.__width = abs(width)
        else:
            self.__width = BitSet.__bit
        self.__data = BitSet.__typedarray( math.ceil(self.__width/(BitSet.__bit*1.0)) )

    def __str__(self):
        """
        Return string representation of BitSet object.
        """
        return "%s" % self.__class__

    def __repr__(self):
        """
        Return string of the indexes of the set bits.
        """
        setBit = []
        for index in xrange(self.__width):
            if self.get(index):
                setBit.append(str(index))
        return "{" + ", ".join(setBit) + "}"

    def __getitem__(self, index):
        """
        Get bit by index.
        """
        return self.get(index)

    def __setitem__(self, index, value):
        """
        Set bit by index.
        """
        self.set(index, value)

    def __len__(self):
        """
        Get bit length.
        """
        for index in xrange(self.__width-1, -1, -1):
            if self.get(index):
                break
        return index+1

    def __iter__(self):
        """
        Iterate over bits.
        """
        index = 0
        while index < self.__width:
            yield self.get(index)
            index += 1

    def get(self, index, toIndex=None):
        """
        Get bit by index.
        Arguments include index of bit, and optional toIndex that return a slice as a BitSet.
        """
        if index > self.__width-1:
            if not toIndex:
                return False
            else:
                size = toIndex-index
                if size > 0:
                    return BitSet(size)
                else:   #use exception
                    return None
        if toIndex is None:
            return bool( self.__data[ int(index/BitSet.__bit) ] & BitSet.__bitmask[ index%BitSet.__bit ] )
        else:
            size = toIndex-index
            if size > 0:
                bitset = BitSet(size)
                ix = 0
                if toIndex > self.__width:
                    toIndex = self.__width
                for i in xrange(index, toIndex):
                    bitset.set(ix, bool( self.__data[ int(i/BitSet.__bit) ] & BitSet.__bitmask[ i%BitSet.__bit ] ))
                    ix += 1
                return bitset
            else:    #use exception
                return None 

    def set(self, index, value=1):
        """
        Set bit by index.
        Optional argument value is the bit state of 1(True) or 0(False). Default:1
        """
        if index > self.__width-1:
            if value:
                self.resize(index+1)
            else:
                return
        if value:
            self.__data[ int(index/BitSet.__bit) ] = self.__data[ int(index/BitSet.__bit) ] | BitSet.__bitmask[ index%BitSet.__bit ]
#            self.__data[ int(index/BitSet.__bit) ] |= BitSet.__bitmask[ index%BitSet.__bit ]    #pyjs -O: |= not processed
        else:
            self.__data[ int(index/BitSet.__bit) ] = self.__data[ int(index/BitSet.__bit) ] & ~(BitSet.__bitmask[ index%BitSet.__bit ])
#            self.__data[ int(index/BitSet.__bit) ] &= ~(BitSet.__bitmask[ index%BitSet.__bit ])     #pyjs -O: &= not processed
        return None

    def clear(self, index=None, toIndex=None):
        """
        Clear the bit. If no argument provided, all bits are cleared.
        Optional argument index is bit index to clear, and toIndex to clear a range of bits.
        """
        if index is None:
            for i in xrange(len(self.__data)):
                self.__data[i] = 0
        else:
            if toIndex is None:
                self.set(index, 0)
            else:
                if index == 0 and toIndex == self.__width:
                    for byte in xrange(len(self.__data)):
                        self.__data[byte] = 0
                else:
                    for i in xrange(index, toIndex):
                        self.set(i, 0)

    def flip(self, index, toIndex=None):
        """
        Flip the state of the bit.
        Argument index is the bit index to flip, and toIndex to flip a range of bits
        """
        if toIndex is None:
            self.set(index, not self.get(index))
        else:
            if toIndex > self.__width:
                self.resize(toIndex)
                toIndex = self.__width
            if index == 0 and toIndex == self.__width:
                for byte in xrange(len(self.__data)):
                    self.__data[byte] = ~self.__data[byte]
            else:
                for i in xrange(index, toIndex):
                    self.set(i, not self.get(i))

    def cardinality(self):
        """
        Return the count of bit set.
        """
        count = 0
        for bit in xrange(self.__width):
            if self.get(bit):
                count += 1
        return count

    def intersects(self, bitset):
        """
        Check if set bits in this BitSet are also set in the bitset argument.
        Return True if bitsets intersect, other return False.
        """
        for byte in xrange(len(bitset.__data)):
            if bitset.__data[byte] & self.__data[byte]:
                return True
        return False

    def andSet(self, bitset):
        """
        BitSet and BitSet
        """
        bytes = min(len(self.__data), len(bitset.__data))
        for byte in xrange(bytes):
            self.__data[byte] = self.__data[byte] & bitset.__data[byte]
#            self.__data[byte] &= bitset.__data[byte]     #pyjs -O: &= not processed
#        pyjs -S: &= calls __and__ instead of __iand__, -O: no call to operator methods
#        return self

    def orSet(self, bitset):
        """
        BitSet or BitSet
        """
        bytes = min(len(self.__data), len(bitset.__data))
        for byte in xrange(bytes):
            self.__data[byte] = self.__data[byte] | bitset.__data[byte]
#            self.__data[byte] |= bitset.__data[byte]    #pyjs -O: |= not processed
#        return self

    def xorSet(self, bitset):
        """
        BitSet xor BitSet
        """
        bytes = min(len(self.__data), len(bitset.__data))
        for byte in xrange(bytes):
            self.__data[byte] = self.__data[byte] ^ bitset.__data[byte]
#            self.__data[byte] ^= bitset.__data[byte]    #pyjs -O: |= not processed
#        return self

    def resize(self, width):
        """
        Resize the BitSet to width argument.
        """
        if width > self.__width:
            self.__width = width
            if self.__width > len(self.__data) * BitSet.__bit:
                array = BitSet.__typedarray( math.ceil(self.__width/(BitSet.__bit*1.0)) )
                array.set(self.__data)
                self.__data = array
        elif width < self.__width:
            if width < len(self):
                width = len(self)
            self.__width = width
            if self.__width <= len(self.__data) * BitSet.__bit - BitSet.__bit:
                array = BitSet.__typedarray( math.ceil(self.__width/(BitSet.__bit*1.0)) )
                array.set(self.__data.subarray(0,math.ceil(self.__width/(BitSet.__bit*1.0))))
                self.__data = array            

    def size(self):
        """
        Return bits used by BitSet storage array.
        """
        return len(self.__data) * BitSet.__bit

    def isEmpty(self):
        """
        Check whether any bit is set.
        Return True if none set, other return False.
        """
        for data in self.__data:
            if data:
                return False
        return True

    def clone(self):
        """
        Return a copy of the BitSet.
        """
        new_bitset = BitSet(1)
        data = BitSet.__typedarray(self.__data)
        new_bitset.__data = data
        new_bitset.__width = self.__width
        return new_bitset


class BitSet16(BitSet):
    """
    BitSet using PyUint16Array.
    """
    __bit = 16
    __typedarray = PyUint16Array
    
    def __init__(self, width=None):
        BitSet.__init__(width)


class BitSet32(BitSet):
    """
    BitSet using PyUint32Array.
    """
    __bit = 32
    __typedarray = PyUint32Array
    
    def __init__(self, width=None):
        BitSet.__init__(width)

