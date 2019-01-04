from collections import Counter
from simplemr import SimpleMapReducer, SimpleMapCollector
from pprint import pprint


class WordFreqCounter(SimpleMapReducer):
    def __init__(self, sentences):
        super(WordFreqCounter, self).__init__(
            sentences, Counter(), parallelism=4, threaded=False)

    def reduce(self, sentence, wordfreq, error):
        print('Reducing:', sentence, wordfreq, error)
        if error:
            return
        for word, freq in wordfreq.items():
            self.results[word] += freq

    def map(self, sentence):
        print('Mapping:', sentence)
        wordfreq = Counter()
        for word in sentence.split(' '):
            wordfreq[word] += 1
        return wordfreq


class SentenceLengthCollector(SimpleMapCollector):
    def map(self, sentence):
        return len(sentence)


if __name__ == '__main__':
    datasource = [
        "Humpty Dumpty sat on a wall",
        "Humpty Dumpty had a great fall",
        "All the King's horses and all the King's men",
        "Couldn't put Humpty together again",
    ] * 1000
    pprint(WordFreqCounter(datasource).mapreduce())
    pprint(SentenceLengthCollector(datasource).collect())
