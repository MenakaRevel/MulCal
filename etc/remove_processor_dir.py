#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
import sys

def main():
    # Validate command-line argument
    if len(sys.argv) < 2:
        print("Usage: "+sys.argv[0]+" <tag> <odir>")
        sys.exit(1)

    tag  = sys.argv[1]
    odir = sys.argv[2]
    ROOT = os.path.join(odir,tag)

    if not os.path.isdir(ROOT):
        print(f"Error: Directory '{ROOT}' does not exist.")
        sys.exit(1)

    deleted = 0
    for current_dir, dirnames, _ in os.walk(ROOT, topdown=False):  # bottom-up traversal
        for d in dirnames:
            if d.startswith("processor_"):
                full_path = os.path.join(current_dir, d)
                try:
                    shutil.rmtree(full_path)
                    print(f"✅ Removed: {full_path}")
                    deleted += 1
                except Exception as e:
                    print(f"⚠️  Couldn’t delete {full_path}: {e}")

    print(f"\n✅ Finished. {deleted} processor_* directories removed from {ROOT}.")

if __name__ == "__main__":
    main()