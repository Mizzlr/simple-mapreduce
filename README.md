# Simple MapReduce
`simplemr` is a simple map reduce framework in pure python3.

## Why?
Because existing frameworks are too heavy and complicated to use. This includes
hadoop-ish frameworks, mincemeatpy, mrjob etc.

## Installation
Download the [simplemr.py](
https://raw.githubusercontent.com/Mizzlr/simple-mapreduce/master/simplemr.py)
file and embed it in your application. It is less than 100 lines of pure python.

## Features
The `simplemr.SimpleMapReducer` class gives you enough level of abstraction to
run simple map reduce task parallely with either threads or process pool.
It also print a nice progress bar in the console.

## Framework and Concepts

### Datasource
A list (or iterable) from which each element is fed to the `map` function.

### Results
An object that stores/ accumulates the result through `reduce` function.

### SimpleMapReducer
It is a class that provides the framework for `map` and `reduce` to be used.
It is an abstract class, so we need to implement its `map(self, data)` and
`reduce(self, data, result, error)` method.

### SimpleMapCollector
It is a specialization of SimpleMapReducer that collects results in dictionary
where keys are elements from datasource and values of the results. For this class
we just need to implement the `map` method.

### Configuration
We can specify `parallelism`, that is the maximum number of threads or processes
to be used for running the mapreduce job.

We can specify `threaded`, a boolean indication if thread pool executor is to be
instead of process pool executor. By default this is false, that is we use process
pool executor.

### Notes
1. The datasource should be lightweight such as simple list of strings, list
of filenames etc. Packing heavy objects in not suggested.
2. You are include of what the result storage is and how to store/ accumulate
results into it. You control it through the `reduce` method.
3. You can also handle errors in `reduce` method. This is useful if you need
to collect stats about which jobs failed and which passed. You are in control.
4. Avoid sending duplicate entries into datasource.
5. There many things that cannot be serialized in a meaning way by the python's
multiprocessing and multithreading modules such as lambda's, open file objects
etc and some time including imports inside the `map` and `reduce` methods itself
might help. Handle with care.

## Example
Below is a classic word frequency counting problem used to demonstrate mapreduce.

``` python
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
```
