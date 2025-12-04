import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime


# GOOGLE_SHEET_NAME should match your sheet's name ("LinkedIn Job Tracker")
GOOGLE_SHEET_NAME = "LinkedIn Job Tracker"


def get_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open(GOOGLE_SHEET_NAME).sheet1
    return sheet


def append_job(sheet, job):
    """Append a job with application tracking columns"""
    row = [
        job.get("company", ""),
        job.get("role", ""),
        job.get("location", ""),
        ", ".join(job.get("skills_matched", [])),
        job.get("date_posted", ""),
        job.get("apply_url", ""),
        job.get("description_excerpt", ""),
        "unread",  # status
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # date-time pulled
        "Saved",   # application status (new!)
        ""         # notes (empty initially)
    ]
    sheet.append_row(row, value_input_option="USER_ENTERED")

    last_row = len(sheet.get_all_values())  # This will be the new row after append
    formula = f'=HYPERLINK(F{last_row}, "Apply")'
    sheet.update_cell(last_row, 11, formula)



def is_duplicate(sheet, job):
    """Check if job already exists using company + role + location"""
    try:
        all_data = sheet.get_all_values()
        
        if len(all_data) > 1:
            all_data = all_data[1:]  # Skip header
        
        job_signature = f"{job.get('company', '').strip().lower()}|{job.get('role', '').strip().lower()}|{job.get('location', '').strip().lower()}"
        
        for row in all_data:
            if len(row) >= 3:
                existing_signature = f"{row[0].strip().lower()}|{row[1].strip().lower()}|{row[2].strip().lower()}"
                if job_signature == existing_signature:
                    # Don't print here, let main loop handle it
                    return True
        
        return False
    except Exception as e:
        print(f"⚠️ Error checking duplicates: {e}")
        return False



# Test run (optional - you can keep or remove this)
if __name__ == "__main__":
    sheet = get_sheet()
    job = {
        "company": "Test Corp",
        "role": "Data Engineer",
        "location": "Remote",
        "skills_matched": ["Microsoft Fabric", "Python"],
        "date_posted": "2024-06-01",
        "apply_url": "https://linkedin.com/jobs/view/test123",
        "description_excerpt": "Test job posting...",
    }
    
    if not is_duplicate(sheet, job['apply_url']):
        append_job(sheet, job)
        print("✅ Job appended to sheet.")
    else:
        print("⏭️ Job already exists, skipping.")
