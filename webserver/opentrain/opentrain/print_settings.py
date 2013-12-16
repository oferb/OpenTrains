import sys
old_stdout = sys.stdout 
sys.stdout = open('/dev/null','w') 
import settings
sys.stdout = old_stdout
if __name__ == '__main__':
    if sys.argv[1] == '-env':
        print 'export DATA_DIR="%s"' % (settings.DATA_DIR)


