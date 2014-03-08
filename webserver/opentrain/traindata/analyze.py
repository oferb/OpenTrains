import codecs
def read_file(fname):
    with codecs.open(fname,encoding="windows-1255") as fh:
        for idx,line in enumerate(fh):
            print line
            print line.split()
            
if __name__ == '__main__':
    read_file('data/2013-12.txt')
    
    
    
    