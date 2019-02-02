import sys, os, unittest
path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'src/main'))

print("Enhancing syspath with src:", path)

sys.path.insert(0, path)

path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'src/test'))

print("Enhancing syspathwith tests:", path)

sys.path.insert(0, path)

test_suite = unittest.TestLoader().discover("src/test")

test_results = unittest.TextTestRunner(verbosity=2).run(test_suite)

if not test_results.wasSuccessful():
    sys.exit(1)