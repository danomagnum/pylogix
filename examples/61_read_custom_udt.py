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
# to do this, we dfine a UDT and then fill in the fields in the same order
# as defined on the PLC
basicUDT = udt.UDT()
basicUDT["Bools"]= udt.BOOLS(["b_BOOL"]) # bits in UDTs are packed into DINTs.  This lets you break them out.
basicUDT["b_BITS"]= udt.DINT
basicUDT["b_SINT"]= udt.SINT
basicUDT["b_INT"]= udt.INT
basicUDT["b_DINT"]= udt.DINT
basicUDT["b_LINT"]= udt.LINT
basicUDT["b_REAL"]= udt.REAL
basicUDT["b_STRING"]= udt.STRING() # default 82 length string
basicUDT["b_Timer"]= udt.TIMER


comm = PLC()
comm.IPAddress = '192.168.2.241'
ret = comm.Read('UDTBasic')
print(list(ret.Value))
udt_data = basicUDT.unpack(ret.Value)
print(udt_data)


comm.Close()
