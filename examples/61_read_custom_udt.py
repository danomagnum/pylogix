'''
the following import is only necessary because eip is not in this directory
'''
import sys
from collections import OrderedDict
sys.path.append('..')


'''
The simplest example of reading a timer from a PLC

NOTE: You only need to call .Close() after you are done exchanging
data with the PLC.  If you were going to read in a loop or read
more tags, you wouldn't want to call .Close() every time.
'''
from pylogix import PLC, udt

udt_str = OrderedDict()
udt_str["b_BOOL"]= udt.BOOLS(("MyFlag1", "MyFlag2"))
udt_str["b_BITS"]= udt.DINT
udt_str["b_SINT"]= udt.SINT
udt_str["b_INT"]= udt.INT
udt_str["b_DINT"]= udt.DINT
udt_str["b_LINT"]= udt.LINT
udt_str["b_REAL"]= udt.REAL
udt_str["b_STRING"]= udt.STRING(60)
udt_str["b_Timer"]= udt.TIMER

myudt = udt.UDT(udt_str)

comm = PLC()
comm.IPAddress = '192.168.2.241'
ret = comm.Read('UDTBasic')
print(list(ret.Value))
udt_data = myudt.unpack(ret.Value)
print(udt_data)


comm.Close()
