# Dependencies
```
pip install -r requirements.txt
```
# Data
Download wikipedia dump from: [https://dumps.wikimedia.org/zhwiki/latest/zhwiki-latest-pages-articles.xml.bz2](https://dumps.wikimedia.org/zhwiki/latest/zhwiki-latest-pages-articles.xml.bz2)

Put the data into media/word2vec/ folder.

# Data Preprocessing
* Extract Chinese words from downloaded xml files using.
* Convert traditional version into simplified version text. Use [opencc](https://github.com/yichen0831/opencc-python)

```
'hk2s': Traditional Chinese (Hong Kong standard) to Simplified Chinese 
's2hk': Simplified Chinese to Traditional Chinese (Hong Kong standard) 
's2t': Simplified Chinese to Traditional Chinese 
's2tw': Simplified Chinese to Traditional Chinese (Taiwan standard)
's2twp': Simplified Chinese to Traditional Chinese (Taiwan standard, with phrases)
't2hk': Traditional Chinese to Traditional Chinese (Hong Kong standard)
't2s': Traditional Chinese to Simplified Chinese
't2tw': Traditional Chinese to Traditional Chinese (Taiwan standard)
'tw2s': Traditional Chinese (Taiwan standard) to Simplified Chinese
'tw2sp': Traditional Chinese (Taiwan standard) to Simplified Chinese (with phrases)
```

* Tokenize sentence into words for training. Use [jieba](https://github.com/fxsjy/jieba)

# Train
Produce word vectors with deep learning via word2vec’s “skip-gram and CBOW models”, using either hierarchical softmax or negative sampling [[1]](https://arxiv.org/pdf/1301.3781.pdf) [[2]](http://papers.nips.cc/paper/5021-distributed-representations-of-words-and-phrases-and-their-compositionality.pdf).

The training algorithms were originally ported from the C package [https://code.google.com/p/word2vec/](https://code.google.com/p/word2vec/) and extended with additional functionality.

For a blog tutorial on gensim word2vec, with an interactive web app trained on GoogleNews, visit [http://radimrehurek.com/2014/02/word2vec-tutorial/](http://radimrehurek.com/2014/02/word2vec-tutorial/)
