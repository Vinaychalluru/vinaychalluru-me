import timeit
from pathlib import Path
import os

# Simulate the environment
# In app/config.py:
# BASE_DIR = Path(__file__).resolve().parent
# STATIC_DIR = BASE_DIR / "staticfiles"
# Here we just use absolute paths for the benchmark
BASE_DIR = Path("/app/app").resolve()
STATIC_DIR = BASE_DIR / "staticfiles"

def current_logic():
    # This matches the code in app/main.py:57
    favicon_path = STATIC_DIR / 'about' / 'icons' / 'VinayChalluru.ico'
    if favicon_path.exists():
        return str(favicon_path)
    return None

# Optimization 1: Path object is pre-created
FAVICON_PATH = STATIC_DIR / 'about' / 'icons' / 'VinayChalluru.ico'

def optimized_logic_path_cached():
    if FAVICON_PATH.exists():
        return str(FAVICON_PATH)
    return None

# Optimization 2: Existence and Path string are pre-calculated
FAVICON_EXISTS = FAVICON_PATH.exists()
FAVICON_PATH_STR = str(FAVICON_PATH)

def optimized_logic_fully_cached():
    if FAVICON_EXISTS:
        return FAVICON_PATH_STR
    return None

def main():
    iterations = 100000
    print(f"Running benchmark with {iterations} iterations...")

    t1 = timeit.timeit(current_logic, number=iterations)
    print(f"Current logic: {t1:.4f}s")

    t2 = timeit.timeit(optimized_logic_path_cached, number=iterations)
    print(f"Optimized logic (Path cached): {t2:.4f}s")

    t3 = timeit.timeit(optimized_logic_fully_cached, number=iterations)
    print(f"Optimized logic (Fully cached): {t3:.4f}s")

    improvement_p = (t1 - t2) / t1 * 100
    print(f"Improvement (Path cached): {improvement_p:.2f}%")

    improvement_f = (t1 - t3) / t1 * 100
    print(f"Improvement (Fully cached): {improvement_f:.2f}%")

if __name__ == "__main__":
    main()
