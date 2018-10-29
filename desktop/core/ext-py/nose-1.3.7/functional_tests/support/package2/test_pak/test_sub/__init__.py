from test_pak import state

def setup():
    # print "SUB setup called", state, id(state)
    state.append('test_pak.test_sub.setup')

def teardown():
    # print "SUB teardown called", state, id(state)
    state.append('test_pak.test_sub.teardown')

def test_sub_init():
    state.append('test_pak.test_sub.test_sub_init')
