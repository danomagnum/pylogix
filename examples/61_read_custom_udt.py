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
BasicUDT_Struct = OrderedDict()
BasicUDT_Struct["Bools"]= udt.BOOLS(["b_BOOL"]) # bits in UDTs are packed into DINTs.  This lets you break them out.
BasicUDT_Struct["b_BITS"]= udt.DINT
BasicUDT_Struct["b_SINT"]= udt.SINT
BasicUDT_Struct["b_INT"]= udt.INT
BasicUDT_Struct["b_DINT"]= udt.DINT
BasicUDT_Struct["b_LINT"]= udt.LINT
BasicUDT_Struct["b_REAL"]= udt.REAL
BasicUDT_Struct["b_STRING"]= udt.STRING() # default 82 length string
BasicUDT_Struct["b_Timer"]= udt.TIMER

basicUDT = udt.UDT(BasicUDT_Struct)

comm = PLC()
comm.IPAddress = '192.168.2.241'
ret = comm.Read('UDTBasic')
print(list(ret.Value))
udt_data = basicUDT.unpack(ret.Value)
print(udt_data)


comm.Close()
