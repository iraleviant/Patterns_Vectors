import codecs
import numpy as np
from scipy.sparse import csr_matrix, lil_matrix
import scipy.sparse as ss
import time


def main():
   
    mat_out_file='mat_ppmi_all_out.npz'
    #dic_file='/home/ira/Dropbox/IraTechnion/Patterns_Research/sp_sg/cws_dictionary_all.txt'
    dic_file_order='/home/ira/Google_Drive/IraTechnion/PhD/python/py_patts/cws_dictionary_allpats_python_order.dat'
    
    mat_input_file='/home/ira/Google_Drive/IraTechnion/PhD/python/py_patts/all_pats_python_mat.npz'
    ###############################################################################################
   
    fread=codecs.open(dic_file_order)
    cws_clean={}
    
    lines_f = fread.readlines()[1:]
    for line_g in lines_f:
        line_f=line_g.strip()
        line=line_f.split(" ")
        cws_clean[line[0]]=line[1]
    print ("Finished reading content word dictionary its length is:", len(cws_clean) )
   
    
    mat=ss.load_npz(mat_input_file)
    #(nrows, ncols) = mat.get_shape() # gets the original shape in this case (169836, 169836)
        
    colTotals =  mat.sum(axis=0)  # sum the columns
    N = np.sum(colTotals)
    rowTotals = mat.sum(axis=1)  # sum the rows
 
    nonzeroRows=mat.nonzero()[0]
    nonzeroCols=mat.nonzero()[1]
    
    matres = lil_matrix((len(cws_clean), len(cws_clean)) )
    
    for ind, row in enumerate(nonzeroRows):
        if ind % 100000 == 0: #n_lines divides in 10000 without remainder
            print  (str(row)+'\r' , end="\r")
            time.sleep(0.01)
        col=nonzeroCols[ind]
        val = np.log((mat[row,col] * N) / float(rowTotals[row,0] * colTotals[0,col])) #its actually ln
        #matres[row,col] = max(0, val) #consider round
        matres[row,col] = max(0, round(val,2))
   
    ss.save_npz(mat_out_file, csr_matrix(matres))
    print (" i'm here")
    
#################################################################     
########################

if __name__ == '__main__':
    main()
