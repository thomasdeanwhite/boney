import sys
import os

path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../main'))

if not path in sys.path:
    print("Enhancing syspath:", path)
    sys.path.insert(0, path)
