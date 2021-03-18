from threading import Thread

def f():
    for i in range(1000):
        print(i)

def g():
    x = Thread(target = f)
    x.start()

a = [(1, 2, 3), ((1, 2, 3 ), 4)]

print(str(a))
