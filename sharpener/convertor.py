from subprocess import check_output, STDOUT



def convert(source_file, destination_file, amount ):
    output = check_output(["convert",
                           source_file,
                           "-sharpen", amount,
                           destination_file], stderr=STDOUT)
