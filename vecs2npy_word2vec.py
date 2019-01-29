import numpy as np
import sys
import codecs


filne="dim200vecs"    #file(sys.argv[1])
#fh= open(filne, 'r+')


with open(filne, 'r') as fh:
    first = fh.readline()
    

foutname="vecs"  #sys.argv[2]
size=list (map(int,first.strip().split()) )

wvecs=np.zeros((size[0],size[1]),float)

vocab=[]
fh= codecs.open(filne, 'r')
next(fh)
for i,line in enumerate(fh):
    line = line.strip().split()
    vocab.append(line[0])
    wvecs[i,] = np.array( list(map(float,line[1:]))   )

np.save(foutname+".npy",wvecs)
with codecs.open(foutname+".vocab","w") as outf:
    outf.write(" ".join(vocab))
    
print("I'm here")
