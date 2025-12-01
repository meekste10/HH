import csv, json

# -----------------------
# Helper: Read CSV into list of dicts
# -----------------------
def load_csv(name):
    with open(name, newline='', encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))

# -----------------------
# Safe converters
# -----------------------
def safe_float(x):
    try:
        return float(str(x).replace(",", ""))
    except:
        return 0.0

def safe_int(x):
    try:
        return int(float(str(x).replace(",", "")))
    except:
        return 0

# -----------------------
# Normalize name -> empId
# Example: "Barber, Candice" -> "CandiceB"
# -----------------------
def normalize_name(full):
    if not full:
        return ""
    if "," in full:
        last, first = [x.strip() for x in full.split(",", 1)]
    else:
        parts = full.split()
        first, last = parts[0], parts[-1]
    return f"{first}{last[0]}"

# -----------------------
# 1. EMPLOYEES.JSON
# from Employee Reference.csv
# -----------------------
def build_employees(data):
    """
    Build employees.json from Employee Reference.csv.

    Assumes columns (among others):
      Name, Employee Name 1, Department, Direct Report, EmpID,
      Employee Status, Age, Hire Month, Compensation Category, Gender,
      Tenure (in years), Tenure Category,
      Health Ins, Health Plan, Dental Ins, Dental Plan, Vision Ins, Vision Plan,
      401k Enrolled, 401k Eligibility, 401k Elig Date,
      Alabama Tax, Fed Tax (W4),
      Plan ID, Tier, Relationship,
      Health Employee Monthly Cost, Health Employer Monthly Cost,
      Health Employee Weekly Cost, Health Employer Weekly Cost,
      Dental Employee Monthly Cost, Dental Employer Monthly Cost,
      Vision Employee Monthly Cost, Vision Employer Monthly Cost
    """

    out = []

    for row in data:
        emp_id = row.get("EmpID") or normalize_name(
            row.get("Employee Name 1") or row.get("Name") or ""
        )

        emp = {
            # ---- core identity ---
            "empId": emp_id,
            "name": row.get("Employee Name 1") or row.get("Name"),
            "department": row.get("Department"),
            "directReport": row.get("Direct Report"),
            "email1": row.get("Email 1"),
            "email2": row.get("Email 2"),
            "passcode": row.get("Passcode") or "",

            # ---- enrollment + plan names ----
            "healthIns":  (row.get("Health Ins")  or "").strip(),
            "healthPlan": (row.get("Health Plan") or "").strip(),

            "dentalIns":  (row.get("Dental Ins")  or "").strip(),
            "dentalPlan": (row.get("Dental Plan") or "").strip(),

            "visionIns":  (row.get("Vision Ins")  or "").strip(),
            "visionPlan": (row.get("Vision Plan") or "").strip(),

            # ---- 401k + tax codes ----
            "k401Enrolled":     (row.get("401k Enrolled")   or "").strip(),
            "k401Eligibility":  (row.get("401k Eligibility") or "").strip(),
            "k401EligibleDate": (row.get("401k Elig Date")   or "").strip(),

            "alabamaTaxCode": (row.get("Alabama Tax") or "").strip(),
            "fedTaxCode":     (row.get("Fed Tax (W4)") or "").strip(),

            # ---- meta / demographics ----
            "status": row.get("Employee Status"),
            "age": safe_int(row.get("Age")),
            "hireMonth": safe_int(row.get("Hire Month")),
            "compensationCategory": row.get("Compensation Category"),
            "gender": row.get("Gender"),
            "tenure": row.get("Tenure (in years)"),
            "tenureCategory": row.get("Tenure Category"),

            # ---- NEW: per-employee plan cost info (AR+ columns) ----
            "planId":      (row.get("Plan ID") or "").strip(),
            "planTier":    (row.get("Tier") or "").strip(),
            "planRelationship": (row.get("Relationship") or "").strip(),

            "healthEmployeeMonthlyCost":  safe_float(row.get("Health Employee Monthly Cost")),
            "healthEmployerMonthlyCost":  safe_float(row.get("Health Employer Monthly Cost")),
            "healthEmployeeWeeklyCost":   safe_float(row.get("Health Employee Weekly Cost")),
            "healthEmployerWeeklyCost":   safe_float(row.get("Health Employer Weekly Cost")),

            "dentalEmployeeMonthlyCost":  safe_float(row.get("Dental Employee Monthly Cost")),
            "dentalEmployerMonthlyCost":  safe_float(row.get("Dental Employer Monthly Cost")),

            "visionEmployeeMonthlyCost":  safe_float(row.get("Vision Employee Monthly Cost")),
            "visionEmployerMonthlyCost":  safe_float(row.get("Vision Employer Monthly Cost")),
        }

        out.append(emp)

    return out

# -----------------------
# 2. PTO_EMPLOYEE_INFO.JSON
# from PTO Employee Info.csv
# -----------------------
def build_pto_employee_info(data):
    out = []
    for row in data:
        # Try all reasonable name header variants
        name = (
            row.get("Employee Name 1")
            or row.get("Employee Name 2")
            or row.get("NAME")
            or row.get("Name")
            or ""
        )

        # Make sure empId matches employees.json:
        # 1) Prefer EmpID if present
        # 2) Fall back to normalized name
        emp_id = (
            row.get("EmpID")
            or row.get("Employee ID")
            or normalize_name(name)
        )

        out.append({
            "empId": emp_id,
            "name": name,
            "department": row.get("Department"),
            "directReport": row.get("Direct Report"),

            "balances": {
                "vacationBeginning": safe_float(row.get("Vacation Beginning", 0)),
                "vacationApproved": safe_float(row.get("Vacation Approved", 0)),
                "futureVacationApproved": safe_float(row.get("Future Vacation Days Approved", 0)),
                "vacationUsed": safe_float(row.get("Vacation Days Used", 0)),
                "vacationAvailable": safe_float(row.get("Vacation Available", 0)),

                "sickBeginning": safe_float(row.get("Sick Beginning", 0)),
                "sickApproved": safe_float(row.get("Sick Approved", 0)),
                "futureSickDays": safe_float(row.get("Future Sick Days", 0)),
                "sickUsed": safe_float(row.get("Sick Days Used", 0)),
                "sickAvailable": safe_float(row.get("Sick Available", 0)),

                "unpaidBeginning": safe_float(row.get("Unpaid Beginning", 0)),
                "unpaidApproved": safe_float(row.get("Unpaid Approved", 0)),
                "futureUnpaidDays": safe_float(row.get("Future Unpaid Days", 0)),
                "unpaidUsed": safe_float(row.get("Unpaid Days Used", 0)),
                "unpaidAvailable": safe_float(row.get("Unpaid Available", 0))
            },

            "meta": {
                "status": row.get("Employee Status") or row.get("Status"),
                "age": safe_int(row.get("Age", 0)),
                "hireMonth": safe_int(row.get("Hire Month") or row.get("HireMonth") or 0),
                "compensationCategory": row.get("Compensation Category"),
                "gender": row.get("Gender"),
                "tenure": row.get("Tenure (in years)"),
                "tenureCategory": row.get("Tenure Category"),
                "salaryHourly": row.get("Salary/Hourly"),
                "indirectCosOverhead": row.get("Indirect/COS/Overhead"),
                "compensation": row.get("Compensation"),
                "dob": row.get("Date of Birth") or row.get("DOB")
            }
        })
    return out

# -----------------------
# 3. PTO_REQUESTS.JSON
# from PTO Requests.csv
# -----------------------
def build_pto_requests(data):
    out = []
    for row in data:
        name = (
            row.get("Employee Name")
            or row.get("Employee")
            or ""
        )

        # Make empId consistent with employees.json & pto_employee_info.json
        emp_id = (
            row.get("EmpID")
            or row.get("Employee ID")
            or normalize_name(name)
        )

        out.append({
            "id": row.get("Response ID"),
            "empId": emp_id,
            "name": name,
            "type": row.get("PTO Request Type"),
            "startDate": row.get("PTO Request Start Date"),
            "startHalf": row.get("Start AM/PM"),
            "endDate": row.get("PTO Request End Date"),
            "endHalf": row.get("End AM/PM"),
            "totalDays": safe_float(row.get("PTO Request Total Days", 0)),
            "department": row.get("Department"),
            "directReport": row.get("Direct Report"),
            "calendar": {
                "requestMonth": row.get("Month of Start Date"),
                "requestYear": row.get("Year"),
                "weekOfYear": row.get("Week # of year")
            }
        })
    return out

# -----------------------
# 4. CONTACTS.JSON
# from HH_Contacts_2025.csv
# Header you showed:
# First Name,Last Name,Email Address,Work Number,Personal Number,
# Department,Address,Region,Model Home,Model Home Phone,Model Home 2,Model Home 2 Phone
# -----------------------
def build_contacts(data):
    out = []
    for row in data:
        first = row.get("First Name", "").strip()
        last = row.get("Last Name", "").strip()
        full_name = f"{first} {last}".strip()
        emp_id = normalize_name(f"{last}, {first}") if first and last else ""

        model_homes = []
        mh1 = row.get("Model Home", "").strip()
        mh1_phone = row.get("Model Home Phone", "").strip()
        mh2 = row.get("Model Home 2", "").strip()
        mh2_phone = row.get("Model Home 2 Phone", "").strip()

        if mh1 or mh1_phone:
            model_homes.append({
                "name": mh1,
                "phone": mh1_phone
            })
        if mh2 or mh2_phone:
            model_homes.append({
                "name": mh2,
                "phone": mh2_phone
            })

        out.append({
            "empId": emp_id,
            "name": full_name,
            "firstName": first,
            "lastName": last,
            "email": row.get("Email Address"),
            "workNumber": row.get("Work Number"),
            "personalNumber": row.get("Personal Number"),
            "department": row.get("Department"),
            "address": row.get("Address"),
            "region": row.get("Region"),
            "modelHomes": model_homes
        })
    return out

# -----------------------
# MAIN PROGRAM
# -----------------------
def main():
    ref = load_csv("Employee Reference.csv")
    pto_info = load_csv("PTO Employee Info.csv")
    pto_req = load_csv("PTO Requests.csv")
    contacts_csv = load_csv("HH_Contacts_2025.csv")

    # Write JSONs
    with open("employees.json", "w", encoding="utf-8") as f:
        json.dump(build_employees(ref), f, indent=2)

    with open("pto_employee_info.json", "w", encoding="utf-8") as f:
        json.dump(build_pto_employee_info(pto_info), f, indent=2)

    with open("pto_requests.json", "w", encoding="utf-8") as f:
        json.dump(build_pto_requests(pto_req), f, indent=2)

    with open("contacts.json", "w", encoding="utf-8") as f:
        json.dump(build_contacts(contacts_csv), f, indent=2)

    print("All JSON files created successfully.")

if __name__ == "__main__":
    main()
