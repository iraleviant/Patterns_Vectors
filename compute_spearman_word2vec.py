import numpy
import codecs
import sys
import time
from numpy.linalg import norm
from numpy import dot
from scipy.stats import spearmanr

from sklearn.metrics.pairwise import pairwise_distances
import sklearn.preprocessing as pp

 
 
 
def distance(v1, v2, normalised_vectors=False):
    """
    Returns the cosine distance between two vectors.
    If the vectors are normalised, there is no need for the denominator, which is always one.
    """
    if normalised_vectors:
        return 1 - dot(v1, v2)
    else:
        return 1 - dot(v1, v2) / (norm(v1) * norm(v2))
 

 
 
def main():
     
    word_pairs_file='english_simlex_word_pairs_human_scores.dat' #0.451
    #word_pairs_file='SL_pairs_adj.dat' #0.674 (111 pairs)
    #word_pairs_file='SL_pairs_nouns.dat'  #0.437 (666 pairs)
    #word_pairs_file='SL_pairs_verbs.dat' #0.443 (222  pairs)
    
    
    
    words_model_file="vecs.vocab"
    vecs_model_file="vecs.npy"
    
    f = open(words_model_file, "r")
    words_model_list=(f.readlines()[0].split(" ")  )
    vecs_model=numpy.load(vecs_model_file)
    
    fread_human=codecs.open(word_pairs_file, 'r', 'utf-8')  #scores from felix hill

    model_dic={}
    for i,word in enumerate(words_model_list):
        model_dic[word]=vecs_model[i]
    
    
     
    scores_human=[]
    scores_model=[]
    lines_f = fread_human.readlines()[1:]  # skips the first line of "number of vecs, dimension of each vec"
    for line_f in lines_f:
        tokens = line_f.split(",")
        word_i = tokens[0].lower()
        word_j = tokens[1].lower()
        human_score = float(tokens[2])  
         
        if word_i in words_model_list and word_j in words_model_list:
            scores_human.append(human_score)
            current_distance=distance(model_dic[word_i],model_dic[word_j])
            scores_model.append(current_distance)
        else:
            pass
         
    
     
    spearman_rho = spearmanr(scores_model, scores_human)
     #spearman_rho_test = spearmanr([1,2,3,4,5], [5,6,7,8,7])  # (corr=0.82, pval=0.088)
     
    print ("The spearman corr is: ",  round(spearman_rho[0], 3) )
    print ("The coverage is: ", len(scores_human))
  
   
         
#################################################################     
########################
 
if __name__ == '__main__':
    main()
