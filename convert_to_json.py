import csv, json

# -----------------------
# Helper: Read CSV into list of dicts
# -----------------------
def load_csv(name):
    with open(name, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

# -----------------------
# 1. EMPLOYEES.JSON
# -----------------------
def build_employees(data):
    out = []
    for row in data:
        out.append({
            "empId": row.get("EmpID") or row.get("EmployeeID"),
            "name": row.get("Name"),
            "department": row.get("Department"),
            "directReport": row.get("Direct Report"),
            "email": row.get("Email 1"),
            "passcode": row.get("Passcode")
        })
    return out

# -----------------------
# 2. PTO_EMPLOYEE_INFO.JSON
# -----------------------
def build_pto_employee_info(data):
    out = []
    for row in data:
        out.append({
            "empId": normalize_name(row["NAME"]),
            "name": row["NAME"],
            "department": row["Department"],
            "directReport": row["Direct Report"],

            "balances": {
                "vacationBeginning": safe_float(row["Vacation Beginning"]),
                "vacationApproved": safe_float(row["Vacation Approved"]),
                "futureVacationApproved": safe_float(row["Future Vacation Days Approved"]),
                "vacationUsed": safe_float(row["Vacation Days Used"]),
                "vacationAvailable": safe_float(row["Vacation Available"]),

                "sickBeginning": safe_float(row["Sick Beginning"]),
                "sickApproved": safe_float(row["Sick Approved"]),
                "futureSickDays": safe_float(row["Future Sick Days"]),
                "sickUsed": safe_float(row["Sick Days Used"]),
                "sickAvailable": safe_float(row["Sick Available"]),

                "unpaidBeginning": safe_float(row["Unpaid Beginning"]),
                "unpaidApproved": safe_float(row["Unpaid Approved"]),
                "futureUnpaidDays": safe_float(row["Future Unpaid Days"]),
                "unpaidUsed": safe_float(row["Unpaid Days Used"]),
                "unpaidAvailable": safe_float(row["Unpaid Available"])
            },

            "meta": {
                "status": row["Employee Status"],
                "age": safe_int(row["Age"]),
                "hireMonth": safe_int(row["Hire Month"]),
                "compensationCategory": row["Compensation Category"],
                "gender": row["Gender"],
                "tenure": row["Tenure (in years)"],
                "tenureCategory": row["Tenure Category"],
                "salaryHourly": row["Salary/Hourly"],
                "indirectCosOverhead": row["Indirect/COS/Overhead"],
                "compensation": row["Compensation"],
                "dob": row["DOB"]
            }
        })
    return out

# -----------------------
# Normalize name → empId (same as employees.json)
# -----------------------
def normalize_name(full):
    # Example: “Barber, Candice” → “CandiceB”
    if "," in full:
        last, first = [x.strip() for x in full.split(",")]
    else:
        parts = full.split()
        first, last = parts[0], parts[-1]

    return f"{first}{last[0]}"

# -----------------------
# Safe converters
# -----------------------
def safe_float(x):
    try: return float(x)
    except: return 0

def safe_int(x):
    try: return int(float(x))
    except: return 0

# -----------------------
# 3. PTO_REQUESTS.JSON
# -----------------------
def build_pto_requests(data):
    out = []
    for row in data:
        out.append({
            "id": row["Response ID"],
            "empId": normalize_name(row["Employee Name"]),
            "name": row["Employee Name"],
            "type": row["PTO Request Type"],
            "startDate": row["PTO Request Start Date"],
            "startHalf": row["Start AM/PM"],
            "endDate": row["PTO Request End Date"],
            "endHalf": row["End AM/PM"],
            "totalDays": safe_float(row["PTO Request Total Days"]),
            "department": row["Department"],
            "directReport": row["Direct Report"],
            "calendar": {
                "requestMonth": row["Month of Start Date"],
                "requestYear": row["Year"],
                "weekOfYear": row["Week # of year"]
            }
        })
    return out

# -----------------------
# 4. CONTACTS.JSON
# -----------------------
def build_contacts(data):
    out = []
    for row in data:
        empId = normalize_name(f"{row['Last Name']}, {row['First Name']}")
        out.append({
            "empId": empId,
            "name": f"{row['First Name']} {row['Last Name']}",
            "firstName": row["First Name"],
            "lastName": row["Last Name"],
            "email": row["Email Address"],
            "workNumber": row["Work Number"],
            "personalNumber": row["Personal Number"],
            "department": row["Department"],
            "address": row["Address"],
            "region": row["Region"]
        })
    return out

# -----------------------
# MAIN PROGRAM
# -----------------------
def main():

    ref = load_csv("Employee Reference.csv")
    pto_info = load_csv("PTO Employee Info.csv")
    pto_req = load_csv("PTO Requests.csv")
    contacts = load_csv("HH_Contacts_2025.csv")

    # Write JSONs
    json.dump(build_employees(ref), open("employees.json", "w"), indent=2)
    json.dump(build_pto_employee_info(pto_info), open("pto_employee_info.json", "w"), indent=2)
    json.dump(build_pto_requests(pto_req), open("pto_requests.json", "w"), indent=2)
    json.dump(build_contacts(contacts), open("contacts.json", "w"), indent=2)

    print("All JSON files created successfully.")

if __name__ == "__main__":
    main()
