from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error
import pickle
import joblib
import traceback

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Cache recently loaded models using a dictionary 
loaded_models = {}

def load_model(model_path):
    if model_path in loaded_models:
        return loaded_models[model_path]
    with open(model_path, 'rb') as f:
        model = pickle.load(f)

    loaded_models[model_path] = model
    return model

# MySQL Connection
def create_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Raman@20",
        database="employee_db"
    )

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
# Utility: Preprocess input for model
@app.route('/predict', methods=['POST'])
def predict():
    try:
        form = request.form
        features = preprocess_input(form)
        prediction = model.predict([features])[0]
        return render_template('result.html', prediction=prediction)

    except Exception as e:
        print(f"❌ Error while preparing pfeatures: {e}")
        return "There was an error processing your input data."


def preprocess_input(form):
    # Mappings for categorical fields
    gender_mapping = {'male': 1, 'female': 0}
    marital_status_mapping = {'single': 0, 'married': 1, 'divorced': 2}
    education_mapping = {
        "matric": 1, "intermediate": 2, "graduate": 3, "bachelor": 3,
        "post_graduate": 4, "master": 4, "phd": 5, "doctorate": 5
    }
    overtime_mapping = {'yes': 1, 'no': 0}
    business_travel_mapping = {
        'non-travel': 0, 'travel_rarely': 1, 'travel_frequently': 2
    }
    job_role_mapping= {
        'Sales Executive': 0,
        'Research Scientist': 1,
        'Laboratory Technician': 2,
        'Manufacturing Director': 3,
        'Healthcare Representative': 4,
        'Manager': 5,
        'Sales Representative': 6,
        'Research Director': 7,
        'Human Resources': 8
    }
    department_mapping={
        'Sales': 0,
        'Research & Development': 1,
        'Human Resources': 2
    }
    Education_field_mappping={
        'life Sciences': 0,
        'medical': 1,
        'marketing': 2,
        'technical degree': 3,
        'human resources': 4
    }
    # Mapping dictionary for unified access
    mapping = {
        'gender': gender_mapping,
        'marital_status': marital_status_mapping,
        'education': education_mapping,
        'overtime': overtime_mapping,
        'business_travel': business_travel_mapping,
        'job_role': job_role_mapping,
        'department': department_mapping,
        'education_field': Education_field_mappping
    }

    # Fields expected to be numeric directly
    numeric_fields = [
        "employee_number", "employee_age", "total_working_years",
        "companies_worked", "performance_rating", "training_times_last_year",
        "distance_from_home", "job_level", "job_involvement", "years_at_company",
        "years_in_role", "years_with_manager", "years_since_last_promotion",
        "work_life_balance", "job_satisfaction", "environment_satisfaction",
        "relationship_satisfaction", "monthly_income", "salary_hike",
        "stock_option_level"
    ]

    processed = []


    # Loop through each form field

    for field in form:
        clean_field = field.strip().lower()  # Normalize field name
        val = form[field]  # Get the value for the field
        val_str = val.strip().lower() if isinstance(val, str) else val  # Normalize string values

        # Handle categorical fields

        if clean_field in mapping:
            processed.append(mapping[clean_field].get(val_str, 0))  # Default to 0 if not found

        # Handle numeric fields

        elif clean_field in numeric_fields:

            try:

                processed.append(int(val))  # Convert to integer

            except:

                processed.append(0)  # In case of error, append 0

        else:

            processed.append(0)  # Default case if the field doesn't match

    return processed
 # Helper: sanitize and cast inputs
def sanitize(value, cast_type=int):
    try:
        return cast_type(value) if value not in [None, '', 'None'] else None
    except:
        return None
@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        conn = None
        cursor = None
        try:
            conn = create_connection()
            cursor = conn.cursor(dictionary=True)

   

            # 1. Retrieve all form data
            form_data = request.form.to_dict(flat=True)
            print("🔥 Form Data Received:", form_data)

            # 2. Mapping for encoding categorical values
            bt_map = {'non-travel': 0, 'travel_rarely': 1, 'travel_frequently': 2}
            e_map = {"8th pass": 1, "intermediate": 2, "graduate": 3, "bachelor": 3, "post graduate": 4, "master": 4, "phd": 5, "doctor": 5}
            ef_map = {'life sciences': 0, 'medical': 1, 'marketing': 2, 'technical degree': 3, 'human resources': 4}
            gender_map = {'male': 0, 'female': 1}
            ms_map = {'single': 0, 'married': 1, 'divorced': 2}
            ot_map = {'no': 0, 'yes': 1}

            # 3. Feature encoding for ML
            try:
                features = [
                    sanitize(form_data.get('employee_age')),
                    bt_map.get(form_data.get('business_travel', 'non-travel').lower(), 0),
                    sanitize(form_data.get('distance_from_home')),
                    e_map.get(form_data.get('education', 'graduate').lower(), 3),
                    ef_map.get(form_data.get('education_field', 'life sciences').lower(), 0),
                    sanitize(form_data.get('employee_number')),
                    gender_map.get(form_data.get('gender', 'male').lower(), 0),
                    ms_map.get(form_data.get('marital_status', 'single').lower(), 0),
                    sanitize(form_data.get('companies_worked')),
                    ot_map.get(form_data.get('overtime', 'no').lower(), 0),
                    sanitize(form_data.get('performance_rating')),
                    sanitize(form_data.get('total_working_years')),
                    sanitize(form_data.get('training_times_last_year'))
                ]
            except Exception as e:
                print("❌ Error while preparing features:", e)
                return render_template("index.html", error="Invalid input format!")

            # 4. SQL INSERT values (sanitize all)
            values = [
                sanitize(form_data.get('employee_age')),                         # age
                form_data.get('business_travel'),                                # business_travel
                form_data.get('department'),                                     # department
                sanitize(form_data.get('distance_from_home')),                   # distance_from_home
                form_data.get('education'),                                      # education
                form_data.get('education_field'),                                # education_field
                sanitize(form_data.get('employee_number')),                      # employee_number (PRIMARY)
                sanitize(form_data.get('environment_satisfaction')),             # environment_satisfaction
                form_data.get('gender'),                                         # gender
                sanitize(form_data.get('job_involvement')),                      # job_involvement
                sanitize(form_data.get('job_level')),                            # job_level
                form_data.get('job_role'),                                       # job_role
                sanitize(form_data.get('job_satisfaction')),                     # job_satisfaction
                form_data.get('marital_status'),                                 # marital_status
                sanitize(form_data.get('monthly_income')),                       # monthly_income
                sanitize(form_data.get('companies_worked')),                     # num_companies_worked
                form_data.get('overtime'),                                       # overtime
                sanitize(form_data.get('salary_hike')),                          # percent_salary_hike
                sanitize(form_data.get('performance_rating')),                   # performance_rating
                sanitize(form_data.get('relationship_satisfaction')),            # relationship_satisfaction
                sanitize(form_data.get('stock_option_level')),                   # stock_option_level
                sanitize(form_data.get('total_working_years')),                  # total_working_years
                sanitize(form_data.get('training_times_last_year')),            # training_times_last_year
                sanitize(form_data.get('work_life_balance')),                    # work_life_balance
                sanitize(form_data.get('years_at_company')),                     # years_at_company
                sanitize(form_data.get('years_in_current_role')),                # years_in_current_role
                sanitize(form_data.get('years_since_last_promotion')),           # years_since_last_promotion
                sanitize(form_data.get('years_with_curr_manager'))               # years_with_curr_manager
            ]

            # 5. Insert query
            insert_query = """
                INSERT INTO employee_data (
                    age, business_travel, department, distance_from_home,
                    education, education_field, employee_number, environment_satisfaction, gender,
                    job_involvement, job_level, job_role, job_satisfaction, marital_status,
                    monthly_income, num_companies_worked, overtime, percent_salary_hike, performance_rating,
                    relationship_satisfaction, stock_option_level, total_working_years, training_times_last_year,
                    work_life_balance, years_at_company, years_in_current_role, years_since_last_promotion,
                    years_with_curr_manager
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            try:
                cursor.execute(insert_query, values)
                conn.commit()
                print("✅ Data Inserted into DB Successfully!")
            except Error as e:
                print(f'❌ Error inserting data into database: {e}')

            """print("==== DEBUG: Form Data Received ====")
            for key in request.form:
                print(f"{key} => {request.form.get(key)}")"""

            # --- Prediction Logic Starts ---
            # Define section-wise columns (ONLY ONCE)
            '''section_1_2_3 = [
                'employee_age', 'business_travel', 'distance_from_home', 'education',
                'education_field', 'employee_number', 'gender', 'marital_status',
                'companies_worked', 'overtime', 'performance_rating',
                'total_working_years', 'training_times_last_year'
            ]

            section_4 = ['department', 'job_involvement', 'job_level', 'job_role','years_at_company', 'years_in_role', 'years_since_last_promotion', 'years_with_manager']
            section_5 = ['environment_satisfaction', 'job_satisfaction', 'relationship_satisfaction', 'work_life_balance']
            section_6 = ['monthly_income', 'salary_hike', 'stock_option_level',]
            

# --- Encoding the Fields ---
            selected = []
            columns = section_1_2_3[:]  # base fields

            for i, section in enumerate([section_4, section_5, section_6], start=4):
                if any(data.get(col) not in [None, '', 'None'] for col in section):  # ✅ safe access
                    selected.append(str(i))
                    columns.extend(section)
'''
            selected_sections = request.form.get('checked_sections', "").strip()
            print("checked_sections:", selected_sections)

            # Fix condition to check for empty string or None properly
            if not selected_sections:
                selected_sections = "1_2_3"
            else:
                # Join user-selected sections with 1_2_3 always included
                selected_sections = "1_2_3_" + "_".join(selected_sections.split(","))

            model_filename = f"models/model_{selected_sections}.pkl"
            print("✅ Model Filename:", model_filename)

            
            
            # Fetch most recent data
            if model_filename == "models/model_1_2_3.pkl":
                cursor.execute('''
    SELECT 
        employee_number,
        age AS employee_age,
        gender,
        marital_status,
        education,
        education_field,
        total_working_years,
        num_companies_worked AS companies_worked,
        performance_rating,
        training_times_last_year,
        distance_from_home,
        overtime,
        business_travel
    FROM employee_data
    ORDER BY employee_number DESC
    LIMIT 1
''')
                data = cursor.fetchone()

            elif model_filename == "models/model_1_2_3_4.pkl":
                cursor.execute('''SELECT 
    age,
    business_travel,
    department,
    distance_from_home,
    education,
    education_field,
    employee_number,
    gender,
    job_involvement,
    job_level,
    job_role,
    marital_status,
    num_companies_worked,
    overtime,
    performance_rating,
    total_working_years,
    training_times_last_year,
    years_at_company,
    years_in_current_role,
    years_since_last_promotion,
    years_with_curr_manager
FROM employee_data
ORDER BY employee_number DESC
LIMIT 1;
''')
                data = cursor.fetchone()
            elif model_filename == "models/model_1_2_3_5.pkl":
                cursor.execute('''SELECT 
    age,
    business_travel,
    distance_from_home,
    education,
    education_field,
    employee_number,
    environment_satisfaction,
    gender,
    job_satisfaction,
    marital_status,
    num_companies_worked,
    overtime,
    performance_rating,
    relationship_satisfaction,
    total_working_years,
    training_times_last_year,
    work_life_balance
FROM employee_data
ORDER BY employee_number DESC
LIMIT 1;
''')
                data = cursor.fetchone()
            elif model_filename == "models/model_1_2_3_6.pkl":
                cursor.execute('''SELECT 
    age,
    business_travel,
    distance_from_home,
    education,
    education_field,
    employee_number,
    gender,
    marital_status,
    monthly_income,
    num_companies_worked,
    overtime,
    percent_salary_hike,
    performance_rating,
    stock_option_level,
    total_working_years,
    training_times_last_year
FROM employee_data
ORDER BY employee_number DESC
LIMIT 1;
''')
                data = cursor.fetchone()
            elif model_filename == "models/model_1_2_3_4_5.pkl":
                cursor.execute('''SELECT 
    age,
    business_travel,
    department,
    distance_from_home,
    education,
    education_field,
    employee_number,
    environment_satisfaction,
    gender,
    job_involvement,
    job_level,
    job_role,
    job_satisfaction,
    marital_status,
    num_companies_worked,
    overtime,
    performance_rating,
    relationship_satisfaction,
    total_working_years,
    training_times_last_year,
    work_life_balance,
    years_at_company,
    years_in_current_role,
    years_since_last_promotion,
    years_with_curr_manager
FROM employee_data
ORDER BY employee_number DESC
LIMIT 1;
''')
                data = cursor.fetchone()
            elif model_filename == "models/model_1_2_3_4_6.pkl":
                cursor.execute('''SELECT
    age,
    business_travel,
    department,
    distance_from_home,
    education,
    education_field,
    employee_number,
    gender,
    job_involvement,
    job_level,
    job_role,
    marital_status,
    monthly_income,
    num_companies_worked,
    overtime,
    percent_salary_hike,
    performance_rating,
    stock_option_level,
    total_working_years,
    training_times_last_year,
    years_at_company,
    years_in_current_role,
    years_since_last_promotion,
    years_with_curr_manager
FROM employee_data
ORDER BY employee_number DESC
LIMIT 1;
''')
                data = cursor.fetchone()
            elif model_filename == "models/model_1_2_3_5_6.pkl":
                cursor.execute('''SELECT
    age,
    business_travel,
    distance_from_home,
    education,
    education_field,
    employee_number,
    environment_satisfaction,
    gender,
    job_satisfaction,
    marital_status,
    monthly_income,
    num_companies_worked,
    overtime,
    percent_salary_hike,
    performance_rating,
    relationship_satisfaction,
    stock_option_level,
    total_working_years,
    training_times_last_year,
    work_life_balance
FROM employee_data
ORDER BY employee_number DESC
LIMIT 1;
''')
                data = cursor.fetchone()
            elif model_filename == "models/model_1_2_3_4_5_6.pkl":
                cursor.execute('''SELECT employee_number,
                               SELECT age, business_travel, department, distance_from_home,
       education, education_field, employee_number, environment_satisfaction, gender,
       job_involvement, job_level, job_role, job_satisfaction, marital_status,
       monthly_income, num_companies_worked, overtime, percent_salary_hike, performance_rating,
       relationship_satisfaction, stock_option_level, total_working_years, training_times_last_year,
       work_life_balance, years_at_company, years_in_current_role, years_since_last_promotion,
       years_with_curr_manager from employee_data ORDER BY employee_number DESC LIMIT 1''')
                data = cursor.fetchone()
            print("Form values:", request.form)

            
            print("Model Filename:", model_filename)
            try:
                dynamic_model = joblib.load(model_filename)
            except FileNotFoundError:
                return render_template('index.html', prediction_text='Model file not found!')

            features = preprocess_input(data)
            prediction_result = "No" if dynamic_model.predict([features])[0] == 1 else "Yes"
            employee_number = form_data.get('employee_number')
            try:
                return render_template("result.html", employee_number=employee_number ,prediction=prediction_result)
                print("Prediction Result:", prediction_result)
            except Exception as e:
                print("Error rendering result:", e)
                return render_template("index.html", error="Error rendering result page.")

        except Exception as e:
            print("Database Error:", e)
            traceback.print_exc()  # 🧠 Shows the full stack trace


        finally:
            if cursor:
                cursor.close()
            if conn is not None:
                try:
                    if conn.is_connected():
                        conn.close()
                except Exception as e:
                    print("Error closing connection:", e)



    return render_template('index.html')

# Run Server
if __name__ == '__main__':
    app.run(debug=True)
