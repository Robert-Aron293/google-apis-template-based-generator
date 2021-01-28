
import os
import json
import chevron
import re

PATH = "google-api-dlang-client"
MUSTACHE_FILE = "Lib.mustache"
ALL_FILES = list()

for (dirpath, dirnames, filenames) in os.walk(PATH):
    ALL_FILES += [os.path.join(dirpath, file) for file in filenames]

print(ALL_FILES)

JSON_RESOURCE_FILES = list(filter(lambda x: (x.split(".")[1] == "json"), ALL_FILES))

print(JSON_RESOURCE_FILES)

def to_class_name(text, render):
    result = render(text)
    return ''.join(map(lambda x: x[0].upper() + x[1:], result.split("_"))).replace('.', '')

def to_var_name(text, render):
    result = render(text)
    return ''.join(list([result.split("_")[0]]) + list(map(lambda x: x[0].upper() + x[1:], result.split("_")[1:]))).replace('.', '')

def to_lower(text, render):
    result = render(text)
    return ''.join(result.split("_")).lower()

def to_rest_path(text, render):
    result = render(text)
    for format in re.findall("{[a-zA-Z]+}", result):
        print(format)
        result = result.replace(format, "%s");
    return result

with open(MUSTACHE_FILE) as mustache_file:
    for json_file in JSON_RESOURCE_FILES:
        with open(json_file) as open_json_file:
            data = open_json_file.read()

            json_content = json.loads(data)
            json_content['to_class_name'] = to_class_name
            json_content['to_var_name'] = to_var_name
            json_content['to_lower'] = to_lower
            json_content['to_rest_path'] = to_rest_path

            result = chevron.render(mustache_file, json_content)
            #print(result)
            output_file_name = json_file.split(".")[0] + ".d"
            output_file_name_handler = open(output_file_name, "w")
            output_file_name_handler.write(result)
            output_file_name_handler.close()


print(JSON_RESOURCE_FILES)
