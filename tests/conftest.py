import sys
from pathlib import Path

# Add the 'src' directory to the Python path
# This allows tests to import modules directly from 'src'
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
