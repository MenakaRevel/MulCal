import os
import shutil

# Root of the tree you want to clean
ROOT = "/home/menaka/scratch/MulCal"

deleted = 0
for current_dir, dirnames, _ in os.walk(ROOT, topdown=False):   # bottom‑up so children go first
    for d in dirnames:
        if d.startswith("processor_"):
            full_path = os.path.join(current_dir, d)
            try:
                shutil.rmtree(full_path)
                print(f"Removed: {full_path}")
                deleted += 1
            except Exception as e:
                print(f"⚠️  Couldn’t delete {full_path}: {e}")

print(f"\nFinished. {deleted} processor_* directories removed.")