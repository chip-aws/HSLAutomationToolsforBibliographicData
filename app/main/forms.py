from flask_pagedown.fields import PageDownField
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, IntegerField, TextAreaField, \
    SelectMultipleField, widgets, FloatField
from wtforms.validators import DataRequired, Length, Email, EqualTo, NumberRange
from flask_wtf.file import FileField, FileAllowed, FileRequired
from werkzeug.utils import secure_filename
from flask import Markup


class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')


class UploadRisForm(FlaskForm):
    file = FileField('file', validators=[
        FileRequired(),
        FileAllowed(['ris'], 'RIS file only!')
    ])
    submit = SubmitField('Submit')


class Ris2CsvDownloadForm(FlaskForm):
    submit = SubmitField('Submit')


class UploadCsvForm(FlaskForm):
    file = FileField('file', validators=[
        FileRequired(),
        FileAllowed(['csv'], 'csv file only!')
    ])
    submit = SubmitField('Submit')


class Csv2RisDownloadForm(FlaskForm):
    submit = SubmitField('Submit')


class UploadClusterForm(FlaskForm):
    file = FileField('file', validators=[
        FileRequired(),
        FileAllowed(['csv', 'ris'], 'csv or ris files only!')
    ])
    submit = SubmitField('Submit')


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class ClusterTextForm(FlaskForm):
    check_options = MultiCheckboxField()
    submit = SubmitField("Submit")


class ClusterAlgoForm(FlaskForm):
    columns = StringField()
    label_for_algorithm = Markup('<span style="color: firebrick;">*</span> Clustering Algorithm:')
    algorithm = SelectField(label_for_algorithm,
                            choices=[('kMean', 'kMean'), ('NMF', 'NMF'), ('LDA', 'LDA')],
                            validate_choice=False)

    label_for_topics = Markup('<span style="color: firebrick;">*</span> Desired Number of Topics:')
    topics = IntegerField(label_for_topics, validators=[
        DataRequired(),
        NumberRange(min=10, max=20, message='topic is between 10 and 20')
    ], default=10)

    label_for_length = Markup('<span style="color: firebrick;">*</span> Maximum Phrase Length:')
    length = IntegerField(label_for_length, validators=[
        DataRequired(),
        NumberRange(min=1, max=3, message='length is between 1 and 3')
    ], default=1)

    stopwords = TextAreaField('Stopwords:', default='copyright, publication, abstract')
    submit = SubmitField('Submit')


class ClusterPreForm(FlaskForm):
    filename = StringField()
    columns = StringField()
    algorithm = StringField()
    topics = StringField()
    length = StringField()
    stopwords = StringField()
    submit = SubmitField('Submit')


class ClusterResultForm(FlaskForm):
    filename = StringField()
    columns = StringField()
    algorithm = StringField()
    topics = StringField()
    length = StringField()
    stopwords = StringField()
    outputfile = StringField()

    submit = SubmitField('Submit')


class UploadSupClusterForm(FlaskForm):
    file = FileField('file', validators=[
        FileRequired(),
        FileAllowed(['csv', 'ris'], 'CSV or RIS files only!')
    ])
    submit = SubmitField('Submit')


class SupClusterTextForm(FlaskForm):
    check_options = MultiCheckboxField()
    label_for_seeds = Markup('<span style="color: firebrick;">*</span> Seed Location::')
    seeds = SelectField(label_for_seeds,
                       choices=[],
                       validate_choice=False)
    submit = SubmitField("Submit")


class SupClusterAlgoForm(FlaskForm):
    columns = StringField()
    seeds = StringField()

    label_for_algorithm = Markup('<span style="color: firebrick;">*</span> Clustering Algorithm:')
    algorithm = SelectField(label_for_algorithm,
                            choices=[('kMean', 'kMean'), ('NMF', 'NMF'), ('LDA', 'LDA')],
                            validate_choice=False)

    label_for_threshold = Markup('<span style="color: firebrick;">*</span> Desired Recall Threshold:')
    threshold = FloatField(label_for_threshold, validators=[
        DataRequired(),
        NumberRange(min=0.75, max=0.92, message='Values must be between 0.75 and 0.92')
    ], default=0.9)

    stopwords = TextAreaField('Stopwords:', default='copyright, publication, abstract')
    label_for_output_type = Markup('<span style="color: firebrick;">*</span>  Output Type::')
    output_type = SelectField(label_for_output_type,
                            choices=[('Ensemble Only', 'Ensemble')],
                            validate_choice=False)
    submit = SubmitField('Submit')


class SupClusterPreForm(FlaskForm):
    filename = StringField()
    columns = StringField()
    seeds = StringField()
    algorithm = StringField()
    threshold = StringField()
    stopwords = StringField()
    output_type = StringField()
    submit = SubmitField('Submit')


class SupClusterResultForm(FlaskForm):
    filename = StringField()
    columns = StringField()
    seeds = StringField()
    # algorithm = StringField()
    threshold = StringField()
    # length = StringField()
    stopwords = StringField()
    output_type = StringField()
    outputfile = StringField()

    submit = SubmitField('Submit')


"""
            form.filename.data = filename
            form.columns.data = formdata["columns"]
            form.seeds.data = formdata["seeds"]
            form.algorithm.data = formdata["algorithm"]
            form.threshold.data = formdata["threshold"]
            form.stopwords.data = formdata["stopwords"]
            form.output_type.data = formdata["output_type"]
            form.outputfile.data = output_file
"""