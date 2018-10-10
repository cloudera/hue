import eventlet
from eventlet.green import profile
import tests


def test_green_profile_basic():
    statement = 'eventlet.sleep()'
    result = profile.Profile().runctx(statement, {'eventlet': eventlet}, {})
    assert ('profile', 0, statement) in result.timings
