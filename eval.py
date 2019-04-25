from metrics import *
import sys

def eval_tsv(fld, ckpt_name, src_as_ref=False, parrot_threshold=-1, sub='test', max_n=4000, n_ref=1, hyp_first=True):
    if src_as_ref:
        assert(path_extra_ref is None)

    path_tsv = fld + '%s_%s.tsv'%(ckpt_name, sub)
    print(path_tsv)
    srcs = []
    hyps = []
    refs = []
    n_refs = []
    n_parrot = 0
    for i, line in enumerate(open(path_tsv, encoding='utf-8')):
        ss = line.strip('\n').split('\t')
        src = ss[0]
        if hyp_first:
            hyp = ss[1]
            _refs = ss[2:]
        else:
            hyp = ss[-1]
            _refs = ss[1:-1]

        if parrot_threshold > 0:
            parrot = src.split(' EOS ')[-1].strip() + ' _EOS_'
            bleu = sentence_bleu([refs[-1][0].split()], parrot.split(), weights=[1./4]*4)
            if bleu > parrot_threshold:
                n_parrot += 1
                continue

        srcs.append(src)
        hyps.append(hyp)
        if src_as_ref:
            refs.append([src])
        else:
            refs.append(_refs)
        n_refs.append(len(refs[-1]))
        if i == max_n:
            break

    print('n_ref_desired: %i'%n_ref)
    print('n_ref_actual: min=%i, max=%i, avg=%.1f'%(min(n_refs), max(n_refs), np.mean(n_refs)))

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

    header = ['config', 'ckpt', 'src_as_ref', 'n_ref'] + [
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
    value = [config, ckpt_name, str(src_as_ref), str(n_ref)] + [
                '%.4f'%x for x in nist] + [
                '%.4f'%x for x in sbleu] + [
                '%.4f'%x for x in bleu] + [
                '%.4f'%meteor] + [
                '%.4f'%x for x in entropy] + [
                '%.4f'%x for x in distinct] + [
                '%.4f'%avg_len] + [
                ]

    if parrot_threshold > 0:
        path_out = fld + '/eval_no_parrot%.2f.tsv'%parrot_threshold
    else:
        path_out = fld + '/eval.tsv'
    with open(path_out,'a') as f:
        f.write('\t'.join(header) + '\n')
        f.write('\t'.join(value) + '\n')

    print('done. %i samples evaluated'%len(hyps))
    if parrot_threshold > 0:
        print('removed %i parrot samples'%n_parrot)


def create_parrot_csv(path_in, path_out):
    # in/out is tsv: src \t ref \t hyp
    # repeat the last turn of src as hyp

    lines = []
    for line in open(path_in, encoding='utf-8'):
        src, ref, _ = line.strip('\n').split('\t')
        parrot = src.split(' EOS ')[-1].strip() + ' _EOS_'
        lines.append('\t'.join([src, ref, parrot]))
    with open(path_out, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print('done. see '+path_out)


def create_const_csv(path_in, path_out, hyp="i do n't know"):
    # in/out is tsv: src \t ref \t hyp
    # use a constant reply

    lines = []
    for line in open(path_in, encoding='utf-8'):
        src, ref, _ = line.strip('\n').split('\t')
        lines.append('\t'.join([src, ref, hyp.strip() + ' _EOS_']))
    with open(path_out, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print('done. see '+path_out)


def create_rand_csv(path_in, path_out, hyp="i do n't know"):
    # in/out is tsv: src \t ref \t hyp
    # use a constant reply

    srcs = []
    refs = []
    for line in open(path_in, encoding='utf-8'):
        src, ref, _ = line.strip('\n').split('\t')
        srcs.append(src)
        refs.append(ref)

    hyps = refs[:]
    np.random.seed(9)
    np.random.shuffle(hyps)
    lines = []
    for i in range(len(hyps)):
        lines.append('\t'.join([srcs[i], refs[i], hyps[i]]))
    with open(path_out, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print('done. see '+path_out)


def check_parrot(path_tsv):
    tuples = []
    for line in open(path_tsv, encoding='utf-8'):
        src, ref, _ = line.strip('\n').split('\t')
        parrot = src.split(' EOS ')[-1].strip() + ' _EOS_'
        bleu = sentence_bleu([ref.split()], parrot.split(), weights=[1./4]*4)
        tuples.append((bleu, src, ref))

    tuples = sorted(tuples, reverse=True)
    lines = ['\t'.join(['%.6f'%bleu, src, ref]) for bleu, src, ref in tuples]
    with open(path_tsv + '.parrot_bleu', 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
