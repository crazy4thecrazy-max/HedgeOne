import sys
import os

# Add the package to the Python path
sys.path.append(os.path.dirname(__file__))

from hedgeone_agent.__main__ import main

if __name__ == "__main__":
    main()