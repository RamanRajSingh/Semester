from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error
import pickle
import joblib

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
# Function to get model name from selected sections
def get_model_name_from_sections(sections_str):
    # Example input: '1_2_3_4'
    return f"models/model_{sections_str}.pkl"
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
        "8th pass": 1, "intermediate": 2, "graduate": 3, "bachelor": 3,
        "post graduate": 4, "master": 4, "phd": 5, "doctor": 5
    }
    overtime_mapping = {'yes': 1, 'no': 0}
    business_travel_mapping = {
        'non-travel': 0, 'travel_rarely': 1, 'travel_frequently': 2
    }

    # Mapping dictionary for unified access
    mapping = {
        'gender': gender_mapping,
        'marital_status': marital_status_mapping,
        'education': education_mapping,
        'overtime': overtime_mapping,
        'business_travel': business_travel_mapping
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
@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        conn = None
        cursor = None
        try:
            conn = create_connection()
            cursor = conn.cursor(dictionary=True)

            # Collect all form fields (essential + optional)
            data = {
                'employee_number': request.form.get('employee_number'),
                'employee_age': request.form.get('employee_age'),
                'gender': request.form.get('gender'),
                'marital_status': request.form.get('marital_status'),
                'education': request.form.get('education'),
                'education_field': request.form.get('education_field'),
                'total_working_years': request.form.get('total_working_years'),
                'companies_worked': request.form.get('companies_worked'),
                'performance_rating': request.form.get('performance_rating'),
                'training_times_last_year': request.form.get('training_times_last_year'),
                'distance_from_home': request.form.get('distance_from_home'),
                'overtime': request.form.get('overtime'),
                'business_travel': request.form.get('business_travel'),
                'job_role': request.form.get('job_role') or None,
                'job_level': request.form.get('job_level') or None,
                'job_involvement': request.form.get('job_involvement') or None,
                'department': request.form.get('department') or None,
                'years_at_company': request.form.get('years_at_company') or None,
                'years_in_role': request.form.get('years_in_role') or None,
                'years_with_manager': request.form.get('years_with_manager') or None,
                'years_since_last_promotion': request.form.get('years_since_last_promotion') or None,
                'work_life_balance': request.form.get('work_life_balance') or None,
                'job_satisfaction': request.form.get('job_satisfaction') or None,
                'environment_satisfaction': request.form.get('environment_satisfaction') or None,
                'relationship_satisfaction': request.form.get('relationship_satisfaction') or None,
                'monthly_income': request.form.get('monthly_income') or None,
                'salary_hike': request.form.get('salary_hike') or None,
                'stock_option_level': request.form.get('stock_option_level') or None,
            }
            # 1. Collect form data# 1. Retrieve all form data
            form_data = request.form.to_dict(flat=True)

            # 2. Define encoding maps
            bt_map = {'Non-Travel': 0, 'Travel_Frequently': 1, 'Travel_Rarely': 2}
            e_map = {"8th pass": 1, "intermediate": 2, "graduate": 3, "bachelor": 3,"post graduate": 4, "master": 4, "phd": 5, "doctor": 5}
            ef_map = {'Life Sciences': 0, 'Medical': 1, 'Marketing': 2, 'Technical Degree': 3, 'Human Resources': 4}
            gender_map = {'Male': 0, 'Female': 1}
            ms_map = {'Single': 0, 'Married': 1, 'Divorced': 2}
            ot_map = {'No': 0, 'Yes': 1}

            # 3. Extract and encode inputs
            try:
                features = [
                    int(form_data.get('employee_age', 0)),
                    bt_map.get(form_data.get('business_travel', 'Non-Travel'), 0),
                    int(form_data.get('distance_from_home', 0)),
                    e_map.get(form_data.get('education', 'graduate'), 0),
                    ef_map.get(form_data.get('education_field', 'Life Sciences'), 0),
                    int(form_data.get('employee_number', 0)),
                    gender_map.get(form_data.get('gender', 'Male'), 0),
                    ms_map.get(form_data.get('marital_status', 'Single'), 0),
                    int(form_data.get('companies_worked', 0)),
                    ot_map.get(form_data.get('overtime', 'No'), 0),
                    int(form_data.get('performance_rating', 0)),
                    int(form_data.get('total_working_years', 0)),
                    int(form_data.get('training_times_last_year', 0))
                ]
            except Exception as e:
                print("❌ Error while preparing features:", e)
                return render_template("index.html", error="Invalid input format!")
            print("🔥 Form Data Received:", form_data)

            # 2. Extract values (you can do validation here)
            values = [
                form_data.get('employee_number'),
                form_data.get('employee_age'),
                form_data.get('gender'),
                form_data.get('marital_status'),
                form_data.get('education'),
                form_data.get('education_field'),
                form_data.get('total_working_years'),
                form_data.get('companies_worked'),
                form_data.get('performance_rating'),
                form_data.get('training_times_last_year'),
                form_data.get('distance_from_home'),
                form_data.get('overtime'),
                form_data.get('business_travel'),
                form_data.get('job_role'),
                form_data.get('job_level'),
                form_data.get('job_involvement'),
                form_data.get('department'),
                form_data.get('years_at_company'),
                form_data.get('years_in_role'),
                form_data.get('years_with_manager'),
                form_data.get('years_since_last_promotion'),  
                form_data.get('work_life_balance'),            
                form_data.get('job_satisfaction'),             
                form_data.get('environment_satisfaction'),     
                form_data.get('relationship_satisfaction'),    
                form_data.get('monthly_income'),
                form_data.get('salary_hike'),
                form_data.get('stock_option_level')
            ]

            # Insert into SQL
            insert_query = """
                INSERT INTO employee_data (
                    employee_number, employee_age, gender, marital_status, education, education_field,
                    total_working_years, companies_worked, performance_rating, training_times_last_year,
                    distance_from_home, overtime, business_travel,
                    job_role, job_level, job_involvement, department, years_at_company, years_in_role, 
                    years_with_manager, years_since_last_promotion,
                    work_life_balance, job_satisfaction, environment_satisfaction, relationship_satisfaction,
                    monthly_income, salary_hike, stock_option_level
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            print("INSERTING DATA =>", data)

            cursor.execute(insert_query, tuple(data.values()))
            conn.commit()
            for key, val in data.items():
                if val in [None, '', 'None']:
                    data[key] = None

            print("Query Preview:")
            print(insert_query)
            print("Values:", tuple(data.values()))

            print("==== DEBUG: Form Data Received ====")
            for key in request.form:
                print(f"{key} => {request.form.get(key)}")

            # --- Prediction Logic Starts ---
            # Fetch most recent data
            cursor.execute("SELECT * FROM employee_data ORDER BY employee_number DESC LIMIT 1")
            data = cursor.fetchone()
            print("Form values:", request.form)
           # Define section-wise columns (ONLY ONCE)
            section_1_2_3 = [
                'employee_age', 'business_travel', 'distance_from_home', 'education',
                'education_field', 'employee_number', 'gender', 'marital_status',
                'companies_worked', 'overtime', 'performance_rating',
                'total_working_years', 'training_times_last_year'
            ]

            section_4 = ['department', 'job_involvement', 'job_level', 'job_role']
            section_5 = ['environment_satisfaction', 'job_satisfaction', 'relationship_satisfaction', 'work_life_balance']
            section_6 = ['monthly_income', 'salary_hike', 'stock_option_level',
                        'years_at_company', 'years_in_role', 'years_since_last_promotion', 'years_with_manager']

            # Get selected model version
            selected_sections = request.form.get("checked_sections", "1_2_3")
            model_path = f"models/model_{selected_sections}.pkl"

            # Load model
            dynamic_model = joblib.load(model_path)

# --- Encoding the Fields ---

            columns = section_1_2_3[:]

            for i, section in enumerate([section_4, section_5, section_6], start=4):
                if any(data[col] not in [None, '', 'None'] for col in section):
                    selected.append(str(i))
                    columns.extend(section)

            # Build features
            for col in columns:
                val = data[cursor.column_names.index(col)]
                features.append(int(val) if val is not None else 0)

            selected_sections = request.form.get('checked_sections', "").strip()# 🧠 TRACKED SECTION VALUES
            if not selected_sections:
                selected_sections = '1_2_3'  # Or any default section if not selected 
            model_filename = f'models/model_{selected_sections}.pkl'

            with open(model_filename, 'rb') as f:
                model = load_model(model_filename)
            model_input = [float(val) if val not in [None, '', 'NULL'] else 0 for val in values[:13]]  # Only 1_2_3 fields used


            try:
                dynamic_model = joblib.load(model_path)
            except FileNotFoundError:
                return render_template('index.html', prediction_text='Model file not found!')

            features = preprocess_input(data)
            prediction = dynamic_model.predict([features])

            flash(f"Prediction: {'Yes' if prediction == 1 else 'No'}")
            print("Form data received =>", request.form)

        except Exception as e:
            print("Database Error:", e)
            if conn:
                conn.rollback()
                flash(f"Error: {e}")
                print("Error during DB insert:", e)

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
