# src/tests.py

from src.main import main

if __name__ == "__main__":
    print("Running tests: scrape → spotify pull")
    try:
        main()
        print("Completed.")
    except Exception as e:
        print("Test failed while running main()")
        print(f"Error: {e}")
