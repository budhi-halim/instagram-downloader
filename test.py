from datetime import datetime
import time

timestamp = datetime.now()
time.sleep(3)
timestamp2 = datetime.now()

# print(timestamp)
# print(timestamp.strftime("%Y-%m-%d %H:%M:%S"))
print((timestamp2 - timestamp).strftime('%H:%M:%S'))
