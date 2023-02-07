__test__ = False

if __name__ == "__main__":
    import eventlet
    eventlet.monkey_patch(builtins=True, os=True)

    with open(__file__, mode="rt", buffering=16):
        pass

    print("pass")
