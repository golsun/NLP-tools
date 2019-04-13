from urllib.request import urlopen

def download_log(url):
	with urlopen(url) as f:
		return f.read().decode('utf-8')

def download_all(path_tsv):
	ss = path_tsv.split('/')
	fld = '/'.join(ss[:-1])
	for line in open(path_tsv):
		fname, url = line.strip('\n').split('\t')
		print('downloading '+fname)
		s = download_log(url)
		print('lines = %.1f k'%(len(s.split('\n'))/1000))
		with open(fld + '/' + fname + '.txt', 'w', encoding='utf-8') as f:
			f.write(s)


if __name__ == '__main__':
	download_all('C:/Users/xiag/Documents/GitHub/SpaceFusion-Holmes/temp/url_arxiv.tsv')