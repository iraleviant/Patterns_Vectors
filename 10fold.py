import numpy
import codecs
import sys
import time
from scipy.stats import spearmanr
import scipy.sparse as ss
from sklearn.metrics.pairwise import pairwise_distances
import sklearn.preprocessing as pp
from scipy.sparse import csr_matrix
from scipy.sparse import csc_matrix
from scipy  import sparse
import sklearn.preprocessing as pp
from sklearn.model_selection import train_test_split
from sklearn import model_selection
from operator import itemgetter 

def main():
    #######################################################################################################################
    dic_file_order='cws_dictionary_allpats_python_order_2phrase.dat'

    word_pairs_file='english_simlex_word_pairs_human_scores.dat'
    #word_pairs_file='SL_pairs_adj.dat' #0.63 (111 pairs)
    #word_pairs_file='SL_pairs_nouns.dat'  #0.373 (666 pairs)
    #word_pairs_file='SL_pairs_verbs.dat' #0.402 (222  pairs)
    ppmi_mat='mat_ppmi_all_2phrase.npz' #0.407
    #ppmi_mat='all_pats_python_mat.npz'
 
    
    fread=codecs.open(dic_file_order)
    cws_clean={}
    
    lines_f = fread.readlines()[1:]
    for line_g in lines_f:
        line_f=line_g.strip()
        line=line_f.split(" ")
        cws_clean[line[0]]=line[1]
    print ("Finished reading content word dictionary its length is:", len(cws_clean) )     
     
    fread_human=codecs.open(word_pairs_file, 'r', 'utf-8')  #scores from felix hill

    pair_list_human=[]
    lines_f = fread_human.readlines()[1:]  # skips the first line of "number of vecs, dimension of each vec"
    for line_f in lines_f:
        tokens = line_f.split(",")
        word_i = tokens[0].lower()
        word_j = tokens[1].lower()
        score = float(tokens[2])  
        if word_i in cws_clean and word_j in cws_clean:
            pair_list_human.append(((word_i, word_j), score))
    ############################  10FOLD     ###############################################
    
    spr_list=[]
    n_splits=10
    for n in range(0,n_splits):
        print("Split number", n)
        train, test= train_test_split(pair_list_human, test_size=0.75, random_state=None) #None is random
        print("len test", len(test) )
        count=0
        new_dic={}
        cols_to_cos=[]
        for ((word_i,word_j),y) in test: #pair_list_human:((vanish,disappear),9.8)
            
            if word_i not in new_dic:
                cols_to_cos.append(int(cws_clean[word_i]))
                new_dic[word_i]=int(cws_clean[word_i])
                count+=1
            if word_j not in new_dic:
                cols_to_cos.append(int(cws_clean[word_j]))
                new_dic[word_j]=int(cws_clean[word_j])
                count+=1
        else:
            pass
         
        cols_cos=list(sorted(set(cols_to_cos))) 
        list_dic=sorted(new_dic.items(), key=lambda x: x[1]) #sort dictionary by increasing values
     
        new_dic_s={}
        index=0
        for (e,ind) in list_dic:
            new_dic_s[e]=index
            index+=1
         
        mat=ss.load_npz(ppmi_mat)
    
        nmat=mat.T #important for svd, for regular doesn't matter since the matrix is symmetric
        col_normed_mat = pp.normalize(nmat.tocsc(), axis=0) 
        del mat
    
    
    
        new_mat=col_normed_mat[:,cols_cos]
        simL= new_mat.T * new_mat # cosine values matrix (count, count)
        #rowsL, colsL = simL.nonzero()
     
    
        #new_pair_list.sort(key=lambda x: - x[1])  ###sorts the list according to the human scores in descreasing order
        #coverage = len(new_pair_list)
 
        model_scores = {} #{key=(word1,word2), value=cosine_sim_betwen_vectors}    
        cnt=0
        for (x, y) in test: #pair_list_human:((vanish,disappear),9.8)
            (word_i, word_j) = x
            cnt+=1
            if cnt % 10 == 0: #n_lines divides in 10000 without remainder
            #print  str(cnt)+'\r'
                sys.stdout.flush()
            r=new_dic_s[word_i]
            c=new_dic_s[word_j]
            cosval=simL[r,c]
            model_scores[(word_i, word_j)] = round(cosval,2)
      
        spearman_human_scores=[]
        spearman_model_scores=[]
         
        for position_1, (word_pair, score_1) in enumerate(test):
            score_2 = model_scores[word_pair]
            spearman_human_scores.append(score_1)
            spearman_model_scores.append(score_2)  
      
        spearman_rho = spearmanr(spearman_human_scores, spearman_model_scores)
        spr_list.append(round(spearman_rho[0], 3))
        print ("The spearman corr is: ",  round(spearman_rho[0], 3) )
        print ("The coverage is: ", len(new_dic_s))
         
    print ("The avg spearman corr is: ", round( sum(spr_list) / float(len(spr_list))  , 3)  )
         
    print ("i'm here")
#################################################################     
########################
 
if __name__ == '__main__':
    main()
