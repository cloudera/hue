from mako.util import LRUCache
import string, unittest, time, random

import thread

class item:
    def __init__(self, id):
        self.id = id

    def __str__(self):
        return "item id %d" % self.id

class LRUTest(unittest.TestCase):


    def testlru(self): 
        l = LRUCache(10, threshold=.2)
 
        for id in range(1,20):
            l[id] = item(id)
 
        # first couple of items should be gone
        self.assert_(not l.has_key(1)) 
        self.assert_(not l.has_key(2))
 
        # next batch over the threshold of 10 should be present
        for id in range(11,20):
            self.assert_(l.has_key(id))

        l[12]
        l[15]
        l[23] = item(23)
        l[24] = item(24)
        l[25] = item(25)
        l[26] = item(26)
        l[27] = item(27)

        self.assert_(not l.has_key(11))
        self.assert_(not l.has_key(13))
 
        for id in (25, 24, 23, 14, 12, 19, 18, 17, 16, 15):
            self.assert_(l.has_key(id)) 

    def _disabled_test_threaded(self):
        size = 100
        threshold = .5
        all_elems = 2000
        hot_zone = range(30,40)
        cache = LRUCache(size, threshold)
 
        # element to store
        class Element(object):
            def __init__(self, id):
                self.id = id
                self.regets = 0
 
        # return an element.  we will favor ids in the relatively small
        # "hot zone" 25% of  the time.
        def get_elem():
            if random.randint(1,4) == 1:
                return hot_zone[random.randint(0, len(hot_zone) - 1)]
            else:
                return random.randint(1, all_elems)
 
        total = [0]
        # request thread.
        def request_elem():
            while True:
                total[0] += 1
                id = get_elem()
                try:
                    elem = cache[id]
                    elem.regets += 1
                except KeyError:
                    e = Element(id)
                    cache[id] = e
 
                time.sleep(random.random() / 1000)

        for x in range(0,20):
            thread.start_new_thread(request_elem, ())
 
        # assert size doesn't grow unbounded, doesnt shrink well below size
        for x in range(0,5):
            time.sleep(1)
            print "size:", len(cache)
            assert len(cache) < size + size * threshold * 2
            assert len(cache) > size - (size * .1)
 
        # computs the average number of times a range of elements were "reused",
        # i.e. without being removed from the cache.
        def average_regets_in_range(start, end):
            elem = [e for e in cache.values() if e.id >= start and e.id <= end]
            if len(elem) == 0:
                return 0
            avg = sum([e.regets for e in elem]) / len(elem)
            return avg

        hotzone_avg = average_regets_in_range(30, 40)
        control_avg = average_regets_in_range(450,760)
        total_avg = average_regets_in_range(0, 2000)
 
        # hotzone should be way above the others
        print "total fetches", total[0], "hotzone", \
                                hotzone_avg, "control", \
                                control_avg, "total", total_avg
 
        assert hotzone_avg > total_avg * 5 > control_avg * 5
 
 

