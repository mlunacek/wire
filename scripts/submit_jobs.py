#!/curc/admin/benchmarks/bin/python
import os

#==============================================================================  
if __name__ == '__main__':  
    
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-d", "--directory", dest="directory", help="Which directory")
    (options, args) = parser.parse_args()
    
    directory = "."
    if options.directory != None:
        directory = options.directory
    else:
        print "please specify a directory: -d <dirname>"
        exit()

    for dirname, dirnames, filenames in os.walk(directory):
        current = os.getcwd()
        print current
        print dirname
        os.chdir(dirname)
        for filename in filenames:
            if filename.find("script_") == 0:
                cmd = "qsub " + filename
                os.system(cmd)
        os.chdir(current)        
            

