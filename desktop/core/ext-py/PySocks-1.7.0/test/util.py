import time
from socket import socket, error, AF_INET, SOCK_STREAM


def wait_for_socket(server_name, host, port, timeout=2):
    ok = False
    for x in range(10):
        try:
            print('Testing [%s] proxy server on %s:%d'
                  % (server_name, host, port))
            s = socket(AF_INET, SOCK_STREAM)
            s.connect((host, port))
            s.close()
        except error as ex:
            print('ERROR', ex)
            time.sleep(timeout/10.0)
        else:
            print('Connection established')
            ok = True
            break
    if not ok:
        raise Exception('The %s proxy server has not started in %d seconds'
                        % (server_name, timeout))
