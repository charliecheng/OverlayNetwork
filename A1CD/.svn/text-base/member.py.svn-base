import threading
import datetime
import socket
import sys
import graph
import datapacket


myHostName = socket.gethostname()
Hellotime=2
BROADCASTTIME=5
class Member():
    def __init__(self,vid,monitorname):
        self.g=graph.graph('neighbor.txt')
        self.vid=vid
        self.monitorname=monitorname
        self.monitorsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.monitorsocket.connect((self.monitorname, 40000))
        self.neighbors={}
        self.host_to_key={}
        self.hellotimestamp=datetime.datetime.now()
        self.failure_dtc_timestamp=datetime.datetime.now()
        self.broad_latency_timestamp=datetime.datetime.now()
        self.sendingSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.receivingSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.receivingSock.bind((myHostName, 40001))
        self.helloseq=0
        self.metricseq=0
        self.neighborstimestamp={}
        self.latency={}
        self.file=open('overlay.log','a')
        self.distance=[]
        self.prev=[]
        self.joinevent=''
        self.downevent=''
        self.tcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcpSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.tcpSocket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.tcpSocket.bind((myHostName, 40000)) #bind to localhost
        self.tcpSocket.listen(20)
        self.bootstrap=False
        self.datatimestamp=datetime.datetime.now()
    
    def serveOneConnection(self,s):
        run=True
        while (run):           
            try:
                line = s.recv(4096)
                #print line
                self.parsing_metric(line)
                if not line:
                    run=False
                    s.close
            except socket.error:
                s.close()
                   
    def serve(self):
        while (True):
            try:
                s,addr = self.tcpSocket.accept()
                t = threading.Thread(target=self.serveOneConnection, args = [s])
                t.setDaemon(True)
                t.start();
            except KeyboardInterrupt:
                print "\r\nBye!"
                return
       
    def failure_detection(self):
        self.failure_dtc_timestamp=datetime.datetime.now()
        while 1:
            if datetime.datetime.now()>=self.failure_dtc_timestamp+datetime.timedelta(0,5):
                for key in self.neighbors.keys():
                    if self.neighborstimestamp[key]=='':
                        continue
                    if self.neighborstimestamp[key]>datetime.datetime.now():
                        print '\nSystem Log:'+key+'is DOWN!'
                        print 'VID '+str(self.vid)+':',
                        self.g.remove(key)
                        self.neighborstimestamp[key]=''
                        del self.host_to_key[self.neighbors[key]]
                        self.neighbors[key]=''
                        self.latency[key]=[0.0,{}]
                        self.distance,self.prev=self.g.dijkstra(self.vid)
                        #print self.distance
                        #print self.prev
                        self.file.write('\n'+str(datetime.datetime.now())+'\n')
                        self.file.write(str(self.distance)+'\n')
                        self.file.write(str(self.prev)+'\n')
                        self.monitorsocket.sendall('TopoChanged '+str(self.vid))
                        #print str(self.latency)
                        
                                               
                    else:
                        self.neighborstimestamp[key]=self.failure_dtc_timestamp+datetime.timedelta(0,20)                    
                self.failure_dtc_timestamp=datetime.datetime.now() 
            
    
    def failure_detection_start(self):
        run = True
        while run:
            for key,time in self.neighborstimestamp.items():
                if time=='':
                    run = True
                    break
                else:
                    run=False
        print 'Start failure detection!'
        print 'Bootstrapping Finished...'
        self.bootstrap=True
        fd_thread=threading.Thread(target=self.failure_detection)
        fd_thread.setDaemon(True)
        fd_thread.start()
                    
    def udp_receive_thread(self):
        while 1:
            try:
                data,address=self.receivingSock.recvfrom(4096)
                receivtime=datetime.datetime.now()
                h=''
                for host in self.host_to_key.keys():
                    if str(address[0])==str(socket.gethostbyname(host)):
                        h=host
                        break
                for key, name in self.neighbors.items():
                    if name==h:
                        self.neighborstimestamp[key]=receivtime
                        #print 'updating receiving time for '+str(h)
                        break
                if data.startswith('Hello'):
                    parsing_hello_thread=threading.Thread(target=self.parsingHello,args=[data, address,receivtime])
                    parsing_hello_thread.start()
                if data.startswith('Data') or data.startswith('Ack'):
                   parsing_data_thread=threading.Thread(target=self.parsingData_Ack, args=[data,receivtime])
                   parsing_data_thread.start()
                
            except socket.error:
                print 'UDP receiving Socket error'
    def parsingData_Ack(self,msg,recvtime):
        header=msg.split('\n')[0]
        route=header.split(' ')[1]
        nodes=route.split('-')
        l=len(nodes)
        print nodes
        if header.startswith('Data'):
            if nodes[l-1]==str(self.vid):
                reply='Ack '+route+'\n'
                self.sendingSock.sendto(reply,(self.neighbors[nodes[l-2]],40001))
            else:
                index=nodes.index(str(self.vid))
                self.sendingSock.sendto(msg,(self.neighbors[nodes[index+1]],40001))
        if header.startswith('Ack'):
            if nodes[0]==str(self.vid):
                print "\nAck Received"
                print "Total Time: "+str(recvtime-self.datatimestamp)
                print "Estimated Time: "+str(self.distance[int(nodes[l-1])-1])
                print 'VID '+str(self.vid)+':',
            else:

                index=nodes.index(str(self.vid))
                self.sendingSock.sendto(msg,(self.neighbors[nodes[index-1]],40001))
                
        
    def parsingHello(self, msg,addr,receivtime):
        words=msg.split(' ')
        seq=int(words[2])
        if seq%2==0 and words[3]=='Request':#new hello from others, need feed back
            self.sendingSock.sendto("Hello "+myHostName+' '+str(seq+1)+' Reply',(addr[0],40001))
        else:#old hello from myself, calculate the latency 
            seq=seq-1
            #print 'Recving '+ str(seq)+' time '+ str(receivtime)
            '''
            v=0
            for (vid,name) in self.neighbors.items():
                if name==words[1]:
                    v=vid
                    break
            '''
            
            try:
                vid=self.host_to_key[words[1]]
                
                t3=(receivtime-self.latency[vid][1][seq])
                l=(float(t3.seconds)+float(t3.microseconds)/1000000)
                #l=float('%.4f'%l)
                #print "New Latency to "+words[1]+" "+str(l)
                if self.latency[vid][0]==0:
                    self.latency[vid][0]=l
                else:
                    self.latency[vid][0]=self.latency[vid][0]*0.9+l*0.1
                self.latency[vid][0]=round(self.latency[vid][0],4)
                self.g.insert(self.vid, vid, self.latency[vid][0])
                #print str(self.latency[vid][0])+' to '+str(vid)
                #self.file.write('Avg:\t'+str(self.latency[vid][0])+'\tNew:\t'+str(l)+' '+str(vid)+'\n')
                #self.g.insert(self.vid, vid, self.latency[vid][0])
            #print "Average Latency: "+str(self.latency[vid][0])
                del self.latency[vid][1][seq]
            except:
                pass
    def broadcast_down(self):
        pass
    def broadcast_latency(self):
        
        while 1:
            if datetime.datetime.now()>=self.broad_latency_timestamp+datetime.timedelta(0,BROADCASTTIME):
                #print 'broadcast latency'
                #self.g.printgraph()
                for vid in self.neighbors.keys():
                    for v in self.latency.keys():
                        #print str(self.latency[v][0])
                        m='Metric '+str(self.metricseq)+' '+str(self.vid)+':'+str(v)+' '+str(self.latency[v][0])+'\n'
                        try:
                            self.tempsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            self.tempsocket.connect((self.neighbors[vid], 40000))
                            self.tempsocket.sendall(m)
                            self.tempsocket.close()
                        except:
                            continue
                self.metricseq=self.metricseq+1
                self.broad_latency_timestamp=datetime.datetime.now()
                 
    def parsing_metric(self,msg):#Syntax: 'Metric seq a:b Metric'
        if msg=='':
            return
        words=msg.split('\n')[0].split(' ')
        #print words
        a=int(words[2].split(':')[0])
        if a==self.vid:
            #print 'Will not forward metric information'
            return
        b=int(words[2].split(':')[1])
        seq=int(words[1])
        if self.g.metric_seq[a-1][b-1]>=seq:#this is an old metric information
            #print 'Will not forward metric information'
            return
        else:
            #print 'Forward information'
            try:
                #print msg    
                metric=float(words[3])
                #print 'metric is '+str(words[3])
                if metric==0 and not self.g.metric_seq[a-1][b-1]==-1:
                    if not self.downevent==' Down '+str(b):
                        self.monitorsocket.sendall('TopoChanged '+str(self.vid)+' Down '+str(b))
                        self.downevent=' Down '+str(b)
                    metric=999
                    seq=-1
                if  self.g.metric_seq[a-1][b-1]==-1:
                    if not self.joinevent==' Join '+str(b):
                        self.monitorsocket.sendall('TopoChanged '+str(self.vid)+' Join '+str(b))
                        self.joinevent=' Join '+str(b)
                self.g.metric_seq[a-1][b-1]=seq
                self.g.insert(a, b, metric)
                #self.g.printgraph()
                tempprev=self.prev[:]
                self.distance,self.prev=self.g.dijkstra(self.vid)
                #print msg
                #print self.distance
                #print self.prev
                if not self.prev == tempprev:
                    #print self.distance
                    #print self.prev
                    self.file.write('\n'+str(datetime.datetime.now())+'\n')
                    self.file.write(str(self.distance)+'\n')
                    self.file.write(str(self.prev)+'\n')
                for vid in self.neighbors.keys():
                    try:
                        self.tempsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        self.tempsocket.connect((self.neighbors[vid], 40000))
                        self.tempsocket.sendall(msg)
                        self.tempsocket.close()
                    except:
                        continue
            except socket.error:
                return
                        
            #print self.distance
            #print self.prev
            
    def hellothread(self):
        while 1:
            if datetime.datetime.now()>=self.hellotimestamp+datetime.timedelta(0,Hellotime):
                for key in self.neighbors.keys():
                    
                    #print 'Sending '+str(self.helloseq) + ' time: '+str(self.latency[key][1][self.helloseq])+' to '+self.neighbors[key]
                    try:
                        self.sendingSock.sendto("Hello "+myHostName+' '+str(self.helloseq)+' Request',(self.neighbors[key],40001))
                    except:
                        continue
                    self.latency[key][1][self.helloseq]=datetime.datetime.now()
                    
                self.helloseq=self.helloseq+2
                self.hellotimestamp=datetime.datetime.now()    
    def waitforneighbor(self):
        run = True
        for i in self.neighbors.keys():
            self.latency[i]=[0.0,{}]
        udp_receive_thread=threading.Thread(target=self.udp_receive_thread)
        udp_receive_thread.setDaemon(True)
        udp_receive_thread.start()
        hello_thread=threading.Thread(target=self.hellothread)
        hello_thread.setDaemon(True)
        hello_thread.start()
        while run:
            for (vid,host) in self.neighbors.items():
                if host=='':
                    run=True
                    break
                else:
                    run=False 
            
        print 'All neighbors alive !!'        
        failure_detection_thread=threading.Thread(target=self.failure_detection_start)
        failure_detection_thread.setDaemon(True)
        failure_detection_thread.start()
        broadcast_metric_thread=threading.Thread(target=self.broadcast_latency())
        broadcast_metric_thread.setDaemon(True)
        broadcast_metric_thread.start()
        
        
    def calculate_route(self,dst_vid):
        dst_vid=int(dst_vid)
        msg='Source Node: '+str(self.vid)+' Destination Node: '+str(dst_vid)+' Route: '
        if self.distance[dst_vid-1]==999:
            msg=msg+'no-route Estimated Time: none'
            return msg
        else:
            templist=[]
            templist.append(dst_vid)
            n=dst_vid
            while not n == self.vid:
                n=self.prev[n-1]
                templist.append(n)
            while not templist == []:
                v=templist.pop()
                msg=msg+str(v)+'-'
            msg=msg[:-1]
            msg=msg+' Estimated Time '+str(self.distance[dst_vid-1])
            return msg
        
    def sendingpacket(self,i,dst):
        i=int(i)
        dst=int(dst)
        data=datapacket.packet(1)
        route=str(self.calculate_route(dst)).split('Route: ')[1].split(' ')[0]
        if route=='no-route':
            print 'No route to destination'
            return
        
        header='Data '+route+'\n'

        header=header+data.m
        nexthop=route.split('-')[1]
        self.sendingSock.sendto(header,(self.neighbors[nexthop],40001))

        print 'Waiting for Ack'
        self.datatimestamp=datetime.datetime.now()
        
    def monitor_connection(self):
        self.monitorsocket.sendall('JOIN '+str(self.vid)+' '+myHostName)
        run=True
        while run:
            try:
                line=self.monitorsocket.recv(4096)
                words=line.split('\n')
                #print words
                for word in words:
                    if not word == '':
                        self.neighbors[word.split(' ')[0]]=word.split(' ')[1]
                        self.host_to_key[word.split(' ')[1]]=word.split(' ')[0]
                if line == 'USED VID':
                    print 'VID is used'
                    run=False
                    self.monitorsocket.close()
                    sys.exit()
            except socket.error:
                print 'Monitor Down'
                run=False
    
    def start(self):
        print 'Member Node Start'
        print 'Bootstrapping Started...'
        #Read topology from files       
        f=open('neighbor.txt','r')
        for line in f:
            line=line[:-1]
            words=line.split(':')
            if words[0]==str(self.vid):
                ids=words[1].split(' ')
                for id in ids:
                    self.neighbors[id]=''
        for key in self.neighbors.keys():
            self.neighborstimestamp[key]=''
        
        #Build Connection to the monitor
        t = threading.Thread(target=self.monitor_connection)
        t.setDaemon(True)
        t.start();
        #self tcp
        tcp_socket=threading.Thread(target=self.serve)
        tcp_socket.setDaemon(True)
        tcp_socket.start()
        #Wait for neighbors alive
        b = threading.Thread(target=self.waitforneighbor)
        b.setDaemon(True)
        b.start()
                
        while 1:
            if self.bootstrap==False:
                continue
            else:
                usr_input=''
                try:
                    usr_input=raw_input('VID '+str(self.vid)+':')
                    if usr_input=='route' or usr_input=='route '+str(self.vid):
                        for i in range(1,self.g.Vcnt+1):
                            if not i==self.vid:
                                print self.calculate_route(i)
                    elif usr_input.startswith('route'):
                        print self.calculate_route(usr_input.split(' ')[1])
                    elif usr_input.startswith('send'):
                        self.sendingpacket(int(usr_input.split(' ')[1]),int(usr_input.split(' ')[2]))
                    elif usr_input=='quit':
                        sys.exit()
                    else:
                        print 'Invalid Input'
                except KeyboardInterrupt:
                    sys.exit()
                #except:
                    #print 'Invalid Input'
                    #print 'Usage: route [vid]'
                    #continue
                    
        

if __name__ == '__main__':
    m=Member()
    m.send()
        