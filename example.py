import threading

def run_http():
    print("HTTP сервер запущено.")

def run_udp():
    print("UDP сервер запущено.")
    while True:
        pass

if __name__ == '__main__':
    t1 = threading.Thread(target=run_http)
    t2 = threading.Thread(target=run_udp)

t1.start()
t2.start()