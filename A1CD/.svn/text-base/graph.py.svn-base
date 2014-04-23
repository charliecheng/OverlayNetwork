import datetime

class graph():
    def __init__(self,file):
        self.file=file
        self.Vcnt=0
        self.Ecnt=0
        self.metric_matrix=[]
        self.metric_seq=[]
        self.nodes=[]
        self.readfile()
        self.distance=[]
        self.prev=[]
        self.vid=1
    def readfile(self):
        f=open(self.file,'r')
        for line in f:
            self.metric_matrix.append([])
            self.metric_seq.append([])
            self.Vcnt=self.Vcnt+1       
        f.close()
        for i in range(1,self.Vcnt+1):
            self.nodes.append(i)

        #print self.nodes
        for i in range(0,self.Vcnt):
            for j in range(0,self.Vcnt):
                self.metric_matrix[i].append(999)
                self.metric_seq[i].append(-1)
        f=open(self.file,'r')
        for line in f:
            line=line[:-1]
            vid=int(line.split(':')[0])
            neighbour_str=line.split(':')[1].split(' ')
            for node in neighbour_str:
                neighbour_str
                self.metric_matrix[vid-1][int(node)-1]=0
        f.close()
    
    def insert(self,aa,bb,metric):
        a=int(aa)
        b=int(bb)
        metric=float(metric)
        
        #metric=round(float(metric),4)
        self.metric_matrix[a-1][b-1]=metric
        #print 'insert finish inside '+str(metric)
    def remove(self,aa):
        a=int(aa)
        #print 'start removing'
        for i in range(0,self.Vcnt):
            if i==a-1:
                for j in range(0,self.Vcnt):
                    self.metric_matrix[i][j]=999
            for j in range(0,self.Vcnt):
                if j==a-1:
                    self.metric_matrix[i][j]=999
        #self.printgraph()
                    
    
    def printgraph(self):
        for i in range(0,self.Vcnt):
            for j in range(0,self.Vcnt):
                print self.metric_matrix[i][j],
            print '\n'
    def returnneighbor(self,n):
        l=[]
        for i in range(0,self.Vcnt):
            if not self.metric_matrix[n-1][i]==999:
                l.append(i+1)
        return l
    def dijkstra(self,source):
        source=int(source)
        dist=[]
        tempdist=[]
        previous=[]
        for i in range(0,self.Vcnt):
            dist.append(999)
            tempdist.append(999)
            previous.append(0)
        dist[source-1]=0
        tempdist[source-1]=0

        q=self.nodes[:]
        while not q==[]:        
            u=tempdist.index(min(tempdist))+1       
            u_neighbor=self.returnneighbor(u)
            #print 'neighbors: '+str(u_neighbor)
            if tempdist[u-1]==999:
                #print 'break!'
                break
            #print 'u is '+str(u)
            #print 'q is '+str(q)
            q.remove(u) 
            for v in u_neighbor:
                alt=dist[u-1]+self.metric_matrix[u-1][v-1]
                #print 'alt is '+str(alt)
                if self.metric_matrix[u-1][v-1]==0: #neighbor metric is unknown, break in next loop
                    alt=999
                #print 'metric '+str(self.metric_matrix[u-1][v-1])
                if alt<dist[v-1]:
                    dist[v-1]=alt
                    tempdist[v-1]=alt
                    previous[v-1]=u              
            tempdist[u-1]=999
            #print 'dist is '+str(dist)
            #print 'templist'+str(tempdist)
        self.distance=dist
        self.prev=previous
        return dist, previous
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
    
if __name__=='__main__':
    g=graph('neighbor.txt')

    g.insert('1', '2', 1)
    g.insert('2', '1', 1)
    g.insert('2', '3', 1)
    g.insert('2', '4', 2)
    g.insert('3', '2', 1)
    g.insert('3', '4', 0.5)
    g.insert('3', '5', 7)
    g.insert('4', '2', 2)
    g.insert('4', '3', 0.5)
    g.insert('4', '5', 3)
    g.insert('5', '3', 7)
    g.insert('5', '4', 3)
    #g.printgraph()

    dis,prv=g.dijkstra(5)
    g.vid=5
    print dis
    print prv
    print g.calculate_route('3')
    #g.remove(4)
    #g.printgraph()
    #dis,prv=g.dijkstra(1)
    #print dis
    #print prv
    #g.insert('5', '4', 3)
    #dis,prv=g.dijkstra(1)
    #print dis
    #print prv
    
            
            
            