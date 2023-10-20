import string
import re
from flask import Flask, render_template, request
from fuzzywuzzy import fuzz
import pandas as pd
#import jellyfish
#import nltk
#from nltk.corpus import stopwords
#nltk.download('stopwords')

app = Flask(__name__, template_folder='index')

# function

artikel = "rmh sakit"
kalimat = artikel

def levenshtein_ratio(s1, s2):
    len1 = len(s1)
    len2 = len(s2)

    if len1 == 0:
        return 0 if len2 == 0 else 100
    if len2 == 0:
        return 0 if len1 == 0 else 100

    distance = [[0] * (len2 + 1) for _ in range(len1 + 1)]

    for i in range(len1 + 1):
        distance[i][0] = i

    for j in range(len2 + 1):
        distance[0][j] = j

    for i in range(1, len1 + 1):
        for j in range(1, len2 + 1):
            cost = 0 if s1[i - 1] == s2[j - 1] else 1
            distance[i][j] = min(
                distance[i - 1][j] + 1,        # Deletion
                distance[i][j - 1] + 1,        # Insertion
                distance[i - 1][j - 1] + cost  # Substitution
            )

    max_len = max(len1, len2)
    similarity_ratio = (max_len - distance[len1][len2]) / max_len * 100

    return similarity_ratio

# Example usage:
string1 = "kata dr"
string2 = "mata air"
ratio = levenshtein_ratio(string1, string2)
print(f"The similarity ratio between '{string1}' and '{string2}' is {ratio:.2f}%")
print(fuzz.ratio(string1,string2))



#df2 = df2[~df2['Majemuk terdeteksi'].isin(df0['Majemuk terdeteksi'])]
#df2 = df2[~df2['Majemuk terdeteksi'].isin(df1['Majemuk terdeteksi'])]

#df3 = df3[~df3['Majemuk terdeteksi'].isin(df0['Majemuk terdeteksi'])]
#df3 = df3[~df3['Majemuk terdeteksi'].isin(df1['Majemuk terdeteksi'])]
#df3 = df3[~df3['Majemuk terdeteksi'].isin(df2['Majemuk terdeteksi'])]

#df2 = df2[df2['Jaccard'].apply(lambda x: x >= 0.83)]
#df2 = df2.sort_values(by=['Jaccard'])
#df2 = df2.drop_duplicates(subset=['Majemuk terdeteksi'])

#df3 = df3[df3['Jaccard'].apply(lambda x: x >= 0.79)]
#df3 = df3.sort_values(by=['Jaccard'])
#df3 = df3.drop_duplicates(subset=['Majemuk terdeteksi'])

#kata_majemuk_benar = df0_1kata['Majemuk terdeteksi'].values.tolist()
#kata_majemuk_salah = df1_1kata['Majemuk terdeteksi'].values.tolist()
#kata_majemuk_salah_koreksi = df1_1kata['Majemuk Koreksi'].values.tolist()

#kata_majemuk_mungkin_temp = pd.concat([df2, df3], ignore_index = True)
#kata_majemuk_mungkin_temp = kata_majemuk_mungkin_temp.groupby('Majemuk terdeteksi', as_index=False)['Majemuk Koreksi'].apply(', '.join)
#kata_majemuk_mungkin = kata_majemuk_mungkin_temp['Majemuk terdeteksi'].values.tolist()
#kata_majemuk_mungkin_koreksi = kata_majemuk_mungkin_temp['Majemuk Koreksi'].values.tolist()

#olah = damerau_levenshtein("olah raga", "olahraga")

#rumah sakit kepala bagian olahraga rumah skit kepla bagian olah raga rumh skit kepla baian batang tubuh mta kaki mta kki mata kaim matakaim matahari mata hari





