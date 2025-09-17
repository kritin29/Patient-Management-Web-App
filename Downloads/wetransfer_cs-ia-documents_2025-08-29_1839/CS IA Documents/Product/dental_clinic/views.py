from datetime import datetime, date
from io import BytesIO
import os

from flask import render_template, url_for, flash, redirect, request, send_file, session
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.utils import secure_filename
from sqlalchemy import or_

from dental_clinic import app, db, bcrypt
from dental_clinic.setup import (
    User, Patient, Picture, Appointment, SignUpForm, SignInForm, AddPatientForm, 
    UpdateDiagnosisForm, AddPictureForm, AppointmentForm, UpdateAppointmentForm
)
from dental_clinic.auth import generate_otp, send_otp_email


@app.route('/', methods=['POST', 'GET'])
@login_required
def home():
    num_patients = len(Patient.query.all())
    num_appointments = len(Appointment.query.all())
    appointments_for_today = Appointment.query.filter_by(date=date.today()).all()
    return render_template('dashboard.html', num_patients=num_patients, 
                           num_appointments=num_appointments, appointments_for_today=appointments_for_today)


@app.route('/patients/view', methods=['POST', 'GET'])
@login_required
def view_patients():
    patients = Patient.query.all()
    search_term = request.args.get('search')
    if search_term:
        patients = Patient.query.filter(or_(Patient.name.ilike(f"%{search_term}%"),
                                       Patient.gender.ilike(f"%{search_term}%"),
                                       Patient.age.ilike(f"%{search_term}%"))).all()
    else:
        search_term = ""

    return render_template('patients/view.html', patients=patients)


@app.route('/patients/add', methods=['POST', 'GET'])
@login_required
def add_patient():
    form = AddPatientForm()
    if form.validate_on_submit():
        patient = Patient(name=form.name.data, gender=form.gender.data, age=form.age.data, diagnosis=form.diagnosis.data, author=current_user)
        db.session.add(patient)
        db.session.commit()
        flash(f'Patient "{form.name.data}" was added', 'success')
        return redirect(url_for('view_patients'))
    return render_template('patients/add.html', form=form)


@app.route('/patients/<int:patient_id>/pictures/view', methods=['POST', 'GET'])
@login_required
def view_pictures(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    return render_template('/patients/pictures/view.html', pictures=patient.pictures, patient=patient)


@app.route('/patients/pictures/add', methods=['POST', 'GET'])
@login_required
def add_picture():
    form = AddPictureForm()
    if form.validate_on_submit():
        print(form.picture.data)
        new_picture = Picture(patient_id=form.patient_id.data, image_data=form.picture.data.read(), image_type=os.path.splitext(secure_filename(form.picture.data.filename))[1])
        patient = Patient.query.get_or_404(form.patient_id.data).name
        db.session.add(new_picture)
        db.session.commit()
        flash(f'The image has been successfully added for patient "{patient}"', 'success')
        return redirect(url_for('view_pictures', patient_id=form.patient_id.data))
    return render_template('/patients/pictures/add.html', form=form)


@app.route('/pictures/<int:picture_id>')
@login_required
def retrieve_picture(picture_id):
    picture = Picture.query.get_or_404(picture_id)
    return send_file(BytesIO(picture.image_data), mimetype=f'image/{picture.image_type}')


@app.route('/patients/<int:patient_id>/diagnosis', methods=['POST', 'GET'])
@login_required
def update_diagnosis(patient_id):
    patient_info = Patient.query.get_or_404(patient_id)
    form = UpdateDiagnosisForm()

    if form.validate_on_submit():
        patient_info.diagnosis = form.diagnosis.data
        flash(f'Diagnosis for patient "{patient_info.name}" was updated', 'success')
        db.session.commit()
        return redirect(url_for('view_patients'))

    return render_template('/patients/diagnosis.html', patient_info=patient_info, form=form)


@app.route('/appointments/add', methods=['POST', 'GET'])
@login_required
def add_appointment():
    form = AppointmentForm()

    if form.validate_on_submit():
        patient_id = form.patient_id.data
        date = form.date.data
        start_time = form.start_time.data
        end_time = form.end_time.data

        existing_appointments = Appointment.query.filter_by(date=date).all()

        for appointment in existing_appointments:
            appointment_start = datetime.combine(datetime.today(), appointment.start_time)
            appointment_end = datetime.combine(datetime.today(), appointment.end_time)
            input_start = datetime.combine(datetime.today(), start_time)
            input_end = datetime.combine(datetime.today(), end_time)

            if input_start < appointment_end and input_end > appointment_start:
                flash('There is already an appointment scheduled at that time. Please choose another time.', 'danger')
                return redirect(url_for('add_appointment'))

        new_appointment = Appointment(patient_id=patient_id, date=date, start_time=start_time, end_time=end_time)
        db.session.add(new_appointment)
        db.session.commit()

        flash('Appointment created successfully', 'success')
        return redirect(url_for('view_appointments'))

    return render_template('/appointments/add.html', form=form)


@app.route('/appointments/view', methods=['POST', 'GET'])
@login_required
def view_appointments():
    appointments = Appointment.query.all()
    search_term = request.args.get('search')
    if search_term:
        appointments = Appointment.query.filter(Appointment.date.ilike(f"%{search_term}%")).all()
    else:
        search_term = ""

    return render_template('/appointments/view.html', appointments=appointments, Patient=Patient)


@app.route('/appointments/<int:appointment_id>/update', methods=['POST', 'GET'])
@login_required
def update_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    form = UpdateAppointmentForm()
    patient = Patient.query.get_or_404(appointment.patient_id).name

    if form.validate_on_submit():
        existing_appointments = Appointment.query.filter_by(date=form.date.data).all()

        for exiting_appointment in existing_appointments:
            appointment_start = datetime.combine(datetime.today(), exiting_appointment.start_time)
            appointment_end = datetime.combine(datetime.today(), exiting_appointment.end_time)
            input_start = datetime.combine(datetime.today(), form.start_time.data)
            input_end = datetime.combine(datetime.today(), form.end_time.data)

            if input_start < appointment_end and input_end > appointment_start:
                flash('There is already an appointment scheduled at that time. Please choose another time.', 'danger')
                return redirect(url_for('update_appointment', appointment_id=appointment_id))
        else:
            appointment.date = form.date.data
            appointment.start_time = form.start_time.data
            appointment.end_time = form.end_time.data
            db.session.commit()

        flash(f'Appointment for patient "{patient}" was updated', 'success')

        return redirect(url_for('view_appointments'))
    return render_template('/appointments/update.html', form=form, patient=patient, appointment=appointment)


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = SignUpForm()
    valid = False
    if form.validate_on_submit():
        valid = True
        otp = generate_otp()
        session['otp'] = otp
        send_otp_email(form.username.data, form.email.data, otp)
        flash('Please check your email for the OTP', 'success')
    return render_template('signup.html', form=form, valid=valid)


@app.route('/signup/otp', methods=['POST', 'GET'])
def check_otp():
     if 'otp' not in session:
        flash('Invalid or expired OTP. Please try again.', 'danger')
        return redirect(url_for('signup'))
     
     if request.form.get('otp_input') == str(session['otp']):
        hashed_password = bcrypt.generate_password_hash(request.form.get('password')).decode('utf-8')
        user = User(username=request.form.get('username'), email=request.form.get('email'), password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created', 'success')

        session.pop('otp', None)
        return redirect(url_for('signin'))
     else:
        flash('Invalid OTP. Please try again.', 'danger')
        return redirect(url_for('signup'))


@app.route('/signin', methods=['POST', 'GET'])
def signin():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = SignInForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')

    return render_template('signin.html', form=form)


@app.route("/signout")
def signout():
    logout_user()
    return redirect(url_for('signin'))