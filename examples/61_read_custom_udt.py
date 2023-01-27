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
udt_str["MyDint"]= udt.DINT
udt_str["MyReal"]= udt.REAL
udt_str["Flags"]= udt.BITS(("MyFlag1", "MyFlag2"))
udt_str["MyTimer"]= udt.TIMER
udt_str["MyInt"]= udt.INT

myudt = udt.UDT(udt_str)

comm = PLC()
comm.IPAddress = '10.40.39.26'
ret = comm.Read('MyExampleUDT')
udt_data = myudt.unpack(ret.Value)
print(list(ret.Value))
print(udt_data)


comm.Close()
