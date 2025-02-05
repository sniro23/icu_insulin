from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///patients.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Model
class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.String(20), unique=True, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    diabetes_status = db.Column(db.String(50), nullable=False)
    treatment_type = db.Column(db.String(50), nullable=True)
    diet_status = db.Column(db.String(50), nullable=False)
    indication = db.Column(db.String(50), nullable=False)
    glucose_1 = db.Column(db.Float, nullable=False)
    glucose_2 = db.Column(db.Float, nullable=True)
    insulin_rate = db.Column(db.Float, nullable=True)
    potassium = db.Column(db.Float, nullable=True)
    sodium = db.Column(db.Float, nullable=True)
    creatinine = db.Column(db.Float, nullable=True)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

# Insulin Infusion Calculation Logic
def calculate_insulin_rate(glucose_1, glucose_2, weight, diabetes_status):
    if glucose_2 and glucose_2 > 12:
        return round(0.1 * weight, 2)  # Increased insulin rate
    elif glucose_2 and 8 <= glucose_2 <= 12:
        return round(0.05 * weight, 2)  # Standard insulin rate
    else:
        return round(0.02 * weight, 2)  # Reduced insulin rate

# Fluid Rate Calculation
def calculate_fluid_rate(weight, sodium, potassium):
    if potassium and potassium < 3.5:
        return "Dextrose 5% + KCl 40mmol/L at 100ml/hr"
    elif potassium and 3.5 <= potassium <= 5.0:
        return "0.9% Saline + KCl 20mmol/L at 125ml/hr"
    else:
        return "0.9% Saline at 125ml/hr"

# Home Page
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        patient_id = request.form['patient_id']
        patient = Patient.query.filter_by(patient_id=patient_id).first()
        if patient:
            return redirect(url_for('update_patient', patient_id=patient_id))
        else:
            return redirect(url_for('new_patient'))
    return render_template('index.html')

# Update Existing Patient Data
@app.route('/update_patient/<patient_id>', methods=['GET', 'POST'])
def update_patient(patient_id):
    patient = Patient.query.filter_by(patient_id=patient_id).first()
    if request.method == 'POST':
        patient.glucose_1 = float(request.form['glucose_1'])
        patient.glucose_2 = float(request.form['glucose_2']) if request.form['glucose_2'] else None
        patient.insulin_rate = calculate_insulin_rate(patient.glucose_1, patient.glucose_2, patient.weight, patient.diabetes_status)
        patient.potassium = float(request.form['potassium'])
        patient.sodium = float(request.form['sodium'])
        patient.creatinine = float(request.form['creatinine'])
        patient.last_updated = datetime.utcnow()
        db.session.commit()
        return redirect(url_for('index'))
    insulin_rate = calculate_insulin_rate(patient.glucose_1, patient.glucose_2, patient.weight, patient.diabetes_status)
    fluid_rate = calculate_fluid_rate(patient.weight, patient.sodium, patient.potassium)
    return render_template('update_patient.html', patient=patient, insulin_rate=insulin_rate, fluid_rate=fluid_rate, 
                           diabetes_status_options=["Type 1 DM", "Type 2 DM", "No Diabetes"],
                           treatment_type_options=["Oral drugs", "Basal-Bolus", "Pre-Mix", "Basal only"],
                           diet_status_options=["Nil by Mouth", "Enteral Feeding", "Normal Diet"],
                           indication_options=["DKA", "HHS", "Sepsis", "ACS", "CVA", "Other Critical Illness"],
                           js_script="<script>
                           function toggleTreatmentType() {
                               var diabetesStatus = document.getElementById('diabetes_status').value;
                               var treatmentTypeField = document.getElementById('treatment_type');
                               treatmentTypeField.disabled = (diabetesStatus === 'No Diabetes');
                           }
                           </script>")

@app.route('/new_patient', methods=['GET', 'POST'])
def new_patient():
    if request.method == 'POST':
        return redirect(url_for('index'))
    return render_template('new_patient.html', 
                           diabetes_status_options=["Type 1 DM", "Type 2 DM", "No Diabetes"],
                           treatment_type_options=["Oral drugs", "Basal-Bolus", "Pre-Mix", "Basal only"],
                           diet_status_options=["Nil by Mouth", "Enteral Feeding", "Normal Diet"],
                           indication_options=["DKA", "HHS", "Sepsis", "ACS", "CVA", "Other Critical Illness"],
                           js_script="<script>
                           function toggleTreatmentType() {
                               var diabetesStatus = document.getElementById('diabetes_status').value;
                               var treatmentTypeField = document.getElementById('treatment_type');
                               treatmentTypeField.disabled = (diabetesStatus === 'No Diabetes');
                           }
                           </script>")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
