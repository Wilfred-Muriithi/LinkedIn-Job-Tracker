import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from linkedin_scraper import fetch_jobs
from sheet_writer import get_sheet, append_job, is_duplicate
from email_notifier import EmailNotifier


app = Flask(__name__)
CORS(app)


def _parse_input_list(raw_value):
    if isinstance(raw_value, list):
        return [item.strip() for item in raw_value if isinstance(item, str) and item.strip()]
    if isinstance(raw_value, str):
        return [item.strip() for item in raw_value.split(",") if item.strip()]
    return []


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.post("/api/search")
def api_search():
    try:
        data = request.get_json(force=True)
    except Exception:
        return jsonify({"error": "Invalid JSON payload"}), 400

    raw_skills = data.get("skills", [])
    raw_locations = data.get("locations", [])
    target_email = (data.get("email") or "").strip()

    skills = _parse_input_list(raw_skills)
    locations = _parse_input_list(raw_locations)

    errors = []
    if not skills:
        errors.append("Provide at least one skill keyword.")
    if not locations:
        errors.append("Provide at least one location.")
    if not target_email:
        errors.append("Provide a valid email address.")

    if errors:
        return jsonify({"errors": errors}), 400

    sheet = get_sheet()
    all_new_jobs = []
    total_new = 0
    combinations = []

    for keyword in skills:
        for location in locations:
            combinations.append({"skill": keyword, "location": location})
            try:
                results = fetch_jobs(keyword, location, num_jobs=10, days_back=7)
                for job in results:
                    if not is_duplicate(sheet, job):
                        append_job(sheet, job)
                        all_new_jobs.append(job)
                        total_new += 1
            except Exception as exc:
                # Continue with remaining combinations, but log failure
                print(f"Error fetching {keyword} / {location}: {exc}")

    notifier = EmailNotifier(to_email_override=target_email)
    if all_new_jobs:
        notifier.send_job_alert(all_new_jobs)

    return jsonify(
        {
            "total_new": total_new,
            "email_sent": bool(all_new_jobs),
            "combinations_checked": combinations,
        }
    )


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)



