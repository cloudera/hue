from collections import deque
import time


class cache(object):
    """ Cache decorator that memoizes the return value of a method for some time.
    """
    def __init__(self, ttl):
        self.ttl = ttl
        # Queue that contains tuples of (expiration_time, key) in order of expiration
        self.expiration_queue = deque()
        self.cached_values = {}

    def purge_expired(self, now):
        while len(self.expiration_queue) > 0 and self.expiration_queue[0][0] < now:
            expired = self.expiration_queue.popleft()
            del self.cached_values[expired[1]]

    def add_to_cache(self, key, value, now):
        assert key not in self.cached_values, "Re-adding the same key breaks proper expiration"
        self.cached_values[key] = value
        # Since TTL is constant, expiration happens in order of addition to queue,
        # so queue is always ordered by expiration time.
        self.expiration_queue.append((now + self.ttl, key))

    def get_from_cache(self, key):
        return self.cached_values[key]

    def __call__(self, fn):
        def wrapped(this, *args):
            now = time.time()
            self.purge_expired(now)

            try:
                cached_value = self.get_from_cache(args)
            except KeyError:
                cached_value = fn(this, *args)
                self.add_to_cache(args, cached_value, now)

            return cached_value

        return wrapped
