from flask_pagedown.fields import PageDownField
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, IntegerField, TextAreaField
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


class ClusterTextForm(FlaskForm):
    submit = SubmitField('Submit')


class ClusterAlgoForm(FlaskForm):
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

    stopwords = TextAreaField('Stopwords:')
    submit = SubmitField('Submit')


class ClusterPreForm(FlaskForm):
    submit = SubmitField('Submit')
