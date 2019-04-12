from metrics import *
import sys

def eval_tsv(fld, ckpt_name, src_as_ref=False):

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
    for i, line in enumerate(open(path_tsv, encoding='utf-8')):
        src, ref, hyp = line.strip('\n').split('\t')
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

    nist, bleu, meteor, entropy, distinct, avg_len = nlp_metrics(
	  path_refs=["temp/ref.txt"], 
	  path_hyp="temp/hyp.txt")

    header = ['ckpt', 'src_as_ref'] + [
                'nist%i'%i for i in range(1, 5)] + [
                'bleu%i'%i for i in range(1, 5)] + [
                'meteor'] + [
                'entropy%i'%i for i in range(1, 5)] + [
                'distinct%i'%i for i in range(1, 3)] + [
                'avg_len'] + [
                ]
    value = [ckpt_name, str(src_as_ref)] + [
                '%.4f'%x for x in nist] + [
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



if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('model_name', type=str)
    parser.add_argument('--ckpt_name', type=str, default='')
    parser.add_argument('--src_as_ref', '-s', action='store_true')
    args = parser.parse_args()

    root = 'C:/Users/xiag/Documents/GitHub/cut_the_noise/out/'
    eval_tsv(root + '/%s/'%args.model_name, args.ckpt_name, src_as_ref=args.src_as_ref)

