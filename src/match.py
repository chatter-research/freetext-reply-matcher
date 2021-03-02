import numpy as np
import pandas as pd
from fuzzywuzzy import process
from pprint import pprint


class Matcher():
    def __init__(self, categories, threshold=80):
        """
        categories:
            Dict of true labels to match against with category name as key and
            list of different variants as value
        threshold:
            Float - the threshold score to use when matching`

        """
        self.categories = categories
        self.categories_reverse = self.build_reverse_mapping(self.categories)
        self.threshold = threshold
        #self.queries = None
        #$self.match_results = None


    def check(self, queries):
        condition = isinstance(queries, list) or isinstance(queries, np.ndarray)
        assert condition, '"queries" can only be a Python list or Numpy array!'
        return condition


    def match_one(self, query, limit=1, variants_to_categories=True):
        """
        Match the given query (string) against available categories.
        Returns a list of tuples with each tuple representing one potential match.
        """
        all_variants = [variant \
                        for category, variants in self.categories.items() \
                        for variant in variants]
        variants_matched = process.extract(query=query, choices=all_variants,limit=limit)
        if variants_to_categories:
            categories_matched = self.variants_to_categories(variants_matched)
            return categories_matched
        return variants_matched


    def match_multiple(self, queries, limit, variants_to_categories):
        """
        Match the given list of queries against available categories
        """
        match_results = [
            self.match_one(
                query=str(q),
                limit=limit,
                variants_to_categories=variants_to_categories
            ) for q in queries
        ]
        return match_results


    def add_variants(self, category: str, variants: list) -> list:
        # Convert all variants to lowercase and remove leading and trailing spaces
        variants = [i.strip().lower() for i in variants]
        self.categories[category] = list(set(self.categories.get(category, []) + variants))
        # Update reverse mapping
        self.categories_reverse = self.build_reverse_mapping(self.categories)


    def remove_variants(self, category: str) -> None:
        try:
            del self.categories[category]
            print(f'Category "{category}" removed')
        except KeyError:
            print(f'Category "{category}" doesn\'t exist')


    def build_reverse_mapping(self, categories):
        return {variant: category \
                for category, variants in categories.items() \
                for variant in variants}


    def variants_to_categories(self, variants_matched):
        # Map the variant back to the category
        categories_matched = \
        [(self.categories_reverse.get(variant_tuple[0]), variant_tuple[1]) \
         for variant_tuple in variants_matched]
        return categories_matched


    def filter(self, match_results: list) -> list:
        """
        Filter the results based on threshold. "results" is a list of matches
        for all queries, where each match is a list of tuples.

        """
        #print(f'filtering using threshold: {self.threshold}')
        # Use the best match for each query if the match score is greater than
        # or equal to the threshold.
        #if keep_all:
        #    return [[i[0][0]]+i[0] if i[0][1] >= self.threshold else ['no_match']+i[0] for i in match_results]
        # Grab the best match and filter
        return [i[0][0] if i[0][1] >= self.threshold else 'no_match' for i in match_results]


    def to_dict(self, queries, match_results):
        return dict(zip(queries, match_results))


    def __call__(self, queries, limit=1):
        self.check(queries)
        match_results = self.match_multiple(queries=queries, limit=limit, variants_to_categories=False)
        match_results_filtered = self.filter(match_results)
        print(f'match_results_filtered: {match_results_filtered}')
        match_results_filtered = [self.categories_reverse[i] if i!='no_match' else 'no_match' for i in match_results_filtered]
        if limit > 1: # exploration mode
            match_results_filtered = [
                [match_results_filtered[i]] + match_results[i] for i in range(len(queries))
            ]
        return match_results_filtered
        #return self.to_dict(queries, match_results_filtered)


    def report(self, n=20):
        assert np.array(self.results_list).ndim == 1, 'Report is only available when limit=1'
        no_match_bool = np.array(self.results_list)=='no_match'
        #print(f'no_match_bool: {no_match_bool}')
        no_match_ratio = no_match_bool.mean()
        #print('done!')
        #print(f'no_match_ratio: {no_match_ratio}')
        print('-------------------Matching Report-------------------')
        print(f'--> {no_match_ratio:.2%} of the replies couldn\'t be matched')
        print(f'--> Using threshold of {self.threshold}')
        no_match_samples = np.array(self.queries)[no_match_bool]
        # When the number of no matches is smaller than the total number of
        # replies, use the total number of replies
        if len(no_match_samples) <= n:
            n = len(no_match_samples)
        samples_n = np.random.choice(no_match_samples, n, replace=False)
        print(f'--> A random sample of {n} unmatched replies:\n')
        #pprint(samples_n)
        [print(i) for i in samples_n]
        print('-------------------End of Report-------------------')
