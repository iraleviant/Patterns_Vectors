import codecs
import sys
import re
import numpy as np
import json
import h5py
from scipy.sparse import csr_matrix, lil_matrix
from scipy import sparse
import scipy.sparse as ss

PATT_STR="PATT"
CW_SYMBOL="CW"
PATT_ELEMENTS_SEPERATOR="-"
HIGH_FREQUENCY_THR = 0.002#use constant HIGH_FREQUENCY_THR => 0.002; orig, mine_test=0.8
MIN_FREQ =200 #orig=100, mine_test=3

# link to the script that downloads and preprocesses the corpora: https://code.google.com/archive/p/word2vec/

#files="/home/ira/Google_Drive/IraTechnion/PhD/corpus/webbase_all_clean.txt" #unique word num 3166906, tokens 3332411362 ~ 3.3 G
#files="/home/ira/Google_Drive/IraTechnion/PhD/corpus/clean_wiki_new.txt" # 9455968  ,  4151058980~ $4G
#files="/home/ira/Google_Drive/IraTechnion/PhD/corpus/billion_word_clean.txt"  # 936249  #791845574 ~791.8 M
#files="/home/ira/Google_Drive/IraTechnion/PhD/corpus/news_2012_clean"  #565336 , :  354722554 ~354.7 M
#files="/home/ira/Google_Drive/IraTechnion/PhD/corpus/news_2013_clean" #758994 ,  508011282 ~508 M
#files="/home/ira/Google_Drive/IraTechnion/PhD/corpus/english_test" 

#files="/home/ira/Google_Drive/IraTechnion/PhD/corpus/webbase_phrase2.txt" #tokens  3199825084 ~3.19G
files="/home/ira/Google_Drive/IraTechnion/PhD/corpus/wiki_phrase2.txt" # 3911786598 ~3.9G
#files="/home/ira/Google_Drive/IraTechnion/PhD/corpus/billion_phrase2.txt"  #  747554756 ~747 M
#files="/home/ira/Google_Drive/IraTechnion/PhD/corpus/news2012_phrase2.txt"  #  336068364 ~336M
#files="/home/ira/Google_Drive/IraTechnion/PhD/corpus/news_2013_phrase2.txt" #478173581~ 478M


#vocab={}
def main():
    words_num=0

    print ("Generating word count")
    # Generate list from text
    n_sent=0
 
    ifs = files.split(",")
    for corpus_file in ifs:
        print ("Reading  ", corpus_file)
    
        with open(corpus_file, 'r',  encoding = "ISO-8859-1") as ifh:
            for line in ifh:
                n_sent+=1
                if n_sent % 500000 == 0: #n_sent divides in 10000 without remainder
                    print ( str(round(float(n_sent)/1000, 0))+'K'+'\r', )
                    sys.stdout.flush()
                # Randomly skip 90% of the sentences to get an even distribution of the data.
                line=line.rstrip()
         
                words=re.findall(r'\w+|[^\w\s]+', line) #this is the closest to perl                
                words_num+=len(words)
                #===============================================================
                # 
                # for word in words:
                #     if not bool(re.match(r'^[a-z_$]+$', word)): #only words that include a-z or _ or $ included special word dont go through like confédération
                #         continue
                #        
                #     elif word not in vocab:
                #         vocab[word]=1
                #     else:
                #         vocab[word]+=1
                #===============================================================
    
    print ("The number of words is: ",words_num) 
       
   

#################################################################################################
#################################################################################################
if __name__ == '__main__':
    main()
