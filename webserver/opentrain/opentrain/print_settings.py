import settings
if __name__ == '__main__':
    import sys
    if sys.argv[1] == '-env':
        print 'export DATA_DIR="%s"' % (settings.DATA_DIR)


