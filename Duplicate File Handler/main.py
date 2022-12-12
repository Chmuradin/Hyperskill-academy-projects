import os
import argparse
import hashlib# For part 3

parser = argparse.ArgumentParser()
parser.add_argument("path", nargs="?", default=None)
args = parser.parse_args()

if args.path is None:
    print("Directory is not specified")
    exit()

print("Enter file format:")
file_format = input().lower()

files_list = []
free_space = 0
for root, dirs, files in os.walk(args.path):
    files_list.extend([(os.path.join(root, file),
                        os.path.getsize(os.path.join(root, file)))
                       for file in files])

if file_format != "":
    files_list = [file for file in files_list if file[0].lower().endswith(f".{file_format}")]

# Part 2: Sorting
print("\nSize sorting options:")
print("1. Descending")
print("2. Ascending")

print("\nEnter a sorting option:")
size_sort = input()
while size_sort not in ["1", "2"]:
    print("\nWrong option")
    size_sort = input()
print()

size_dict = {}
for pathname, size in files_list:
    size_dict.setdefault(size, []).append(pathname)

size_keys = sorted(size_dict, reverse=True) if int(size_sort) == 1 else sorted(size_dict)

for sk in size_keys:
    print(f"{sk} bytes")
    for v in size_dict[sk]:
        print(v)
    print()
# Part 3: checking for duplicates
duplicates_list = []

print("\nCheck for duplicates?")
check_duplicates = input()
while check_duplicates not in ["yes", "no"]:
    print("Wrong option!")
    check_duplicates = input()
    print()
if check_duplicates == "no":
    exit()

counter = 1
for sk in size_keys:
    hash_dict = {}
    hash_set = set()
    print(f"{sk} bytes")
    for v in size_dict[sk]:
        with open(v, "rb") as f:
            file_hash = hashlib.md5()
            file_hash.update(f.read())
            hash_dict.setdefault(file_hash.hexdigest(), []).append(v)
        for hash_value in hash_dict.keys():
            if len(hash_dict[hash_value]) > 1 and hash_value not in hash_set:
                print(f"Hash: {hash_value}")
                for filepath in hash_dict[hash_value]:
                    print(f"{counter}. {filepath}")
                    duplicates_list.append([filepath, sk])
                    counter += 1
                hash_set.add(hash_value)
    print()

# Part 4: deleting files
print("\nDo you want to delete files?")
check_deletion = input()
while check_deletion not in ["yes", "no"]:
    print("Wrong option!")
    check_duplicates = input()
    print()
if check_deletion == "no":
    exit()

print("Enter file numbers to be deleted")
numbers = [x for x in input().split()]
while len(numbers) < 1 or any(not x.isdigit() for x in numbers):
    print("wrong format")
    file_numbers = [x for x in input().split()]
while max(int(x) for x in numbers) > (len(duplicates_list)):
    print("wrong format")
    file_numbers = [x for x in input().split()]

for file_num in numbers:
    full_path = duplicates_list[int(file_num) - 1][0]
    os.remove(full_path)
    free_space += duplicates_list[int(file_num) - 1][1]

print(f"Total freed up space: {free_space} bytes")
