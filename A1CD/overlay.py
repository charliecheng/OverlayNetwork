import socket
import sys, getopt
import monitor
import member
#Global Parameters
myHostName = socket.gethostname()
def main():
    name=''
    vid=0
    try:
        opts, args = getopt.getopt(sys.argv[1:],"hMm:v:")
    except getopt.GetoptError:
        print 'USAGE: overlay.py [-M] -m monitor name -v VID'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'USAGE: overlay.py [-M] -m monitor name -v VID'
            sys.exit()
        elif opt == "-M":
            return myHostName,vid
        if opt == "-m":
            name=arg
        if opt == "-v":
            try:
                vid=int(arg)
            except:
                print "Invalid VID"
                sys.exit(2)
    return name, vid


if __name__ == "__main__":
    Monitorname, myVID=main()
    myLogFile = open("overlay.log",'w')
    myLogFile.close()
    myHostName = socket.gethostname()
    if Monitorname==myHostName:
        #Monitor Mode
        monitornode=monitor.Monitor()
        monitornode.serve()
    else:
        membernode=member.Member(myVID,Monitorname)
        membernode.start()

            