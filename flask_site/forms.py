from flask_wtf import FlaskForm
from wtforms import validators
from wtforms import StringField, PasswordField, SelectField, TextAreaField

class LoginForm(FlaskForm):
    username = StringField('Username', [validators.Length(min=4, max=20), validators.InputRequired()])
    password = PasswordField('Password', [validators.Length(min=10), validators.InputRequired()])


class RegisterForm(FlaskForm):
    username = StringField('Username', [validators.Length(min=4, max=20), validators.InputRequired()])
    password = PasswordField('Password', [validators.Length(min=10), validators.InputRequired(),
                                          validators.EqualTo('password2', message='Passwords must match')])
    password2 = PasswordField('Repeat Password', [validators.Length(min=10), validators.InputRequired()])

class ArgumentForm(FlaskForm):
    title = StringField('Title', [validators.Length(min=1, max=100), validators.InputRequired()])
    content = TextAreaField('Description', [validators.Length(min=1, max=500), validators.InputRequired()])

class PremiseForm(FlaskForm):
    title = StringField('Title', [validators.Length(min=1, max=100), validators.InputRequired()])
    content = TextAreaField('Description', [validators.Length(min=1, max=500), validators.InputRequired()])
    argument = SelectField('Argument', coerce=int, validators=[validators.Optional()])

class ConclusionForm(FlaskForm):
    title = StringField('Title', [validators.Length(min=1, max=100), validators.InputRequired()])
    content = TextAreaField('Description', [validators.Length(min=1, max=500), validators.InputRequired()])
    argument = SelectField('Argument', coerce=int, validators=[validators.Optional()])

class ConnectionForm(FlaskForm):
    argument = SelectField('Connect to Argument', coerce=int, validators=[validators.InputRequired()])
    category = SelectField('Select Premise or Conclusion', validators=[validators.InputRequired()])
    connection = SelectField('Select', validators=[validators.InputRequired()])
