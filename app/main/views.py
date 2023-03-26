# application routes in main blueprint

"""
The from . import <some-module> syntax is used in Python to represent relative imports.
The . in this statement represents the current package.
You are going to see another very useful relative import soon that uses the form
from .. import <some-module>, where .. represents the parent of the current package.

"""
import os
from config import Config
from datetime import datetime
from time import gmtime, strftime
from flask import render_template, session, redirect, url_for, Flask, flash, request, \
    redirect, Response, send_file, send_from_directory
from flask_bootstrap import Bootstrap
from werkzeug.utils import secure_filename
from werkzeug.datastructures import MultiDict
import pandas as pd
from pandas import ExcelWriter
from . import main
from .forms import NameForm, UploadRisForm, Ris2CsvDownloadForm, UploadCsvForm, Csv2RisDownloadForm, \
    UploadClusterForm, ClusterTextForm, ClusterAlgoForm, ClusterPreForm, ClusterResultForm, UploadSupClusterForm, \
    SupClusterTextForm, SupClusterAlgoForm, SupClusterPreForm, SupClusterResultForm

from .. import ris, ml

# define globe variable df
df, sup_cluster_df = pd.DataFrame(), pd.DataFrame()


@main.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        # ...
        return redirect(url_for('.index'))
    return render_template('index.html',
                           form=form, name=session.get('name'),
                           known=session.get('known', False),
                           current_time=datetime.utcnow())

@main.route('/about', methods=['GET', 'POST'])
def about():
    form = NameForm()
    if form.validate_on_submit():
        # ...
        return redirect(url_for('.about'))
    return render_template('about.html',
                           form=form, name=session.get('name'),
                           known=session.get('known', False),
                           current_time=datetime.utcnow())



# 1-------------------------Unsupervised Clustering-------------------------
# step 1: select an input file
@main.route('/cluster_select_file', methods=['GET', 'POST'])
def cluster_select_file():
    this_form = UploadClusterForm()
    if this_form.validate_on_submit():
        f = this_form.file.data
        filename = secure_filename(f.filename)
        f.save(os.path.join(Config.UPLOAD_FOLDER, filename))
        # flash('Your file has been uploaded.')
        return redirect(url_for('.cluster_select_text', filename=filename))

    return render_template('cluster_select_file.html', form=this_form)


# step 2: select text
@main.route('/cluster_select_text/<filename>', methods=['GET', 'POST'])
def cluster_select_text(filename):
    # define globle variable df
    global df
    # display the data table from csv or ris
    if not filename is None and filename != "":
        upload_full_path_file = os.path.join(Config.UPLOAD_FOLDER, filename)
        if filename.endswith('ris'):
            df = ris.ris2csv(upload_full_path_file)
        elif filename.endswith('csv'):
            # fix bug caused by encoded error, Feb 5,2023
            # df = pd.read_csv(upload_full_path_file, keep_default_na=False)
            df = pd.read_csv(upload_full_path_file,
                             encoding = "utf-8",
                             encoding_errors ='ignore',
                             engine = 'python',
                             keep_default_na = False)
        else:
            return redirect(url_for('.cluster_select_file'))
    else:
        return redirect(url_for('.cluster_select_file'))

    total_length = len(df)
    heading = df.head(0).to_string().split("\n")
    heading = heading[1].replace("Columns: ", "").replace('[', '').replace(']', '')
    heading = heading.split(', ')
    # get first 5 rows of records
    array = df.head(5).to_dict(orient='records')

    form = ClusterTextForm()
    form.check_options.choices = heading
    if request.method == 'GET':
        formdata = session.get('formdata', None)  # formdate is dictionary
        if formdata:
            form.filename.data = filename
            # this_form.columns.data = formdata["columns"]
            # initial checkbox choices
            form.check_options.choices = heading

    if form.validate_on_submit():
        # transfer checkbox options
        # columns = form.check_options.data  # return list
        # columns = ','.join(map(str, columns))  # convert list to string
        # return redirect(url_for('.cluster_select_algo', filename=filename, columns=columns))
        session['formdata'] = request.form
        return redirect(url_for('.cluster_select_algo', filename=filename))

    return render_template('cluster_select_text.html', form=form, filename=filename,
                           length=total_length, heading=heading, array=array)


# step 3: select algo
# fix bug: if columns includes /, it will cause parase error
# @main.route('/cluster_select_algo/<filename>/<columns>', methods=['GET', 'POST'])
@main.route('/cluster_select_algo/<filename>', methods=['GET', 'POST'])
def cluster_select_algo(filename):
    # this_form = ClusterAlgoForm()
    # this_form.columns.data = columns
    form = ClusterAlgoForm()
    if request.method == 'GET':
        formdata = session.get('formdata', None)  # formdate is dictionary
        # bug: select cols will lose /
        if formdata:
            form.filename.data = filename
            form.columns.data = formdata["check_options"]

    if form.validate_on_submit():
        session['formdata'] = request.form
        return redirect(url_for('.cluster_preview', filename=filename))

    return render_template('cluster_select_algo.html', form=form)


# step 4: preview input parameters before running unsupervised clustering algorithm
@main.route('/cluster_preview/<filename>', methods=['GET', 'POST'])
def cluster_preview(filename):
    form = ClusterPreForm()

    if request.method == 'GET':
        formdata = session.get('formdata', None)  # formdate is dictionary
        if formdata:
            form.filename.data = filename
            form.columns.data = formdata["columns"]
            form.algorithm.data = formdata["algorithm"]
            form.topics.data = formdata["topics"]
            form.length.data = formdata["length"]
            form.stopwords.data = formdata["stopwords"]
    if form.validate_on_submit():
        session['formdata'] = request.form
        return redirect(url_for('.cluster_result', filename=filename))
    return render_template('cluster_preview.html', form=form)


# step 5: generate the analysed result
@main.route('/cluster_result/<filename>', methods=['GET', 'POST'])
def cluster_result(filename):
    form = ClusterResultForm()
    # write the analysis result to result/***.csv file

    if form.validate_on_submit():
        return redirect(url_for('.download_file', filename=form.outputfile.data))

    now = datetime.utcnow()
    timestr = now.strftime("%Y%m%d-%H%M%S")

    output_file = str(timestr) + '.csv'
    output_file_full_path = os.path.join(Config.DOWNLOAD_FOLDER, output_file)

    if request.method == 'GET':
        formdata = session.get('formdata', None)  # formdate is dictionary
        if formdata:
            form.filename.data = filename
            form.columns.data = formdata["columns"]
            form.algorithm.data = formdata["algorithm"]
            form.topics.data = formdata["topics"]
            form.length.data = formdata["length"]
            form.stopwords.data = formdata["stopwords"]
            form.outputfile.data = output_file
    # call ml_cluster algorithm  -----------
    # filename_full_path = os.path.join(Config.UPLOAD_FOLDER, filename)
    # deal with additional stopwords.txt
    # url_for('templates', filename='css/button_nav.css')
    stopwords_list = list()
    """
    stopwords_file = render_template('stopwords.txt')
    for line in stopwords_file:
        # use append method to add stopwords list
        stopwords_list.append(line.strip())
    """
    # call machine learning cluster algothrim
    df2 = ml.ml_cluster(df, form, stopwords_list)

    result = pd.concat([df, df2], axis=1)

    f = open(output_file_full_path, 'w')  # create csv file
    f.write(result.to_csv(index=False))  # set index to id
    f.close()

    # job_time = now.strftime("%Y-%m-%d %H:%M %I")
    job_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    return render_template('cluster_result.html', form=form, tables=[df2.to_html(classes='data', index=False)],
                           filename=filename, job_time=job_time)


# 2-------------------------RIS to CSV Route:-------------------------
@main.route('/ris_to_csv', methods=['GET', 'POST'])
def ris_to_csv():
    # upload_file = request.files.get('file')
    # add form as parameter
    this_form = UploadRisForm()
    if this_form.validate_on_submit():
        f = this_form.file.data
        filename = secure_filename(f.filename)
        f.save(os.path.join(Config.UPLOAD_FOLDER, filename))
        flash('Your file has been uploaded.')
        return redirect(url_for('.ris_to_csv_preview', filename=filename))

    return render_template('ris_to_csv_file_upload.html', form=this_form)


# ris to CSV preview page
@main.route('/ris_to_csv_preview/<filename>', methods=['GET', 'POST'])
def ris_to_csv_preview(filename):
    # this_form = RisForm()
    flash(filename + ' file has been uploaded successfully.')
    # df = ris2csv.convert_ris_pd_df(file)
    df = ris.ris2csv(filename)
    # df = url_for('api.convert_ris_pd_df', file=filename)

    # try to output Excel file instead of CSV because some field, like AU, AB maybe exceed CSV cell limitation
    """
    output_file_name = filename.replace('.ris', '') + '.csv'
    output_full_path_file = os.path.join(Config.DOWNLOAD_FOLDER, output_file_name)
    # df.to_csv(output_full_path_file, index=False)   # for non utf-8 encoding will occure bug
    df.to_csv(output_full_path_file, index=False, encoding='utf-8-sig')
    """
    # Auto-adjust columns' width
    # writer = pd.ExcelWriter(filename, engine='xlsxwriter')
    output_file_name = filename.replace('.ris', '')  + '.xlsx'
    output_file_full_path = os.path.join(Config.DOWNLOAD_FOLDER, output_file_name)
    writer = pd.ExcelWriter(output_file_full_path, engine='xlsxwriter')
    # Given a dict of dataframes

    dfs = {filename.replace('.ris', ''): df}

    for sheetname, df in dfs.items():  # loop through `dict` of dataframes
        df.to_excel(writer, sheet_name=sheetname, index=False, encoding='utf-8-sig')  # send df to writer
        worksheet = writer.sheets[sheetname]  # pull worksheet object
        for idx, col in enumerate(df):  # loop through all columns
            series = df[col]
            max_len = max((
                # len of the largest item of Seeds
                20 if series.astype(str).map(len).max() > 20 else series.astype(str).map(len).max(),
                len(str(series.name))  # len of column name/header
            )) + 1  # adding a little extra space
            worksheet.set_column(idx, idx, max_len)  # set column width
    writer.save()

    # add transfer parameter: length heading, array
    total_length = len(df)
    heading = df.head(0).to_string().split("\n")
    heading = heading[1].replace("Columns: ", "").replace('[', '').replace(']', '')
    heading = heading.split(', ')
    # get first 5 rows of recorders
    array = df.head(5).to_dict(orient='records')

    form = Ris2CsvDownloadForm()
    if form.validate_on_submit():
        flash('Your file has been downloaded.')
        return redirect(url_for('.download_file', filename=output_file_name))

    return render_template('ris_to_csv_preview.html', form=form, filename=filename,
                           length=total_length, heading=heading, array=array)


# download file
@main.route('/download_file/<filename>', methods=['GET', 'POST'])
def download_file(filename):
    file = os.path.join(Config.DOWNLOAD_FOLDER, filename)
    try:
        with open(file) as fp:  # download csv file
            csv = fp.read()
    except:
        with open(file, 'rb') as fp:  # download other than csv file, like xlsx file
            csv = fp.read()
    return Response(csv,
                    headers={"Content-disposition": "attachment; filename=" + filename})


# 3-------------------------CSV to RIS Route:-------------------------
@main.route('/csv_to_ris', methods=['GET', 'POST'])
def csv_to_ris():
    # upload_file = request.files.get('file')
    # add form as parameter
    this_form = UploadCsvForm()
    if this_form.validate_on_submit():
        f = this_form.file.data
        filename = secure_filename(f.filename)
        f.save(os.path.join(Config.UPLOAD_FOLDER, filename))
        flash('Your file has been uploaded.')
        return redirect(url_for('.csv_to_ris_preview', filename=filename))

    return render_template('csv_to_ris_file_upload.html', form=this_form)


# csv to ris preview page
@main.route('/csv_to_ris_preview/<filename>', methods=['GET', 'POST'])
def csv_to_ris_preview(filename):
    # this_form = RisForm()
    flash(filename + ' file has been uploaded successfully.')

    upload_full_path_file = os.path.join(Config.UPLOAD_FOLDER, filename)
    output_file_name = filename.replace('.csv', '') + '.ris'
    output_full_path_file = os.path.join(Config.DOWNLOAD_FOLDER, output_file_name)

    df = pd.read_csv(upload_full_path_file, keep_default_na=False)
    ris.csv2ris(df, output_full_path_file)

    # add transfer parameter: length heading, array
    total_length = len(df)
    heading = df.head(0).to_string().split("\n")
    heading = heading[1].replace("Columns: ", "").replace('[', '').replace(']', '')
    heading = heading.split(', ')
    # get first 5 rows of recorders
    array = df.head(5).to_dict(orient='records')

    form = Ris2CsvDownloadForm()
    if form.validate_on_submit():
        flash('Your file has been downloaded.')
        return redirect(url_for('.download_file', filename=output_file_name))

    return render_template('csv_to_ris_preview.html', form=form, filename=filename,
                           length=total_length, heading=heading, array=array)


# 4-------------------------Supervised Clustering-------------------------
# step 1: select an input file
@main.route('/sup_cluster_select_file', methods=['GET', 'POST'])
def sup_cluster_select_file():
    this_form = UploadSupClusterForm()
    if this_form.validate_on_submit():
        f = this_form.file.data
        filename = secure_filename(f.filename)
        f.save(os.path.join(Config.UPLOAD_FOLDER, filename))
        # flash('Your file has been uploaded.')
        return redirect(url_for('.sup_cluster_select_text', filename=filename))

    return render_template('sup_cluster_select_file.html', form=this_form)


# step 2: select text
@main.route('/sup_cluster_select_text/<filename>', methods=['GET', 'POST'])
def sup_cluster_select_text(filename):
    # define globle variable df
    global sup_cluster_df
    # display the data table from csv or ris
    if not filename is None and filename != "":
        upload_full_path_file = os.path.join(Config.UPLOAD_FOLDER, filename)
        if filename.endswith('ris'):
            sup_cluster_df = ris.ris2csv(upload_full_path_file)
        elif filename.endswith('csv'):
            sup_cluster_df = pd.read_csv(upload_full_path_file, keep_default_na=False)
        else:
            return redirect(url_for('.sup_cluster_select_file'))
    else:
        return redirect(url_for('.sup_cluster_select_file'))

    total_length = len(sup_cluster_df)
    heading = sup_cluster_df.head(0).to_string().split("\n")
    heading = heading[1].replace("Columns: ", "").replace('[', '').replace(']', '')
    heading = heading.split(', ')
    # get first 5 rows of records
    array = sup_cluster_df.head(5).to_dict(orient='records')

    this_form = SupClusterTextForm()
    this_form.AN.choices = heading    # add AN col as unique key
    # initial checkbox choices
    this_form.check_options.choices = heading
    this_form.seeds.choices = heading

    if this_form.validate_on_submit():
        # transfer checkbox options
        columns = this_form.check_options.data  # return list
        columns = ','.join(map(str, columns))  # convert list to string
        AN = str(this_form.AN.data)
        seeds = str(this_form.seeds.data)
        return redirect(url_for('.sup_cluster_select_algo', filename=filename, AN=AN, columns=columns, seeds=seeds))

    return render_template('sup_cluster_select_text.html', form=this_form, filename=filename,
                           length=total_length, heading=heading, array=array)


# step 3: select algo
@main.route('/sup_cluster_select_algo/<filename>/<AN>/<columns>/<seeds>', methods=['GET', 'POST'])
def sup_cluster_select_algo(filename, AN, columns, seeds):
    this_form = SupClusterAlgoForm()
    this_form.AN.data = AN
    this_form.columns.data = columns
    this_form.seeds.data = seeds

    if this_form.validate_on_submit():
        session['formdata'] = request.form
        return redirect(url_for('.sup_cluster_preview', filename=filename))

    return render_template('sup_cluster_select_algo.html', form=this_form)


# step 4: preview input parameters before running unsupervised clustering algorithm
@main.route('/sup_cluster_preview/<filename>', methods=['GET', 'POST'])
def sup_cluster_preview(filename):
    form = SupClusterPreForm()

    if request.method == 'GET':
        formdata = session.get('formdata', None)  # formdate is dictionary
        if formdata:
            form.filename.data = filename
            form.AN.data = formdata["AN"]
            form.columns.data = formdata["columns"]
            form.seeds.data = formdata["seeds"]
            # form.algorithm.data = formdata["algorithm"]
            form.threshold.data = formdata["threshold"]

            # form.length.data = formdata["length"]
            form.stopwords.data = formdata["stopwords"]
            form.output_type.data = formdata["output_type"]
            # form = ClusterPreForm(MultiDict(formdata))
            # form.validate()
            # session.pop('formdata')
            # return render_template('cluster_preview.html', form=form)
    if form.validate_on_submit():
        session['formdata'] = request.form
        return redirect(url_for('.sup_cluster_result', filename=filename))
    return render_template('sup_cluster_preview.html', form=form)


# step 5: generate the analysed result
@main.route('/sup_cluster_result/<filename>', methods=['GET', 'POST'])
def sup_cluster_result(filename):
    form = SupClusterResultForm()
    # write the analysis result to result/***.csv file

    if form.validate_on_submit():
        return redirect(url_for('.download_file', filename=form.outputfile.data))

    now = datetime.utcnow()
    timestr = now.strftime("%Y%m%d-%H%M%S")

    output_file = str(timestr) + '.xlsx'
    output_file_full_path = os.path.join(Config.DOWNLOAD_FOLDER, output_file)

    if request.method == 'GET':
        formdata = session.get('formdata', None)  # formdate is dictionary
        if formdata:
            form.filename.data = filename
            form.AN.data = formdata["AN"]
            form.columns.data = formdata["columns"]
            form.seeds.data = formdata["seeds"]
            # form.algorithm.data = formdata["algorithm"]
            form.threshold.data = formdata["threshold"]
            form.stopwords.data = formdata["stopwords"]
            form.output_type.data = formdata["output_type"]
            form.outputfile.data = output_file
    # call ml_cluster algorithm  -----------
    # filename_full_path = os.path.join(Config.UPLOAD_FOLDER, filename)
    # deal with additional stopwords.txt
    # url_for('templates', filename='css/button_nav.css')
    stopwords_list = list()
    """
    stopwords_file = render_template('stopwords.txt')
    for line in stopwords_file:
        # use append method to add stopwords list
        stopwords_list.append(line.strip())
    """
    # call machine learning cluster algorithm
    df2, df2_filter_seed, df2_pivot, df2_seed_capture = ml.sup_cluster(sup_cluster_df, form, stopwords_list)

    # Auto-adjust columns' width
    # writer = pd.ExcelWriter(filename, engine='xlsxwriter')
    writer = pd.ExcelWriter(output_file_full_path, engine='xlsxwriter')
    # Given a dict of dataframes

    dfs = {'Supervised Clustering': df2,
           'Filtered for Seeds only': df2_filter_seed,
           'Pivot Tables': df2_pivot,
           'Seed Capture': df2_seed_capture}

    for sheetname, df in dfs.items():  # loop through `dict` of dataframes
        df.to_excel(writer, sheet_name=sheetname, index=False)  # send df to writer
        worksheet = writer.sheets[sheetname]  # pull worksheet object
        for idx, col in enumerate(df):  # loop through all columns
            series = df[col]
            max_len = max((
                # len of the largest item of Seeds
                50 if series.astype(str).map(len).max() > 50 else series.astype(str).map(len).max(),
                len(str(series.name))  # len of column name/header
            )) + 1  # adding a little extra space
            worksheet.set_column(idx, idx, max_len)  # set column width
    writer.save()

    job_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())

    heading = df2.head(0).to_string().split("\n")
    heading = heading[1].replace("Columns: ", "").replace('[', '').replace(']', '')
    heading = heading.split(', ')
    array = df2.head(10).to_dict(orient='records')

    return render_template('sup_cluster_result.html', form=form, heading=heading,
                           array=array, filename=filename, job_time=job_time)
