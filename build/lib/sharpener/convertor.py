from subprocess import check_output, STDOUT



def convert(source_file, level, destination_file ):
    output = check_output(["convert",
                           source_file,
                           "-sharpen",level,
                           destination_file], stderr=STDOUT)