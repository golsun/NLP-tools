# author: Xiang Gao @ Microsoft Research, Oct 2018
# clean and tokenize natural language text

from util import *
from nltk.tokenize import TweetTokenizer


def clean_str(txt):
	txt = txt.lower()

	# url and tag
	words = []
	for word in txt.split():
		if word[0] == '#':	# don't allow tag
			continue
		i = word.find('http') 
		if i >= 0:
			word = word[:i] + ' ' + '__url__'
		words.append(word.strip())
	txt = ' '.join(words)

	# remove markdown URL
	txt = txt.replace('] ( __url__ )','')

	# remove illegal char
	txt = re.sub('__url__','URL',txt)
	txt = re.sub(r"[^A-Za-z0-9():,.!?' ]", " ", txt)
	txt = re.sub('URL','__url__',txt)	

	# contraction
	add_space = ["'s", "'m", "'re", "n't", "'ll","'ve","'d","'em"]
	tokenizer = TweetTokenizer(preserve_case=False)
	txt = ' ' + ' '.join(tokenizer.tokenize(txt)) + ' '
	txt = txt.replace(" won't ", " will n't ")
	txt = txt.replace(" can't ", " can n't ")
	for a in add_space:
		txt = txt.replace(a+' ', ' '+a+' ')
	
	# remove un-necessary space
	return ' '.join(txt.split())


if __name__ == '__main__':
	ss = [
		" I don't know:). how about this?https://github.com/golsun/deep-RL-time-series",
		"please try [ GitHub ] ( https://github.com )",
		]
	for s in ss:
		print(s)
		print(clean_str(s))
		print()
	
