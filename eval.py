from metrics import *
import sys

def eval_tsv(fld, ckpt_name='', sub='test', max_n=3000, n_ref=1, path_refs=None, is_human=False, suffix=''):
    # path_hyp is a tsv file, each line is '\t'.join([src, ref, hyp])
    # you can provide extra multi_ref via path_refs, where each line is '\t'.join([src, ref0, ref1, ref2, ...])

    path_hyp = fld
    if ckpt_name != '':
        path_hyp += ckpt_name + '_'
    path_hyp += sub + '.tsv'
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
        src = src.strip(' EOS')
        hyps.append(hyp.replace('_EOS_','').strip())
        ref = ref.replace('_EOS_','').strip()

        if f_refs is not None:
            ss = f_refs.readline().strip('\n').split('\t')
            src_matching += sentence_bleu([src.split()], ss[0].split(), weights=[1./3]*3)
            if is_human:
                refs_ = []
                for ref in ss[1:]:
                    if ref != hyp:
                        refs_.append(ref)
                refs.append(refs_)
            else:
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
        if src_matching < 0.75:
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

    header = ['config', 'test', 'ckpt', 'n_sample', 'n_ref'] + [
                'nist%i'%i for i in range(1, 5)] + [
                'sbleu%i'%i for i in range(1, 5)] + [
                'bleu%i'%i for i in range(1, 5)] + [
                'meteor'] + [
                'entropy%i'%i for i in range(1, 5)] + [
                'distinct%i'%i for i in range(1, 3)] + [
                'avg_len'] + [
                ]
    config = fld.strip('/').split('/')[-1] + suffix
    value = [config, sub, ckpt_name, str(n_sample), '%.1f/%i'%(np.mean(n_refs), n_ref)] + [
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

    print('done' + '-'*20)
    for k, v in zip(header, value):
        print(' '*(15 - len(k)) + k + ': ' + v)


def create_parrot_csv(path_in, path_out):
    # in/out is tsv: src \t ref \t hyp
    # repeat the last turn of src as hyp

    lines = []
    for line in open(path_in, encoding='utf-8'):
        ss = line.strip('\n').split('\t')
        src = ss[0]
        ref = ss[1]
        hyp = src.split(' EOS ')[-1].strip() + ' _EOS_'
        lines.append('\t'.join([src, ref, hyp]))
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
        src = ss[0]
        ref = ss[1]
        lines.append('\t'.join([src, ref, hyp]))
    with open(path_out, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print('done. see '+path_out)


def create_rand_csv(path_in, path_out, hyp="i do n't know"):
    # in/out is tsv: src \t ref \t hyp
    # use a constant reply

    refs = []
    srcs = []
    for line in open(path_in, encoding='utf-8'):
        ss = line.strip('\n').split('\t')
        srcs.append(ss[0])
        refs.append(ss[1])

    np.random.seed(9)
    hyps = refs[:]
    np.random.shuffle(hyps)
    lines = []
    for i in range(len(hyps)):
        lines.append('\t'.join([srcs[i], refs[i], hyps[i]]))
    with open(path_out, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print('done. see '+path_out)


def create_human_csv(path_in, path_out):
    lines = []
    for line in open(path_in, encoding='utf-8'):
        ss = line.strip('\n').split('\t')
        lines.append('\t'.join(ss[:3]))
    with open(path_out, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print('done. see '+path_out)


def align_src(path_actual, path_desired):
    desired = [line.strip('\n').split('\t')[0].strip() for line in open(path_desired, encoding='utf-8')]
    d = dict()
    for line in open(path_actual, encoding='utf-8'):
        k = line.strip('\n').split('\t')[0].strip()
        d[k] = line.strip('\n')

    lines = []
    for k in desired:
        if k in d:
            lines.append(d[k])
        else:
            break

    print('aligned %i / %i lines'%(len(lines), len(desired)))
    with open(path_actual + '.aligned', 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
