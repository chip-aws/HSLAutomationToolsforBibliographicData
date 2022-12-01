# @Function: Machine Learning Algorithm
# @Author: Shouqiang Ye

from config import Config
from flask import Flask, request, redirect, render_template, Response, send_file, send_from_directory
from flask_wtf import FlaskForm
from wtforms import SelectMultipleField
from flask_bootstrap import Bootstrap
from os.path import join, dirname, realpath
import pandas as pd
# from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer  # add CountVectorizer for NMF
from sklearn.cluster import KMeans
from datetime import datetime
import io, os
import numpy as np

# import  additional lib for NMF
from sklearn import decomposition
import matplotlib.pyplot as plt
import re
import nltk
from nltk.stem.porter import PorterStemmer
from sklearn.model_selection import train_test_split


# single Kmean or NMF algo
def ml_cluster(df, form, stopwords_list):
    """
    type df: dataframe
    type form: form
    type stopwords_list: additional stopwords list from stopwords.txt
    rtype: dataframe
    """
    file = form.filename.data
    text = form.columns.data
    algorithm = form.algorithm.data
    topics = form.topics.data
    length = form.length.data
    stopwords = form.stopwords.data

    # filename = os.path.join(Config.DOWNLOAD_FOLDER, output_file_name)
    stopword = stopwords
    pd.set_option('max_colwidth', 400)
    df.head()
    df.info()

    text_list = text.split(",")

    # initial the first colum -> joined_col
    df['joined_col'] = df[text_list[0]]
    # combine all the selected columns -> joined_col and sep with space
    for i in range(1, len(text_list)):
        df['joined_col'] = df['joined_col'].str.cat(df[text_list[i]], sep=" ")

    documents = df['joined_col'].values.astype("U")

    if not stopwords == None:
        stopwords = stopwords.split(',')
    # combine stopwords from form with stopwords.txt list
    # Call create_stopwords_list() which will return a list of stopwords from stopwords.txt
    # stopwords_list = create_stopwords_list(filename_stopwords)
    # combine with the orginal list
    stopwords += stopwords_list

    # combine stopwords with nltk lib
    stemmer = nltk.stem.SnowballStemmer('english')
    nltk.download('stopwords')
    # stopwords = set(nltk.corpus.stopwords.words('english'))
    stopwords += set(nltk.corpus.stopwords.words('english'))

    k = int(topics)
    if algorithm == 'kMean':
        vectorizer = TfidfVectorizer(stop_words=stopwords, ngram_range=(1, 3))
        features = vectorizer.fit_transform(documents)
        # why every time has different outcome even with the same parameters?
        # Explanation: When using k-means, you want to set the random_state parameter in KMeans (see the documentation).
        # Set this to either an int or a RandomState instance.
        model = KMeans(n_clusters=k, init='k-means++', max_iter=int(length), n_init=1, verbose=0, random_state=3425)
        model.fit(features)

        df['Cluster'] = model.labels_
        clusters = df.groupby('Cluster')
        order_centroids = model.cluster_centers_.argsort()[:, ::-1]
        terms = vectorizer.get_feature_names_out()

    elif algorithm == 'NMF':
        vectorizer = CountVectorizer(stop_words=stopwords, ngram_range=(1, 3))
        # vectors = vectorizer.fit_transform(documents).todense()
        vectors = vectorizer.fit_transform(documents)
        # model = decomposition.NMF(n_components=k, random_state=3425)
        model = decomposition.NMF(n_components=k, init='nndsvda', max_iter=int(length), verbose=0, random_state=3425)

        W1 = model.fit_transform(vectors)
        H1 = model.components_
        # Calculate Dominant topic with NMF
        # colnames = ["Topic" + str(i) for i in range(clf.n_components)]
        # docnames = df['AN']
        # df_doc_topic = pd.DataFrame(np.round(W1, 2), columns=colnames, index=docnames)
        # df_doc_topic = pd.DataFrame(np.round(W1, 2), columns=colnames)
        # significant_topic = np.argmax(df_doc_topic.values, axis=1)
        df['Cluster'] = np.argmax(W1, axis=1)

        order_centroids = H1.argsort()[:, ::-1]
        terms = np.array(vectorizer.get_feature_names_out())

    # drop joined_col column because we don't need to display it in the result CSV file
    df.drop('joined_col', axis=1, inplace=True)

    # Stemming or Lemmatization; necessary / additive with ngram 1-3 range?
    # not sure here, for lables_ length not equal to np length
    # df['Cluster'] = model.labels_

    df2 = pd.DataFrame()
    for i in range(k):
        subset_df = df[df.Cluster == i].shape[0]
        top_ten_words = [terms[ind] for ind in order_centroids[i, :10]]
        data = {'Cluster Number': i,
                'Number of Items': subset_df,
                'Top Cluster Terms': top_ten_words}
        # use concat instead of append
        # df2 = df2.append(data, ignore_index=True)
        df2 = pd.concat([df2, pd.DataFrame([data])], axis=0, ignore_index=True)

    df2.head()
    return df2


# Ensemble Algo
def sup_cluster(df, form, stopwords_list):
    """
    type df: dataframe
    type form: form
    type stopwords_list: additional stopwords list from stopwords.txt
    rtype: dataframe
    """
    file = form.filename.data
    text = form.columns.data
    # algorithm = form.algorithm.data
    stopwords = form.stopwords.data
    threshold = form.threshold.data

    # filename = os.path.join(Config.DOWNLOAD_FOLDER, output_file_name)
    stopword = stopwords
    # pd.set_option('max_colwidth', 100)
    # pd.set_option('display.width', 5)

    df_filter_seeds, df_pivot, df_seed_capture = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    text_list = text.split(",")

    # initial the first colum -> joined_col
    df['joined_col'] = df[text_list[0]]
    # combine all the selected columns -> joined_col and sep with space
    for i in range(1, len(text_list)):
        df['joined_col'] = df['joined_col'].str.cat(df[text_list[i]], sep=" ")

    documents = df['joined_col'].values.astype("U")
    df.drop('joined_col', axis=1, inplace=True)

    if stopwords:
        stopwords = stopwords.split(',')
    # combine stopwords from form with stopwords.txt list
    # Call create_stopwords_list() which will return a list of stopwords from stopwords.txt
    # stopwords_list = create_stopwords_list(filename_stopwords)
    # combine with the original list
    stopwords += stopwords_list
    # combine with nltk stopwords
    stemmer = nltk.stem.SnowballStemmer('english')
    nltk.download('stopwords')
    stopwords += set(nltk.corpus.stopwords.words('english'))


    # add NMF algo, Aug 13,2022 by Shouqiang Ye
    # define all models
    algo_dict = {'Kmeans_': [10, 20, 30], 'NMF_': [10, 20, 30]}

    # >>>>>>>>>>>> use DF: df_filter_seeds  output 'Filtered for Seeds only' sheet
    # 'Filtered for Seeds only': step 1: select AN column
    df_filter_seeds = df.loc[df['Seed'] == '1', ['AN']]
    for algo in algo_dict:
        k_list = algo_dict[algo]
        # >>>>>>>>>>>> output 'Supervised Clustering' sheet -- Kmeans_10, Kmeans_20,
        vectorizer = TfidfVectorizer(stop_words=stopwords, ngram_range=(1, 3)) if algo == 'Kmeans_' \
            else CountVectorizer(stop_words=stopwords, ngram_range=(1, 3)) if algo == 'NMF_' else "Null"
        features = vectorizer.fit_transform(documents)

        for k in k_list:
            # Kmeans and NMF have different call function, so we add determination here
            if algo == 'Kmeans_':
                # max_iter= 1 could faster running time
                # model = KMeans(n_clusters=k, init='k-means++', n_init=1, verbose=0, random_state=3425)
                model = KMeans(n_clusters=k, init='k-means++', max_iter=1, n_init=1, verbose=0, random_state=3425)
                model.fit(features)
                df[algo + str(k)] = model.labels_
            elif algo == 'NMF_':
                # max_iter= 1 could faster running time
                # model = decomposition.NMF(n_components=k, init='nndsvda', verbose=0, random_state=3425)
                model = decomposition.NMF(n_components=k, max_iter=1, init='nndsvda', verbose=0, random_state=3425)
                W1 = model.fit_transform(features)
                H1 = model.components_
                df[algo + str(k)] = np.argmax(W1, axis=1)

            # 'Filtered for Seeds only':  step 2: concat seeds = 1 to sheet 'Filtered for Seeds only'
            # df_filter_seeds = df.loc[df['Seed'] == '1', ['Kmeans_10', 'Kmeans_20', 'Kmeans_30'], ['NMF_10', 'NMF_20', 'NMF_30']]
            df_kmean = df.loc[df['Seed'] == '1', [algo + str(k)]]
            df_filter_seeds = pd.concat([df_filter_seeds, df_kmean], axis=1)

            # >>>>>>>>>>>> output 'Pivot Tables' sheet --
            df_km = pd.DataFrame()
            for i in range(k):
                # DataFrame.shape, Return a tuple representing the dimensionality of the DataFrame.
                # 'Pivot Tables': step1: cal the sum of cluster no
                sum_cluster = df_kmean[df_kmean[algo + str(k)] == i].shape[0]
                data = {f'Cluster Number({algo[0]}-{str(k)})': i,
                        f'# of Seeds({algo[0]}-{str(k)})': sum_cluster}
                # df_km = df_km.append(data, ignore_index=True)
                df_km = pd.concat([df_km, pd.DataFrame([data])], axis=0, ignore_index=True)

            # 'Pivot Tables': step2: sort by # of Seeds
            df_km = df_km.sort_values(by=f'# of Seeds({algo[0]}-{str(k)})', ascending=False, ignore_index=True)
            df_pivot = pd.concat([df_pivot, df_km], axis=1)

    # >>>>>>>>>>>> output 'Seed Capture' sheet
    # cal k_list from algo_dict dict, return list, like: [10, 20, 30, 10, 20, 30]
    algo_dict_list = list(algo_dict.values())
    k_list = []
    for i in range(len(algo_dict_list)):
        k_list += algo_dict_list[i]

    total_nums_seeds = df_filter_seeds.shape[0]
    df_unique = pd.DataFrame()
    cur_unique_seeds, cum_unique_seeds, cum_unique_percent, Continue_flag = 0, 0, 0, ''
    # loop for vertical
    for i in range(max(k_list)):
        # cur_unique_seeds = 0
        row_data = {'Step': i + 1,
                    'Cluster (all models)': '',
                    'Seed Capture by model (unique seeds only)': cur_unique_seeds,
                    'Seed Capture Running total (unique seeds only)': cum_unique_seeds,
                    'Cumulative %': cum_unique_percent,
                    'Continue or Stop?': Continue_flag}
        # loop for horizontal
        for j in range(len(k_list)):
            # 'Seed Capture': step1: add Cluster (all models)
            clus_no = df_pivot.iloc[i, 2 * j].astype(int)
            if row_data.get('Cluster (all models)') == '':
                row_data['Cluster (all models)'] = clus_no.astype(str)
            else:
                row_data['Cluster (all models)'] += ',' + clus_no.astype(str)
                # row_data['Cluster (all models)'] += '' if row_data.get('Cluster (all models)') == '' else ',' + clus_no

            # 'Seed Capture': step2: Seed Capture by model (unique seeds only)
            df_AN = df_filter_seeds.loc[df_filter_seeds.iloc[:, 1 + j] == clus_no, ['AN']]
            # cal unique by drop duplicated AN rows
            df_unique = pd.concat([df_unique, df_AN]).drop_duplicates().reset_index(drop=True)

        # 'Seed Capture': step3: Seed Capture Running total (unique seeds only)
        cum_unique_seeds = df_unique.shape[0]
        row_data['Seed Capture Running total (unique seeds only)'] = cum_unique_seeds

        # 'Seed Capture': step4:cal Cumulative % and Continue Yes or No
        cum_unique_percent = cum_unique_seeds / total_nums_seeds

        Continue_flag = 'Continue' if cum_unique_percent <= float(threshold) else 'Stop'
        row_data['Continue or Stop?'] = Continue_flag
        # format Cumulative % with percent
        cum_unique_percent = "{0:.2f}%".format(cum_unique_percent * 100)
        row_data['Cumulative %'] = cum_unique_percent

        # 'Seed Capture': step5: finally append row
        df_seed_capture = pd.concat([df_seed_capture, pd.DataFrame([row_data])], axis=0, ignore_index=True)
        if Continue_flag == 'Stop':
            break

    # 'Seed Capture': step6: Seed Capture by model (unique seeds only) by diff function
    df_seed_capture['Seed Capture by model (unique seeds only)'] = \
        df_seed_capture['Seed Capture Running total (unique seeds only)'].diff()

    # >>>>>>>>>>>> output 'Supervised Clustering' - Ensemble_Score
    # define a dictionary to save the top cluster
    dict_top_cluster = {}
    # split top cluster, like 6,5,24  -> 3 columns: 6    5   24
    df_top_cluster = df_seed_capture['Cluster (all models)'].str.split(pat=',', n=-1, expand=True)
    i_index = 0
    df['Ensemble_Score'] = 0
    # algo_dict = {'Kmeans_': [10, 20, 30], 'NMF_': [10, 20, 30]}
    for algo in algo_dict:
        k_list = algo_dict[algo]
        for k in k_list:
            dict_top_cluster[algo + str(k)] = df_top_cluster[i_index].astype(int).tolist()
            i_index += 1
            # cal every model if it is included in the top cluster
            df['Ensemble_Score'] += \
                df[algo + str(k)].apply(lambda x: 1 if x in dict_top_cluster[algo + str(k)] else 0)

    # Ensemble_AnyOnePositive
    df['Ensemble_AnyOnePositive'] = np.where(
        df['Ensemble_Score'] != 0, 1, 0)

    return df, df_filter_seeds, df_pivot, df_seed_capture


def create_stopwords_list(filename_stopwords):
    # initial an empty return list
    stopwords_list = list()
    try:
        # Open the file with the encoding argument, like this: open(filename, 'r', encoding='utf8')
        stopwords_file = open(stop_file_full_filepath, 'r', encoding='utf8')
        # read line from openfile
        for line in stopwords_file:
            # use append method to add stopwords list
            stopwords_list.append(line.strip())
        # close opening file
        stopwords_file.close()
    except FileNotFoundError as err:
        print('Error: cannot find file,', STOP_FILE_NAME)
        print('Error:', err)
        stopwords_list = False
    except OSError as err:
        print('Error: cannot access file,', STOP_FILE_NAME)
        print('Error:', err)
        stopwords_list = False
    except ValueError as err:
        print('Error: invalid data found in file', STOP_FILE_NAME)
        print('Error:', err)
        stopwords_list = False
    except Exception as err:  # catch all error handler, if the above handlers do not apply
        print('An unknown error occurred')
        print('Error:', err)
        stopwords_list = False
    finally:
        return stopwords_list
