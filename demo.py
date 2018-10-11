from metrics import cal_all
from tokenizers import gentle_clean, heavy_clean

# evaluation

nist, bleu, entropy, avg_len = cal_all(
	['demo/ref0.txt', 'demo/ref1.txt'], 
	'demo/hyp.txt')

print(nist)
print(bleu)
print(entropy)
print(avg_len)

# tokenization 

s = " I don't know:). how about this?https://github.com/golsun/deep-RL-time-series"
print(gentle_clean(s))
print(heavy_clean(s))

