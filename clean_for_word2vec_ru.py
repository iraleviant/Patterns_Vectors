import sys
import re
import numpy as np
from scipy.sparse import csr_matrix, lil_matrix
import scipy.sparse as ss
import time

  
def main():
    
    input_file="/home/ira/Google_Drive/IraTechnion/PhD/corpus_ru/wiki_ru"
    #input_files="/home/ira/Google_Drive/IraTechnion/PhD/corpus_ru/russian_test"

    outfile="clean_ru.txt"
    #
    n_lines = 0
    #pat_words={}
    word_vocab={}
    context_vocab={}
    ofh = open(outfile ,'w', encoding="utf-8")


    with open(input_file, 'r', encoding="utf-8") as ifh:
        for line in ifh:
            list_words=[]
            n_lines=n_lines+1
            if n_lines % 10000 == 0: #n_lines divides in 10000 without remainder
                print  (str(round(float(n_lines)/10000, 0))+'K', end="\r")
                time.sleep(0.1)
                 
            line=line.strip()
            line=line.lower() 
            #my @words = split("[ \t]++|\\b", $line);
            words=re.findall(r'\w+|[^\w\s]+', line) #this version the same as perl, \w+ - 1 or more word chars (letters, digits or underscores), | - or, [^\w\s] - 1 char other than word / whitespace
            
            #words=re.split(" ", line)
            
            for word in words:
                    # Skip empty words and punctuation.
                
                    if not bool(re.match(r'[^\W0-9a-z]+$', word)) or not(len(word))  : #a-z_ for word 2 phrase
                        continue
                    else:
                        list_words.append(word)
            
            
            new_str=" ".join(list_words)
            ofh.write(new_str)
            ofh.write(" \n")

    ofh.close()
    
   
    print ("I'm here")
#################################################################     
#################################################################

if __name__ == '__main__':
    main()
