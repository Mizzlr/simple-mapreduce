import abc
import tqdm
import traceback
import concurrent.futures as cf


class SimpleMapReducer(abc.ABC):
    def __init__(self, datasource, results, parallelism=1, threaded=False):
        self.datasource = list(datasource)
        self.results = results
        self.parallelism = parallelism
        self.threaded = threaded

    def mapreduce(self):
        return SimpleMapReducer.distribute(self)

    @abc.abstractmethod
    def reduce(self, data, result, error):
        pass

    @abc.abstractmethod
    def map(self, data):
        pass

    @classmethod
    def distribute(cls, mapreducer):
        ProgressReporter.register(mapreducer, len(mapreducer.datasource))
        if mapreducer.threaded:
            Executor = cf.ThreadPoolExecutor
        else:
            Executor = cf.ProcessPoolExecutor
        pool = Executor(max_workers=mapreducer.parallelism)
        futures = {}
        for data in mapreducer.datasource:
            future = pool.submit(mapreducer.map, data)
            futures[future] = data

        for future in cf.as_completed(futures):
            data = futures[future]
            try:
                result, error = future.result(), None
            except Exception as exc:
                traceback.print_exc()
                result, error = None, exc
            mapreducer.reduce(data, result, error)
            ProgressReporter.report(mapreducer)
        return mapreducer.results


class SimpleMapCollector(SimpleMapReducer):
    def __init__(self, datasource, parallelism=1, threaded=False):
        super(SimpleMapCollector, self).__init__(
            datasource, {}, parallelism=parallelism, threaded=threaded)

    def reduce(self, data, result, error):
        if error is None:
            self.results[data] = result

    def collect(self):
        return self.mapreduce()


class ProgressReporter:
    bars = {}

    @classmethod
    def register(cls, obj, total):
        cls.bars[obj] = tqdm.tqdm(desc=obj.__class__.__name__, total=total)

    @classmethod
    def report(cls, obj, progress=1):
        cls.bars[obj].update(progress)
