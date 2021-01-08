# Python program to convert text
# file to JSON


import json


# the file to be converted
filename = "mapping.txt"

# resultant dictionary
dict0 = {}
sno = "celeb"

# fields in the sample file
fields = ["stt", "ten", "link", "path"]

with open(filename) as fh:

    dict1 = []

    for line in fh:
        # print(line, type(line))
        # reading line by line from the text file
        description = list(line.strip().split(None, 1))

        # for output see below

        url = (
            "https://www.google.com/search?q="
            + description[1].replace(" ", "+")
            + "&client=ubuntu&hl=en&source=lnms&tbm=isch&sa=X"
        )

        
        print(url)
        description.append(url)
        print(description)
        # for automatic creation of id for each employee

        # loop variable
        i = 0
        # intermediate dictionary
        dict2 = {}
        while i < len(fields):

            # creating dictionary for each employee
            # print(description[i], type(description[i]))
            dict2[fields[i]] = description[i]
            i = i + 1

        # appending the record of each employee to
        # the main dictionary
        dict1.append(dict2)

    dict0[sno] = dict1

# creating json file
out_file = open("test1.json", "w", encoding="utf-8")
json.dump(dict0, out_file, ensure_ascii=False, indent=4)
out_file.close()
