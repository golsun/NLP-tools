from metrics import *
import sys

def eval_tsv(fld, ckpt_name, sub='test', max_n=3000, n_ref=1, path_refs=None):
    path_hyp = fld + '%s_%s.tsv'%(ckpt_name, sub)
    print(path_hyp)
    hyps = []
    refs = []
    n_refs = []
    src_matching = 0.

    f_hyp = open(path_hyp, encoding='utf-8')
    if path_refs is not None:
        f_refs = open(path_refs, encoding='utf-8')
    else:
        f_refs = None

    n = 0
    while True:
        line = f_hyp.readline()
        if len(line) == 0:
            break
        src, ref, hyp = line.strip('\n').split('\t')
        hyps.append(hyp)

        if f_refs is not None:
            ss = f_refs.readline().strip('\n').split('\t')
            src_matching += sentence_bleu([src.split()], ss[0].split(), weights=[1./4]*4)
            refs.append(ss[1:])
        else:
            refs.append([ref])
        n_refs.append(len(refs[-1]))
        n += 1
        if n == max_n:
            break

    n_sample = len(hyps)
    print('n_sample: %i'%n_sample)
    print('n_ref_desired: %i'%n_ref)
    print('n_ref_actual: min=%i, max=%i, avg=%.1f'%(min(n_refs), max(n_refs), np.mean(n_refs)))

    if path_refs is not None:
        src_matching = src_matching/n
        print('src_matching: %.4f'%(src_matching))
        if src_matching < 0.6:
            print('f_hyp and f_refs does not match on src')
            return

    path_refs = []
    for r in range(n_ref):
        _refs = [refs[i][r%n_refs[i]] for i in range(len(hyps))]
        _path = 'temp/ref%i.txt'%r
        with open(_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(_refs))
        path_refs.append(_path)
                
    with open('temp/hyp.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(hyps))

    print('evaluating')
    nist, sbleu, bleu, meteor, entropy, distinct, avg_len = nlp_metrics(
	  path_refs=path_refs, 
	  path_hyp="temp/hyp.txt")

    header = ['config', 'ckpt', 'n_sample', 'n_ref'] + [
                'nist%i'%i for i in range(1, 5)] + [
                'sbleu%i'%i for i in range(1, 5)] + [
                'bleu%i'%i for i in range(1, 5)] + [
                'meteor'] + [
                'entropy%i'%i for i in range(1, 5)] + [
                'distinct%i'%i for i in range(1, 3)] + [
                'avg_len'] + [
                ]
    config = fld.strip('/').split('/')[-1]
    if sub != 'test':
        config += '(%s)'%sub
    value = [config, ckpt_name, str(n_sample), str(n_ref)] + [
                '%.4f'%x for x in nist] + [
                '%.4f'%x for x in sbleu] + [
                '%.4f'%x for x in bleu] + [
                '%.4f'%meteor] + [
                '%.4f'%x for x in entropy] + [
                '%.4f'%x for x in distinct] + [
                '%.4f'%avg_len] + [
                ]

    path_out = fld + '/eval.tsv'
    with open(path_out,'a') as f:
        f.write('\t'.join(header) + '\n')
        f.write('\t'.join(value) + '\n')

    print('done')


def create_parrot_csv(path_in, path_out):
    # in/out is tsv: src \t ref \t hyp
    # repeat the last turn of src as hyp

    lines = []
    for line in open(path_in, encoding='utf-8'):
        ss = line.strip('\n').split('\t')
        src = ss[0]
        parrot = src.split(' EOS ')[-1].strip() + ' _EOS_'
        ss[1] = parrot
        lines.append('\t'.join(ss))
    with open(path_out, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print('done. see '+path_out)


def create_const_csv(path_in, path_out, hyp="i do n't know"):
    # in/out is tsv: src \t ref \t hyp
    # use a constant reply

    lines = []
    hyp = hyp.strip() + ' _EOS_'
    for line in open(path_in, encoding='utf-8'):
        ss = line.strip('\n').split('\t')
        ss[1] = hyp
        lines.append('\t'.join(ss))
    with open(path_out, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print('done. see '+path_out)


def create_rand_csv(path_in, path_out, hyp="i do n't know"):
    # in/out is tsv: src \t ref \t hyp
    # use a constant reply

    hyps = []
    cells = []
    for line in open(path_in, encoding='utf-8'):
        ss = line.strip('\n').split('\t')
        hyps.append(ss[-1])
        cells.append(ss)

    np.random.seed(9)
    np.random.shuffle(hyps)
    lines = []
    for i in range(len(hyps)):
        ss = cells[i]
        ss[1] = hyps[i]
        lines.append('\t'.join(ss))
    with open(path_out, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print('done. see '+path_out)


def create_human_csv(path_in, path_out):

    lines = []
    for line in open(path_in, encoding='utf-8'):
        ss = line.strip('\n').split('\t')
        ix_hyp, ix_rep = np.random.choice(len(ss)-2, 2, replace=False)
        ss[1] = ss[ix_hyp]
        ss[ix_hyp] = ss[ix_rep]
        lines.append('\t'.join(ss))
    with open(path_out, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print('done. see '+path_out)