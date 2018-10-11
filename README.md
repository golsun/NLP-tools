# What does it do?
provides easy Python ways to
* calculate automated NLP evaluation metrics (BLEU, NIST, entropy, etc...)
```python
from metrics import cal_all
nist, bleu, entropy, avg_len = cal_all(
	  ["demo/ref0.txt", "demo/ref1.txt"], 
	  "demo/hyp.txt")
# nist = [1.0633, 1.1258, 1.1258, 1.1258]
# bleu = [0.3158, 0.2433, 0.2088, 0.1737]
# entropy = [2.5232, 2.4849, 2.1972, 1.7918]
# avg_len = 5.0000
```
* and more...

# Requirement
please download [mteval-v14c.pl](https://goo.gl/YUFajQ) and install the following perl modules (e.g. by `cpan install`)
* XML:Twig
* Sort:Naturally
* String:Util 

Works fine for both Python 2.7 and 3.6
