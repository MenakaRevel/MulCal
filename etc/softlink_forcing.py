#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
import sys

def main():
    # Validate input
    if len(sys.argv) < 2:
        print("Usage: "+sys.argv[0]+" <tag> <odir>")
        sys.exit(1)

    reg  = sys.argv[1]
    tag  = sys.argv[2]
    odir = sys.argv[3]

    ROOT = os.path.join(odir,tag)

    if not os.path.isdir(ROOT):
        print(f"❌ Error: Directory '{ROOT}' does not exist.")
        sys.exit(1)

    # Path to the real forcing directory
    target_link = f'/project/def-btolson/menaka/{reg}_OstrichRaven/RavenInput/forcing'

    if not os.path.isdir(target_link):
        print(f"❌ Error: Target forcing directory '{target_link}' does not exist.")
        sys.exit(1)

    updated = 0
    for root, dirs, _ in os.walk(ROOT, topdown=True):
        if 'forcing' in dirs:
            full_path = os.path.join(root, 'forcing')
            print(f"🔁 Replacing: {full_path}")

            try:
                # Remove old symlink or folder
                if os.path.islink(full_path):
                    os.unlink(full_path)
                    # print(f"🧹 Removed symlink: {full_path}")
                elif os.path.isdir(full_path):
                    shutil.rmtree(full_path)
                    # print(f"🧹 Removed directory: {full_path}")

                # Create new symlink
                os.symlink(target_link, full_path)
                # print(f"🔗 Created symlink: {full_path} -> {target_link}")
                updated += 1
            except Exception as e:
                print(f"⚠️  Failed to update {full_path}: {e}")

    print(f"\n✅ Done. Replaced {updated} 'forcing' directories with symlinks under {ROOT}.")

if __name__ == "__main__":
    main()