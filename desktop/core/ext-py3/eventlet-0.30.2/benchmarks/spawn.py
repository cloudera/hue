import contextlib

import eventlet
import benchmarks


def dummy(i=None):
    return i


def linked(gt, arg):
    return arg


def benchmark_sleep():
    eventlet.sleep()


def benchmark_spawn_link1():
    t = eventlet.spawn(dummy)
    t.link(linked, 1)
    t.wait()


def benchmark_spawn_link5():
    t = eventlet.spawn(dummy)
    t.link(linked, 1)
    t.link(linked, 2)
    t.link(linked, 3)
    t.link(linked, 4)
    t.link(linked, 5)
    t.wait()


def benchmark_spawn_link5_unlink3():
    t = eventlet.spawn(dummy)
    t.link(linked, 1)
    t.link(linked, 2)
    t.link(linked, 3)
    t.link(linked, 4)
    t.link(linked, 5)
    t.unlink(linked, 3)
    t.wait()


@benchmarks.configure(max_iters=1e5)
def benchmark_spawn_nowait():
    eventlet.spawn(dummy, 1)


def benchmark_spawn():
    eventlet.spawn(dummy, 1).wait()


@benchmarks.configure(max_iters=1e5)
def benchmark_spawn_n():
    eventlet.spawn_n(dummy, 1)


@benchmarks.configure(max_iters=1e5)
def benchmark_spawn_n_kw():
    eventlet.spawn_n(dummy, i=1)


@contextlib.contextmanager
def pool_setup(iters):
    pool = eventlet.GreenPool(iters)
    yield pool
    pool.waitall()


@benchmarks.configure(manager=pool_setup)
def benchmark_pool_spawn(pool):
    pool.spawn(dummy, 1)


@benchmarks.configure(manager=pool_setup, max_iters=1e5)
def benchmark_pool_spawn_n(pool):
    pool.spawn_n(dummy, 1)
