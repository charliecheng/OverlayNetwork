import socket
import threading
import atexit
import time
import sys
import os
import datetime



CO_LOOKUP_TIMEOUT = 3
PINGPERIOD=10
LISTENING_PORT= 47865
MAX_BYTES_RESPONSE = 1000
CoordinatorName = 'NONE'
NODELIST = []
myHostName = socket.gethostname()
IsCoordinator = False
sendingSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#Functions for Member
def Log(NodeList,timestamp,action,node):
    myLogFile = open("Log.log",'a')
    if IsCoordinator == True:       
        myLogFile.write("Identity: Coordinator node "+str(timestamp)+':\n') 
        if node==myHostName:
            myLogFile.write('\t[MEMBERS]: ['+myHostName+']\n')
        else:
            myLogFile.write('\t[EVENT '+action+']: '+node+'\n')
            myLogFile.write('\t[MEMBERS]: [')
            for i in NodeList:
                myLogFile.write(i+" ")
            myLogFile.write(']\n')
        myLogFile.close()
    else:
        myLogFile.write("Identity: Member node "+str(timestamp)+':\n') 
        myLogFile.write('\t[COORDINATOR]: ['+NodeList[0]+']\n')
        myLogFile.write('\t[MEMBERS]: [')
        for i in NodeList:
            myLogFile.write(i+" ")
        myLogFile.write(']\n')
        myLogFile.close()
    return

        
        
def join():
    message="JOIN "+myHostName
    try:
        for i in range(3):
            sendingSock.sendto(message,(CoordinatorName,LISTENING_PORT))
    except:
        print "Socket Error to "+CoordinatorName+" JOIN message sending failed"
    return
datetime.datetime.now()
def leave():
    message="LEAVE "+myHostName
    try:
        for i in range(3):
            sendingSock.sendto(message,(CoordinatorName,LISTENING_PORT))
    except:
        print "Socket Error to "+CoordinatorName+" JOIN message sending failed"
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
    for node in nodelist:
        try:
            for i in range(3):
                sendingSock.sendto("PING "+myHostName+" "+str(time.mktime(time.localtime())),(node,LISTENING_PORT))

        except Exception, msg:
            print msg
            print "Socket Error: Ping  "+node
    return

def PARSING(data,address,Nodelist):
    nodelist=Nodelist
    if data.startswith("Coordinator Lookup"):
        try:
            for i in range(3):
                sendingSock.sendto(CoordinatorName,(address[0],LISTENING_PORT))
        except:
            print "Socket Error: Sending Coordinator Name to "+address
        return nodelist
        
 
 #########For members########   
    if data.startswith("LIST"):
        nodelist=[]
        DATA=data.split(" ")
        DATA.remove("LIST")
        for i in DATA:
            nodelist.append(i)
        Log(nodelist,datetime.datetime.now(),'','')
        return nodelist
    
    if data.startswith("PING"):
        '''
        DATA=data.split(" ")
        index=datalist.index(DATA[1])
        timelist[index]=time.mktime(time.localtime())
        message="PONG "+myHostName+" "+DATA[2]
        try:
            for i in range(3):
                sendingSock.sendto(message,(address[0],LISTENING_PORT))
        except:
            print "Socket Error: Sending Pong "+address
        return nodelist,timelist
        '''
        pass

#########For Coordinator    
    if data.startswith("JOIN"):
        #"JOIN "+member host name
        DATA=data.split(" ")
        if DATA[1] in nodelist:
            return nodelist
        else:
            nodelist.append(DATA[1])
            Log(nodelist,datetime.datetime.now(),"JOIN",DATA[1])
            message='LIST'
            for i in nodelist:
                message=message+" "+i            
            try:
                for i in range(1):
                    for node in nodelist:
                        sendingSock.sendto(message,(node,LISTENING_PORT))
            except:
                    print "Socket Error: Sending Coordinator Name to "+address
            
            return nodelist
            
            
    if data.startswith("LEAVE"):
        DATA=data.split(" ")
        if not (DATA[1] in nodelist):
            return nodelist
        else:
            nodelist.remove(DATA[1])
            Log(nodelist,datetime.datetime.now(),"LEAVE",DATA[1])
            message='LIST'
            for i in nodelist:
                message=message+" "+i
            
            try:
                for i in range(1):
                    for node in nodelist:
                        sendingSock.sendto(message,(node,LISTENING_PORT))
            except:
                    print "Socket Error: Sending Coordinator Name to "+address
            return nodelist
    if data.startswith("PONG"):
        '''
        DATA=data.split(" ")
        index=datalist.index(DATA[1])
        '''
        
        pass
    
    


class MYThread(threading.Thread):
    def __init__(self, port, NODELIST):
        threading.Thread.__init__(self)
        self.port = port
        self.willStop = True
        self.NODELIST=NODELIST
        #self.TIMELIST=[0]
    def run(self):       
        firstPing = True
        while self.willStop:
            try:
                receivingSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                receivingSock.bind((myHostName, LISTENING_PORT))
                data, address = receivingSock.recvfrom(MAX_BYTES_RESPONSE)
                
                print data
                self.NODELIST=PARSING(data, address,self.NODELIST)
                '''
                if data.startswith("JOIN") and firstPing == True and IsCoordinator== True:
                    ping(self.NODELIST)
                    firstPing = False
                '''    
                
                
                print "NEW LIST:"
                print self.NODELIST
                #print self.TIMELIST
            except KeyboardInterrupt:
                receivingSock.close()
                print "Exit Gracefully"
                raise
    def stop(self):
        self.willStop=False
 

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
    myLogFile.close()
    ####### Coordinator Stuff
    if IsCoordinator:
        CoordinatorName = myHostName
        NODELIST.append(CoordinatorName)
        Log(NODELIST,datetime.datetime.now(),'',myHostName)
    else:
        for i in range(3):
            join()

                
    print "Coordinator name: "+ CoordinatorName

    MyThread=MYThread(LISTENING_PORT, NODELIST)
    MyThread.setDaemon(True)
    def cleanUp():
        if IsCoordinator!=True:
            leave()
        MyThread.stop()
    atexit.register(cleanUp)
    MyThread.run()
    
    

    
    

            

    