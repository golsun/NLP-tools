from metrics import cal_all
nist, bleu, entropy, avg_len = cal_all(
	['demo/ref0.txt', 'demo/ref1.txt'], 
	'demo/hyp.txt')

print(nist)
print(bleu)
print(entropy)
print(avg_len)