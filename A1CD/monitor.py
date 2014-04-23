import threading
import datetime
import socket
import graph
myHostName = socket.gethostname()

class Monitor():
    def __init__(self):
        self.vid_hostip_mapping={}
        self.vids=self.vid_hostip_mapping.keys().sort()
        self.topo={}
        self.socketsdict={}
        self.tcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcpSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.tcpSocket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.tcpSocket.bind((myHostName, 40000)) #bind to localhost
        self.tcpSocket.listen(20)
        self.start_t=datetime.datetime.now()
        self.flag=[]
        self.times={}
        self.g=graph.graph('neighbor.txt')
        self.count=0
        self.boot=False
    
    def log(self, action, vid, hostname):
        myLogFile = open('overlay.log','a')
        myLogFile.write('\n')
        myLogFile.write(str(datetime.datetime.now())+'\n')
        if action=='JOIN':
            myLogFile.write('JOIN NEW NODE:\n')
        if action=='DOWN':
            myLogFile.write('LEAVE NODE:\n')
        myLogFile.write('VID: '+vid+'\n')
        myLogFile.write('HOSTNAME:\t'+hostname+'\n')
        myLogFile.write('Current Mapping Table:\n')
        for key in self.vid_hostip_mapping.keys():
            try:
                myLogFile.write(key+'\t'+self.vid_hostip_mapping[key][0]+'\n')
            except:
                continue
        myLogFile.write('\n')
        myLogFile.close()
        
        
        
    def serveOneClient(self, s):
        run = True
        while (run):           
            try:
                line = s.recv(4096)
                #print line
                if not line.startswith('Topo'):
                    print line
                if line.startswith('JOIN'):
                    words=line.split(' ')
                    if words[1] in self.vid_hostip_mapping.keys():
                        s.sendall('USED VID')
                    else:
                        self.count=self.count+1
                        if self.count>self.g.Vcnt:
                            self.boot=True
                        self.vid_hostip_mapping[words[1]]=words[2],str(socket.gethostbyname(words[2]))
                        self.socketsdict[words[1]]=s
                        self.log('JOIN',words[1],words[2])
                        #First send its alive neighbor name
                        for i in self.topo[words[1]]:
                            if i in self.vid_hostip_mapping.keys():
                                s.sendall(i+' '+self.vid_hostip_mapping[i][0]+'\n')
                        #Then tell its all alive neighbors the node name
                        for node in self.vid_hostip_mapping.keys():
                            if words[1] in self.topo[node]:
                                self.socketsdict[node].sendall(words[1]+' '+words[2])
                        if self.boot==True:
                            msg='Join '+words[1]
                            self.times[msg]=[[],datetime.datetime.now()]
                            for i in range(0,self.g.Vcnt):
                                self.times[msg][0].append('True')
                            self.times[msg][0][int(words[1])-1]='False'
                            #for key in self.vid_hostip_mapping.keys():
                             #   if self.vid_hostip_mapping[key]=='':
                              #      self.times[msg][0][int(key)-1]='False'
                            self.times[msg][1]=datetime.datetime.now()
                            
                if line.startswith('TopoChanged'):#TopoChanged sendervid Join/Down targetvid
                    try:
                        words=line.split(' ')
                        v=int(words[1])
                        event=words[2]+' '+words[3]
                        for key,value in self.times.items():
                            if key==event:
                                value[0][v-1]='False'
                                if 'True' in value[0][v-1]:
                                    return
                                else:
                                    time=datetime.datetime.now()
                                    delta=time-value[1]
                                    print str(delta)
                                    del self.times[event]
                                    if self.boot==True:
                                        
                                        myLogFile = open('overlay.log','a')
                                        myLogFile.write('\n'+event+' Reaction Time: '+str(delta)+'\n')
                                        myLogFile.close()
                    except:
                        pass
                         #print line
                
                                        
                if not line:
                    print 'Member Node Down!' 
                    for vid, address in self.vid_hostip_mapping.iteritems():
                        if address[1]==s.getpeername()[0]:
                            print str(vid)+'\t'+address[0]
                            msg='Down '+str(vid)
                            self.count=self.count+1
                            self.boot=True
                            self.times[msg]=[[],datetime.datetime.now()]
                            for i in range(0,self.g.Vcnt):
                                self.times[msg][0].append('True')
                            self.times[msg][0][int(vid)-1]='False'
                            self.times[msg][1]=datetime.datetime.now()
                            del self.vid_hostip_mapping[vid]
                            del self.socketsdict[vid]
                            self.log('DOWN',vid,address[0])
                            break
                    run = False
                    s.close()
                    return
            except socket.error:
                print str(datetime.datetime.now())
                run = False
                s.close()
                return
    
    def serve(self):
        print "Monitor started ..."
        f = open('neighbor.txt','r')
        for line in f:
            words=line.split(':')
            newline=words[1][:-1] # Delete '\n'
            self.topo[words[0]]=newline.split(' ')
            self.flag.append('True')
        f.close()
        while (True):
            try:
                s,addr = self.tcpSocket.accept()
                t = threading.Thread(target=self.serveOneClient, args = [s])
                t.setDaemon(True)
                t.start();
            except KeyboardInterrupt:
                print "\r\nBye!"
                return
#             except:
#                 print "Unexpected error:", sys.exc_info()[0]
#             finally:
#                 pass
        self.tcpSocket.close()
        
if __name__ == '__main__':
    m=Monitor()
    m.serve()