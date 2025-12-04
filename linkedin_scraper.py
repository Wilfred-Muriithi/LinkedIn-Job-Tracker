from sheet_writer import get_sheet, append_job, is_duplicate  # ✅ All three imported
from email_notifier import EmailNotifier
import httpx
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

MY_SKILLS = [
    "Microsoft Fabric", "DataFlows", "PowerBI", "Azure", "Lakehouse",
    "pyspark", "ADLS", "Medallion Architecture", "Data Engineering"
]

def is_recent_job(date_posted, days_back=7):
    if not date_posted or date_posted == 'Unknown':
        return True
    try:
        job_date = datetime.fromisoformat(date_posted.replace('Z', '+00:00'))
        cutoff_date = datetime.now() - timedelta(days=days_back)
        return job_date >= cutoff_date
    except:
        return True

def get_job_description(job_url):
    try:
        with httpx.Client(timeout=30, headers={"User-Agent": "Mozilla/5.0"}) as client:
            r = client.get(job_url)
            soup = BeautifulSoup(r.text, "lxml")
            desc_elem = soup.select_one('.description__text')
            if desc_elem:
                return desc_elem.get_text(" ", strip=True)
    except Exception:
        pass
    return ""

def fetch_jobs(query, location, num_jobs=10, days_back=7):
    url = (
        "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
        f"?keywords={query}&location={location}&start=0"
    )
    jobs = []
    with httpx.Client(http2=True, timeout=30) as client:
        r = client.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(r.text, "lxml")
        for job_card in soup.select('li'):
            try:
                title = job_card.select_one('.base-search-card__title').text.strip()
                company = job_card.select_one('.base-search-card__subtitle').text.strip()
                location = job_card.select_one('.job-search-card__location').text.strip()
                link = job_card.select_one('.base-card__full-link')['href']
                date_posted = job_card.select_one('time')
                date_posted = date_posted['datetime'] if date_posted else 'Unknown'
                if not is_recent_job(date_posted, days_back):
                    continue
                description = get_job_description(link)
                matched_skills = [skill for skill in MY_SKILLS if skill.lower() in description.lower()]
                if matched_skills:
                    jobs.append({
                        'company': company,
                        'role': title,
                        'location': location,
                        'date_posted': date_posted,
                        'apply_url': link,
                        'skills_matched': matched_skills,
                        'description_excerpt': description[:120] + "..."
                    })
            except Exception:
                continue
    return jobs

if __name__ == "__main__":
    SKILL_KEYWORDS = [
        "Microsoft Fabric", "Power BI", "Azure Data Engineer", "Stream Analytics",
        "Batch Streaming", "Azure Synapse", "Data Analyst", "Data Analysis", "ETL/ELT"
    ]
    LOCATIONS = [
        "Remote", "Kenya", "Anywhere"
    ]

    print("🚀 Multi-Keyword Job Search Starting...")
    print(f"📋 Searching for {len(SKILL_KEYWORDS)} skills across {len(LOCATIONS)} locations")
    print(f"📊 Total combinations: {len(SKILL_KEYWORDS) * len(LOCATIONS)}\n")
    print("="*60)

    sheet = get_sheet()
    total_new = 0
    total_duplicates = 0
    all_new_jobs = []

    for keyword in SKILL_KEYWORDS:
        for location in LOCATIONS:
            print(f"\n🔍 Searching: {keyword} in {location}")
            try:
                results = fetch_jobs(keyword, location, num_jobs=10, days_back=7)
                new_jobs = 0
                duplicate_jobs = 0

                for job in results:
                    if not is_duplicate(sheet, job):
                        append_job(sheet, job)
                        new_jobs += 1
                        all_new_jobs.append(job)
                        print(f"  ✅ Added: {job['role'][:50]} at {job['company']}")
                    else:
                        duplicate_jobs += 1

                total_new += new_jobs
                total_duplicates += duplicate_jobs

                print(f"  📊 {new_jobs} new, {duplicate_jobs} duplicates")

            except Exception as e:
                print(f"  ❌ Error: {e}")
                continue

    print(f"\n{'='*60}")
    print(f"✅ Total new jobs added: {total_new}")
    print(f"⏭️  Total duplicates skipped: {total_duplicates}")
    print(f"🎯 Search complete across {len(SKILL_KEYWORDS)} skills × {len(LOCATIONS)} locations")
    print(f"{'='*60}")

    # 📧 EMAIL ONLY IF THERE ARE NEW JOBS!
    if all_new_jobs:
        notifier = EmailNotifier()
        notifier.send_job_alert(all_new_jobs)
