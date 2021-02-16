import numpy as np
from fuzzywuzzy import process
from pprint import pprint


class Matcher():
    def __init__(self, choices, threshold=80):
        """
        choices:
            List of true labels to match against
        threshold:
            Float - the threshold score to use when matching`

        """
        self.choices = choices
        self.threshold = threshold
        self.queries = None
        self.results_list = None


    def check(self, queries):
        condition = isinstance(queries, list) or isinstance(queries, np.ndarray)
        assert condition, '"queries" can only be a Python list or Numpy array!'
        return condition


    def match_one(self, query, limit=1):
        """
        Match the given query (string) against available choices (patterns).
        """
        return process.extract(
            query=query,
            choices=self.update_choices(query=query),
            limit=limit
        )


    def match_multiple(self, queries, limit=1):
        """
        Match the given list of queries against available choices.

        queries:
            List or numpy array object containing all strings to be matched
        choices:
            List of true labels to match against
        limit:
            Number of matches to return

        """
        return [self.match_one(query=str(q), limit=limit) for q in queries]


    def add_variant(self, choice_name, variant):
        self.choices.get(choice_name).append(variant)


    def choose_variant(self, query, variants):
        """
        Given the query string and the variants, this method returns the best
        variant as a tuple of variant and score.
        """
        return process.extractOne(query=query, choices=variants)[0]


    def update_choices(self, query):
        """
        Update the choices from {choice name: choices list} to {choice name: choice}
        """
        return {choice_name: self.choose_variant(query=query, variants=choices) \
                if len(choices) > 1 else choices[0] \
                for choice_name, choices in self.choices.items()}


    def filter(self, results):
        """
        Filter the results based on threshold
        """
        #print(f'filtering using threshold: {self.threshold}')
        return [i[0][0] if i[0][1] >= self.threshold else 'no_match' for i in results]


    def to_dict(self, queries, results):
        return dict(zip(queries, results))


    def run(self, queries, limit=1):
        self.check(queries)
        results = self.match_multiple(queries=queries, limit=limit)
        if limit == 1:
            self.results_list = self.filter(results)
            #print(f'filtered results: {self.results_list}')
        else:
            self.results_list = results
        self.queries = queries
        return self.to_dict(queries=self.queries, results=self.results_list)


    def report(self, n=20):
        assert np.array(self.results_list).ndim == 1, 'Report is only available when limit=1'
        no_match_bool = np.array(self.results_list)=='no_match'
        #print(f'no_match_bool: {no_match_bool}')
        no_match_ratio = no_match_bool.mean()
        #print('done!')
        #print(f'no_match_ratio: {no_match_ratio}')
        print('-------------------Matching Report-------------------')
        print(f'Using threshold of {self.threshold}')
        print(f'{no_match_ratio:.2%} of the replies couldn\'t be matched ({no_match_bool.sum()}/{len(no_match_bool)}). Samples:')
        no_match_samples = np.array(self.queries)[no_match_bool]
        # When the number of no matches is smaller than the total number of
        # replies, use the total number of replies
        if len(no_match_samples) <= n:
            n = len(no_match_samples)
        samples_n = np.random.choice(no_match_samples, n, replace=False)
        pprint(samples_n)
        print('-------------------End of Report-------------------')
