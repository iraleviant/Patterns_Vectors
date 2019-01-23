import codecs
import time
from scipy.stats import spearmanr
import scipy.sparse as ss
import sklearn.preprocessing as pp


def main():
 
    mat_ant=ss.load_npz('mat_ppmi_ant.npz')

    #mat_sym=ss.load_npz('mat_ppmi_pos.npz')
    mat_sym=ss.load_npz('mat_ppmi_all_out.npz')
    
    dic_file_order='/home/ira/Google_Drive/IraTechnion/PhD/python/py_patts/cws_dictionary_allpats_python_order.dat'
    word_pairs_file='english_simlex_word_pairs_human_scores.dat'
    #word_pairs_file='SL_pairs_adj.dat' #0.63 (111 pairs), 0.632
    #word_pairs_file='SL_pairs_nouns.dat'  #0.373 (666 pairs), 0.358
    word_pairs_file='SL_pairs_verbs.dat' #0.402 (222  pairs),  0.526
    
    fread=codecs.open(dic_file_order)
    cws_clean={}
    
    lines_f = fread.readlines()[1:]
    for line_g in lines_f:
        line_f=line_g.strip()
        line=line_f.split(" ")
        cws_clean[line[0]]=line[1]
    print ("Finished reading content word dictionary its length is:", len(cws_clean))
    
    pair_list_human = [] #((word1,word2), human_score), only words that have vecs
    
    fread_simlex=codecs.open(word_pairs_file, 'r', 'utf-8')  #scores from felix hill
    
    new_dic={}
    rows_to_smooth=[]
    lines_f = fread_simlex.readlines()[1:]  # skips the first line of "number of vecs, dimension of each vec"
    for line_f in lines_f:
        tokens = line_f.split(",")
        word_i = tokens[0].lower()
        word_j = tokens[1].lower()
        score = float(tokens[2])  
        if word_i in cws_clean and word_j in cws_clean:
            pair_list_human.append(((word_i, word_j), score))
            if word_i not in new_dic:
                rows_to_smooth.append(int(cws_clean[word_i]))
                new_dic[word_i]=int(cws_clean[word_i])
            if word_j not in new_dic:
                rows_to_smooth.append(int(cws_clean[word_j]))
                new_dic[word_j]=int(cws_clean[word_j])
        
    rows_to_knn=set(rows_to_smooth)
    
    ######################################################################
   
    print (" Start to loop over beta values" )
    
    for a in range (103,104): #a=103, b=202 corr=0.421; a=103 b=210  corr=0.427 (not with pos mat)
        print ("The value of a is:", a)
        for b in range(210,211):
        #beta=10 #Typical values are 7 and 10
            mat_f=a*mat_sym-b*mat_ant
            #mat_f=a*mat_ant-b*mat_sym
            ######################################################  COSINE            ################################
            nmat=mat_f.T #important for svd, for regular doesn't matter since the matrix is symmetric
            col_normed_mat = pp.normalize(nmat.tocsc(), axis=0) 
            del mat_f
               
            cols_cos=list(sorted(set(rows_to_knn))) 
         
            new_mat=col_normed_mat[:,cols_cos]
            simL= new_mat.T * new_mat # cosine values matrix (count, count)
            #rowsL, colsL = simL.nonzero()
            
            pair_list_human.sort(key=lambda x: - x[1])  ###sorts the list according to the human scores in descreasing order
            #coverage = len(pair_list_human)
        
            model_scores = {} #{key=(word1,word2), value=cosine_sim_betwen_vectors}    
            cnt=0
            for (x, y) in pair_list_human: #pair_list_human:((vanish,disappear),9.8)
                (word_i, word_j) = x
                cnt+=1
                #r=new_dic_s[word_i]
                #c=new_dic_s[word_j]
                r=list(cols_cos).index(new_dic[word_i])
                c=list(cols_cos).index(new_dic[word_j])
                cosval=simL[r,c]
                model_scores[(word_i, word_j)] = round(cosval,2)
             
            spearman_human_scores=[]
            spearman_model_scores=[]
                 
            for position_1, (word_pair, score_1) in enumerate(pair_list_human):
                score_2 = model_scores[word_pair]
                spearman_human_scores.append(score_1)
                spearman_model_scores.append(score_2)  
             
            spearman_rho = spearmanr(spearman_human_scores, spearman_model_scores)
             
            print ("The beta and spearman corr is: ", b ,":", round(spearman_rho[0], 3))
        
        
    #mat_res_file='/home/ira/Dropbox/IraTechnion/Patterns_Research/sp_sg/svd_reduced800_mat_ppmi_round_allpats_ant_sym_10.npz'
    #ss.save_npz(mat_res_file, csr_matrix(mat_f))
    print ("i'm here")
#################################################################     
########################

if __name__ == '__main__':
    main()
