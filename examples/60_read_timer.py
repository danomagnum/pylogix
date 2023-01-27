'''
the following import is only necessary because eip is not in this directory
'''
import sys
sys.path.append('..')


'''
The simplest example of reading a timer from a PLC

NOTE: You only need to call .Close() after you are done exchanging
data with the PLC.  If you were going to read in a loop or read
more tags, you wouldn't want to call .Close() every time.
'''
from pylogix import PLC, udt

comm = PLC()
comm.IPAddress = '10.40.39.26'
ret = comm.Read('Timer1')
timer_data = udt.TIMER.unpack(ret.Value)
# timer_data is now in the form of {'Padding': None, 'StatusBits': {'DN': True, 'TT': False, 'EN': True}, 'PRE': 1, 'ACC': 2}
print(timer_data)

if timer_data['StatusBits']['DN']:
    print("timer is done!")
else:
    left = timer_data['PRE'] - timer_data['ACC']
    print("{} ms left.".format(left))

comm.Close()
