import os
import sys
import shutil

kilobytes = 1024
megabytes = kilobytes * 1000
chunksize = int(200 * megabytes)  # default chunksize


def split(fromfile, todir, chunksize=chunksize):
    if not os.path.exists(todir):  # check whether todir exists or not
        os.mkdir(todir)
    else:
        shutil.rmtree(todir)
        os.mkdir(todir)
    partnum = 0
    inputfile = open(fromfile, 'rb')  # open the fromfile
    while True:
        chunk = inputfile.read(chunksize)
        if not chunk:  # check the chunk is empty
            break
        partnum += 1
        filename = os.path.join(todir, ('part%04d' % partnum))
        fileobj = open(filename, 'wb')  # make partfile
        fileobj.write(chunk)  # write data into partfile
        fileobj.close()
    return partnum


if __name__ == '__main__':
    try:
        fromfile = sys.argv[1]
    except:
        fromfile = "./nohup.out"
    try:
        todir = sys.argv[2]
    except:
        todir = "./log"
    try:
        chunksize = int(sys.argv[3])*megabytes
    except:
        chunksize = chunksize
    absfrom, absto = map(os.path.abspath, [fromfile, todir])
    print('Splitting', absfrom, 'to', absto, 'by', chunksize)
    try:
        parts = split(fromfile, todir, chunksize)
    except:
        print('Error during split:')
        print(sys.exc_info()[0], sys.exc_info()[1])
    else:
        print('split finished:', parts, 'parts are in', absto)
