#._cv_part guppy.heapy.test.test_dependencies

# Test the libraries we are dependent on
# Only sets right now.

def test_main(debug = 0):
    print 'Testing sets'
    from guppy.sets import test
    test.test_main()

if __name__ == "__main__":
    test_main()


