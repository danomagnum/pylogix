'''
the following import is only necessary because eip is not in this directory
'''
import sys
from collections import OrderedDict
sys.path.append('..')


'''
The simplest example of reading a udt from a PLC

NOTE: You only need to call .Close() after you are done exchanging
data with the PLC.  If you were going to read in a loop or read
more tags, you wouldn't want to call .Close() every time.
'''
from pylogix import PLC, udt

# First we have to define the UDT structure to match the one in the PLC.
# to do this, we dfine an OrderedDict and then fill it one key at a time in the same
# order the UDT is defined.  Finally we have to create a UDT from the OrderedDict
basicUDT = udt.UDT()
basicUDT["Bools2"]= udt.BOOLS(["b_BOOL"]) # bits in UDTs are packed.  This lets you break them out.
basicUDT["b_BITS"]= udt.DINT
basicUDT["b_SINT"]= udt.SINT
basicUDT["b_INT"]= udt.INT
basicUDT["b_DINT"]= udt.DINT
basicUDT["b_LINT"]= udt.LINT
basicUDT["b_REAL"]= udt.REAL
basicUDT["b_STRING"]= udt.STRING() # default 82 length string
basicUDT["b_Timer"]= udt.TIMER


# Defining another UDT that contains the first one.
NestedUDT = udt.UDT()
NestedUDT['Bools'] = udt.BOOLS(['b_Bool1', 'b_Bool2'])
NestedUDT['b_Basic'] = basicUDT # UDTs can be nested
NestedUDT['b_DINT'] = udt.DINT
NestedUDT['b_Counter'] = udt.COUNTER

comm = PLC()
comm.IPAddress = '192.168.2.241'
ret = comm.Read('Program:MainProgram.NestedUDT')
print(f'Raw ({len(ret.Value)}): {list(ret.Value)}')
udt_data = NestedUDT.unpack(ret.Value)
print(udt_data)


comm.Close()
