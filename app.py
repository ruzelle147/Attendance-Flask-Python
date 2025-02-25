from flask import Flask, render_template, request, redirect, url_for, flash
from flask_pymongo import PyMongo
import qrcode
import io
import base64
from datetime import datetime
from bson import ObjectId

app = Flask(__name__, template_folder="docs")  # Set custom template folder
app.secret_key = "qwe123"

# MongoDB Connection
app.config["MONGO_URI"] = "mongodb+srv://ruzellegabriel:qwe123@cluster.42ut6.mongodb.net/attendance_db?retryWrites=true&w=majority"
mongo = PyMongo(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form.get("name", "").strip()
        position = request.form.get("position", "").strip()

        if name and position:
            existing_employee = mongo.db.employees.find_one({"name": name, "position": position})
            if existing_employee:
                flash("Employee already registered!", "warning")
            else:
                employee_data = {"name": name, "position": position}
                inserted = mongo.db.employees.insert_one(employee_data)

                qr_data = str(inserted.inserted_id)
                qr = qrcode.make(qr_data)
                buffer = io.BytesIO()
                qr.save(buffer, format="PNG")
                qr_base64 = base64.b64encode(buffer.getvalue()).decode()

                mongo.db.employees.update_one(
                    {"_id": inserted.inserted_id},
                    {"$set": {"qr_data": qr_data, "qr_code": qr_base64}}
                )
                flash("Employee registered successfully!", "success")

        return redirect(url_for('index'))

    employees = list(mongo.db.employees.find())
    attendance = list(mongo.db.attendance.find().sort("checkin_time", -1))

    for att in attendance:
        if "checkin_time" in att and isinstance(att["checkin_time"], str):
            att["checkin_time"] = datetime.fromisoformat(att["checkin_time"])

    return render_template('index.html', employees=employees, attendance=attendance)

@app.route('/checkin', methods=['POST'])
def checkin():
    qr_data = request.form.get("qr_code", "").strip()
    if not qr_data:
        flash("Invalid QR Code input!", "danger")
        return redirect(url_for('index'))

    employee = mongo.db.employees.find_one({"qr_data": qr_data})
    if employee:
        today = datetime.now().strftime('%Y-%m-%d')
        existing_checkin = mongo.db.attendance.find_one({
            "employee_id": ObjectId(employee["_id"]),
            "checkin_time": {"$regex": f"^{today}"}
        })

        if existing_checkin:
            flash(f"{employee['name']} has already checked in today!", "warning")
        else:
            checkin_time = datetime.now().isoformat()
            mongo.db.attendance.insert_one({
                "employee_id": ObjectId(employee["_id"]),
                "name": employee["name"],
                "position": employee["position"],
                "checkin_time": checkin_time
            })
            flash(f"{employee['name']} checked in at {datetime.fromisoformat(checkin_time).strftime('%Y-%m-%d %H:%M:%S')}", "success")
    else:
        flash("Invalid QR Code. Employee not found!", "danger")

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
