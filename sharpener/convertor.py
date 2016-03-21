from subprocess import check_output, STDOUT



def convert(source_file, destination_file ):
    output = check_output(["convert",
                           source_file,
                           "-sharpen","0x1",
                           destination_file], stderr=STDOUT)