from scripts.data_model.ingredient import Ingredient
from scripts.data_model.recipe import Recipe 
import ast


def data_load(args, nlg, cluster_ingrs, kaggle_prot, ingredient_parser, instruction_parser):
    recipes = []
    for title, ner, source, instrs in zip(nlg['title'], nlg['NER'], nlg['source'], nlg["directions"]):
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
                parsed_ingrs = []
                for ingr in ingr_list:
                    ready_ingr = get_clustered_ingr(ingredient_parser.parse_entry(ingr), cluster_ingrs)
                    protein = protein_handler(ready_ingr, kaggle_prot)
                    parsed_ingrs.append(Ingredient(ready_ingr, protein))
                    
                recipes.append(Recipe(title, parsed_ingrs, instr_list))
    
    return recipes


def protein_handler(ingr, kaggle_prot):
    # check if full match possible
    if ingr in kaggle_prot.keys():
        return kaggle_prot[ingr]
    
    # check if part match possible
    ingr_cat = ingr.split(sep='_')[0]
    if ingr in kaggle_prot.keys():
        return kaggle_prot[ingr_cat]

    # for key in kaggle_prot.keys():
    #     if ingr in key:
    #         return kaggle_prot[key]
    return None


def get_clustered_ingr(ingr, cluster_ingrs):
    for key, arr in cluster_ingrs.items():
        if ingr in arr:
            return key
    return ingr 