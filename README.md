# What does it do?
provides easy Python ways for
*  **evaluation**: calculate automated NLP metrics (BLEU, NIST, entropy, etc...)
```python
from metrics import nlp_metrics
nist, bleu, entropy, diversity, avg_len = nlp_metrics(
	  path_refs=["demo/ref0.txt", "demo/ref1.txt"], 
	  path_hyp="demo/hyp.txt")
	  
# nist = [1.8338, 2.0838, 2.1949, 2.1949]
# bleu = [0.4667, 0.441, 0.4017, 0.3224]
# entropy = [2.5232, 2.4849, 2.1972, 1.7918]
# diversity = [0.8667, 1.000]
# avg_len = 5.0000
```
* **tokenizatioin**: clean string and deal with punctation, contraction, url, mention, tag, etc
```python
from tokenizers import clean_str
s = " I don't know:). how about this?https://github.com"
clean_str(s)

# i do n't know :) . how about this ? __url__
```

# Requirement
please download [mteval-v14c.pl](https://goo.gl/YUFajQ) and install the following perl modules (e.g. by `cpan install`)
* XML:Twig
* Sort:Naturally
* String:Util 

Works fine for both Python 2.7 and 3.6
