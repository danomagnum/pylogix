import struct
from collections import OrderedDict


class CIPType(object):
    """
    Complex data such as arrays and nested structs need to have a little wits about them.  This object is the
    template for classes that provide those wits.
    """

    def __init__(self, endianness = None):
        """
        Needs to define the format and instantiate the struct
        """
        self.format = ''
        if endianness is None:
            self.endianness = ''
        else:
            self.endianness = '<'
        self.struct = struct.Struct(self.format)
        self.alignment = 4


    def __len__(self):
        return self.struct.size

    def set_endianness(self, endianness):
        self.endianness = endianness
        self.struct = struct.Struct(self.endianness + self.format)

    def parse_unpacked(self, unpacked_data):
        """
        :param unpacked_data: a python list of the unpacked elements
        :return: (value, number of items used from list)
        """

        return 0, 0

    def create_packlist(self, value):
        """
        :return: Returns a list that gets combined onto the end of the current list to be packed.
         It should match the format
        """
        return []

    def pack(self, value, endian=None):
        """
        Takes a dictionary (dict_input)
        and a OrderedDict as described at the top of the file
        and an opitonal offset and then return a regular (non-Ordered) dictionary
        with the data assigned to the keys.
        """
        pack_struct = self.struct
        if endian is not None:
          pack_struct = struct.Struct(endian + self.format)
        data_list = self.create_packlist(value)
        return pack_struct.pack(*data_list)

    def unpack(self, data_array, offset=0, endian=None):
        """
        Take raw response data which should be an iterable byte structure,
        and then return an ordered dictionary with the data assigned to the keys.
        """
        unpack_struct = self.struct
        endian = '<'
        if endian is not None:
          unpack_struct = struct.Struct(endian + self.format)
        unpacked = unpack_struct.unpack_from(data_array, offset)

        return self.parse_unpacked(unpacked)[0]



class BasicType(CIPType):
    def __init__(self, format_str, alignment=4):
        self.format = format_str
        self.endianness = '<'
        self.struct = struct.Struct(self.format)
        self.alignment = alignment

    def parse_unpacked(self, unpacked_data):
        """
        :param unpacked_data: a python list of the unpacked elements
        :return: (value, number of items used from list)
        """

        return unpacked_data[0], 1

    def create_packlist(self, value):
        """
        :return: Returns a list that gets combined onto the end of the current list to be packed.
         It should match the format returned by get_format
        """
        return [value]

    def __reduce__(self):
        return (self.__class__, (self.format,))




# Provide easier to use definitions of the constants the struct module uses.
# See https://docs.python.org/3/library/struct.html
SINT = BasicType('b', 1)
USINT = BasicType('B', 1)
BOOL = BasicType('?', 1)
INT = BasicType('h', 2)
UINT = BasicType('H', 2)
DINT = BasicType('i', 4)
UDINT = BasicType('I', 4)
LINT = BasicType('q', 8)
ULINT = BasicType('Q', 8)
REAL = BasicType('f')
LREAL = BasicType('d', 8)


class BYTES(CIPType):
    def __init__(self, length):
        """
        Structure object for creating strings that correspond to python byte objects bytes (no encodings)
        :param length: how many elements the array contains
        """
        self.length = length
        self.format = '{}s'.format(length)
        self.struct = struct.Struct(self.format)
        self.alignment = 1

    def __reduce__(self):
        return (self.__class__, (self.length,))

    def parse_unpacked(self, unpacked_data):
        """
        :param unpacked_data: a python list of the unpacked elements
        :return: (value, number of items used from list)
        """

        str_data = unpacked_data[0]

        return str_data, 1

    def create_packlist(self, value):
        """
        :return: Returns a list that gets combined onto the end of the current list to be packed.
         It should match the format returned by get_format
        """
        return [value]

    def null(self):
        """
        :return: a null byte array as long as this structure
        """
        return bytes([0] * len(self))


class STRING(CIPType):
    def __init__(self, length=82, null_term=False, encoding=None):
        """
        Structure object for creating strings.  These map to python strings
        :param length: how many elements the array contains
        :param null_term: whether the returned string should end at the first null byte
        :param encoding: what encoding to use when converting to a string and back
        """
        self.length = length
        self.encoding = encoding
        self.null_term = null_term
        self.format = 'I{}s'.format(length)
        self.struct = struct.Struct(self.format)
        self.alignment = 4

    def __reduce__(self):
        return (self.__class__, (self.length, self.null_term, self.encoding))


    def parse_unpacked(self, unpacked_data):
        """
        :param unpacked_data: a python list of the unpacked elements
        :return: (value, number of items used from list)
        """

        strlen = unpacked_data[0]
        if self.encoding is None:
            str_data = unpacked_data[1].decode()
        else:
            str_data = unpacked_data[1].decode(encoding=self.encoding)

        if self.null_term:
            str_data = str_data[:str_data.find('\x00')]
        else:
            str_data = str_data[:strlen]

        return str_data, 2

    def create_packlist(self, value):
        """
        :return: Returns a list that gets combined onto the end of the current list to be packed.
         It should match the format returned by get_format
        """
        if self.encoding is not None:
            return [len(value), value.encode(encoding=self.encoding)]
        else:
            return [len(value), value.encode()]


class SPARE(CIPType):
    """
    This StructObject provides a way to add "padding" bytes to your structure.
    """

    def __init__(self, length):
        '''

        :param length: how many bytes of padding to use
        '''
        self.length = length
        self.format = '{}x'.format(self.length)
        self.struct = struct.Struct(self.format)
        self.alignment = 1

    def __reduce__(self):
        return (self.__class__, (self.length,))

    def parse_unpacked(self, unpacked_data):
        """
        Because this is a padding value, we will return that we took 0 elements off the unpack_data list.
        and we'll return None as our value
        :param unpacked_data: a python list of the unpacked elements
        :return: value, number of items used from list
        """
        return None, 0

    def create_packlist(self, value):
        """
        in this case we return nothing because this is padding and no values need to end up converted
        to bytes
        :return: returns a list that gets combined onto the end of the current list to be packed.
         It should match the format returned by get_format
        """
        return []


PADDING = SPARE  # alias


class ARRAY(CIPType):
    def __init__(self, data_type, length):
        """
        Structure object for creating arrays.  These map to python lists
        :param data_type: a CIPType): instance
        param length: how many elements the array contains
        """
        self.data_type = data_type
        self.length = length
        self.format = self.data_type.format * self.length
        self.struct = struct.Struct(self.format)
        self.alignment = 4

    def __reduce__(self):
        return (self.__class__, (self.data_type, self.length))

    def parse_unpacked(self, unpacked_data):
        """
        In the case of the array we will take the first <self.length> items from the unpacked data list
        and let the caller know that's how many we needed
        :param unpacked_data: a python list of the unpacked elements
        :return: value, number of items used from list
        """

        item_count = 0
        value_list = []
        for i in range(self.length):
            new_value, new_count = self.data_type.parse_unpacked(unpacked_data[item_count:])
            item_count += new_count
            value_list.append(new_value)
        return value_list, item_count

    def create_packlist(self, value):
        """
        :return:
         returns a list that gets combined onto the end of the current list to be packed.
         It should match the format returned by get_format
         In this case value should be a listlike object
        """
        packlist = []
        for i in range(self.length):
            new_list = self.data_type.create_packlist(value[i])
            packlist += new_list
        return packlist

class BOOLS(CIPType):
    def __init__(self, BitNames):
        """
        Structure object for creating packed bools in a UDT
        :param BitNames: a list of strings, one per bit in order from first to last
        """

        self.bitlen = 8

        # bit packed structs are aligned on 32 bit words.  Figure out how many we've got.
        self.length = ((len(BitNames) - 1) // self.bitlen) + 1
        self.format = '{}B'.format(self.length)
        self.struct = struct.Struct(self.format)
        self.BitNames = BitNames
        self.alignment = 1

    def add(self, bitname):
        self.BitNames.append(bitname)

    def __reduce__(self):
        return (self.__class__, (self.length,))

    def parse_unpacked(self, unpacked_data):
        """
        :param unpacked_data: a python list of the unpacked elements
        :return: (value, number of items used from list)
        """

        str_data = {}
        print(unpacked_data)

        bitpos = 0
        for bitname in self.BitNames:
            wordpos = bitpos // self.bitlen
            wordbit = bitpos % self.bitlen
            word = unpacked_data[wordpos]
            mask = 1 << wordbit
            result = word & mask != 0
            if bitname != "":
                str_data[bitname] = result
            bitpos+= 1

        return str_data, self.length

    def create_packlist(self, value):
        """
        :return: Returns a list that gets combined onto the end of the current list to be packed.
         It should match the format returned by get_format
        """
        bitpos = 0
        words = [0] * self.length
        for bitname in self.BitNames:
            wordpos = bitpos // 32
            wordbit = bitpos % 32
            word = words[wordpos]
            bitval = value.get(bitname)
            if bitval:
                mask =  1 << wordbit
                words[wordpos] |= mask
            bitpos+= 1
        return words

    def null(self):
        """
        :return: a null byte array as long as this structure
        """
        return bytes([0] * len(self))


class UDT(CIPType):
    """
    This is the core binary struct class that will need used.
    """

    def __init__(self):
        """
        Initialize this class with a structure ordereddict (see example in the tests) to get an object
        you can use to convert back and forth from binary data and dicts
        :param structure_dict: ordereddict of the ALLCAPS types.  Can be nested to create complex structs
        """
        self.endianness = ''

        self.format = '' + self.endianness

        self.structure_def = []
        self.struct = struct.Struct(self.format)
        self.alignment = 4

    def __setitem__(self, item, value):
        #if isinstance(value, BOOL):
        #    # adding a bool we need to see if we're currently building a bool byte
        #    if isinstance(self.structure_def[-1][1], BOOLS):
        #        # already packing some bools.
        #        self.structure_def[-1][1].Add(item)

        self.structure_def.append((item, value))
        self.rebuild_format()

        # per 1756-rm094_-en-p.pdf any UDT with an 8-byte data type in it gets promoted to
        # an 8-byte alignment also.
        if value.alignment == 8:
            self.alignment = 8
    
    def rebuild_format(self):
        self.format = self.endianness
        for k, v in self.structure_def:
            s = struct.Struct(self.format)
            offset = s.size % v.alignment
            if offset > 0 :
                self.format += "{}x".format(v.alignment - offset)
            self.format += v.format

        print(self.format)
        self.struct = struct.Struct(self.format)

    def __reduce__(self):
        return (self.__class__, (self.structure_def,))

    def create_packlist(self, value):
        """
         returns a list that gets combined onto the end of the current list to be packed.
         It should match the format returned by get_format
        :return:
        """
        data_list = []
        keys = list(self.structure_def.keys())

        for k in keys:
            struct_type = self.structure_def[k]
            val = value.get(k)  # will return None if the key is missing
            data_list += struct_type.create_packlist(val)

        return data_list

    def parse_unpacked(self, unpacked_data):
        # final_dict = OrderedDict()
        final_dict = {}


        unpack_offset = 0
        x = 0
        for k, v in self.structure_def:
            final_dict[k], new_offset = v.parse_unpacked(unpacked_data[x + unpack_offset:])
            print(f'{k}: {final_dict[k]}')
            unpack_offset += new_offset - 1
            x += 1

        return final_dict, x + unpack_offset




# note that for some reason the bits on these built-in data types are backwards (big endian on a 16 bit word boundary)
TIMER = UDT()
TIMER['StatusBits'] = BOOLS( [""]*29 + ["DN", "TT", "EN"])
TIMER['PRE'] = DINT
TIMER['ACC'] = DINT

COUNTER = UDT()
COUNTER['StatusBits'] = BOOLS([""] * 27 + ["UN", "OV", "DN", "CD", "CU"])
COUNTER['PRE'] = DINT
COUNTER['ACC'] = DINT
