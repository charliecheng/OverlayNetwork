import sys
class packet():
    def __init__(self,size):
        if size==1:
            self.f=open('overlay.py','r')
        if size==10:
            self.f=open('data.txt','r')
        self.m=''
    def read(self):
        for line in self.f:
            self.m=self.m+line
        

if __name__=='__main__':
    p=packet(10)
    p.read()
    s=''
    while 1:
        try:
            s=raw_input('VID:>')
            print s
        except KeyboardInterrupt:
            sys.exit()