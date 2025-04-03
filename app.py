from flask import Flask, render_template, jsonify, send_from_directory, request
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
import os
import base64

app = Flask(__name__)
notebook_path = "Workforce_attrition_Prediction.ipynb"
image_dir = "static/images"

# Ensure the static/images folder exists
os.makedirs(image_dir, exist_ok=True)

# Run first three cells automatically
def execute_initial_cells():
    with open(notebook_path, "r", encoding="utf-8") as f:
        notebook = nbformat.read(f, as_version=4)

    executor = ExecutePreprocessor(timeout=600, kernel_name="python3")
    notebook.cells = notebook.cells[:3]  # Execute first 3 cells only

    try:
        executor.preprocess(notebook, {'metadata': {'path': os.path.dirname(notebook_path)}})
        print("✅ First three cells executed successfully!")
    except Exception as e:
        print(f"❌ Error executing initial cells: {str(e)}")

# Function to execute a specific cell
def execute_cell(cell_index):
    with open(notebook_path, "r", encoding="utf-8") as f:
        notebook = nbformat.read(f, as_version=4)

    executor = ExecutePreprocessor(timeout=600, kernel_name="python3")
    executed_cells = notebook.cells[:cell_index + 1]  # Execute up to the requested cell
    notebook.cells = executed_cells

    try:
        executor.preprocess(notebook, {'metadata': {'path': os.path.dirname(notebook_path)}})
        output_text = []
        image_paths = []

        for output in notebook.cells[cell_index].outputs:
            if 'text/plain' in output.get('data', {}):
                output_text.append(output['data']['text/plain'])

            if 'image/png' in output.get('data', {}):
                image_data = output['data']['image/png']
                image_path = f"{image_dir}/cell_{cell_index}.png"

                with open(image_path, "wb") as f:
                    f.write(base64.b64decode(image_data))

                image_paths.append(image_path)

        return {"text": "\n".join(output_text) if output_text else None, "images": image_paths if image_paths else None}

    except Exception as e:
        return {"text": f"Error executing cell {cell_index}: {str(e)}", "images": None}

# Function to execute a specific cell with inputs
def execute_cell_with_inputs(cell_index, inputs):
    # Load the notebook
    with open(notebook_path, "r", encoding="utf-8") as f:
        notebook = nbformat.read(f, as_version=4)

    # Modify the specific cell with the inputs
    cell = notebook.cells[cell_index]
    input_code = f"""
employee_number = {inputs['employee_number']}
employee_age = {inputs['employee_age']}
gender = '{inputs['gender']}'
marital_status = '{inputs['marital_status']}'
"""
    cell.source = input_code + "\n" + cell.source

    # Execute the notebook up to the specified cell
    executor = ExecutePreprocessor(timeout=600, kernel_name="python3")
    try:
        executor.preprocess(notebook, {'metadata': {'path': os.path.dirname(notebook_path)}})
        return {"status": "success", "message": "Cell executed successfully!"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Run initial cells on startup
execute_initial_cells()

@app.route("/")
def home():
    notebook = nbformat.read(open(notebook_path, "r", encoding="utf-8"), as_version=4)
    total_cells = len(notebook.cells)
    return render_template("index.html", total_cells=total_cells)

@app.route("/run-cell/<int:cell_index>", methods=["GET", "POST"])
def run_cell(cell_index):
    if request.method == "POST":
        inputs = {
            "employee_number": request.form.get("employee_number"),
            "employee_age": request.form.get("employee_age"),
            "gender": request.form.get("gender"),
            "marital_status": request.form.get("marital_status"),
        }
        result = execute_cell_with_inputs(cell_index, inputs)
        return jsonify(result)
    else:
        if cell_index < 3:
            return jsonify({"output": "⚠️ First three cells are already executed in the backend!"})

        output = execute_cell(cell_index)
        return jsonify(output)

@app.route('/static/images/<path:filename>')
def serve_image(filename):
    return send_from_directory(image_dir, filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
