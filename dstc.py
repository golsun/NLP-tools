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


def extract_hyp_refs(raw_hyp, raw_ref, path_hash, fld_out, n_ref=6, clean=False):
	cells_hyp = extract_cells(raw_hyp, path_hash)
	cells_ref = extract_cells(raw_ref, path_hash)
	if not os.path.exists(fld_out):
		os.makedirs(fld_out)

	def _clean(s):
		if clean:
			return clean_str(s)
		else:
			return s

	keys = sorted(cells_hyp.keys())
	lines = [_clean(cells_hyp[k][-1]) for k in keys]
	path_hyp = fld_out + '/hyp.txt'
	with open(path_hyp, 'w', encoding='utf-8') as f:
		f.write(unicode('\n'.join(lines)))
	
	lines = []
	for _ in range(n_ref):
		lines.append([])
	for k in keys:
		refs = cells_ref[k]
		for i in range(n_ref):
			lines[i].append(_clean(refs[i].split('|')[1]))

	path_refs = []
	for i in range(n_ref):
		path_ref = fld_out + '/ref%i.txt'%i
		with open(path_ref, 'w', encoding='utf-8') as f:
			f.write(unicode('\n'.join(lines[i])))
		path_refs.append(path_ref)
	return path_hyp, path_refs


def eval_a_system(submitted, 
	keys='dstc/keys.2k.txt', multi_ref='dstc/test.refs', n_ref=6, n_line=None,
	clean=False, PRINT=True):

	fld_out = submitted.replace('.txt','')
	if clean:
		fld_out += '_cleaned'
	path_hyp, path_refs = extract_hyp_refs(submitted, multi_ref, keys, fld_out, n_ref, clean=clean)
	nist, bleu, entropy, div1, div2, avg_len = nlp_metrics(path_refs, path_hyp, fld_out, n_line=n_line)
	if PRINT:
		print(submitted)
		print('NIST = '+str(nist))
		print('BLEU = '+str(bleu))
		print('entropy = '+str(entropy))
		print('diversity = ' + str([div1, div2]))
		print('avg_len = '+str(avg_len))

	return nist + bleu + entropy + [avg_len]

#def eval_all()


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('--submitted', '-s', default='dstc/baseline/primary.txt')
	parser.add_argument('--clean', '-c', action='store_true', default=False)
	parser.add_argument('--n_line', '-n', type=int, default=-1)
	args = parser.parse_args()

	#print(args.clean)
	if args.n_line < 0:
		n_line = None
	else:
		n_line = args.n_line
	
	eval_a_system(args.submitted, clean=args.clean, n_line=n_line)

