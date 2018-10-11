# What does it do?
provides easy Python way to
* calculate automated NLP evaluation metrics (BLEU, NIST, entropy, etc...)
```python
from eval import cal_nist
nist, bleu = cal_nist(['demo/ref.txt'], 'demo/hyp.txt')
# nist = [1.0633, 1.1258, 1.1258, 1.1258]
# bleu = [0.3158, 0.2433, 0.2088, 0.1737]
```
* and more...

# Requirement
please download [mteval-v14c.pl](ftp://jaguar.ncsl.nist.gov/mt/resources) and save in the folder where eval.py lives. You may need to install the following perl modules (e.g. by cpan install)
* XML:Twig
* Sort:Naturally
* String:Util 
tested on Python 2.7, but Python 3.6 will work fine soon
