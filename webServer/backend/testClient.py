import zmq
host = '127.0.0.1'
port = 1234 
def ping():
    """Sends ping requests and waits for replies."""
    context = zmq.Context()
    sock = context.socket(zmq.REQ)
    sock.connect('tcp://%s:%s' % (host, port))

    for i in range(5):
        sock.send_json(['connectionReq', i])
        rep = sock.recv_json()
        print('Ping got reply:', rep)

    sock.send_json(['plzdiekthxbye', None])

if __name__ == '__main__':
    ping()
