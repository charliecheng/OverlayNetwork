from __future__ import with_statement
import socket
import threading
import atexit
import time
import sys
import os
import datetime
from threading import Timer
import subprocess

##Newest
a=0.9
CO_LOOKUP_TIMEOUT = 5
PINGPERIOD=30
PINGTIMEOUT=10
FailurePeriod=60
LISTENING_PORT= 47865
MAX_BYTES_RESPONSE = 1000
CoordinatorName = 'NONE'
NODELIST = {}
TIMELIST = []
myHostName = socket.gethostname()
IsCoordinator = False
sendingSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#Functions for Member
def Log(NodeList,timestamp,action,node,name):
    myLogFile = open("Log.log",'a')
    if myHostName == name:       
        myLogFile.write("Identity: Coordinator node "+str(timestamp)+':\n') 
        if node==myHostName:
            myLogFile.write('\t[MEMBERS]: ['+myHostName+']\n')
        else:
            myLogFile.write('\t[EVENT '+action+']: '+node+'\n')
            myLogFile.write('\t[MEMBERS]: [')
            for i in NodeList.keys():
                myLogFile.write(i+" ")
            myLogFile.write(']\n')
        myLogFile.close()
    else:
        myLogFile.write("Identity: Member node "+str(timestamp)+':\n') 
        myLogFile.write('\t[COORDINATOR]: ['+name+']\n')
        myLogFile.write('\t[MEMBERS]: [')
        for i in NodeList.keys():
            myLogFile.write(i+" ")
        myLogFile.write(']\n')
        myLogFile.close()
    return

def LatencyLog(node1,node2,latency,m,timestamp,name):
    myLogFile = open("LatencyLog.log",'a')
    if myHostName==name:
        myLogFile.write(m+"\n")
        myLogFile.close()
        return 0
    else:
        with open('LatencyLog.log') as openfileobject:
            line=""
            for line in openfileobject:
                if line.startswith(node1+" "+node2):
                    Line=line.split(" ")
                    avg=float(Line[3])
                    avgnew=a*avg+0.1*latency
                    break
            if not line.startswith(node1+" "+node2):
                avgnew=latency
        myLogFile.write(node1+" "+node2+ " "+str(avgnew)+" "+str(latency)+" "+ str(timestamp)+"\n")
        myLogFile.close()
        return avgnew
        
        
        
        
def join(name):
    message="JOIN "+myHostName
    try:
        for i in range(5):
            print "Sending JOIN MESSSAGE"
            sendingSock.sendto(message,(name,LISTENING_PORT))
    except:
        print "Socket Error to "+CoordinatorName+" JOIN message sending failed"
    return

def leave(name):
    message="LEAVE "+myHostName
    try:
        for i in range(1):
            sendingSock.sendto(message,(name,LISTENING_PORT))
    except:
        print "Socket Error to "+name+" JOIN message sending failed"
    return
    


#Functions for Coordinator
def listMembers():
    return NODELIST
    

def addMember(hostname):
    NODELIST.append(hostname)
    return

def removeMember(hostname):
    NODELIST.remove(hostname)
    return


#Functions for Coordinator
def ping(Nodelist):
    nodelist=Nodelist
    for node in nodelist.keys():
        if node==myHostName:
            continue
        try:
            for i in range(5):
                sendingSock.sendto("PING "+myHostName+" "+str(time.mktime(time.localtime())),(node,LISTENING_PORT))
                print "Sending Ping to "+node

        except Exception, msg:
            print msg
            print "Socket Error: Ping  "+node
    return

def SendingList(Nodelist):
    message="LIST"
    for node in Nodelist.keys():
        message=message+" "+node
    
    for node in Nodelist.keys():
        if node == myHostName:
            continue
        try:
            for i in range(2):
                sendingSock.sendto(message,(node,LISTENING_PORT))
                print "sending LIST to " +node
                

        except Exception, msg:
            print msg
            print "Socket Error: Sending List  "+node
    return
        
        

def PARSING(data,address,Nodelist,Times,Name):
    nodelist=Nodelist
    timestamp=Times
    if data.startswith("Coordinator Lookup"):
        try:
            for i in range(1):
                sendingSock.sendto(Name,(address[0],LISTENING_PORT))
        except:
            print "Socket Error: Sending Coordinator Name to "+address
        return nodelist
        
 
 #########For members########   
    if data.startswith("LIST"):
        nodelist={}
        DATA=data.split(" ")
        DATA.remove("LIST")
        for i in DATA:
            nodelist[i]=timestamp
        Log(nodelist,datetime.datetime.now(),'','',Name)
        return nodelist
    
    if data.startswith("PING"):
        nodelist[Name]=timestamp
        DATA=data.split(" ")
        message="PONG "+myHostName+" "+DATA[2]
        print "Sending Pong"
        try:
            for i in range(5):
                sendingSock.sendto(message,(address[0],LISTENING_PORT))
        except:
            print "Socket Error: Sending Pong "+address
        #LatencySensor(nodelist)
        for node in nodelist.keys():
            p = subprocess.Popen(["ping", "-c", "3", "-w", "3", "-A", node], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = p.communicate()
            latency = 0
            if (p.returncode == 0):
            # in ms
                latency = float(out.split('/')[4])
                print "Latency = "+str(latency)
                avgnew=LatencyLog(myHostName,node,latency," ",datetime.datetime.now(),Name)
                try:
                    for i in range(1):
                        sendingSock.sendto("LATENCY "+myHostName+" "+node+" "+str(avgnew),(CoordinatorName,LISTENING_PORT))
                except:
                    print "Socket Error to "+name+" JOIN message sending failed"
                
            else:
                latency = -1
             
        return nodelist

#########For Coordinator    
    if data.startswith("JOIN"):
        #"JOIN "+member host name
        DATA=data.split(" ")
        if DATA[1] in nodelist.keys():
            return nodelist
        else:
            nodelist.update({DATA[1]:timestamp})
            Log(nodelist,datetime.datetime.now(),"JOIN",DATA[1],Name)
            SendingList(nodelist)
            
            
            return nodelist
            
            
    if data.startswith("LEAVE"):
        DATA=data.split(" ")
        if not (DATA[1] in nodelist.keys()):
            return nodelist
        else:
            del nodelist[DATA[1]]
            Log(nodelist,datetime.datetime.now(),"LEAVE",DATA[1],Name)
            SendingList(nodelist)
        return nodelist
        
    if data.startswith("PONG"):
        DATA=data.split(" ")
        nodelist[DATA[1]]=timestamp      
        return nodelist
    
    if data.startswith("LATENCY"):
        x=LatencyLog(" ", " ", " ", data, datetime.datetime.now(),Name)
        DATA=data.split(" ")
        nodelist[DATA[1]]=timestamp
        
        return nodelist
    
class PINGThread(threading.Thread):
    def __init__(self, port, NODELIST,TIMELIST,PingInterval):
        threading.Thread.__init__(self)
        self.port = port
        #self.willStop = True
        self.NODELIST=NODELIST
        self.TIMELIST=TIMELIST
        self.PingInterval=PingInterval
        self.timestamp=datetime.datetime.now()
    
    def updateLists(self,NODELIST,TIMELIST):
        self.NODELIST=NODELIST
        self.TIMELIST=TIMELIST
        
    def run(self):
        while 1:
            if datetime.datetime.now()>=self.timestamp+datetime.timedelta(0,self.PingInterval):
                ping(self.NODELIST)
                self.timestamp=datetime.datetime.now()
        
class TimerThread(threading.Thread):
    def __init__(self,IsCoordinator,NODELIST,FailurePeriod,PINGPERIOD,scaddr,message):
        threading.Thread.__init__(self)
        self.isCoordinator=IsCoordinator
        self.Nodelist=NODELIST
        self.FailurePeriod=FailurePeriod
        self.PINGPERIOD=PINGPERIOD
        self.timestamp=datetime.datetime.now()
        self.scaddr=scaddr
        self.message=message
        self.newMessage=False
        self.PINGTIMER=False
        self.STARTED=False
        self.Coordinatorname=CoordinatorName

    def MessageComing(self,scaddr,message):
        self.scaddr=scaddr
        self.message=message
        self.newMessage=True    
    def run(self):
        while 1:
            if self.newMessage==True:
                self.newMessage=False
                self.Nodelist=PARSING(self.message, self.scaddr, self.Nodelist,datetime.datetime.now(),self.Coordinatorname)
                self.STARTED=True
                
                
            if self.isCoordinator==True:
                if datetime.datetime.now()>=self.timestamp+datetime.timedelta(0,PINGPERIOD):
                    ping(self.Nodelist)
                    self.timestamp=datetime.datetime.now()
                    self.PINGTIMER=True
                    
                    print "PING TIMER STARTED"
                    for node in self.Nodelist.keys():
                        self.Nodelist[node]=self.timestamp+datetime.timedelta(0,PINGTIMEOUT+5)
                if self.PINGTIMER==True:
                    if datetime.datetime.now()>=self.timestamp+datetime.timedelta(0,PINGTIMEOUT):

                        for node in self.Nodelist.keys():
                            if node==myHostName:
                                continue
                            if datetime.datetime.now()<self.Nodelist[node]:
                                print "NO PONG RECEIVED FROM "+node
                                del self.Nodelist[node]
                                SendingList(self.Nodelist)
                                Log(self.Nodelist,datetime.datetime.now(),"FAILURE",node,self.Coordinatorname)
                            self.PINGTIMER=False
                        
            if self.isCoordinator==False and self.STARTED==True:
                try:
                    if datetime.datetime.now()>=self.Nodelist[self.Coordinatorname]+datetime.timedelta(0,FailurePeriod):
                        print "Server Down"
                        del self.Nodelist[self.Coordinatorname]
                        self.Coordinatorname=self.Nodelist.keys()[0]
                        CoordinatorName=self.Coordinatorname
                        if myHostName==self.Nodelist.keys()[0]:
                            self.isCoordinator=True;
                            IsCoordinator=True

                            print "I am the next"
                            self.Nodelist={}
                            self.Nodelist[myHostName]=datetime.datetime.now()
                            self.timestamp=datetime.datetime.now()
                            Log(self.NodeList, self.timestamp, '', myHostName, self.Coordinatorname)
                        else:
                            self.Nodelist={}
                            self.Nodelist[self.Coordinatorname]=datetime.datetime.now()
                            t=threading.Timer(2,join,[self.Coordinatorname])
                            t.start()
                            atexit.register(leave,self.Coordinatorname)
                except:
                    pass

                
                
                    
                    

class MYThread(threading.Thread):
    def __init__(self, port, NODELIST):
        threading.Thread.__init__(self)
        self.port = port
        self.willStop = True
        self.NODELIST=NODELIST
    def run(self):       
        #firstPing = True
        mytimer=TimerThread(IsCoordinator,NODELIST,FailurePeriod,PINGPERIOD,'','')
        mytimer.setDaemon(True)
        mytimer.start()
        while self.willStop:
            try:
                receivingSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                receivingSock.bind((myHostName, LISTENING_PORT))
                data, address = receivingSock.recvfrom(MAX_BYTES_RESPONSE)
                print "RECEIVED DATA:\n"+data
                mytimer.MessageComing(address,data)
                #print self.TIMELIST
            except KeyboardInterrupt:
                receivingSock.close()
                print "Exit Gracefully"
                raise
            except Exception:
                pass
    def stop(self):
        self.willStop=False
        
    def returnList(self):
        return self.NODELIST, self.TIMELIST
 

if __name__ == '__main__':
    seeds = []
    try:
        f = open('seeds.txt', 'r')
    except:
        print "No Seeds file under this directory\nProgram Terminated"
        sys.exit()
    for line in f:
        seeds.append(line[:-1])
    
 ##########BOOTSTRAPPing PHRASE  STARTED
    for nodename in seeds:
        
        message = "Coordinator Lookup"
        try:
            for i in range(3):
                sendingSock.sendto(message,(nodename,LISTENING_PORT))
        except:
            print "Socket Error to "+nodename+" Coordinator Lookup Fail"
    
    receivingSock_Boot = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    receivingSock_Boot.bind((myHostName, LISTENING_PORT))
    receivingSock_Boot.settimeout(CO_LOOKUP_TIMEOUT)
    while True:
        try:
            data, address = receivingSock_Boot.recvfrom(MAX_BYTES_RESPONSE)
            #print address
            CoordinatorName = data
            break
        except socket.timeout, msg:
            IsCoordinator = True
            break
    receivingSock_Boot.close()
    #######BOOTSTRAPPING PHRASE FINISHED
    myLogFile = open("Log.log",'w')
    myLogf=open("LatencyLog.log",'w')
    myLogFile.close()
    myLogf.close()
    ####### Coordinator Stuff
    if IsCoordinator:
        CoordinatorName = myHostName
        Log(NODELIST,datetime.datetime.now(),'',myHostName,myHostName)
    else:
        for i in range(1):
            join(CoordinatorName)
    NODELIST[CoordinatorName]=datetime.datetime.now()
                
    print "Coordinator name: "+ CoordinatorName
    print "INITIALS: "+str(NODELIST.keys())
    MyThread=MYThread(LISTENING_PORT, NODELIST)
    MyThread.setDaemon(True)

    def cleanUp():
        if IsCoordinator!=True:
            leave(CoordinatorName)
        MyThread.stop()
    atexit.register(cleanUp)
    MyThread.start()
    while 1:
        continue
    '''
    print "TEST TO SEE IF THE CODE CAN COME TO HERE"
    StartPING = True
    while 1:
        if IsCoordinator==True and StartPING == True:
            print "Start Ping thread"
            mypingthread=PINGThread(LISTENING_PORT,NODELIST,TIMELIST,PINGPERIOD)
            mypingthread.setDaemon(True)
            StartPING=False
            mypingthread.start()
        mypingthread.updateLists(mypingthread,MyThread.returnList())
        '''
    
    

    
    

            

    