import pandas as pd
from PIL import Image
import requests
from io import BytesIO
import numpy as np
from skimage import measure
import pickle
import imagehash
from flag_util import FlagUtil
from flag_scraping import FlagScraper
import operator
import sys

class FlagIdentifier:

    def __init__(self):
        self.util = FlagUtil()
        
        self.flag_df = pd.read_csv("flag_df.csv", index_col = "country")
        self.flag_df["flag"] = self.flag_df["flag"].apply(self.util.makeArray)

    def mse(self, imageA, imageB):
        err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
        err /= float(imageA.shape[0] * imageA.shape[1])

        return err

    def closest_flag(self, country):
        return self.abstract_compare_flags(country, operator.lt)

    def farthest_flag(self, country):
        return self.abstract_compare_flags(country, operator.gt)

    def abstract_compare_flags(self, country, op):
        flag = self.flag_df["flag"].loc[country]
        mse = -1
        max_country = 0
        for c in self.flag_df.index:
            cur_flag = self.flag_df["flag"].loc[c]
            dist = self.mse(flag, cur_flag)
            if (op(dist, mse) or mse == -1) and c != country:
                mse = dist
                max_country = c
                
        return max_country

    def identify_flag_ssim(self, url):
        flag = self.util.process_img(url)
        
        max_ssim = -1
        max_index = 0
        for c in self.flag_df.index:
            cur_flag = self.flag_df["flag"].loc[c]
            dist = measure.compare_ssim(flag, cur_flag, multichannel = True)
            if dist > max_ssim:
                max_ssim = dist
                max_index = c
                
        return max_index

    def identify_flag_mse(self, url):
        flag = self.util.process_img(url)
        
        min_mse = -1
        max_index = 0
        for c in self.flag_df.index:
            cur_flag = self.flag_df["flag"].loc[c]
            error = self.mse(flag, cur_flag)
            if error < min_mse or min_mse == -1:
                min_mse = error
                max_index = c
                
        return max_index

    def identify_flag_hash(self, url):
        flag = self.util.process_img(url)
        
        min_hash = -1
        max_index = 0
        for c in self.flag_df.index:
            cur_flag = self.flag_df["flag"].loc[c]
            firsthash = imagehash.average_hash(Image.fromarray(flag))
            otherhash = imagehash.average_hash(Image.fromarray(cur_flag))
            hash_dist = firsthash - otherhash
            
            if hash_dist < min_hash or min_hash == -1:
                min_hash = hash_dist
                max_index = c
                
        return max_index

# test = FlagIdentifier()
# print(test.identify_flag_mse(sys.argv[1]))
# print(test.closest_flag(sys.argv[1]))
# print(test.closest_flag("Italy"))
# print(test.closest_flag("Nepal"))
# print(test.closest_flag("The United States"))
# print(test.closest_flag("Liberia"))

# url = "https://flagpedia.net/data/flags/h80/af.png"
# print(test.identify_flag_ssim(url))
# print(test.identify_flag_mse(url))
# print(test.identify_flag_hash(url))