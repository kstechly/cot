import os
import utils
from functools import cache
import tiktoken #type: ignore
### BASIC FUNCTIONS ###
def generator(domain_name, generate_instructions, generate_query, generate_thoughts, generate_correct_evaluation):
    def generate(instance_text, problem_relaxation="full", cot_type="", n_examples=0, magic="", example_type="examples"):
        # cot_type      :      name of the cot prompt (leave blank for no thought annotation)
        # n_examples    :      number of examples to provide
        # magic         :      "let's think step by step" or whatever appended to end of prompt

        # Boilerplate instructions
        instructions = generate_instructions(problem_relaxation)

        # TODO GET RID OF THIS NONSENSE!!!
        current_query = generate_query(instance_text, problem_relaxation)

        prompt = "[Instructions]\n"+instructions
        if n_examples: prompt+=f"\n\nThe following {n_examples} examples are provided. Please follow the formatting used in them.\n\n"
        prompt += generate_cot(cot_type, n_examples, magic, domain_name, generate_query, generate_thoughts, generate_correct_evaluation, problem_relaxation, example_type) + f'\nProblem to solve:\n\n' + current_query + "\n\n" + magic
        ## TODO refactor this. problem_relaxation reading should NOT be here! Only doing this bc in a hurry :((
        if (cot_type or magic) and not problem_relaxation == "dont_think": prompt+= "\n\n[Thoughts]"
        else: prompt+= "\n[Answer]\n"
        return prompt
    return generate

### COT PROMPT UTILITIES ###
def generate_cot(cot_type, n_examples, magic, domain_name, generate_query, generate_thoughts, generate_correct_evaluation, problem_relaxation, example_type="examples"):
    # Example instances have to contain a "c example " line with the example coloring
    # TODO this should know its own name. Just make these classes already cmon
    if not n_examples: return "" 

    example_instances = utils.read_json(domain_name, False, example_type)

    assert n_examples <= len(example_instances)

    example_labels = [f'Example {k}:\n\n' for k in example_instances]
    example_queries = [generate_query(example, problem_relaxation) for example in example_instances.values()]
    example_thoughts = [generate_thoughts(example, cot_type, problem_relaxation) for example in example_instances.values()]
    example_evaluations = [generate_correct_evaluation(example, problem_relaxation) for example in example_instances.values()]

    examples = list(map(lambda w,x,y,z: w+x+"\n\n"+magic+f"{chr(10)+'[Thoughts]' if cot_type else ''}\n"+y+"\n\n[Answer]\n"+z+"\n\n",example_labels, example_queries, example_thoughts, example_evaluations))
    return "".join(examples[:n_examples])

### INSTANCE GENERATION UTILITIES ###
@cache
def get_allowed_words(domain_name, token_length, words_location):
    names = load_all_names(domain_name, words_location)
    return [n for n in names if token_l(n)==token_length]
@cache
def token_l(x):
    return len(get_tokens(x))
@cache
def get_encoding():
    return tiktoken.get_encoding("cl100k_base")
@cache
def get_tokens(x):
    enc = get_encoding()
    return enc.encode(x)


def load_all_names(domain_name, words_location):
    return utils.read_json(domain_name, False, "instances", strange_subloc=words_location)