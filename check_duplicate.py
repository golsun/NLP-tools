import pdb

def get_set(path, split=None):
    print(path)
    ret = dict()
    n = 0
    for line in open(path):
        line = line.strip('\n').lower()
        if split is None:
            sample = line
        else:
            sample = line.split(split)[0]
        utt = ''
        for c in sample:
            if c >= 'a' and c <= 'z':
                utt += c
        if utt not in ret:
            ret[utt] = []
        ret[utt].append(line)
        n += 1
    print(len(ret), n)
    return ret

fld = 'd:/data/dailydialog'
train = get_set(fld + '/train.txt')
vali = get_set(fld + '/vali.txt')
test = get_set(fld + '/test.txt')

def duplicate(a, b):
    d = set(list(a.keys())) & set(list(b.keys()))
    return [k for k in d]

train_vali = duplicate(train, vali)
print('train vs vali', len(train_vali))
train_test = duplicate(train, test)
print('train vs test', len(train_test))
vali_test = duplicate(test, vali)
print('vali vs test', len(vali_test))

pdb.set_trace()