import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict
import os
from dotenv import load_dotenv

load_dotenv()

class EmailNotifier:
    """Send email notifications for new jobs"""
    
    def __init__(self, to_email_override: str | None = None):
        self.enabled = os.getenv("EMAIL_ENABLED", "false").lower() == "true"
        self.from_email = os.getenv("EMAIL_FROM")
        # Allow overriding recipient (e.g. from web form)
        self.to_email = to_email_override or os.getenv("EMAIL_TO")
        self.password = os.getenv("EMAIL_PASSWORD")
        
        if self.enabled and not all([self.from_email, self.to_email, self.password]):
            print("⚠️ Email configuration incomplete. Notifications disabled.")
            self.enabled = False
    
    def send_job_alert(self, jobs: List[Dict]):
        """Send email with new job listings"""
        if not self.enabled or not jobs:
            return
        
        try:
            # Create email
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"🎯 {len(jobs)} New Job Match{'es' if len(jobs) > 1 else ''} Found!"
            msg["From"] = self.from_email
            msg["To"] = self.to_email
            
            # Create HTML body
            html = self._create_html_body(jobs)
            msg.attach(MIMEText(html, "html"))
            
            # Send email
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(self.from_email, self.password)
                server.send_message(msg)
            
            print(f"📧 Email notification sent to {self.to_email}")
            
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
    
    def _create_html_body(self, jobs: List[Dict]) -> str:
        """Create HTML email body"""
        jobs_html = ""
        
        for i, job in enumerate(jobs, 1):
            skills = job.get("skills_matched", [])
            skills_str = ", ".join(skills[:5])  # Show first 5 skills
            
            jobs_html += f"""
            <div style="margin-bottom: 25px; padding: 15px; background: #f5f5f5; border-radius: 8px; border-left: 4px solid #21808d;">
                <h3 style="margin: 0 0 10px 0; color: #1f2121;">
                    {i}. {job.get('role', 'N/A')}
                </h3>
                <p style="margin: 5px 0; color: #626c71;">
                    <strong>Company:</strong> {job.get('company', 'N/A')}<br>
                    <strong>Location:</strong> {job.get('location', 'N/A')}<br>
                    <strong>Skills Matched:</strong> {skills_str}<br>
                    <strong>Posted:</strong> {job.get('date_posted', 'N/A')}
                </p>
                <a href="{job.get('apply_url', '#')}" 
                   style="display: inline-block; margin-top: 10px; padding: 10px 20px; background: #21808d; color: white; text-decoration: none; border-radius: 5px;">
                    View Job →
                </a>
            </div>
            """
        
        html = f"""
        <html>
        <head></head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #21808d; border-bottom: 3px solid #21808d; padding-bottom: 10px;">
                    🎯 New Job Matches Found!
                </h2>
                <p style="font-size: 16px; color: #626c71;">
                    Your LinkedIn Job Tracker found <strong>{len(jobs)} new job{'s' if len(jobs) > 1 else ''}</strong> 
                    matching your skills in Microsoft Fabric, Power BI, and Data Engineering.
                </p>
                
                {jobs_html}
                
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
                <p style="font-size: 14px; color: #999; text-align: center;">
                    Sent by your automated LinkedIn Job Tracker<br>
                    <a href="https://docs.google.com/spreadsheets" style="color: #21808d;">View Full Tracker →</a>
                </p>
            </div>
        </body>
        </html>
        """
        
        return html


if __name__ == "__main__":
    # Test email
    notifier = EmailNotifier()
    
    test_jobs = [{
        "company": "Microsoft",
        "role": "Data Engineer - Fabric",
        "location": "Remote",
        "skills_matched": ["Microsoft Fabric", "Power BI", "Azure"],
        "date_posted": "2025-11-25",
        "apply_url": "https://linkedin.com/jobs/view/123456"
    }]
    
    notifier.send_job_alert(test_jobs)
    print("✅ Email sent!")
