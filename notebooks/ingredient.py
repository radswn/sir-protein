# Copyright (c) Meta Platforms, Inc. and affiliates 
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

import os
import pickle
import re
from typing import Any, Dict, List


class IngredientParser:
    def __init__(self, replace_dict: Dict[str, List[str]]):
        self.replace_dict = replace_dict

    def parse_entry(self, item: Dict[str, Any], clean_digits=False):
        return self.clean(item, clean_digits)

    def clean(self, det_ingr, clean_digits=False) -> str:
        """
        Read an ingredient ingredient and clean the ingredient
        - remove case
        - get rid of some special characters
        - replace some characters
        """
        det_ingr_undrs = det_ingr.lower()
        if clean_digits:
            det_ingr_undrs = "".join(c for c in det_ingr_undrs if not c.isdigit())

        for rep, char_list in self.replace_dict.items():
            for c_ in char_list:
                if c_ in det_ingr_undrs:
                    det_ingr_undrs = det_ingr_undrs.replace(c_, rep)

        det_ingr_undrs = det_ingr_undrs.strip()
        det_ingr_undrs = det_ingr_undrs.replace(" ", "_")

        if not clean_digits:
            pattern = "(?P<char>[" + re.escape("_") + "])(?P=char)+"
            det_ingr_undrs = re.sub(pattern, r"\1", det_ingr_undrs)

        return det_ingr_undrs


def remove_plurals(counter_ingrs, ingr_clusters):
    deleted_ingredients = []

    for k, v in counter_ingrs.items():

        if len(k) == 0:
            deleted_ingredients.append(k)
            continue

        gotit = 0
        if k[-2:] == "es":
            if k[:-2] in counter_ingrs.keys():
                counter_ingrs[k[:-2]] += v
                ingr_clusters[k[:-2]].extend(ingr_clusters[k])
                deleted_ingredients.append(k)
                gotit = 1

        if k[-1] == "s" and gotit == 0:
            if k[:-1] in counter_ingrs.keys():
                counter_ingrs[k[:-1]] += v
                ingr_clusters[k[:-1]].extend(ingr_clusters[k])
                deleted_ingredients.append(k)
    for item in deleted_ingredients:
        del counter_ingrs[item]
        del ingr_clusters[item]
    return counter_ingrs, ingr_clusters


def cluster_ingredients(counter_ingrs):
    mydict = dict()
    mydict_ingrs = dict()

    for k, v in counter_ingrs.items():

        w1 = k.split("_")[-1]
        w2 = k.split("_")[0]
        lw = [w1, w2]
        if len(k.split("_")) > 1:
            w3 = k.split("_")[0] + "_" + k.split("_")[1]
            w4 = k.split("_")[-2] + "_" + k.split("_")[-1]

            lw = [w1, w2, w4, w3]

        gotit = 0
        for w in lw:
            if w in counter_ingrs.keys():
                # check if its parts are
                parts = w.split("_")
                if len(parts) > 0:
                    if parts[0] in counter_ingrs.keys():
                        w = parts[0]
                    elif parts[1] in counter_ingrs.keys():
                        w = parts[1]
                if w in mydict.keys():
                    mydict[w] += v
                    mydict_ingrs[w].append(k)
                else:
                    mydict[w] = v
                    mydict_ingrs[w] = [k]
                gotit = 1
                break
        if gotit == 0:
            mydict[k] = v
            mydict_ingrs[k] = [k]

    return mydict, mydict_ingrs
