
# a_file = open("mapping.txt")
# for line in a_file:
#     key, value = line.split()

# print(a_dictionary)


filename = "mapping.txt"
name = []

with open(filename) as fh:
    d = {}
    for line in fh:
        (key, val) = line.strip().split(None, 1)
        d[int(key)] = val

labels = [10, 300, 1000]
for i, label in enumerate(labels):
    if label < 731 and label >= 0:
        name.append(d[label])
    
print(name)