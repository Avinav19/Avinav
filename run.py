import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_DIR))

try:
    from data.Avinav import main
    main()

except ImportError as error:
    print("AVINAV could not load.")
    print("Check that data/Avinav.py exists.")
    print("Details:", error)

except KeyboardInterrupt:
    print("\nAVINAV closed.")
    
