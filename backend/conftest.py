import sys
import os
from pathlib import Path

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Ensure testing flag is set for instant test execution
os.environ["TESTING"] = "true"
