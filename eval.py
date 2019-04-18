from metrics import *
import sys

def eval_tsv(fld, ckpt_name, src_as_ref=False, parrot_threshold=-1):

    if ckpt_name == '':
        ckpt = 0
        for fname in os.listdir(fld):
            if fname.endswith('_test.tsv'):
                ckpt = max(ckpt, int(fname.split('-')[1].split('_')[0]))
        ckpt_name = 'ckpt-%i'%ckpt

    path_tsv = fld + '%s_test.tsv'%ckpt_name
    print(path_tsv)
    hyps = []
    refs = []
    n_parrot = 0
    for i, line in enumerate(open(path_tsv, encoding='utf-8')):
        src, ref, hyp = line.strip('\n').split('\t')

        if parrot_threshold > 0:
            parrot = src.split(' EOS ')[-1].strip() + ' _EOS_'
            bleu = sentence_bleu([ref.split()], parrot.split(), weights=[1./4]*4)
            if bleu > parrot_threshold:
                n_parrot += 1
                continue

        hyps.append(hyp)
        if src_as_ref:
            refs.append(src)
        else:
            refs.append(ref)
        if i == 4000:
            break

    with open('temp/ref.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(refs))
            
    with open('temp/hyp.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(hyps))

    nist, sbleu, _, bleu, meteor, entropy, distinct, avg_len = nlp_metrics(
	  path_refs=["temp/ref.txt"], 
	  path_hyp="temp/hyp.txt")

    header = ['config', 'ckpt', 'src_as_ref'] + [
                'nist%i'%i for i in range(1, 5)] + [
                'sbleu%i'%i for i in range(1, 5)] + [
                'bleu%i'%i for i in range(1, 5)] + [
                'meteor'] + [
                'entropy%i'%i for i in range(1, 5)] + [
                'distinct%i'%i for i in range(1, 3)] + [
                'avg_len'] + [
                ]
    config = fld.strip('/').split('/')[-1]
    value = [config, ckpt_name, str(src_as_ref)] + [
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
