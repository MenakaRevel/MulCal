#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
import sys
import glob

def main():
    # Validate command-line arguments
    if len(sys.argv) < 4:
        print("Usage: "+sys.argv[0]+" <reg> <tag> <odir>")
        sys.exit(1)

    reg  = sys.argv[1]
    tag  = sys.argv[2]
    odir = sys.argv[3]
    
    ROOT = os.path.join(odir, tag)

    if not os.path.isdir(ROOT):
        print(f"Error: Directory '{ROOT}' does not exist.")
        sys.exit(1)

    # Remove OstErrors*.txt, OstModel*.txt, OstOutput*.txt files
    deleted_files = 0
    patterns = ["OstErrors*.txt", "OstModel*.txt", "OstOutput*.txt"]
    for pattern in patterns:
        for file_path in glob.glob(os.path.join(ROOT, "**", pattern), recursive=True):
            try:
                os.remove(file_path)
                deleted_files += 1
            except Exception as e:
                print(f"⚠️  Couldn’t delete file {file_path}: {e}")

    print(f"\n✅ Finished cleanup in {ROOT}")
    print(f"   🧾 Removed {deleted_files} Ost*.txt files")

if __name__ == "__main__":
    main()
