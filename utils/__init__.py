import sys
import os

source_root = os.path.dirname(__file__)
if source_root not in sys.path:
    sys.path.insert(0, source_root)