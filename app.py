from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error
import pickle
import joblib
model = joblib.load('/models/model_1_2_3.pkl')

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

# Route: Main Form Page
@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        conn = None
        cursor = None

        try:
            conn = create_connection()
            cursor = conn.cursor()

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

            cursor.execute(insert_query, tuple(data.values()))
            conn.commit()

            # --- Prediction Logic Starts ---
            # Fetch most recent row
            cursor.execute("SELECT * FROM employee_data ORDER BY id DESC LIMIT 1")
            row = cursor.fetchone()

            # Get columns used in each section
            section_1_2_3 = ['employee_age','business_travel','distance_from_home','education','education_field','employee_number','gender','marital_status','companies_worked','overtime','performance_rating','total_working_years','training_times_last_year']
            section_4 = ['department','job_involvement','job_level','job_role']
            section_5 = ['environment_satisfaction','job_satisfaction','relationship_satisfaction','work_life_balance']
            section_6 = ['monthly_income','salary_hike','stock_option_level','years_at_company','years_in_role','years_since_last_promotion','years_with_manager']

            selected = ['1', '2', '3']
            features = []
            columns = section_1_2_3[:]

            for i, section in enumerate([section_4, section_5, section_6], start=4):
                if any(data[col] not in [None, '', 'None'] for col in section):
                    selected.append(str(i))
                    columns.extend(section)

            # Build features
            for col in columns:
                val = row[cursor.column_names.index(col)]
                features.append(int(val) if val is not None else 0)

            model_key = '_'.join(selected)
            model_filename = f'models/model_{model_key}.pkl'

            with open(model_filename, 'rb') as f:
                model = pickle.load(f)

            prediction = model.predict([features])[0]
            flash(f"Prediction: {'Yes' if prediction == 1 else 'No'}")

        except Error as e:
            flash(f"Error: {e}")
            print("Database Error:", e)

        finally:
            if cursor:
                cursor.close()
            if conn is not None:
                try:
                    if conn.is_connected():
                        conn.close()
                except:
                    pass

    return render_template('index.html')

# Convert user form data to input format for model
# Example assuming you’ve preprocessed properly


# Run Server
if __name__ == '__main__':
    app.run(debug=True)
