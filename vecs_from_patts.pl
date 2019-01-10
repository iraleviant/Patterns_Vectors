#!/usr/local/bin/perl -w

#########################################################################
#																		#
#	1. input files: one or more plain text files (separated by commas)

#2. patterns input file: a file containing the symmetric pattern types, one pattern per line, 
#where pattern elements are separated by hyphens, and wildcards are marked by the CW symbol. 
#For example, the pattern "X and Y" is written "CW-and-CW". 
#The file for generating the patterns experimented with in the paper can be found in the file "selected_patterns.dat". 
#In order to generate your own set of symmetric patterns,

#3. context pairs output file: an output file that will contain the list of (words,context) pairs 
#to be fed as input to the word2vec toolkit.

#4. word vocab output file: an output file that will contain the word vocabulary to be fed as input to the word2vec toolkit.

#5. context vocab output file: an output file that will contain the context vocabulary to be fed as input to the word2vec toolkit.
#
#6. unigram input file: if you have a pre-computed file with unigram frequencies, This script takes a corpus of plain text and a set of 
#this can speed up the process (otherwise the script computes it, which takes time). 
#The input format is one line per word of the format "word count". E.g.,
#the	438738378				#
#				#
#																		#
#	Author: Roy Schwartz (roys02@cs.huji.ac.il)							#
#																		#
#########################################################################

## write also cws, what the diff between word vocab and context vocab

use strict;
use IO::File;
use warnings FATAL => 'all';
STDOUT->autoflush;

use List::Util qw(sum);

use constant CW_SYMBOL => "CW";
use constant PATT_STR => "PATT";

use constant PATT_ELEMENTS_SEPERATOR => "-";
use constant HIGH_FREQUENCY_THR => 0.2; #use constant HIGH_FREQUENCY_THR => 0.002; orig, mine_test=0.8
use constant MIN_FREQ => 3; #orig=100, mine_test=3

sub add_patt_instance($$$$$$$$);

sub main(@) {
	
	#my $input_files = "/home/ira/Google_Drive/IraTechnion/PhD/corpus/english_test";
	my $input_files = "/home/ira/Google_Drive/IraTechnion/PhD/corpus/mini_english_test.txt";
	my $patterns_input_file ="selected_patterns.dat"; # "output_perl.txt";#"selected_patterns.dat";
	
	my $context_pairs_output_file = "context_file_out_perl.txt"; #all the words(as pairs)in the found patterns:big small, small big_r
	my $word_vocabularty_output_file = "word_vocab_file_perl.txt"; #file mapping words (strings) to their counts: girl 38, boy 19..
	my $context_vocabularty_output_file = "context_vocab_out_perl.txt";#file mapping context strings to their counts:girl 19, boy_r 38
	my $cws_vocabularty_output_file="cws_vocab_out_perl.txt";
	
	my $word_count_file;
	
	if (@_) {
		$word_count_file = shift;
	}

	# Read patterns into a Trie data structure.
	my $patterns_trie = read_patterns_trie($patterns_input_file);

	my %word_vocab;
	my %context_vocab;
	
	my @ifs = split("[,% ]", $input_files);
	
	# Now generate a list of content words which are considered as wildcard candidates.
	my ($cws) = get_cws($word_count_file, \@ifs, $cws_vocabularty_output_file);

	
	
	my $ofh = new IO::File(">$context_pairs_output_file") or die "Can't open $context_pairs_output_file for writing";
		
	my $n_lines = 0;
	
	# Traverse input files.
	foreach my $if (@ifs) {
		my $n_lines = 0;
		print "Reading $if\n";
		my $ifh = new IO::File($if);
		
		unless ($ifh) {
			warn "Cannot open $if for reading";
			next;
		}
		
		while (my $line = $ifh->getline()) {
			if (++$n_lines % 10000 == 0) {
				printf("%dK %c", $n_lines/1000, 13);
			}

			chomp($line);
			$line = lc($line);
            
            my @words = split("[ \t]++|\\b", $line);
			
			# Search for patterns starting at each word in the sentence.
			for (my $start = 0 ; $start < @words - 2 ; ++$start) {
				add_patt_instance(\@words, $start, 0, $patterns_trie, $cws, $ofh, \%word_vocab, \%context_vocab);
			}
		}
		
		$ifh->close();

		print "\n";
	}
	
	$ofh->close();

	# Writing word and context vocabularies.
	write_vocab(\%word_vocab, $word_vocabularty_output_file);
	write_vocab(\%context_vocab, $context_vocabularty_output_file);
	
	return 0;
}


# Write vocabulary to file.
sub write_vocab($$) {
	my $vocab = shift;
	my $of = shift;
	
	my @sorted_vocab = sort {$vocab->{$b} <=> $vocab->{$a}} keys %$vocab;
	
	my $ofh = new IO::File(">$of");
	
	unless ($ofh) {
		warn "Can't open $of for writing";
		return;
	}
	
	# Add dummy </s> node.
	$ofh->print("<\/s> 0\n");
	
	foreach my $k (@sorted_vocab) {
		$ofh->print("$k $vocab->{$k}\n");
	}
	
	$ofh->close();
}


# Read patterns from file and generate a Trie dataset.
sub read_patterns_trie($) {
	my $patterns_input_file = shift;
	
	print "Reading patterns from $patterns_input_file\n";
	
    my $ifh = new IO::File($patterns_input_file) or die "Cannot open $patterns_input_file for reading";
        
	my %trie;
	
	my $n_patts = 0;
	while (my $patt = $ifh->getline()) {
		$n_patts++;
		chomp($patt);
		my @elements = split(PATT_ELEMENTS_SEPERATOR, $patt);
		
		# wildcard indices.
		my @cw_indices;
		my $local_trie = \%trie;
		foreach my $i (0 .. $#elements - 1) {
			if ($elements[$i] eq CW_SYMBOL) {
				push(@cw_indices, $i);
			}
			unless (exists ($local_trie->{$elements[$i]})) {
				$local_trie->{$elements[$i]} = {};
			}
			
			$local_trie = $local_trie->{$elements[$i]};
		}
		
		if ($elements[$#elements] eq CW_SYMBOL) {
			push(@cw_indices, $#elements);
		}
		
		unless (exists $local_trie->{$elements[$#elements]}) {
			$local_trie->{$elements[$#elements]} = {};
		}
		
		$local_trie->{$elements[$#elements]}->{PATT_STR} = [$patt, \@cw_indices];
	}
	
	$ifh->close();
	
	print "Read $n_patts patterns\n";
	return \%trie;
}

# Add pattern instance to statistics.
sub add_patt_instance($$$$$$$$) {
	my $elements = shift;
	my $start = shift;
	my $patt_index = shift;
	my $patterns_trie = shift;
	my $cws = shift;
	my $ofh = shift;
	my $word_vocab = shift;
	my $context_vocab = shift;

	# Pattern found.Selected 6 content words.
	
	if (exists $patterns_trie->{PATT_STR}) {
		my ($orig_patt_str, $cw_indices) = @{$patterns_trie->{PATT_STR}};
		print "Found pattern:  ".$orig_patt_str." \n";

		# Pattern found!
		my @elements = @$elements[map {$_ + $start - $patt_index} @$cw_indices];
		$word_vocab->{$elements[0]}++;
		$context_vocab->{$elements[1]}++;
		$word_vocab->{$elements[1]}++;
		$context_vocab->{$elements[0]."_r"}++;
		$ofh->print($elements[0]." ".$elements[1]."\n");
		
		
		print "Pattern cws 1:  ".$elements[0]." \n";
		print "Pattern cws 2:  ".$elements[1]." \n";
		
		$word_vocab->{$elements[1]}++; ## why increase by one the same right word as before in word_vocab?
		$elements[0] .= "_r";
		
		$context_vocab->{$elements[0]}++; ## why increase by one the same left word as before in word_vocab?

		$ofh->print($elements[1]." ".$elements[0]."\n");
	} 
	
	# Recursion break condition.
	if ($start == @$elements) {
		return;
	 # Return if word is empty of punctuation.
	} elsif ($elements->[$start] =~ /^[^a-z]++$/ or not length($elements->[$start])) {
		return;
	}

	# Next word could either be one of the words the continues a pattern, or a wildcard.
	if (exists $patterns_trie->{$elements->[$start]}) {
		add_patt_instance($elements, $start+1, $patt_index+1, $patterns_trie->{$elements->[$start]}, $cws, $ofh, $word_vocab, $context_vocab);
	} elsif (not $elements->[$start] =~ /^[^a-z]++$/ and exists $cws->{$elements->[$start]} and exists $patterns_trie->{${\CW_SYMBOL}}) {
		add_patt_instance($elements, $start+1, $patt_index+1, $patterns_trie->{${\CW_SYMBOL}}, $cws, $ofh, $word_vocab, $context_vocab);
	} 
}


# Get a list of content words. High freqent words and low frequent words are discarded.
sub get_cws($$$) {
	my $word_count_file = shift;
	my $ifs = shift;
	my $cws_vocabularty_output_file=shift;
	
	my %stats;
	
	my $n_words = 0;
	my $n_sent = 0;
	
	if (defined $word_count_file) {
		print "Reading unigram counts from $word_count_file\n";
		# Read high frequency words list from word count file.
		my $ifh = new IO::File($word_count_file) or die "Canot open $word_count_file for reading";
	
		while (my $line = $ifh->getline()) {
			chomp($line);
			my ($w,$c) = split("[ \t]++", $line);
			
			$stats{$w} = $c;
		}
		
		$ifh->close();
		
		$n_words = sum(values %stats);
	} else {
		print "Generating word count\n";
		
		# Generate list from text.
		foreach my $if (@$ifs) {
			print "Reading $if\n";
			my $ifh = new IO::File($if);
			
			unless ($ifh) {
				warn "Can't open $if for reading";
				next;
			}
			
			while (my $line = $ifh->getline()) {
				
				if (++$n_sent % 10000 == 0) {
					printf("%dK %c", $n_sent/1000, 13);
				}
				
				# Randomly skip 90% of the sentences to get an even distribution of the data.
				chomp($line);
				my @words = split(" ", $line);
				
				foreach my $w (@words) {
					# Skip empty words and punctuation.
					next if ($w =~ /^[^a-z]++$/ or not length($w));
					$stats{$w}++;
					$n_words++;
				}
			}
			
			$ifh->close();
		}
	}	
	
	print "Selected ".scalar(keys %stats)." dictionary words.\n";
	
	my @sorted_words = sort {$stats{$b} <=> $stats{$a}} keys %stats;
	
	my %cws;
	
	foreach my $w (@sorted_words) {
		if ($stats{$w}/$n_words > HIGH_FREQUENCY_THR) {		
			next;
		} elsif ($stats{$w} >= MIN_FREQ) {
			$cws{$w} = 1;
		} else {
			last;
		}
	}
	
	print "Selected ".scalar(keys %cws)." content words.\n";
	
	write_vocab(\%cws, $cws_vocabularty_output_file);
	return \%cws;
}


exit (main(@ARGV));
