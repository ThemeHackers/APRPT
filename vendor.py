import os
import re

import sys

def main():
    if len(sys.argv) > 1:
        target_file = sys.argv[1]
    else:
        target_file = "/etc/bluetooth/main.conf"
    
    target_string = "#DeviceID = bluetooth:004C:0000:0000"
    
    if not os.path.exists(target_file):
        print(f"Error: {target_file} not found.")
        return

    try:
        with open(target_file, 'r') as f:
            lines = f.readlines()
        
        modified = False
        new_lines = []
        for line in lines:
            if "DeviceID" in line:
                new_lines.append(f"{target_string}\n")
                modified = True
            else:
                new_lines.append(line)
        
        if modified:
            with open(target_file, 'w') as f:
                f.writelines(new_lines)
            print(f"Updated {target_file} with {target_string}")
        else:
            print(f"DeviceID setting not found in {target_file}. No changes made.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
