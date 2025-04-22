from flask import Flask, render_template, request, flash, redirect, url_for
import joblib

app = Flask(__name__)
app.secret_key = 'your_secret_key'
# Route: Login Page
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Dummy check for development phase
        if username == 'admin' and password == 'admin':
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password. Please try again.')

    return render_template('login.html')
# A cache for loaded models
global loaded_models
loaded_models = {}

def load_model(key):
    path = f'models/model_{key}.pkl'
    if path not in loaded_models:
        loaded_models[path] = joblib.load(path)
    return loaded_models[path]

# Define for each model key the exact feature order
MODEL_INPUTS = {
    '1_2_3' : ["employee_number",
        "age",
        "gender",
        "marital_status",
        "education",
        "education_field",
        "total_working_years",
        "num_companies_worked",
        "performance_rating",
        "training_times_last_year",
        "distance_from_home",
        "overtime",
        "business_travel"],
    '1_2_3_4': ["age", "business_travel", "department", "distance_from_home", "education", "education_field", "employee_number", "gender", "job_involvement", "job_level", "job_role", "marital_status", "num_companies_worked", "overtime", "performance_rating", "total_working_years", "training_times_last_year", "years_at_company", "years_in_current_role", "years_since_last_promotion", "years_with_curr_manager"],
    '1_2_3_5': ["age", "business_travel", "distance_from_home", "education", "education_field", "employee_number", "environment_satisfaction", "gender", "job_satisfaction", "marital_status", "num_companies_worked", "overtime", "performance_rating", "relationship_satisfaction", "total_working_years", "training_times_last_year", "work_life_balance"],
    '1_2_3_6': ["age", "business_travel", "distance_from_home", "education", "education_field", "employee_number", "gender", "marital_status", "monthly_income", "num_companies_worked", "overtime", "percent_salary_hike", "performance_rating", "stock_option_level", "total_working_years", "training_times_last_year"],
    '1_2_3_4_5':["age", "business_travel", "department", "distance_from_home", "education", "education_field", "employee_number", "environment_satisfaction", "gender", "job_involvement", "job_level", "job_role", "job_satisfaction", "marital_status", "num_companies_worked", "overtime", "performance_rating", "relationship_satisfaction", "total_working_years", "training_times_last_year", "work_life_balance", "years_at_company", "years_in_current_role", "years_since_last_promotion", "years_with_curr_manager"],
    '1_2_3_4_6' : ["age", "business_travel", "department", "distance_from_home", "education", "education_field", "employee_number", "gender", "job_involvement", "job_level", "job_role", "marital_status", "monthly_income", "num_companies_worked", "overtime", "percent_salary_hike", "performance_rating", "stock_option_level", "total_working_years", "training_times_last_year", "years_at_company", "years_in_current_role", "years_since_last_promotion", "years_with_curr_manager"],
    '1_2_3_5_6' : ["age", "business_travel", "distance_from_home", "education", "education_field", "employee_number", "environment_satisfaction", "gender", "job_satisfaction", "marital_status", "monthly_income", "num_companies_worked", "overtime", "percent_salary_hike", "performance_rating", "relationship_satisfaction", "stock_option_level", "total_working_years", "training_times_last_year", "work_life_balance"],
    '1_2_3_4_5_6': ["age", "business_travel", "department", "distance_from_home", "education", "education_field", 
               "employee_number", "environment_satisfaction", "gender", "job_involvement", "job_level", "job_role", 
               "job_satisfaction", "marital_status", "monthly_income", "num_companies_worked", "overtime", 
               "percent_salary_hike", "performance_rating", "relationship_satisfaction", "stock_option_level", 
               "total_working_years", "training_times_last_year", "work_life_balance", "years_at_company", 
               "years_in_current_role", "years_since_last_promotion", "years_with_curr_manager"]

    # ... add the other 7 combinations similarly
}

# Unified mapping for all categorical fields
MAPPING = {
    'gender': {'male':0, 'female':1},
    'marital_status': {'single':0, 'married':1, 'divorced':2},
    'education': {'8th pass':1,'intermediate':2,'graduate':3,'bachelor':3,
        'post graduate':4,'master':4,'phd':5,'doctorate':5
    },
    'education_field': {'life sciences':0,'medical':1,'marketing':2,'technical degree':3,'human resources':4},
    'business_travel': {'non-travel':0,'travel_rarely':1,'travel_frequently':2},
    'overtime': {'no':0,'yes':1},
    'job_role_mapping': {
        'Sales Executive': 0,
        'Research Scientist': 1,
        'Laboratory Technician': 2,
        'Manufacturing Director': 3,
        'Healthcare Representative': 4,
        'Manager': 5,
        'Sales Representative': 6,
        'Research Director': 7,
        'Human Resources': 8
    },
    'department_mapping' :{
        'Sales': 0,
        'Research & Development': 1,
        'Human Resources': 2
    }
}

@app.route('/index', methods=['GET','POST'])
def index():
    if request.method == 'POST':
        # 1. pull only non-empty inputs
        form = {k:v for k,v in request.form.items() if v}

        # 2. determine active sections
        active = ['1','2','3']
        if form.get('section4_enabled'): active.append('4')
        if form.get('section5_enabled'): active.append('5')
        if form.get('section6_enabled'): active.append('6')
        key = '_'.join(active)

        # 3. build feature vector
        names = MODEL_INPUTS[key]
        features = []
        for nm in names:
            val = form.get(nm)
            if nm in MAPPING:
                features.append(MAPPING[nm].get(val.lower(),0))
            else:
                features.append(int(val))

        # 4. predict
        try:
            model = load_model(key)
            pred = model.predict([features])[0]
            result = 'Yes' if pred==1 else 'No'
        except Exception as e:
            flash(f"Prediction error: {e}")
            return redirect(url_for('index'))
        
        return render_template('result.html', employee_number=form.get('employee_number'), prediction=result)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
