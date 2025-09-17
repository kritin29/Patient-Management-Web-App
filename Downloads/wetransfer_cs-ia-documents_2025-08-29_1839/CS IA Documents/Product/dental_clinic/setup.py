from flask_login import UserMixin
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import (
    StringField, PasswordField, SubmitField, SelectField, 
    IntegerField, TextAreaField, DateField, TimeField
)
from wtforms.validators import (
    DataRequired, Length, Email, EqualTo, ValidationError, NumberRange
)

from dental_clinic import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    patient = db.relationship('Patient', backref='author', lazy=True)
    username = db.Column(db.String(16), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"User('{self.username}, '{self.email}')"

class Patient(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(16), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(16), nullable=False)
    diagnosis = db.Column(db.Text)
    pictures = db.relationship('Picture', backref='patient', lazy=True)

class Picture(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    image_data = db.Column(db.LargeBinary, nullable=False)
    image_type = db.Column(db.String(10), nullable=False)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    patient = db.relationship('Patient', backref='appointments', lazy=True)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)


class SignUpForm(FlaskForm):
    username = StringField('Enter Username', validators=[DataRequired(), Length(min=4, max=16)])
    email = StringField('Enter Email', validators=[DataRequired(), Email()])
    password = PasswordField('Enter Password', validators=[DataRequired(), Length(min=8, max=32)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        if User.query.filter_by(username=username.data).first():
            raise ValidationError('That username is already taken. Try Again.')

    def validate_email(self, email):
        if User.query.filter_by(email=email.data).first():
            raise ValidationError('That email is already taken. Try Again.')

class SignInForm(FlaskForm):
    email = StringField('Enter Email', validators=[DataRequired(), Email()])
    password = PasswordField('Enter Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class AddPatientForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=50)])
    gender = SelectField('Gender', choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], validators=[DataRequired()])
    age = IntegerField('Age', validators=[DataRequired(), NumberRange(min=0, max=150)])
    diagnosis = TextAreaField('Enter Diagnosis')
    submit = SubmitField('Add Patient')

class UpdateDiagnosisForm(FlaskForm):
    diagnosis = TextAreaField('Update Diagnosis', validators=[DataRequired()])
    submit = SubmitField('Submit')

class AddPictureForm(FlaskForm):        
    def __init__(self, *args, **kwargs):
        super(AddPictureForm, self).__init__(*args, **kwargs)
        self.patient_id.choices = [(patient.id, patient.name) for patient in Patient.query.all()]

    patient_id = SelectField('Patient', validators=[DataRequired()])
    picture = FileField('Picture', validators=[FileRequired(), FileAllowed(['jpg', 'jpeg', 'png'], 'Only images can be uploaded')])
    submit = SubmitField('Submit')

class AppointmentForm(FlaskForm):        
    def __init__(self, *args, **kwargs):
        super(AppointmentForm, self).__init__(*args, **kwargs)
        self.patient_id.choices = [(patient.id, patient.name) for patient in Patient.query.all()]

    patient_id = SelectField('Patient', validators=[DataRequired()])
    date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()])
    start_time = TimeField('Start Time', format='%H:%M', validators=[DataRequired()])
    end_time = TimeField('End Time', format='%H:%M', validators=[DataRequired()])
    submit = SubmitField('Submit')

class UpdateAppointmentForm(FlaskForm):
    date = DateField('Updated Date:', format='%Y-%m-%d', validators=[DataRequired()])
    start_time = TimeField('Updated Start Time:', format='%H:%M', validators=[DataRequired()])
    end_time = TimeField('Updated End Time:', format='%H:%M', validators=[DataRequired()])
    submit = SubmitField('Update')