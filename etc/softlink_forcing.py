import os
import shutil

# Path to the folder you want 'forcing' to link to
target_link = '/home/menaka/projects/def-btolson/menaka/MulCal/OstrichRaven/RavenInput/forcing'  # <-- change this!

# Walk through the current directory
for root, dirs, files in os.walk('/home/menaka/scratch/MulCal', topdown=True):
    if 'forcing' in dirs:
        full_path = os.path.join(root, 'forcing')
        print(f'Replacing: {full_path}')

        # Remove symlink or directory
        if os.path.islink(full_path):
            os.unlink(full_path)  # removes symlink
            print(f'Removed existing symlink: {full_path}')
        elif os.path.isdir(full_path):
            shutil.rmtree(full_path)  # removes actual folder
            print(f'Removed existing directory: {full_path}')

        # Create the symlink
        os.symlink(target_link, full_path)
        print(f'Created symlink at {full_path} -> {target_link}')
