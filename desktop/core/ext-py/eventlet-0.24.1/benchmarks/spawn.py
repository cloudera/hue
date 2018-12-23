"""Compare spawn to spawn_n"""
from __future__ import print_function

import eventlet
import benchmarks


def cleanup():
    eventlet.sleep(0.2)


iters = 10000
best = benchmarks.measure_best(
    5, iters,
    'pass',
    cleanup,
    eventlet.sleep)
print("eventlet.sleep (main)", best[eventlet.sleep])

gt = eventlet.spawn(
    benchmarks.measure_best, 5, iters,
    'pass',
    cleanup,
    eventlet.sleep)
best = gt.wait()
print("eventlet.sleep (gt)", best[eventlet.sleep])


def dummy(i=None):
    return i


def run_spawn():
    eventlet.spawn(dummy, 1)


def run_spawn_n():
    eventlet.spawn_n(dummy, 1)


def run_spawn_n_kw():
    eventlet.spawn_n(dummy, i=1)


best = benchmarks.measure_best(
    5, iters,
    'pass',
    cleanup,
    run_spawn_n,
    run_spawn,
    run_spawn_n_kw)
print("eventlet.spawn", best[run_spawn])
print("eventlet.spawn_n", best[run_spawn_n])
print("eventlet.spawn_n(**kw)", best[run_spawn_n_kw])
print("%% %0.1f" % ((best[run_spawn] - best[run_spawn_n]) / best[run_spawn_n] * 100))

pool = None


def setup():
    global pool
    pool = eventlet.GreenPool(iters)


def run_pool_spawn():
    pool.spawn(dummy, 1)


def run_pool_spawn_n():
    pool.spawn_n(dummy, 1)


def cleanup_pool():
    pool.waitall()


best = benchmarks.measure_best(
    3, iters,
    setup,
    cleanup_pool,
    run_pool_spawn,
    run_pool_spawn_n,
)
print("eventlet.GreenPool.spawn", best[run_pool_spawn])
print("eventlet.GreenPool.spawn_n", best[run_pool_spawn_n])
print("%% %0.1f" % ((best[run_pool_spawn] - best[run_pool_spawn_n]) / best[run_pool_spawn_n] * 100))
