import codecs
import sys
import re
import numpy as np
from scipy.sparse import csr_matrix, lil_matrix
#from scipy import sparse
import scipy.sparse as ss
import time

PATT_STR="PATT"
CW_SYMBOL="CW"
PATT_ELEMENTS_SEPERATOR=" "
HIGH_FREQUENCY_THR =0.002  #0.002 #0.2#0.002#use constant HIGH_FREQUENCY_THR => 0.002; orig, mine_test=0.8
MIN_FREQ = 100#3  #100 #3#200 #orig=100, mine_test=3

### code assumes lower case corpus 


class Trie(object):
    """ Trie implementation in python 
    """
    def __init__(self, ):
        """ So we use a dictionary at each level to represent a level in the hashmap
        the key of the hashmap is the string and the value is another hashmap 
        
        """
        self.node = {}
        self={}
        
    def build(self, pattern):
        """
        Takes a pattern and splits it to its components  
        Arguments:
        - `pattern`: The pattern to be stored in the trie
        """
        node = self.node
        cw_indices=[]
        for cnt, patt in enumerate(pattern.split(PATT_ELEMENTS_SEPERATOR)):
            if patt==CW_SYMBOL:
                cw_indices.append(cnt)
            if patt in node:
                node = node[patt]
            else:
                node[patt] = {}
                node = node[patt]
        node[PATT_STR]=[pattern, cw_indices]
        node = node[PATT_STR]

    def sub_trie(self, patt): #returns the sub trie with 'root'=patt
        node = self.node
        if patt in node:
            subtr=Trie()
            subtr.node=node[patt]
            return subtr
    

def read_patterns_trie(patterns_input_file):
    """ 
    implementing # Read patterns into a Trie data structure.
    """
    #patterns_input_file='/home/ira/Dropbox/IraTechnion/Patterns_Research/sp_sg/selected_patterns.dat'
    print ("Reading patterns from: ", patterns_input_file)
    
    tr=Trie()
    n_patts=0
    with open(patterns_input_file, 'r', encoding="Latin-1") as ifh:
        for patt_line in ifh:
            n_patts+=1
            patt_line=patt_line.rstrip()
            tr.build(patt_line)
  
    print ("Read", n_patts,  " patterns")
    return tr


def add_patt_instance(words, start, patt_index, patterns_trie, cws_clean_order, co_mat, word_vocab, context_vocab, ofh):
    
    # Pattern found.
    if PATT_STR in patterns_trie.node:
        #orig_patt_str=patterns_trie.node[PATT_STR][0] #for example: 'CW-and-CW'
        cw_indices=np.asarray(patterns_trie.node[PATT_STR][1]) #for example: [0 2]
        beg_index=start-patt_index
        pattern_words=words[beg_index:beg_index+cw_indices[1]+1] #for example: big and small
        elements=np.array(pattern_words)[cw_indices] #elements[0]=big, elements[1]=small
        
        ###############################################################
        ###############    Only for word2vec   #######################
        ##############################################################
        if elements[0] in word_vocab:
            word_vocab[elements[0]]+=1
        else:
            word_vocab[elements[0]]=1
           
        if elements[1] in word_vocab :
            word_vocab[elements[1]]+=1
        else:
            word_vocab[elements[1]]=1
        
        
        if str(elements[0])+"_r" in context_vocab:
            context_vocab[str(elements[0])+"_r"]+=1
        else:
            context_vocab[str(elements[0])+"_r"]=1
           
        if elements[1] in context_vocab :
            context_vocab[elements[1]]+=1
        else:
            context_vocab[elements[1]]=1
        
        ofh.write(elements[0]+" "+elements[1]+"\n")
        
        ### this part not clear at all  ?????????????????????????????
        word_vocab[elements[1]]+=1 ## why increase by one the same right word as before in word_vocab?
        #$elements[0] .= "_r";
        context_vocab[str(elements[0])+"_r"]+=1 ## why increase by one the same left word as before in word_vocab?
        
        ofh.write(elements[1]+" "+elements[0]+"_r"+"\n")
        
        ################################################################
        ################################################################
        
        #update the co-occorence mat
        row=int(cws_clean_order[elements[0]])
        col=int(cws_clean_order[elements[1]])
       
        if row != col:
            co_mat[row,col]+=1
            co_mat[col,row]+=1
        else:
            co_mat[row,col]+=1
        
       
    # Recursion break condition.
    if start== len(words):
        return
    # Return if word is empty or punctuation, same as in function get_cws, check it
    #if len(word)==0 or not re.match(r'^[a-zA-Z]+$', word):  #r'\b[a-zA-Z]+\b', \b-# Assert position at a word boundary
    #match=re.search(r'^[^a-z]+$', words[start])
    elif  not bool(re.match(r'^[a-z]+$', words[start])) or not(len(words[start])) :
        return
    
    
    # Next word could either be one of the words the continues a pattern, or a wildcard.
    if words[start] in patterns_trie.node :
        substr=patterns_trie.sub_trie(words[start])
        add_patt_instance(words, start+1,patt_index+1, substr, cws_clean_order, co_mat, word_vocab, context_vocab, ofh)
    elif (bool(re.search(r'^[a-z]+$', words[start]))) and (words[start] in cws_clean_order ) and (CW_SYMBOL in patterns_trie.node ) :
        substr=patterns_trie.sub_trie(CW_SYMBOL)
        add_patt_instance(words, start+1, patt_index+1, substr, cws_clean_order, co_mat, word_vocab, context_vocab, ofh)
        
def write_vocab(dic, output_file):
    
    sorted_vocab=sorted(dic.items(), key=lambda x:-x[1]) #sorted_vocab is a tuple ('cute', 4)
    
    # Add dummy </s> node.
    with open(output_file, 'w', encoding="Latin-1") as ofh:
        ofh.write('</s> 0\n')
        for k in sorted_vocab:
            ofh.write(k[0])
            ofh.write(' ')
            ofh.write(str(k[1]))
            ofh.write('\n')
    
def get_cws(files):
    print ("Generating word count")
    # Generate list from text
    n_sent=0
    n_words=0
    stats={}
    
    for corpus_file in files:
        print ("Reading  ", corpus_file)        
        #lines = ifh.readlines()
        with open(corpus_file, 'r', encoding="Latin-1") as ifh:
            for line in ifh:
                n_sent+=1
                if n_sent % 1 == 0: #n_sent divides in 10000 without remainder
                    print  (str(round(float(n_sent)/1000, 0))+'K', end="\r")
                    time.sleep(0.1)

                # Randomly skip 90% of the sentences to get an even distribution of the data.
                line=line.rstrip()
                #line=line.lower() #lower case
                #words=line.split(" ")
                words=re.findall(r'\w+|[^\w\s]+', line) #this is the closest to perl

                #words=re.findall(r'\w+|[^\w\s]+', line)
                
                for word in words:
                    # Skip empty words and punctuation.
                
                    if not bool(re.match(r'^[a-z]+$', word)) or not(len(word))  :
                        continue
                    
                    n_words+=1
                    if word in stats:
                        stats[word]+=1  #stats is a dictionary of all words and their counts {alliance=>'1', it=> '1'}
                    else:
                        stats[word]=1
        #ifh.close() 
            
    print ("The size of words dictionary is: ", len(stats))      
       
    cws={}
        
    sotred_words=sorted(stats.items(), key=lambda x:-x[1]) #sorts the words in stats based to their fequency(values) from top to bottom 
    
    for word in sotred_words: #word is a tuple: ('cute', 4)
        #tmp=stats[word[0]]
        if float(stats[word[0]])/n_words > HIGH_FREQUENCY_THR:
            continue    
        elif  stats[word[0]]>= MIN_FREQ:
            cws[word[0]]=word[1]
        else:
            break #it is sorted of the the word with the highest frequency doesn't> min_freq than none will be
            
    print ("Selected", len(cws) , " content words")
    return cws

    
def main():
    
    #input_files="/home/ira/Google_Drive/IraTechnion/PhD/corpus/english_test"
    #input_files="/home/ira/Google_Drive/IraTechnion/PhD/corpus/mini_english_test.txt"
    #input_files="/home/ira.leviant@st.technion.ac.il/clean_corpus/webbase_all_clean.txt,/home/ira.leviant@st.technion.ac.il/clean_corpus/clean_wiki_new.txt,/home/ira.leviant@st.technion.ac.il/clean_corpus/billion_word_clean.txt,/home/ira.leviant@st.technion.ac.il/clean_corpus/news_2012_clean,/home/ira.leviant@st.technion.ac.il/clean_corpus/news_2013_clean"
    #input_files="/home/ira/Google_Drive/IraTechnion/PhD/corpus/billion_word_clean.txt,/home/ira/Google_Drive/IraTechnion/PhD/corpus/news_2012_clean,/home/ira/Google_Drive/IraTechnion/PhD/corpus/news_2013_clean,/home/ira/Google_Drive/IraTechnion/PhD/corpus/webbase_all_clean.txt,/home/ira/Google_Drive/IraTechnion/PhD/corpus/clean_wiki_new.txt"
    input_files="/home/ira/Google_Drive/IraTechnion/PhD/corpus_2/webbase_phrase2.txt,/home/ira/Google_Drive/IraTechnion/PhD/corpus_2/billion_phrase2.txt,/home/ira/Google_Drive/IraTechnion/PhD/corpus_2/wiki_phrase2.txt,/home/ira/Google_Drive/IraTechnion/PhD/corpus_2/news2012_phrase2.txt,/home/ira/Google_Drive/IraTechnion/PhD/corpus_2/news_2013_phrase2.txt"

    
    #patterns_input_file='selected_patterns.dat'#"selected_patterns_py.txt"
    #patterns_input_file='selected_patterns_py.txt'#"selected_patterns_py.txt"
    #patterns_input_file='selected_patterns_py_pos.txt'#"selected_patterns_py.txt"
    patterns_input_file='selected_patterns_py_pos_2.txt'#"selected_patterns_py.txt"

    
    
    
    context_vocab_file="context_vocab_out_python_pos_2phrase.txt"#file mapping context strings to 
    context_pairs_output_file ="context_file_out_python_pos_2phrase.txt"
    #dic_file='cws_dictionary_all_pats_python.dat' #already ready
    #dic_file_order='cws_dictionary_allpats_python_order.dat'#already ready
    dic_file_order='cws_dictionary_allpats_python_order_2phrase.dat'
    word_vocabulary_output_file='word_vocab_python_allpats_python_pos_2phrase.dat'
    mat_file='all_pats_python_mat_pos_2phrase.npz'
    # Read patterns into a Trie data structure.
    patterns_trie = read_patterns_trie(patterns_input_file)
    
    ifs = input_files.split(",")  #ifs=input files, spolits in case there are several input files
        
    #cws_clean={} # dictionary of content words with their counts
   
    fread=codecs.open(dic_file_order, encoding="Latin-1")
    cws_clean_order={}
    
    lines_f = fread.readlines()[1:]
    for line_g in lines_f:
        line_f=line_g.strip()
        line=line_f.split(" ")
        cws_clean_order[line[0]]=line[1]
    print ("Finished reading content word dictionary its length is:", len(cws_clean_order) )
    
    
    #co_mat = lil_matrix((395148), (395148) )
    co_mat = lil_matrix((len(cws_clean_order), len(cws_clean_order)) )
     
    n_lines = 0
    #pat_words={}
    word_vocab={}
    context_vocab={}
    ofh = open(context_pairs_output_file ,'w', encoding="Latin-1")

    for corpus_file in ifs:
        n_lines = 0
        print ("Reading ", corpus_file)
       
        with open(corpus_file, 'r', encoding="Latin-1") as ifh:
          
            for line in ifh:
                n_lines=n_lines+1
                if n_lines % 10000 == 0: #n_lines divides in 10000 without remainder
                    print  (str(round(float(n_lines)/1000, 0))+'K', end="\r")
                    time.sleep(0.1)

                line=line.strip()
                line=line.lower() 
                #my @words = split("[ \t]++|\\b", $line);
                words=re.findall(r'\w+|[^\w\s]+', line) #this version the same as perl, \w+ - 1 or more word chars (letters, digits or underscores), | - or, [^\w\s] - 1 char other than word / whitespace
                
                # Search for patterns starting at each word in the sentence.
                end_loop=len(words)-2 #maybe error,need to change to -1
                for start in range(0,end_loop): 
                    add_patt_instance(words, start, 0, patterns_trie, cws_clean_order, co_mat, word_vocab ,context_vocab, ofh)
                    #add_patt_instance(\@words, $start, 0, $patterns_trie, $cws, $ofh, \%word_vocab, \%context_vocab);
    #===========================================================================
    
    ofh.close()
    print ("Preparing to write co-occurence mat to file")
    
    ss.save_npz(mat_file, csr_matrix(co_mat))

    write_vocab(word_vocab, word_vocabulary_output_file)
    write_vocab(context_vocab, context_vocab_file)
    
    print ("I'm here")
#################################################################     
#################################################################

if __name__ == '__main__':
    main()
