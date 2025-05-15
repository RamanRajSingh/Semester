from flask import Flask, render_template, request, flash, redirect, url_for
import joblib
from tensorflow.keras.models import load_model
from collections import Counter
import numpy as np
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Cache for models
loaded_models = {}

# Mappings
MAPPING = {
    'gender': {'male': 0, 'female': 1},
    'marital_status': {'single': 0, 'married': 1, 'divorced': 2},
    'education': {
        '8th pass': 1, 'intermediate': 2, 'graduate': 3, 'bachelor': 3,
        'post graduate': 4, 'master': 4, 'phd': 5, 'doctorate': 5
    },
    'education_field': {
        'life sciences': 0, 'medical': 1, 'marketing': 2,
        'technical degree': 3, 'human resources': 4
    },
    'business_travel': {
        'non-travel': 0, 'travel_rarely': 1, 'travel_frequently': 2
    },
    'overtime': {'no': 0, 'yes': 1},
    'job_role_mapping': {
        'Sales Executive': 0, 'Research Scientist': 1, 'Laboratory Technician': 2,
        'Manufacturing Director': 3, 'Healthcare Representative': 4,
        'Manager': 5, 'Sales Representative': 6, 'Research Director': 7,
        'Human Resources': 8
    },
    'department_mapping': {
        'Sales': 0, 'Research & Development': 1, 'Human Resources': 2
    }
}

# Input feature orders per model
MODEL_INPUTS = {
    '1_2_3': [
        "employee_number", "age", "gender", "marital_status", "education",
        "education_field", "total_working_years", "num_companies_worked",
        "performance_rating", "training_times_last_year", "distance_from_home",
        "overtime", "business_travel"
    ],
    '1_2_3_4': [
        "age", "business_travel", "department", "distance_from_home", "education",
        "education_field", "employee_number", "gender", "job_involvement", "job_level",
        "job_role", "marital_status", "num_companies_worked", "overtime",
        "performance_rating", "total_working_years", "training_times_last_year",
        "years_at_company", "years_in_current_role", "years_since_last_promotion",
        "years_with_curr_manager"
    ],
    '1_2_3_5': [
        "age", "business_travel", "distance_from_home", "education", "education_field",
        "employee_number", "environment_satisfaction", "gender", "job_satisfaction",
        "marital_status", "num_companies_worked", "overtime", "performance_rating",
        "relationship_satisfaction", "total_working_years", "training_times_last_year",
        "work_life_balance"
    ],
    '1_2_3_6': [
        "age", "business_travel", "distance_from_home", "education", "education_field",
        "employee_number", "gender", "marital_status", "monthly_income",
        "num_companies_worked", "overtime", "percent_salary_hike", "performance_rating",
        "stock_option_level", "total_working_years", "training_times_last_year"
    ],
    '1_2_3_4_5': [
        "age", "business_travel", "department", "distance_from_home", "education",
        "education_field", "employee_number", "environment_satisfaction", "gender",
        "job_involvement", "job_level", "job_role", "job_satisfaction",
        "marital_status", "num_companies_worked", "overtime", "performance_rating",
        "relationship_satisfaction", "total_working_years", "training_times_last_year",
        "work_life_balance", "years_at_company", "years_in_current_role",
        "years_since_last_promotion", "years_with_curr_manager"
    ],
    '1_2_3_4_6': [
        "age", "business_travel", "department", "distance_from_home", "education",
        "education_field", "employee_number", "gender", "job_involvement",
        "job_level", "job_role", "marital_status", "monthly_income",
        "num_companies_worked", "overtime", "percent_salary_hike", "performance_rating",
        "stock_option_level", "total_working_years", "training_times_last_year",
        "years_at_company", "years_in_current_role", "years_since_last_promotion",
        "years_with_curr_manager"
    ],
    '1_2_3_5_6': [
        "age", "business_travel", "distance_from_home", "education", "education_field",
        "employee_number", "environment_satisfaction", "gender", "job_satisfaction",
        "marital_status", "monthly_income", "num_companies_worked", "overtime",
        "percent_salary_hike", "performance_rating", "relationship_satisfaction",
        "stock_option_level", "total_working_years", "training_times_last_year",
        "work_life_balance"
    ],
    '1_2_3_4_5_6': [
        "age", "business_travel", "department", "distance_from_home", "education",
        "education_field", "employee_number", "environment_satisfaction", "gender",
        "job_involvement", "job_level", "job_role", "job_satisfaction", "marital_status",
        "monthly_income", "num_companies_worked", "overtime", "percent_salary_hike",
        "performance_rating", "relationship_satisfaction", "stock_option_level",
        "total_working_years", "training_times_last_year", "work_life_balance",
        "years_at_company", "years_in_current_role", "years_since_last_promotion",
        "years_with_curr_manager"
    ]
}

def load_model_0(key):
    model_path = f'models/model_{key}.pkl'
    if model_path not in loaded_models:
        loaded_models[model_path] = joblib.load(model_path)
    return loaded_models[model_path]
def load_model_1(key):
    model_path_1 = f'models/modelr_{key}.pkl'
    if model_path_1 not in loaded_models:
        loaded_models[model_path_1] = joblib.load(model_path_1)
    return loaded_models[model_path_1]

users={'admin': 'admin'}
@app.route('/', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        users[username] = password
        return redirect(url_for('login'))
    return render_template('sign-up.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if request.form.get('username') == 'admin' and request.form.get('password') == 'admin':
            print("Login successful!")
            return redirect(url_for('index'))
        elif username in users and users[username] == password:
            return redirect(url_for('index'))
        else:
            print("Invalid username or password.")
    return render_template('login.html')

@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        form = {k: v for k, v in request.form.items() if v}

        active = ['1', '2', '3']
        if 'section4_enabled' in form: active.append('4')
        if 'section5_enabled' in form: active.append('5')
        if 'section6_enabled' in form: active.append('6')
        key = '_'.join(active)

        feature_names = MODEL_INPUTS.get(key)
        if not feature_names:
            print(f"No model found for selected inputs: {key}")
            return redirect(url_for('index'))

        try:
            features = []
            for fname in feature_names:
                val = form.get(fname)
                if val is None:
                    raise ValueError(f"Missing value for: {fname}")
                if fname in MAPPING:
                    features.append(MAPPING[fname].get(val.lower(), 0))
                else:
                    features.append(int(val))


                val = val.strip().lower() if isinstance(val, str) else val

                if fname in MAPPING:
                    mapped = MAPPING[fname].get(val)
                    if mapped is None:
                        flash(f"Invalid value for {fname}: {val}")
                        return redirect(url_for('index'))
                    features.append(mapped)

                elif fname == 'job_role':
                    mapped = MAPPING['job_role_mapping'].get(val.title())
                    if mapped is None:
                        flash(f"Invalid job role: {val}")
                        return redirect(url_for('index'))
                    features.append(mapped)

                elif fname == 'department':
                    mapped = MAPPING['department_mapping'].get(val.title())
                    if mapped is None:
                        flash(f"Invalid department: {val}")
                        return redirect(url_for('index'))
                    features.append(mapped)

                else:
                    try:
                        features.append(int(val))
                    except ValueError:
                        flash(f"Invalid numeric input for {fname}: {val}")
                        return redirect(url_for('index'))
            print("FEATURES USED:", features)

        except Exception as e:
            print("❌ Prediction Error:", e)
            flash(f"Prediction error: {e}")
            return render_template('index.html')  # ✅ show form again with error
            

        try:
            model = load_model_0(key)
            names = MODEL_INPUTS[key]
            features = []
            model_1= load_model_1(key)
            model_2= load_model(f'models/modela_{key}.h5')
            for nm in names:
                val = form.get(nm)

                if val is None:
                    raise ValueError(f"Missing value for: {nm}")

                if nm in MAPPING:
                    features.append(MAPPING[nm].get(val.lower(), 0))
                else:
                    features.append(int(val))
            input_array = np.array(features).reshape(1, -1)  # Shape = (1, 28)
            probability = model_2.predict(input_array)[0][0]
            prediction = int(probability > 0.5)
            pred = [model.predict([features])[0],model_1.predict([features])[0],prediction]
            fin=max(set(pred), key=pred.count)
            result = 'Yes' if fin == 1 else 'No'
            print("PREDICTION:", pred,fin)

            return render_template('result.html', employee_number=form.get('employee_number'), prediction=result)

        except Exception as e:
            print("❌ Prediction Error:", e)
            flash(f"Prediction error: {e}")
            return render_template('index.html')  # ✅ show form again with error


        

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
