from datetime import time

# for h in range(0, 24):
#     for m in (0, 30):
#         # strFtime is used to convert the time to string format. I for hour, M for minute and p for am and pm
#         print(time(h, m).strftime('%I:%M %p'))

t = [((time(h, m).strftime('%I:%M %p')),(time(h, m).strftime('%I:%M %p'))) for h in range(0, 24) for m in (0, 30)]
print(t)