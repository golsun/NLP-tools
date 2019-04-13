# author: Xiang Gao @ Microsoft Research, Oct 2018
# clean and tokenize natural language text

import re
from util import *
from nltk.tokenize import TweetTokenizer

def clean_str(txt):
	#print("in=[%s]" % txt)
	txt = txt.lower()
	txt = re.sub('^',' ', txt)
	txt = re.sub('$',' ', txt)

	# url and tag
	words = []
	for word in txt.split():
		i = word.find('http') 
		if i >= 0:
			word = word[:i] + ' ' + '__url__'
		words.append(word.strip())
	txt = ' '.join(words)

	# remove markdown URL
	txt = re.sub(r'\[([^\]]*)\] \( *__url__ *\)', r'\1', txt)

	# remove illegal char
	txt = re.sub('__url__','URL',txt)
	txt = re.sub(r"[^A-Za-z0-9():,.!?\"\']", " ", txt)
	txt = re.sub('URL','__url__',txt)	

	# contraction
	add_space = ["'s", "'m", "'re", "n't", "'ll","'ve","'d","'em"]
	tokenizer = TweetTokenizer(preserve_case=False)
	txt = ' ' + ' '.join(tokenizer.tokenize(txt)) + ' '
	txt = txt.replace(" won't ", " will n't ")
	txt = txt.replace(" can't ", " can n't ")
	for a in add_space:
		txt = txt.replace(a+' ', ' '+a+' ')

	txt = re.sub(r'^\s+', '', txt)
	txt = re.sub(r'\s+$', '', txt)
	txt = re.sub(r'\s+', ' ', txt) # remove extra spaces
	
	#print("out=[%s]" % txt)
	return txt


def dataset_statistics(path, src_tgt_delimiter='\t', turns_delimiter='EOS'):
	print(path)
	sum_src_len = 0
	sum_tgt_len = 0
	sum_src_turns = 0
	n = 0
	for line in open(path, encoding='utf-8'):
		n += 1
		line = line.strip('\n')
		if src_tgt_delimiter is not None:
			src, tgt = line.split(src_tgt_delimiter)
			sum_src_turns += len(src.split(turns_delimiter))
			sum_src_len += len(src.split())
		else:
			tgt = line
		sum_tgt_len += len(tgt.split())
		if n%1e6 == 0:
			print('checked %i M'%(n/1e6))

	print(path)
	print('total sample = %i (%.3f M)'%(n, n/1e6))
	print('src_turns = %.2f'%np.mean(sum_src_turns/n))
	print('src_len = %.2f'%np.mean(sum_src_len/n))
	print('tgt_len = %.2f'%np.mean(sum_tgt_len/n))

