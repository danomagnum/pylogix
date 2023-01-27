import struct
from collections import OrderedDict


class CIPType(object):
    """
    Complex data such as arrays and nested structs need to have a little wits about them.  This object is the
    template for classes that provide those wits.
    """

    def __init__(self):
        """
        Needs to define the format and instantiate the struct
        """
        self.format = ''
        self.endianness = '<'
        self.struct = struct.Struct(self.format)


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
        if endian is not None:
          unpack_struct = struct.Struct(endian + self.format)
        unpacked = unpack_struct.unpack_from(data_array, offset)

        return self.parse_unpacked(unpacked)[0]



class BasicType(CIPType):
    def __init__(self, format_str):
        self.format = format_str
        self.endianness = '<'
        self.struct = struct.Struct(self.format)

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
SINT = BasicType('b')
USINT = BasicType('B')
BOOL = BasicType('?')
INT = BasicType('h')
UINT = BasicType('H')
DINT = BasicType('l')
UDINT = BasicType('L')
LINT = BasicType('q')
ULINT = BasicType('Q')
REAL = BasicType('f')
LREAL = BasicType('d')


class BYTES(CIPType):
    def __init__(self, length):
        """
        Structure object for creating strings that correspond to python byte objects bytes (no encodings)
        :param length: how many elements the array contains
        """
        self.length = length
        self.format = f'{length}s'
        self.struct = struct.Struct(self.format)

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
    def __init__(self, length, null_term=True, encoding=None):
        """
        Structure object for creating strings.  These map to python strings
        :param length: how many elements the array contains
        :param null_term: whether the returned string should end at the first null byte
        :param encoding: what encoding to use when converting to a string and back
        """
        self.length = length
        self.encoding = encoding
        self.null_term = null_term
        self.format = f'{length}s'
        self.struct = struct.Struct(self.format)

    def __reduce__(self):
        return (self.__class__, (self.length, self.null_term, self.encoding))


    def parse_unpacked(self, unpacked_data):
        """
        :param unpacked_data: a python list of the unpacked elements
        :return: (value, number of items used from list)
        """

        if self.encoding is None:
            str_data = unpacked_data[0].decode()
        else:
            str_data = unpacked_data[0].decode(encoding=self.encoding)

        if self.null_term:
            str_data = str_data[:str_data.find('\x00')]

        return str_data, 1

    def create_packlist(self, value):
        """
        :return: Returns a list that gets combined onto the end of the current list to be packed.
         It should match the format returned by get_format
        """
        if self.encoding is not None:
            return [value.encode(encoding=self.encoding)]
        else:
            return [value.encode()]


class SPARE(CIPType):
    """
    This StructObject provides a way to add "padding" bytes to your structure.
    """

    def __init__(self, length):
        '''

        :param length: how many bytes of padding to use
        '''
        self.length = length
        self.format = f'{self.length}x'
        self.struct = struct.Struct(self.format)

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


class UDT(CIPType):
    """
    This is the core binary struct class that will need used.
    """

    def __init__(self, structure_dict, endianness=None):
        """
        Initialize this class with a structure ordereddict (see example in the tests) to get an object
        you can use to convert back and forth from binary data and dicts
        :param structure_dict: ordereddict of the ALLCAPS types.  Can be nested to create complex structs
        """
        self.structure_dict = structure_dict
        if endianness is None:
          endianness = ''
        self.endianness = endianness

        self.format = '' + self.endianness

        for k, v in self.structure_dict.items():
            if isinstance(v, OrderedDict):
                new_binarystructure = UDT(v)
                self.structure_dict[k] = new_binarystructure
                v = new_binarystructure

            self.format += v.format

        self.struct = struct.Struct(self.format)

    def __reduce__(self):
        return (self.__class__, (self.structure_dict,))

    def create_packlist(self, value):
        """
         returns a list that gets combined onto the end of the current list to be packed.
         It should match the format returned by get_format
        :return:
        """
        data_list = []
        keys = list(self.structure_dict.keys())

        for k in keys:
            struct_type = self.structure_dict[k]
            val = value.get(k)  # will return None if the key is missing
            data_list += struct_type.create_packlist(val)

        return data_list

    def parse_unpacked(self, unpacked_data):
        # final_dict = OrderedDict()
        final_dict = {}

        keys = list(self.structure_dict.keys())

        unpack_offset = 0
        for x in range(len(keys)):
            key = keys[x]
            format_type = self.structure_dict[key]
            final_dict[key], new_offset = format_type.parse_unpacked(unpacked_data[x + unpack_offset:])
            unpack_offset += new_offset - 1

        return final_dict, len(keys) + unpack_offset


class BITS(CIPType):
    def __init__(self, BitNames):
        """
        Structure object for creating strings that correspond to python byte objects bytes (no encodings)
        :param length: how many elements the array contains
        """
        
        # bit packed structs are aligned on 16 bit words.  Figure out how many we've got.
        self.length = len(BitNames) // 16
        self.format = f'{self.length}H'
        self.struct = struct.Struct(self.format)
        self.BitNames = BitNames

    def __reduce__(self):
        return (self.__class__, (self.length,))

    def parse_unpacked(self, unpacked_data):
        """
        :param unpacked_data: a python list of the unpacked elements
        :return: (value, number of items used from list)
        """

        str_data = {}

        bitpos = 0
        for bitname in self.BitNames:
            wordpos = bitpos // 16
            wordbit = bitpos % 16
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
            wordpos = bitpos // 16
            wordbit = bitpos % 16
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



# note that for some reason the bits on these built-in data types are backwards (big endian on a 16 bit word boundary)
timer_struct = OrderedDict()
timer_struct['Padding'] = SPARE(2) 
timer_struct['StatusBits'] = BITS(("", "", "", "", "", "", "", "", "", "", "", "", "", "DN", "TT", "EN"))
timer_struct['PRE'] = DINT
timer_struct['ACC'] = DINT
TIMER = UDT(timer_struct)

counter_struct = OrderedDict()
counter_struct['Padding'] = SPARE(2)
counter_struct['StatusBits'] = BITS(("", "", "", "", "", "", "", "", "", "", "", "UN", "OV", "DN", "CD", "CU"))
counter_struct['PRE'] = DINT
counter_struct['ACC'] = DINT
COUNTER = UDT(counter_struct)
