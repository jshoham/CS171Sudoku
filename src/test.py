import sys
import time

for i in range(9):
    sys.stdout.write('\rthis is line {}'.format(i))
    time.sleep(0.5)
sys.stdout.write('\n')