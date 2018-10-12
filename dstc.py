# author: Xiang Gao @ Microsoft Research, Oct 2018
# evaluate DSTC-task2 submissions. https://github.com/DSTC-MSR-NLP/DSTC7-End-to-End-Conversation-Modeling

from metrics import *
from tokenizers import *

def extract_cells(path_in, path_hash):
	keys = [line.strip('\n') for line in open(path_hash)]
	cells = dict()
	for line in open(path_in, encoding='utf-8'):
		c = line.strip('\n').split('\t')
		k = c[0]
		if k in keys:
			cells[k] = c[1:]
	return cells


def extract_hyp_refs(raw_hyp, raw_ref, path_hash, fld_out, n_refs=6, clean=False):
	cells_hyp = extract_cells(raw_hyp, path_hash)
	cells_ref = extract_cells(raw_ref, path_hash)
	if not os.path.exists(fld_out):
		os.makedirs(fld_out)

	def _clean(s):
		if clean == 'heavy':
			return heavy_clean(s)
		elif clean == 'light':
			return clean_str(s)
		else:
			return s

	keys = sorted(cells_hyp.keys())
	with open(fld_out + '/hash.txt', 'w', encoding='utf-8') as f:
		f.write(unicode('\n'.join(keys)))

	lines = [_clean(cells_hyp[k][-1]) for k in keys]
	path_hyp = fld_out + '/hyp.txt'
	with open(path_hyp, 'w', encoding='utf-8') as f:
		f.write(unicode('\n'.join(lines)))
	
	lines = []
	for _ in range(n_refs):
		lines.append([])
	for k in keys:
		refs = cells_ref[k]
		for i in range(n_refs):
			idx = i % len(refs)
			lines[i].append(_clean(refs[idx].split('|')[1]))

	path_refs = []
	for i in range(n_refs):
		path_ref = fld_out + '/ref%i.txt'%i
		with open(path_ref, 'w', encoding='utf-8') as f:
			f.write(unicode('\n'.join(lines[i])))
		path_refs.append(path_ref)

	return path_hyp, path_refs


def eval_one_system(submitted, 
	keys='dstc/keys.2k.txt', multi_ref='dstc/test.refs', n_refs=6, n_lines=None,
	clean=False):

	print('evaluating '+submitted)

	fld_out = submitted.replace('.txt','')
	if clean:
		fld_out += '_%s_cleaned'%clean
	path_hyp, path_refs = extract_hyp_refs(submitted, multi_ref, keys, fld_out, n_refs, clean=clean)
	nist, bleu, meteor, entropy, div, avg_len = nlp_metrics(path_refs, path_hyp, fld_out, n_lines=n_lines)
	if n_lines is None:
		n_lines = len(open(path_hyp, encoding='utf-8').readlines())

	print('n_lines = '+str(n_lines))
	print('NIST = '+str(nist))
	print('BLEU = '+str(bleu))
	print('METEOR = '+str(meteor))
	print('entropy = '+str(entropy))
	print('diversity = ' + str(div))
	print('avg_len = '+str(avg_len))

	return nist + bleu + entropy + div + [avg_len, n_lines]


def eval_all_systems(fld, keys='dstc/keys.2k.txt', multi_ref='dstc/test.refs', n_refs=6, clean=False, n_lines=None):
	# evaluate all systems (*.txt) in `fld`

	print('clean = '+str(clean))
	path_out = fld + '/report'
	if clean:
		path_out += '_%s_cleaned'%clean
	path_out += '.tsv'
	with open(path_out, 'w') as f:
		f.write('\t'.join(
				['fname'] + \
				['nist%i'%i for i in range(1, 4+1)] + \
				['bleu%i'%i for i in range(1, 4+1)] + \
				['entropy%i'%i for i in range(1, 4+1)] +\
				['div1','div2','avg_len','n_lines']
			) + '\n')

	for fname in os.listdir(fld):
		if fname.endswith('.txt'):
			submitted = fld + '/' + fname
			results = eval_one_system(submitted, keys=keys, multi_ref=multi_ref, n_refs=n_refs, clean=clean, n_lines=n_lines)
			print()
			with open(path_out, 'a') as f:
				f.write('\t'.join(map(str, [submitted] + results)) + '\n')

	print('metrics saved to '+path_out)


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('--submitted', '-s', default='')		# eval a single file
	parser.add_argument('--submitted_fld', '-f', default='')	# eval all *.txt in submitted_fld
	parser.add_argument('--clean', '-c', default='no')			# 'no', 'light', or 'heavy'
	parser.add_argument('--n_lines', '-n', type=int, default=-1)# eval all lines (default) or top n_lines
	parser.add_argument('--n_refs', '-r', type=int, default=6)	# number of references
	args = parser.parse_args()

	if args.n_lines < 0:
		n_lines = None	# eval all lines
	else:
		n_lines = args.n_lines	# just eval top n_lines

	if len(args.submitted) > 0:
		eval_one_system(args.submitted, clean=args.clean, n_lines=n_lines, n_refs=args.n_refs)
	if len(args.submitted_fld) > 0:
		eval_all_systems(args.submitted_fld, clean=args.clean, n_lines=n_lines, n_refs=args.n_refs)

