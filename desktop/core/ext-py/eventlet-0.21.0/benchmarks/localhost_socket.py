"""Benchmark evaluating eventlet's performance at speaking to itself over a localhost socket."""
from __future__ import print_function

import time

import benchmarks
from eventlet.support import six


BYTES = 1000
SIZE = 1
CONCURRENCY = 50
TRIES = 5


def reader(sock):
    expect = BYTES
    while expect > 0:
        d = sock.recv(min(expect, SIZE))
        expect -= len(d)


def writer(addr, socket_impl):
    sock = socket_impl(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(addr)
    sent = 0
    while sent < BYTES:
        d = 'xy' * (max(min(SIZE / 2, BYTES - sent), 1))
        sock.sendall(d)
        sent += len(d)


def green_accepter(server_sock, pool):
    for i in six.moves.range(CONCURRENCY):
        sock, addr = server_sock.accept()
        pool.spawn_n(reader, sock)


def heavy_accepter(server_sock, pool):
    for i in six.moves.range(CONCURRENCY):
        sock, addr = server_sock.accept()
        t = threading.Thread(None, reader, "reader thread", (sock,))
        t.start()
        pool.append(t)


import eventlet.green.socket
import eventlet

from eventlet import debug
debug.hub_exceptions(True)


def launch_green_threads():
    pool = eventlet.GreenPool(CONCURRENCY * 2 + 1)
    server_sock = eventlet.green.socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind(('localhost', 0))
    server_sock.listen(50)
    addr = ('localhost', server_sock.getsockname()[1])
    pool.spawn_n(green_accepter, server_sock, pool)
    for i in six.moves.range(CONCURRENCY):
        pool.spawn_n(writer, addr, eventlet.green.socket.socket)
    pool.waitall()


import threading
import socket


def launch_heavy_threads():
    threads = []
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind(('localhost', 0))
    server_sock.listen(50)
    addr = ('localhost', server_sock.getsockname()[1])
    accepter_thread = threading.Thread(
        None, heavy_accepter, "accepter thread", (server_sock, threads))
    accepter_thread.start()
    threads.append(accepter_thread)
    for i in six.moves.range(CONCURRENCY):
        client_thread = threading.Thread(None, writer, "writer thread", (addr, socket.socket))
        client_thread.start()
        threads.append(client_thread)
    for t in threads:
        t.join()


if __name__ == "__main__":
    import optparse
    parser = optparse.OptionParser()
    parser.add_option('--compare-threading', action='store_true', dest='threading', default=False)
    parser.add_option('-b', '--bytes', type='int', dest='bytes',
                      default=BYTES)
    parser.add_option('-s', '--size', type='int', dest='size',
                      default=SIZE)
    parser.add_option('-c', '--concurrency', type='int', dest='concurrency',
                      default=CONCURRENCY)
    parser.add_option('-t', '--tries', type='int', dest='tries',
                      default=TRIES)

    opts, args = parser.parse_args()
    BYTES = opts.bytes
    SIZE = opts.size
    CONCURRENCY = opts.concurrency
    TRIES = opts.tries

    funcs = [launch_green_threads]
    if opts.threading:
        funcs = [launch_green_threads, launch_heavy_threads]
    results = benchmarks.measure_best(TRIES, 3,
                                      lambda: None, lambda: None,
                                      *funcs)
    print("green:", results[launch_green_threads])
    if opts.threading:
        print("threads:", results[launch_heavy_threads])
        print("%", (results[launch_green_threads] - results[launch_heavy_threads]
                    ) / results[launch_heavy_threads] * 100)
