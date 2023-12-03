from scripts.ingredient import *
from scripts.instruction import *
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
        
        
BASE_WORDS = [
    "peppers",
    "tomato",
    "spinach_leaves",
    "turkey_breast",
    "lettuce_leaf",
    "chicken_thighs",
    "milk_powder",
    "bread_crumbs",
    "onion_flakes",
    "red_pepper",
    "pepper_flakes",
    "juice_concentrate",
    "cracker_crumbs",
    "hot_chili",
    "seasoning_mix",
    "dill_weed",
    "pepper_sauce",
    "sprouts",
    "cooking_spray",
    "cheese_blend",
    "basil_leaves",
    "pineapple_chunks",
    "marshmallow",
    "chile_powder",
    "cheese_blend",
    "corn_kernels",
    "tomato_sauce",
    "chickens",
    "cracker_crust",
    "lemonade_concentrate",
    "red_chili",
    "mushroom_caps",
    "mushroom_cap",
    "breaded_chicken",
    "frozen_pineapple",
    "pineapple_chunks",
    "seasoning_mix",
    "seaweed",
    "onion_flakes",
    "bouillon_granules",
    "lettuce_leaf",
    "stuffing_mix",
    "parsley_flakes",
    "chicken_breast",
    "basil_leaves",
    "baguettes",
    "green_tea",
    "peanut_butter",
    "green_onion",
    "fresh_cilantro",
    "breaded_chicken",
    "hot_pepper",
    "dried_lavender",
    "white_chocolate",
    "dill_weed",
    "cake_mix",
    "cheese_spread",
    "turkey_breast",
    "chucken_thighs",
    "basil_leaves",
    "mandarin_orange",
    "laurel",
    "cabbage_head",
    "pistachio",
    "cheese_dip",
    "thyme_leave",
    "boneless_pork",
    "red_pepper",
    "onion_dip",
    "skinless_chicken",
    "dark_chocolate",
    "canned_corn",
    "muffin",
    "cracker_crust",
    "bread_crumbs",
    "frozen_broccoli",
    "philadelphia",
    "cracker_crust",
    "chicken_breast",
]


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
