# author: Xiang Gao @ Microsoft Research, Oct 2018
# clean and tokenize natural language text

import re
from util import *
from nltk.tokenize import TweetTokenizer
import shutil, queue

EOS_token = '_EOS_'	# end of resp
SOS_token = '_SOS_'	# start of resp
UNK_token = '_UNK_'	# unkown 

def clean_str(txt, lang='en'):
	assert(lang in ['en','fr'])

	txt = txt.lower()
	for c in '«»“”':
		txt = re.sub(c, '"', txt)
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
	txt = re.sub(r"[^A-Za-zÀ-ÿ0-9():,.!?\"\']", " ", txt)
	txt = re.sub('URL','__url__',txt)	

	# contraction
	tokenizer = TweetTokenizer(preserve_case=False)
	if lang == 'en':
		txt = ' ' + ' '.join(tokenizer.tokenize(txt)) + ' '
		add_space = ["'s", "'m", "'re", "n't", "'ll","'ve","'d","'em"]
		txt = txt.replace(" won't ", " will n't ")
		txt = txt.replace(" can't ", " can n't ")
		for a in add_space:
			txt = txt.replace(a+' ', ' '+a+' ')
	elif lang == 'fr':
		ww = []
		for w in tokenizer.tokenize(txt):
			if "'" in w:
				ss = w.split("'")
				ww += [s+"'" for s in ss[:-1]] + [ss[-1]]
			else:
				ww.append(w)
		txt = ' '.join(ww)

	return ' '.join(txt.split())	# remove extra space


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


def filter_by_turn(path, min_src_turn=1, max_src_turn=None):
	path_out = path+'.turn(%s,%s)'%(min_src_turn,max_src_turn)
	open(path_out, 'w')
	n = 0
	m = 0
	lines = []
	for line in open(path, encoding='utf-8'):
		n += 1
		line = line.strip('\n')
		src, tgt = line.split('\t')
		n_turn = len(src.split(' EOS '))
		if n_turn >= min_src_turn and (max_src_turn is None or n_turn <= max_src_turn):
			lines.append(line)
			m += 1
			if m%1e5 == 0:
				print('picked %.1f M from %.1f M lines (%.3f)'%(m/1e6, n/1e6, m/n))
				with open(path_out, 'a', encoding='utf-8') as f:
					f.write('\n'.join(lines) + '\n')
				lines = []
	with open(path_out, 'a', encoding='utf-8') as f:
		f.write('\n'.join(lines))


def combine_files(paths_in, path_out):
	open(path_out,'w')
	total_n = 0
	for path in paths_in:
		lines = []
		n = 0
		for line in open(path, encoding='utf-8'):
			lines.append(line.strip('\n'))
			n += 1
			if n%1e5 == 0:
				print('adding %.1f M'%(n/1e6))
				with open(path_out, 'a', encoding='utf-8') as f:
					f.write('\n'.join(lines) + '\n')
				lines = []
		with open(path_out, 'a', encoding='utf-8') as f:
			f.write('\n'.join(lines)+'\n')
		total_n += n
		print('total_n %.1f M after %s'%(total_n/1e6, path))


def shuffle_split(path, n_vali=1000, n_test=3000, n_train=1e7):
	n_vali = int(n_vali)
	n_test = int(n_test)
	n_train = int(n_train)

	print('reading '+path)
	lines = open(path, encoding='utf-8').readlines()
	ii = list(range(len(lines)))
	np.random.seed(9)
	np.random.shuffle(ii)
	
	print('writing test')
	new = [lines[i].strip('\n') for i in ii[:n_test]]
	with open(path+'.test', 'w', encoding='utf-8') as f:
		f.write('\n'.join(new))

	print('writing vali')
	new = [lines[i].strip('\n') for i in ii[n_test: n_test + n_vali]]
	with open(path+'.vali', 'w', encoding='utf-8') as f:
		f.write('\n'.join(new))
	
	print('writing train')
	j0 = n_test + n_vali
	j_max = len(ii)
	if n_train is not None:
		j_max = min(j_max, j0 + n_train)
	j = j0
	open(path+'.train', 'w')
	while True:
		j_next = min(j_max, j + int(1e5))
		new = [lines[i].strip('\n') for i in ii[j:j_next]]
		with open(path+'.train', 'a', encoding='utf-8') as f:
			f.write('\n'.join(new) + '\n')
		print('    %.1f M'%((j_next - j0)/1e6))
		if j_next == j_max:
			break
		j = j_next


PERSON_TITLES = ['mr','mrs','dr','ms','sir','miss']

def build_vocab(fld, n_max=2e6, size=1e4, min_freq=50, fname='train.txt', include_names=False):
	# exclude names by calc ratio of freq_with_person_tital / total_freq
	# exclude pure num 

	print('building vocab')
	counts = dict()
	potential_names = dict()

	n = 0
	for line in open(fld + '/' + fname, encoding='utf-8'):
		n += 1
		if n%1e5 == 0:
			print('processed %.1fM lines'%(n/1e6))
		words = (' '.join(line.split('\t')[:2])).split()
		for i, word in enumerate(words):
			if not include_names and i > 0 and words[i-1] in PERSON_TITLES:
				if word not in potential_names:
					potential_names[word] = [0, 0]
				potential_names[word][0] += 1
			if word in potential_names:
				potential_names[word][1] += 1
			if word not in counts:
				counts[word] = 0
			counts[word] += 1
		if n == n_max:
			break

	print('total %i words'%(len(counts)))

	pq = queue.PriorityQueue()
	for word in counts:
		hasnum = False
		for i in range(10):
			if str(i) in word:
				hasnum = True
				break
		if hasnum:
			continue
		if counts[word] > min_freq:
			pq.put((counts[word], word))
		if pq.qsize() > size:
			pq.get()

	vocab = []
	names = []
	while not pq.empty():
		_, word = pq.get()
		is_name = False
		if word in potential_names:
			ratio = potential_names[word][0] / potential_names[word][1] 
			if ratio > 0.2:
				is_name = True
		if not is_name:
			vocab.append(word)
	
	print('kept %i words'%len(vocab))
	print('last word freq = %i'%counts[vocab[0]])

	with open(fld + '/vocab.txt', 'w', encoding='utf-8') as f:
		f.write('\n'.join([SOS_token, EOS_token, UNK_token] + list(reversed(vocab))))
	
	if include_names:
		return 

	pq = queue.PriorityQueue()
	for k in potential_names:
		ratio = potential_names[k][0] / potential_names[k][1] 
		pq.put((-ratio, k))
	names = []
	while not pq.empty():
		neg_ratio, k = pq.get()
		names.append('%s\t%.3f'%(k, -neg_ratio))
	with open(fld + '/vocab_names.txt', 'w', encoding='utf-8') as f:
		f.write('\n'.join(names))



def tokenize_file(path, lang='en'):
	lines = []
	n = 0
	path_out = path + '.tokenized'
	open(path_out, 'w', encoding='utf-8') 
	for line in open(path, encoding='utf-8'):
		ss = line.strip('\n').split('\t')
		cc = [clean_str(s, lang=lang) for s in ss]
		lines.append('\t'.join(cc))
		n += 1
		if n % 1e5 == 0:
			print('processed %.1f M'%(n/1e6))
			with open(path_out, 'a', encoding='utf-8') as f:
				f.write('\n'.join(lines) + '\n')
			lines = []
	print('totally processed %.1f M'%(n/1e6))
	with open(path_out, 'a', encoding='utf-8') as f:
		f.write('\n'.join(lines))
			


