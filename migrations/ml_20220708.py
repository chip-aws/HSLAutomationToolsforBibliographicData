# @Function: Machine Learning Algorithm
# @Date: May 13th,2022
# @Author: Shouqiang Ye

from config import Config
from flask import Flask, request, redirect, render_template, Response, send_file, send_from_directory
from flask_wtf import FlaskForm
from wtforms import SelectMultipleField
from flask_bootstrap import Bootstrap
from os.path import join, dirname, realpath
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from datetime import datetime
import io, os
import numpy as np


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

    vectorizer = TfidfVectorizer(stop_words=stopwords, ngram_range=(1, 3))
    features = vectorizer.fit_transform(documents)
    k = int(topics)
    if algorithm == 'kMean':
        model = KMeans(n_clusters=k, init='k-means++', max_iter=int(length), n_init=1)
    model.fit(features)

    # drop joined_col column because we don't need to display it in the result CSV file
    df.drop('joined_col', axis=1, inplace=True)

    # Stemming or Lemmatization; necessary / additive with ngram 1-3 range?
    # not sure here, for lables_ length not equal to np length
    # df['Cluster'] = model.labels_
    df['Cluster'] = model.labels_
    df2 = pd.DataFrame()

    clusters = df.groupby('Cluster')
    # cluster_sum = df.groupby('Cluster').sum()

    # print("Cluster centroids: \n")

    order_centroids = model.cluster_centers_.argsort()[:, ::-1]
    terms = vectorizer.get_feature_names_out()
    for i in range(k):
        subset_df = df[df.Cluster == i].shape[0]

        top_ten_words = [terms[ind] for ind in order_centroids[i, :10]]
        # df2['top_ten_words'] = [terms[ind] for ind in order_centroids[i, :10]]
        # print("Cluster {}: {}".format(i, '; '.join(top_ten_words)))

        data = {'Cluster Number': i, 'Number of Items': subset_df,
                'Top Cluster Terms': top_ten_words}

        df2 = df2.append(data, ignore_index=True)

        # print("Cluster %d:" % i)
        # df2['Cluster Topic Number'] = format(i, '; '.join(top_ten_words))
        # for j in order_centroids[i, :10]:  # print out 10 feature terms of each cluster
        # print(' %s' % terms[j])
        # df2['top_ten_words'] = terms[j]
        # df2 = df2.append({'Top Terms': terms[j]}, ignore_index=True)
        # print('------------')

    # df.append(df2, ignore_index=True)
    df2.head()
    return df2


def sup_cluster(df, form, stopwords_list):
    """
    type df: dataframe
    type form: form
    type stopwords_list: additional stopwords list from stopwords.txt
    rtype: dataframe
    """
    file = form.filename.data
    text = form.columns.data
    algorithm = form.algorithm.data
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
    # stopwords += stopwords_list

    vectorizer = TfidfVectorizer(stop_words=stopwords, ngram_range=(1, 3))
    features = vectorizer.fit_transform(documents)

    k_list = [10, 20, 30]  # define Kmean -10, Kmean-20, Kmean-30
    for k in k_list:
        # cal kmeans cluster
        model = KMeans(n_clusters=k, init='k-means++', n_init=1)
        model.fit(features)
        df['Kmeans_' + str(k)] = model.labels_
        # add pivot dataframe
        df_km = pd.DataFrame()
        for i in range(k):
            # subset_df = df[df.Cluster == i].shape[0]
            subset_df = df.loc[df['Seed'] == '1']
            subset_df = subset_df[subset_df['Kmeans_' + str(k)] == i].shape[0]
            data = {f'Cluster Number(k-{str(k)})': i,
                    f'# of Seeds(k-{str(k)})': subset_df}
            # df_km = df_km.append(data, ignore_index=True)
            df_km = pd.concat([df_km, pd.DataFrame([data])], axis=0, ignore_index=True)

        # sort by # of Seeds
        df_km = df_km.sort_values(by=f'# of Seeds(k-{str(k)})', ascending=False, ignore_index=True)
        # cal seeds percentage
        df_km[f'% of Seeds(k-{str(k)})'] = (df_km[f'# of Seeds(k-{str(k)})'] /
                                            df_km[f'# of Seeds(k-{str(k)})'].sum())
        # set Cumulative percentage
        df_km[f'Cumulative %(k-{str(k)})'] = df_km[f'% of Seeds(k-{str(k)})'].cumsum()
        # cal 'include cluster?'
        # df_km[f'Include Cluster?(k-{str(k)})'] = np.where(df_km[f'Cumulative %(k-{str(k)})'] <= 0.5, 'yes', 'no')
        df_km[f'Include Cluster?(k-{str(k)})'] = np.where(
            df_km[f'Cumulative %(k-{str(k)})'] <= float(threshold), 'yes', 'no')
        df_km[f'Model Score(k-{str(k)})'] = np.where(
            df_km[f'Cumulative %(k-{str(k)})'] <= float(threshold), '1', '0')

        # format with .xx%
        df_km[f'% of Seeds(k-{str(k)})'] = pd.Series(["{0:.2f}%".format(val * 100)
                                                      for val in df_km[f'% of Seeds(k-{str(k)})']], index=df_km.index)
        df_km[f'Cumulative %(k-{str(k)})'] = pd.Series(["{0:.2f}%".format(val * 100)
                                                        for val in df_km[f'Cumulative %(k-{str(k)})']],
                                                       index=df_km.index)

        df_pivot = pd.concat([df_pivot, df_km], axis=1)

        # cal seed capture sheet 1st column, cluster, idea: contact all k-means top clusters
        if not 'Cluster (all models)' in df_seed_capture.columns:
            df_seed_capture['Cluster (all models)'] = df_km[f'Cluster Number(k-{str(k)})']
        else:
            df_seed_capture['Cluster (all models)'] = df_seed_capture['Cluster (all models)'].astype(str) + \
                                                      ',' + df_km[f'Cluster Number(k-{str(k)})'].astype(str)
    # cal Filtered for seeds only Sheet
    df_filter_seeds = df.loc[df['Seed'] == '1', ['Kmeans_10', 'Kmeans_20', 'Kmeans_30']]
    # add  column index for unique determine
    df_filter_seeds.insert(loc=0, column='Index', value=range(1, len(df_filter_seeds) + 1))

    # cal unique
    df_unique_k10, df_unique_k20, df_unique_k30 = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    df_unique = pd.DataFrame(columns=['Seed Capture by model (unique seeds only)'])
    for j in range(k_list[0]):
        df_unique_k10 = df_filter_seeds.loc[df_filter_seeds['Kmeans_10'] ==
                                            df_pivot['Cluster Number(k-10)'][j], ['Index']]
        df_unique_k20 = df_filter_seeds.loc[
            df_filter_seeds['Kmeans_20'] == df_pivot['Cluster Number(k-20)'][j], ['Index']]
        df_unique_k30 = df_filter_seeds.loc[
            df_filter_seeds['Kmeans_30'] == df_pivot['Cluster Number(k-30)'][j], ['Index']]
        # count sum
        data = pd.unique(pd.concat([df_unique_k10, df_unique_k20, df_unique_k30]).values.ravel('K')).shape[0]
        # append recorders to the df
        df_unique = pd.concat([df_unique, pd.DataFrame([[data]], columns=df_unique.columns)], ignore_index=True)
    df_seed_capture = pd.concat([df_seed_capture, df_unique], axis=1)
    # Seed Capture Running total
    df_seed_capture['Seed Capture Running total (unique seeds only)'] = \
        df_seed_capture['Seed Capture by model (unique seeds only)'].cumsum()
    # Cumulative %
    df_seed_capture['Cumulative %'] = (df_seed_capture['Seed Capture Running total (unique seeds only)'] /
                                       df_seed_capture['Seed Capture by model (unique seeds only)'].sum())
    df_seed_capture['Continue or Stop?'] = np.where(
        df_seed_capture['Cumulative %'] <= 0.5, 'Continue', 'Stop')
    # format Cumulative % with percent
    df_seed_capture['Cumulative %'] = pd.Series(["{0:.2f}%".format(val * 100)
                                                 for val in df_seed_capture['Cumulative %']],
                                                index=df_seed_capture.index)

    # cal Ensemble_Score
    # df.loc[df['column_name'] == some_value, [col_name1, col_name2]]
    df_top_cluster = df_seed_capture.loc[df_seed_capture['Continue or Stop?'] == 'Continue',
                                         ['Cluster (all models)']]

    # add the first stop row
    row_first_stop = df_seed_capture.iloc[df_seed_capture['Continue or Stop?'].eq('Stop').idxmax(), 0]
    data = {'Cluster (all models)': row_first_stop}
    df_top_cluster = pd.concat([df_top_cluster, pd.DataFrame([data])], axis=0, ignore_index=True)

    # define a dictionary to save the top cluster
    dict_top_cluster = {}
    # split top cluster, like 6,5,24  -> 3 columns: 6    5   24
    df_top_cluster = df_top_cluster['Cluster (all models)'].str.split(pat=',', n=-1, expand=True)
    i_index = 0
    df['Ensemble_Score'] = 0
    for k in k_list:
        dict_top_cluster['Kmeans_' + str(k)] = df_top_cluster[i_index].astype(int).tolist()
        i_index += 1
        # cal every Kmeans if it is included in the top cluster
        df['Ensemble_Score'] += \
            df['Kmeans_' + str(k)].apply(lambda x: 1 if x in dict_top_cluster['Kmeans_' + str(k)] else 0)
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
