from scripts.ingredient_parser import *
from scripts.instruction_parser import *
from scripts.constants import BASE_WORDS
import ast


class Args:
    def __init__(self, minnumingrs, minnuminstrs, maxnuminstrs, 
                 maxnumingrs, minnumwords, majority_lvl, threshold_ingrs):
        self.minnumingrs = minnumingrs
        self.minnuminstrs = minnuminstrs
        self.maxnuminstrs = maxnuminstrs
        self.maxnumingrs = maxnumingrs
        self.minnumwords = minnumwords
        self.majority_lvl = majority_lvl
        self.threshold_ingrs = threshold_ingrs
        

def ingredients_dict(nlg, args, instruction_parser: InstructionParser, ingredient_parser: IngredientParser):
    ingr_counted = {}
    for ner, source, instrs in zip(nlg['NER'], nlg['source'], nlg["directions"]):
        if source == "Recipes1M": 
            ingr_list = ast.literal_eval(ner)  
            instrs_list = ast.literal_eval(instrs)  
            acc_len, instr_list = instruction_parser.parse_entry(instrs_list)
            if (
                len(instrs_list) < args.minnuminstrs
                or len(instrs_list) >= args.maxnuminstrs
                or acc_len < args.minnumwords
            ):
                continue
            else:         
                # preprocess ingr, 
                for ingr in ingr_list:
                    ready_ingr = ingredient_parser.parse_entry(ingr)
                    if ready_ingr in ingr_counted.keys():
                        ingr_counted[ready_ingr] += 1
                    else:
                        ingr_counted[ready_ingr] = 1

    # manually add missing entries for better clustering
    for base_word in BASE_WORDS:
        if base_word not in ingr_counted.keys():
            ingr_counted[base_word] = 1

    counter_ingrs, cluster_ingrs = cluster_ingredients(ingr_counted)
    counter_ingrs, cluster_ingrs = remove_plurals(counter_ingrs, cluster_ingrs)

    # if threshold not achieved - delete
    ingrs = {
            word: cnt
            for word, cnt in ingr_counted.items()
            if cnt >= args.threshold_ingrs
    }

    return ingrs, cluster_ingrs


def kaggle_dict(kaggle, ingredient_parser: IngredientParser):
    ingr_proteined = {}
    for name, protein in zip(kaggle['Descrip'], kaggle['Protein_g']):
        protein_f = float(protein)
        # preprocess ingr, 
        ready_ingr = ingredient_parser.parse_entry(name)
        ingr_proteined[ready_ingr] = protein_f

    return ingr_proteined
