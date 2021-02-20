import os
import json
import sys

import chevron
import re
import argparse

JSON_FILE_EXTENSION = ".json"
D_FILE_EXTENSION = ".d"


def to_camel_case(text, render):
    result = render(text)
    return ''.join(
        [result.split("_")[0]] + list(map(lambda x: x[0].upper() + x[1:], result.split("_")[1:]))
    ).replace(".", "")


def to_upper_camel_case(text, render):
    return ''.join(
        map(lambda x: x[0].upper() + x[1:], render(text).split("_"))
    ).replace(".", "")


def to_lower(text, render):
    return ''.join(render(text).split("_")).lower()


def to_rest_path(text, render):
    result = render(text)
    for pattern in re.findall("{[a-zA-Z]+}", result):
        result = result.replace(pattern, "%s")
    return result


json_helper_function = {
    "to_upper_camel_case":   to_upper_camel_case,
    "to_camel_case":        to_camel_case,
    "to_lower":            to_lower,
    "to_rest_path":       to_rest_path
}


def get_file_extension(filename):
    """
    @type filename: string
    """
    _, extension = os.path.splitext(filename)
    print(extension)
    return extension


def get_lib_services_directory(output_directory, resource_filename):
    """
    @type output_directory string
    @type resource_filename string
    """
    _, resource_file_path = os.path.split(resource_filename)
    libname, _ = os.path.splitext(resource_file_path)
    return (output_directory + os.sep + libname + os.sep\
        + "services" + os.sep, libname)

def get_lib_filename(output_directory, resource_filename):
    """
    @type output_directory string
    @type resource_filename string
    """
    (services_directory, libname) =\
        get_lib_services_directory(output_directory, resource_filename)
    if not os.path.exists(services_directory):
        os.mkdir(services_directory)
    print(libname)
    print(services_directory)
    return services_directory + libname + D_FILE_EXTENSION


def build_lib_file(resource_filename, output_directory, mustache_file):
    """
    @type resource_filename: string
    @type output_directory: string
    @type mustache_file: object
    """
    try:
        with open(resource_filename) as resource_file:
            resource_data = json.loads(resource_file.read())
            resource_data.update(json_helper_function)

            result = chevron.render(mustache_file, resource_data)

            try:
                with open(get_lib_filename(output_directory, resource_filename), "w") as output_file:
                    output_file.write(result)
            except FileNotFoundError as exception:
                print(str(exception))
                sys.exit(os.EX_NOTFOUND)
    except FileNotFoundError as exception:
        print(str(exception))
        sys.exit(os.EX_NOTFOUND)


def get_json_files(dirname):
    """
    @type dirname string
    """
    files = list()
    for (dirpath, dirnames, filenames) in os.walk(dirname):
        files += [os.path.join(dirpath, file) for file in filenames]

    return list(filter(lambda file: (get_file_extension(file) == JSON_FILE_EXTENSION), files))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate dlang libs.")
    parser.add_argument("-tmpl",
                        "--template_file",
                        action="store",
                        default="template.mustache",
                        help="Set the template filename.")
    parser.add_argument("-dir",
                        "--resources_directory",
                        action="store",
                        default="./google-api-dlang-client",
                        help="Set the resource files directory.")
    locals().update(vars(parser.parse_args()))

    output_directory = resources_directory

    try:
        with open(template_file) as mustache_file:
            resource_files = get_json_files(resources_directory)
            for resource_filename in resource_files:
                build_lib_file(resource_filename, output_directory, mustache_file)
    except FileNotFoundError as exception:
        print(str(exception))
        sys.exit(os.EX_NOTFOUND)


