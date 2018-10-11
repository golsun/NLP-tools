# author: Xiang Gao @ Microsoft Research, Oct 2018
# clean and tokenize natural language text

from util import *
from nltk.tokenize import TweetTokenizer


def clean_str(txt):
	txt = txt.lower()

	# url and tag
	words = []
	for word in txt.lower().split():
		if word[0] == '#':	# don't allow tag
			continue
		i = word.find('http') 
		if i >= 0:
			word = word[:i] + ' ' + '__url__'
		words.append(word.strip())
	txt = ' '.join(words)

	# remove illegal char
	txt = txt.replace(chr(92),'')	# chr(92) = '\'. as twitter has 'b\/c' rather than 'b/c'
	txt = txt.replace("b/c","because").replace('j/k','just kidding').replace('w/o','without').replace('w/','with')
	txt = re.sub('__mention__','MENTION',txt)
	txt = re.sub('__url__','URL',txt)
	txt = re.sub(r"[^A-Za-z0-9():,.!?' ]", " ", txt)
	txt = re.sub('MENTION','__mention__',txt)	
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


def clean_twitter(txt):
	# return None if quoted
	if "“__mention__:" in txt:
		return None

	txt = txt.replace('>',' ')		# a symbol never showing in reddit
	txt = txt.replace('#N#',' ')
	return clean_str(txt)


def clean_reddit(txt):
	txt = txt.lower().replace('r/','')
	return clean_str(txt)

def heavy_clean(s):
	s = clean_str(s)
	s = re.sub(r"[^a-z0-9 ]", " ", s)
	return ' '.join(s.split())

if __name__ == '__main__':
	s = " I don't know:). how about this?https://github.com/golsun/deep-RL-time-series"
	s = "they're also the biggest shareholder of apple , 2 % if i remember correctly . edit : 2.6 % https://en.wikipedia.org/wiki/List_of_assets_owned_by_Berkshire_Hathaway"
	print(clean_str(s))
	print(heavy_clean(s))
	