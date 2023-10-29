import string
import re
from flask import Flask, render_template, request, jsonify
from fuzzywuzzy import fuzz
import pandas as pd


app = Flask(__name__, template_folder='index')

# function

@app.route('/', methods=['GET', 'POST'])
def index():

    if request.method == 'POST':
        artikel = request.form['text']
        kalimat = artikel

        def remove_punc(teks) :
            punc = '''!()[]{};:'",<>./?@#$%^&*_~'''
            #words_to_remove = ['ini','juga','hal','dan','dengan','adalah','untuk','kita','yang','tetapi','saja','maka','akan', 'di', 'secara']
            for a in teks:
                if a in punc:
                    teks = teks.replace(a, "")
            # Create a regular expression pattern to match the words to remove with word boundaries
            #pattern = r'\b(?:' + '|'.join(re.escape(word) for word in words_to_remove) + r')\b'

            # Replace matched words with an empty string
            #teks = re.sub(pattern, '', teks)
            return teks
        
        kalimat = kalimat.lower()
        kalimat = re.sub(r'\d', '',kalimat)
        kalimat = remove_punc(kalimat)
        kalimat = ' '.join(kalimat.split())
        
        def generate_bigrams(text):
            list_bigrams = []
            words = text.split()  # Split the text into words
            bigrams = [(words[i], words[i + 1]) for i in range(len(words) - 1)]
            for bigram in bigrams:
                bigrams = ' '.join(bigram)
                list_bigrams.append(bigrams)
            return list_bigrams

        katamajemuk = pd.read_csv('daftarkatamajemuk.csv')
        list_katamajemuk = katamajemuk['kata majemuk'].values.tolist()

        katabenar = pd.read_csv('dataset kata benar.csv')
        katabenar = katabenar['word'].values.tolist()

        kata_typo_gram1 = []

        list_kata = generate_bigrams(kalimat)
        list_kata = list(dict.fromkeys(list_kata))
        gram_1 = kalimat.split()

        for word in gram_1:
            if word not in katabenar:
                kata_typo_gram1.append(word)
        
        kata_typo_gram1 = list(dict.fromkeys(kata_typo_gram1))


        def damerau_levenshtein(str1, str2):
            len_str1, len_str2 = len(str1), len(str2)

            # Create a matrix to store the edit distances
            d = [[0] * (len_str2 + 1) for _ in range(len_str1 + 1)]

            # Initialize the first row and column of the matrix
            for i in range(len_str1 + 1):
                d[i][0] = i
            for j in range(len_str2 + 1):
                d[0][j] = j

            # Populate the matrix using dynamic programming
            for i in range(1, len_str1 + 1):
                for j in range(1, len_str2 + 1):
                    cost = 0 if str1[i - 1] == str2[j - 1] else 1

                    # Calculate the minimum of the three possible operations
                    d[i][j] = min(
                        d[i - 1][j] + 1,      # Deletion
                        d[i][j - 1] + 1,      # Insertion
                        d[i - 1][j - 1] + cost  # Substitution
                    )

                    # Check for a transposition (Damerau condition)
                    if i > 1 and j > 1 and str1[i - 1] == str2[j - 2] and str1[i - 2] == str2[j - 1]:
                        d[i][j] = min(d[i][j], d[i - 2][j - 2] + cost)

            # The Damerau-Levenshtein distance is the value in the bottom-right cell of the matrix
            return d[len_str1][len_str2]

        # Calculate Levenshtein distances
        data = []
        data2 = []

        for a in range(len(list_kata)) :
            for b in range(len(list_katamajemuk)):
                distance1 = damerau_levenshtein(list_kata[a], list_katamajemuk[b])
                value = fuzz.ratio(list_kata[a], list_katamajemuk[b])
                if (distance1<=3) & (value > 80):
                    data2.append([list_kata[a], list_katamajemuk[b], distance1, fuzz.ratio(list_kata[a], list_katamajemuk[b])])

        for a in range(len(kata_typo_gram1)) :
            for b in range(len(list_katamajemuk)):
                distance2 = damerau_levenshtein(kata_typo_gram1[a], list_katamajemuk[b])
                value = fuzz.ratio(kata_typo_gram1[a], list_katamajemuk[b])
                if (distance2<=3) & (value > 80):
                    data.append([kata_typo_gram1[a], list_katamajemuk[b], distance2, fuzz.ratio(kata_typo_gram1[a], list_katamajemuk[b])])

        #Ubah kedalam dataframe
        df_1kata = pd.DataFrame(data, columns=["Majemuk terdeteksi", "Majemuk Koreksi", "Jumlah huruf typo", "Value"])
        df_1kata = df_1kata.sort_values(by=['Jumlah huruf typo'], ascending=True)

        df_2kata = pd.DataFrame(data2, columns=["Majemuk terdeteksi", "Majemuk Koreksi", "Jumlah huruf typo", "Value"])
        df_2kata = df_2kata.sort_values(by=['Jumlah huruf typo'], ascending=True)
        
        #Pemisahan berdasarkan huruf typo
        df0_1kata = df_1kata[df_1kata['Jumlah huruf typo'].apply(lambda x: x == 0)]
        df1_1kata = df_1kata[df_1kata['Jumlah huruf typo'].apply(lambda x: x > 0)]
        #df2_1kata = df_1kata[df_1kata['Jumlah huruf typo'].apply(lambda x: x == 2)]
        #df3_1kata = df_1kata[df_1kata['Jumlah huruf typo'].apply(lambda x: x == 3)]


        df0_2kata = df_2kata[df_2kata['Jumlah huruf typo'].apply(lambda x: x == 0)]
        df1_2kata = df_2kata[df_2kata['Jumlah huruf typo'].apply(lambda x: x == 1)]
        df2_2kata = df_2kata[df_2kata['Jumlah huruf typo'].apply(lambda x: x > 1)]

        #Menghilangkan kata yang duplikat
        #1 kata
        if len(df_1kata)>0:
            df0_1kata = df0_1kata.drop_duplicates(subset=['Majemuk terdeteksi'])

            df1_1kata = df1_1kata[~df1_1kata['Majemuk terdeteksi'].isin(df0_1kata['Majemuk terdeteksi'])]
            df1_1kata = df1_1kata.groupby(['Majemuk terdeteksi', 'Jumlah huruf typo', 'Value']).agg({"Majemuk Koreksi": ", ".join,}).reset_index()
            df1_1kata = df1_1kata.sort_values(by=['Jumlah huruf typo', 'Value'], ascending=[True, False])
            df1_1kata = df1_1kata.drop_duplicates(subset=['Majemuk terdeteksi'])

            #kata_majemuk_salah_1kata = df1_1kata['Majemuk terdeteksi'].values.tolist()
            #kata_majemuk_salah_1kata_koreksi = df1_1kata['Majemuk Koreksi'].values.tolist()
        else :
            df1_1kata = pd.DataFrame()

        #2 kata
        if len(df_2kata)>0:
            df0_2kata = df0_2kata.drop_duplicates(subset=['Majemuk terdeteksi'])

            df1_2kata = df1_2kata[~df1_2kata['Majemuk terdeteksi'].isin(df0_2kata['Majemuk terdeteksi'])]

            data = []
            def df_removespace(df1_2kata_temp):
                x = df1_2kata_temp['Majemuk terdeteksi'].replace(" ", "")
                if x == df1_2kata_temp['Majemuk Koreksi']:
                    data.append([df1_2kata_temp['Majemuk terdeteksi'], df1_2kata_temp['Majemuk Koreksi'], df1_2kata_temp['Jumlah huruf typo'], df1_2kata_temp['Value']])
                    return data

            df1_2kata_temp = df1_2kata.apply(df_removespace, axis=1)
            df1_2kata_new = pd.DataFrame(data, columns=['Majemuk terdeteksi', 'Majemuk Koreksi', 'Jumlah huruf typo', 'Value'])
            #kata_majemuk_salah_2kata_1huruf = df1_2kata_new['Majemuk terdeteksi'].values.tolist()
            #kata_majemuk_salah_2kata_1huruf_koreksi = df1_2kata_new['Majemuk Koreksi'].values.tolist()


            df1_2kata = df1_2kata[~df1_2kata['Majemuk terdeteksi'].isin(df1_2kata_new['Majemuk terdeteksi'])]
            df2_2kata = df2_2kata[~df2_2kata['Majemuk terdeteksi'].isin(df0_2kata['Majemuk terdeteksi'])]
            df2_2kata = df2_2kata[~df2_2kata['Majemuk terdeteksi'].isin(df1_2kata['Majemuk terdeteksi'])]
            df2_2kata = pd.concat([df1_2kata, df2_2kata], ignore_index = True)

            df2_2kata_majemuk = df2_2kata['Majemuk terdeteksi'].values.tolist()
            df2_2kata_koreksi = df2_2kata['Majemuk Koreksi'].values.tolist()
            df2_2kata_huruftypo = df2_2kata['Jumlah huruf typo'].values.tolist()
            df2_2kata_value = df2_2kata['Value'].values.tolist()

            typo_temp = []
            for i in range(len(df2_2kata_majemuk)):
                y = df2_2kata_majemuk[i].split()
                typo_temp.append(y)
            
            typo=[]
            for i in range(len(typo_temp)):
                for j in range(2):
                    if typo_temp[i][j] not in katabenar:
                        typo.append(i)

            typo = list(set(typo))

            data = []
            for i in typo:
                data.append([df2_2kata_majemuk[i], df2_2kata_koreksi[i], df2_2kata_huruftypo[i], df2_2kata_value[i]])
            df2kata = pd.DataFrame(data, columns=["Majemuk terdeteksi", "Majemuk Koreksi", "Jumlah huruf typo", "Value"])

            df2kata = df2kata.groupby(['Majemuk terdeteksi', 'Jumlah huruf typo', 'Value']).agg({"Majemuk Koreksi": ", ".join,}).reset_index()
            
            df2kata = df2kata.sort_values(by=['Jumlah huruf typo', 'Value'], ascending=[True, False])
            df2kata = df2kata.drop_duplicates(subset=['Majemuk terdeteksi'])

            #kata_majemuk_salah_2kata_lebihdari1huruf = df2kata['Majemuk terdeteksi'].values.tolist()
            #kata_majemuk_salah_2kata_lebihdari1huruf_koreksi = df2kata['Majemuk Koreksi'].values.tolist()
        else : 
            df1_2kata_new = pd.DataFrame()
            df2kata = pd.DataFrame()
        
        all_df = pd.concat([df1_1kata, df1_2kata_new, df2kata], ignore_index=True)
        kata_majemuk_salah = all_df['Majemuk terdeteksi'].values.tolist()
        kata_majemuk_salah_koreksi = all_df['Majemuk Koreksi'].values.tolist()

        result = {}
        i = 0
        for kata in kata_majemuk_salah:
            result[kata] = {
                'is_correct' : False,
                'suggestion' : kata_majemuk_salah_koreksi[i]
            }
            i += 1

        finalResults = {
            'result' : result,
            'paragraph' : artikel
        }
        
        return render_template('result.html',  artikel=artikel, result=result)
        #or
        #return jsonify(finalResults)
    return render_template('home.html')

if __name__ == '__main__':
    app.run(debug=True)




