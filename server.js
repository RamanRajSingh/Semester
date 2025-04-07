const express = require('express');
const bodyParser = require('body-parser');
const mysql = require('mysql2');
const cors = require('cors');

const app = express();
app.use(cors());
app.use(bodyParser.json());

// MySQL connection
const db = mysql.createConnection({
    host: 'localhost',
    user: 'root',
    password: 'Raman@20', // Add your password
    database: 'employee_db'
});

db.connect(err => {
    if (err) throw err;
    console.log("Connected to MySQL!");
});

// Route to insert employee data
app.post('/submit', (req, res) => {
    const { employee_number, employee_age, gender, marital_status } = req.body;

    const query = `
        INSERT INTO employee_demographics (employee_number, employee_age, gender, marital_status)
        VALUES (?, ?, ?, ?)`;

    db.query(query, [employee_number, employee_age, gender, marital_status], (err, result) => {
        if (err) {
            console.error("Error inserting data:", err);
            return res.status(500).send("Failed to insert");
        }
        res.send("Data inserted successfully!");
    });
});

app.listen(3000, () => {
    console.log("Server running on port 3000");
});
