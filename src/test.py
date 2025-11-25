# src/test.py

from src.scrape_kworb_top400 import main
from pathlib import Path

if __name__ == "__main__":
    print("Testing scrape_kworb_top400.py")

    root = Path(__file__).resolve().parents[1]
    kworb_top200_test = root / "data" / "kworb_top_200_test.csv"

    # testing with a smaller sample set from Kworb
    import sys
    sys.argv = ["scrape_kworb_top400.py", "--out", str(kworb_top200_test), "--limit", "200"]

    main()

    if kworb_top200_test.exists():
        print("Test file created, yay!:", kworb_top200_test)
    else:
        print("Test file not created...")
