from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error
import pickle
import joblib

app = Flask(__name__)
app.secret_key = 'your_secret_key'

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
        print(f"❌ Error while preparing features: {e}")
        return "There was an error processing your input data."


def preprocess_input(form):
    # Combined mappings
    mapping = {
        "gender": {"male": 0, "female": 1},
        "marital_status": {"single": 0, "married": 1, "divorced": 2},
        "education": {
            "8th pass": 1, "intermediate": 2, "graduate": 3,
            "bachelor": 3, "post graduate": 4, "master": 4,
            "phd": 5, "doctor": 5
        },
        "education_field": {
            "life sciences": 0, "medical": 1, "marketing": 2,
            "technical degree": 3, "other": 4
        },
        "business_travel": {
            "non-travel": 0, "travel rarely": 1, "travel frequently": 2
        },
        "overtime": {"no": 0, "yes": 1},
        "job_role": {
            "sales executive": 0, "research scientist": 1, "laboratory technician": 2,
            "manufacturing director": 3, "healthcare representative": 4,
            "manager": 5, "sales representative": 6,
            "research director": 7, "human resources": 8
        },
        "department": {
            "sales": 0, "research & development": 1, "human resources": 2
        }
    }

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

    for field in form:
        clean_field = field.strip().lower()
        val = form[field].strip().lower() if isinstance(form[field], str) else form[field]

        if clean_field in mapping:
            processed.append(mapping[clean_field].get(val, 0))
        elif clean_field in numeric_fields:
            try:
                processed.append(int(val))
            except:
                processed.append(0)
        else:
            processed.append(0)

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
                    int(form_data.get('education', 0)),
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
                form_data.get('Years Since Last Promotion'),
                form_data.get('WorkLifeBalance'),
                form_data.get('Job Satisfaction'),
                form_data.get('Environment Satisfaction'),
                form_data.get('Relationship Satisfaction'),
                form_data.get('Monthly Income'),
                form_data.get('percent Salary Hike'),
                form_data.get('Stock Option Level')
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
            features = preprocess_input(data)
            selected_sections = data.get("selected_sections", "1_2_3")
            # Detect selected sections
            section_1_2_3 = ['employee_age','business_travel','distance_from_home','education','education_field','employee_number','gender','marital_status','companies_worked','overtime','performance_rating','total_working_years','training_times_last_year']
            section_4 = ['department','job_involvement','job_level','job_role']
            section_5 = ['environment_satisfaction','job_satisfaction','relationship_satisfaction','work_life_balance']
            section_6 = ['monthly_income','salary_hike','stock_option_level','years_at_company','years_in_role','years_since_last_promotion','years_with_manager']

            selected_sections = data.get("selected_sections", "1_2_3")
            model_path = f"models/model_{selected_sections}.pkl"
            
            # ✅ Your line goes here
            dynamic_model = joblib.load(model_path)

            # Get columns used in each section
            section_1_2_3 = ['employee_age','business_travel','distance_from_home','education','education_field','employee_number','gender','marital_status','companies_worked','overtime','performance_rating','total_working_years','training_times_last_year']
            section_4 = ['department','job_involvement','job_level','job_role']
            section_5 = ['environment_satisfaction','job_satisfaction','relationship_satisfaction','work_life_balance']
            section_6 = ['monthly_income','salary_hike','stock_option_level','years_at_company','years_in_role','years_since_last_promotion','years_with_manager']

            selected = ['1', '2', '3']
# --- Encoding the Fields ---
            features = [
                int(data['Age']),
                bt_map.get(data['BusinessTravel'].lower(), 0),
                int(data['DistanceFromHome']),
                int(data['Education']),
                ef_map.get(data['EducationField'].lower(), 0),
                int(data['EmployeeNumber']),
                gender_map.get(data['Gender'].lower(), 0),
                ms_map.get(data['MaritalStatus'].lower(), 0),
                int(data['NumCompaniesWorked']),
                ot_map.get(data['OverTime'].lower(), 0),
                int(data['PerformanceRating']),
                int(data['TotalWorkingYears']),
                int(data['TrainingTimesLastYear'])
            ]

            columns = section_1_2_3[:]

            for i, section in enumerate([section_4, section_5, section_6], start=4):
                if any(data[col] not in [None, '', 'None'] for col in section):
                    selected.append(str(i))
                    columns.extend(section)

            # Build features
            for col in columns:
                val = data[cursor.column_names.index(col)]
                features.append(int(val) if val is not None else 0)

            selected_sections = request.form.get('checked_sections') # 🧠 TRACKED SECTION VALUES
            model_key = selected_sections
            model_filename = f'models/model_{model_key}.pkl'

            with open(model_filename, 'rb') as f:
                model = pickle.load(f)
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

# Cache recently loaded models using a dictionary 
loaded_models = {}

def load_model(model_path):
    if model_path in loaded_models:
        return loaded_models[model_path]
    with open(model_path, 'rb') as f:
        model = pickle.load(f)

    loaded_models[model_path] = model
    return model


# Run Server
if __name__ == '__main__':
    app.run(debug=True)
