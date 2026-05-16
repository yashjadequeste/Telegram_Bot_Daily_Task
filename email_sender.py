import os
import smtplib
from datetime import datetime
from email import encoders
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from dotenv import load_dotenv

from logo_utils import get_email_logo_path

load_dotenv()

EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

NAVY = "#1f3b7a"


def get_email_receivers():
    """Multiple receivers: EMAIL_RECEIVERS=a@x.com,b@y.com or EMAIL_RECEIVER=one@mail.com"""
    raw = os.getenv("EMAIL_RECEIVERS") or os.getenv("EMAIL_RECEIVER", "")
    receivers = [r.strip() for r in raw.split(",") if r.strip()]
    return receivers


def build_signature_html():
    return f"""
<table cellpadding="0" cellspacing="0" border="0" style="font-family:Arial,Helvetica,sans-serif;">
  <tr>
    <td style="vertical-align:top; padding-right:24px; border-right:2px solid {NAVY};">
      <p style="margin:0 0 8px 0; font-size:16px; color:#333;">Thanks,</p>
      <p style="margin:0 0 4px 0; font-size:20px; font-weight:bold; color:{NAVY};">Yash Sojitra</p>
      <p style="margin:0 0 2px 0; font-size:14px; color:{NAVY};">Developer</p>
      <p style="margin:0; font-size:14px; color:{NAVY};">JadeQuest</p>
    </td>
    <td style="vertical-align:top; padding-left:24px; font-size:14px; color:{NAVY};">
      <p style="margin:0 0 6px 0;">
        <span style="color:{NAVY};">📞</span>
        <a href="tel:+918141090814" style="color:{NAVY}; text-decoration:underline;">+91-8141090814</a>
      </p>
      <p style="margin:0 0 6px 0;">
        <span style="color:{NAVY};">✉</span>
        <a href="mailto:yash@jadequest.com" style="color:{NAVY}; text-decoration:underline;">yash@jadequest.com</a>
      </p>
      <p style="margin:0;">
        <span style="color:{NAVY};">🌐</span>
        <a href="https://www.jadequest.com" style="color:{NAVY}; text-decoration:underline;">www.jadequest.com</a>
      </p>
    </td>
  </tr>
</table>
<hr style="border:none; border-top:1px solid {NAVY}; margin:20px 0 16px 0;">
<p style="margin:0;">
  <img src="cid:logo" alt="JadeQuest" style="max-width:220px; height:auto; display:block; background:transparent;">
</p>
"""


def send_email(file_path):
    receivers = get_email_receivers()

    if not all([EMAIL_SENDER, EMAIL_PASSWORD]) or not receivers:
        raise ValueError(
            "Set EMAIL_SENDER, EMAIL_PASSWORD, and EMAIL_RECEIVERS (comma-separated) in .env"
        )

    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"Report file not found: {file_path}")

    current_date = datetime.now().strftime("%d-%m-%Y")
    signature = build_signature_html()

    html_body = f"""<!DOCTYPE html>
<html>
<body style="font-family:Arial,Helvetica,sans-serif; font-size:14px; color:#333;">
  <p>Dear Sir/Madam,</p>
  <p>
    I have attached my daily task report for your review.
    Please let me know if you have any questions or require further information.
  </p>
  <br>
  {signature}
</body>
</html>"""

    msg = MIMEMultipart("related")
    msg["Subject"] = f"Daily Report Task - {current_date}"
    msg["From"] = EMAIL_SENDER
    msg["To"] = ", ".join(receivers)

    alt = MIMEMultipart("alternative")
    alt.attach(MIMEText("Please find attached today's daily task report.", "plain"))
    alt.attach(MIMEText(html_body, "html"))
    msg.attach(alt)

    logo_path = get_email_logo_path()
    if logo_path and Path(logo_path).is_file():
        with open(logo_path, "rb") as logo_file:
            logo = MIMEImage(logo_file.read(), _subtype="png")
        logo.add_header("Content-ID", "<logo>")
        logo.add_header("Content-Disposition", "inline", filename="jadequest_logo.png")
        msg.attach(logo)

    with open(path, "rb") as report_file:
        attachment = MIMEBase(
            "application",
            "vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        attachment.set_payload(report_file.read())
        encoders.encode_base64(attachment)
        attachment.add_header(
            "Content-Disposition",
            "attachment",
            filename=f"Daily_Report_{current_date}.xlsx",
        )
        msg.attach(attachment)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
        smtp.send_message(msg)

    print(f"Email sent to: {', '.join(receivers)}")
