import os
import argparse
import json
from tqdm import tqdm #type: ignore
import domain_utils
from domain_utils import *
from fire import Fire #type: ignore
import pandas as pd #type: ignore
import seaborn as sns #type: ignore
import numpy as np #type: ignore
import matplotlib.pyplot as plt #type: ignore

import utils

def evaluate_responses(domain_name, specified_instances=[], overwrite_previous=False, verbose=False, graph_it=False, values='', columns='', h='ground_truth', **kwargs):
    domain = domain_utils.domains[domain_name]

    # Load response data
    responses = utils.read_json(domain_name, False, "responses", verbose)
    if specified_instances: working_instances = {num: responses[num] for num in responses.key() if num in specified_instances}
    else: working_instances = responses
    
    # Load previously done work
    previous = utils.read_json(domain_name, overwrite_previous, "evaluations", verbose=verbose)
    
    # for each instance, pass through the eval function, then update the dictionary with the eval
    for instance in tqdm(working_instances):
        if instance not in previous.keys(): previous[instance] = []
        for response in working_instances[instance]:
            ind = utils.dict_index(previous[instance], response)
            if not overwrite_previous and ind > -1: continue
            response.update(domain.evaluate(response))

            if ind == -1: previous[instance].append(response)
            else: previous[instance][ind] = response
    utils.write_json(domain_name, previous, "evaluations")

    # TODO factor this into a better place 
    flat_results = utils.flatten(previous)
    df = pd.DataFrame(flat_results)
    df.replace({"cot":{"":"Direct"}}, inplace=True)
    boolean_table = df.select_dtypes(np.bool_).value_counts(normalize=True).mul(100).astype(str)
    print(boolean_table+"%")
    # print(df.pivot_table(columns='uniform_token_length', values='correct'))
    # df['binned'] = pd.cut(df['input_length'],5)
    # print(df.pivot_table(index='steps_to_solve',columns='binned', values='correct'))
    print(f"${df['estimated_cost'].sum():.02f} estimated total spend.")
    df2 = df.drop(columns=['trial_id', 'temp', 'n_examples', 'output_length', 'well_formed_response', 'timestamp', 'estimated_cost'])
    print(df2.corr(numeric_only=True))
    # steps_pivot = df.pivot_table(columns='steps_to_solve', values='correct')
    # print(steps_pivot.head())
    # print(steps_pivot.columns)
    # x = 'uniform_token_length'
    if graph_it:
        sns.color_palette("colorblind")
        sns.set_theme(style="darkgrid")
        x = 'steps_to_solve'
        y = 'correct'
        sns.barplot(x=x, y=y, hue=h,
                data=df)
        sns.despine(offset=10, trim=True)
        if domain_name == "coinflip": plt.plot([df.min()[x]-1, df.max()[x]-2], [0.5, 0.5])
        plt.show()
    if values and columns:
        print(df.pivot_table(columns=columns, values=values))


if __name__=="__main__":
    Fire(evaluate_responses)