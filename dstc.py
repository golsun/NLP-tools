from eval import *
import sys, io
open = io.open

def extract_cells(path_in, path_hash):
	keys = [line.strip('\n') for line in open(path_hash)]
	cells = dict()
	for line in open(path_in, encoding='utf-8'):
		c = line.strip('\n').split('\t')
		k = c[0]
		if k in keys:
			cells[k] = c[1:]
	return cells


def extract_hyp_refs(raw_hyp, raw_ref, path_hash, fld_out, n_ref=6):
	cells_hyp = extract_cells(raw_hyp, path_hash)
	cells_ref = extract_cells(raw_ref, path_hash)
	if not os.path.exists(fld_out):
		os.makedirs(fld_out)

	keys = cells_hyp.keys()
	lines = [cells_hyp[k][-1] for k in keys]
	path_hyp = fld_out + '/hyp.txt'
	with open(path_hyp, 'w', encoding='utf-8') as f:
		f.write(unicode('\n'.join(lines)))
	
	lines = []
	for _ in range(n_ref):
		lines.append([])
	for k in keys:
		refs = cells_ref[k]
		for i in range(n_ref):
			lines[i].append(refs[i].split('|')[1])

	path_refs = []
	for i in range(n_ref):
		path_ref = fld_out + '/ref%i.txt'%i
		with open(path_ref, 'w', encoding='utf-8') as f:
			f.write(unicode('\n'.join(lines[i])))
		path_refs.append(path_ref)
	return path_hyp, path_refs


def main(submitted, n_line=None):

	n_ref = 6
	multi_ref = 'dstc/test.refs'
	keys = 'dstc/keys.2k.txt'
	fld_out = submitted.replace('.txt','')

	path_hyp, path_refs = extract_hyp_refs(submitted, multi_ref, keys, fld_out, n_ref)
	nist, bleu = cal_nist(path_refs, path_hyp, fld_out, n_line=n_line)
	print(nist)
	print(bleu)

if __name__ == '__main__':
	submitted = sys.argv[1]
	if len(sys.argv)>2:
		n_line = int(sys.argv[2])
	else:
		n_line = None
	main(submitted, n_line)
