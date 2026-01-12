import matplotlib.pyplot as plt

temps, hums = [], []
with open("DataLog.txt") as f:
    for line in f:
        h, t = map(float, line.strip().split(','))
        temps.append(t)
        hums.append(h)

plt.subplot(2,1,1)
plt.plot(temps, 'r')
plt.title("Temperature vs Time")

plt.subplot(2,1,2)
plt.plot(hums, 'b')
plt.title("Humidity vs Time")

plt.show()