import os
import requests
from dotenv import load_dotenv
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

BREVO_API_KEY = os.getenv('BREVO_API_KEY')
BREVO_FROM_EMAIL = os.getenv('BREVO_FROM_EMAIL', 'gizmokzu@gmail.com')
BREVO_TO_EMAIL = os.getenv('BREVO_TO_EMAIL', 'gizmokzu@gmail.com')
BREVO_FROM_NAME = os.getenv('BREVO_FROM_NAME', 'The Generation Family')
BREVO_LIST_ID = int(os.getenv('BREVO_LIST_ID', '3'))


# ==================== TRANSACTIONAL EMAILS ====================

def send_contact_notification(name, email, subject, message):
    """Send email to church when someone submits the contact form."""
    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "accept": "application/json",
        "api-key": BREVO_API_KEY,
        "content-type": "application/json"
    }
    data = {
        "sender": {
            "name": BREVO_FROM_NAME,
            "email": BREVO_FROM_EMAIL
        },
        "to": [{
            "email": BREVO_TO_EMAIL,
            "name": "TGF Admin"
        }],
        "subject": f"New Contact Message: {subject or 'No Subject'}",
        "htmlContent": f"""
        <div style="font-family: Arial, sans-serif; max-width:600px; margin:0 auto;">
            <h2 style="color:#D4AF37;">New Message from Website</h2>
            <p><strong>Name:</strong> {name}</p>
            <p><strong>Email:</strong> {email}</p>
            <p><strong>Subject:</strong> {subject or 'N/A'}</p>
            <hr style="border:1px solid #eee;">
            <p style="white-space: pre-line;">{message}</p>
            <hr style="border:1px solid #eee;">
            <p style="color:#999; font-size:12px;">Sent from the Generation Family website contact form.</p>
        </div>
        """
    }
    
    response = requests.post(url, headers=headers, json=data, verify=False)
    print(f"DEBUG send_contact_notification: status={response.status_code}")
    if response.status_code not in [200, 201]:
        print(f"Brevo contact notification failed: {response.status_code} - {response.text}")
    return response.status_code in [200, 201]


def send_subscriber_welcome(email):
    """Send welcome email to new subscriber."""
    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "accept": "application/json",
        "api-key": BREVO_API_KEY,
        "content-type": "application/json"
    }
    data = {
        "sender": {
            "name": BREVO_FROM_NAME,
            "email": BREVO_FROM_EMAIL
        },
        "to": [{
            "email": email
        }],
        "subject": "Welcome to The Generation Family",
        "htmlContent": f"""
        <div style="font-family: Arial, sans-serif; max-width:600px; margin:0 auto; background:#0a0a0a; color:#fff; padding:40px 30px; border-radius:12px;">
            <h1 style="color:#D4AF37; text-align:center;">Welcome to The Generation Family</h1>
            <p style="text-align:center; font-size:16px; color:#ccc;">Thank you for subscribing. You'll receive updates, sermon notifications, and event reminders straight to your inbox.</p>
            <div style="text-align:center; margin:30px 0;">
                <a href="#" style="background:#D4AF37; color:#000; padding:12px 30px; text-decoration:none; border-radius:50px; font-weight:bold;">Visit Our Website</a>
            </div>
            <p style="color:#666; font-size:12px; text-align:center;">If you did not subscribe, you can ignore this email.</p>
        </div>
        """
    }
    
    response = requests.post(url, headers=headers, json=data, verify=False)
    print(f"DEBUG send_subscriber_welcome: status={response.status_code}")
    return response.status_code in [200, 201]


# ==================== NEWSLETTER SUBSCRIPTION ====================

def add_subscriber_to_brevo(email, name=None):
    url = "https://api.brevo.com/v3/contacts"
    headers = {
        "accept": "application/json",
        "api-key": BREVO_API_KEY,
        "content-type": "application/json"
    }
    
    data = {
        "email": email,
        "listIds": [BREVO_LIST_ID],
        "updateEnabled": True
    }
    
    if name:
        parts = name.split(' ', 1)
        data["attributes"] = {
            "FIRSTNAME": parts[0],
            "LASTNAME": parts[1] if len(parts) > 1 else ""
        }
    
    response = requests.post(url, headers=headers, json=data, verify=False)
    print(f"DEBUG add_subscriber_to_brevo: status={response.status_code}")
    
    if response.status_code not in [200, 201, 204]:
        print(f"Brevo add contact failed: {response.status_code} - {response.text}")
        return False
    
    return 

def send_newsletter_to_all(subject, content):
    """Send a newsletter to all contacts in the Brevo list."""
    
    # Step 1: Get all contacts from the list
    list_url = f"https://api.brevo.com/v3/contacts/lists/{BREVO_LIST_ID}/contacts"
    headers = {
        "accept": "application/json",
        "api-key": BREVO_API_KEY
    }
    
    response = requests.get(list_url, headers=headers, verify=False)
    
    if response.status_code != 200:
        print(f"Failed to fetch contacts: {response.status_code} - {response.text}")
        return False
    
    contacts = response.json().get('contacts', [])
    
    if not contacts:
        print("No contacts in the list.")
        return False
    
    # Step 2: Send to each contact
    send_url = "https://api.brevo.com/v3/smtp/email"
    send_headers = {
        "accept": "application/json",
        "api-key": BREVO_API_KEY,
        "content-type": "application/json"
    }
    
    success_count = 0
    
    for contact in contacts:
        contact_email = contact.get('email')
        if not contact_email:
            continue
        
        data = {
            "sender": {
                "name": BREVO_FROM_NAME,
                "email": BREVO_FROM_EMAIL
            },
            "to": [{
                "email": contact_email
            }],
            "subject": subject,
            "htmlContent": f"""
            <div style="font-family: Arial, sans-serif; max-width:600px; margin:0 auto; background:#0a0a0a; color:#fff; padding:30px; border-radius:12px;">
                <div style="text-align:center; margin-bottom:20px;">
                    <h2 style="color:#D4AF37;">The Generation Family</h2>
                </div>
                <div style="background:#111; padding:25px; border-radius:8px; color:#ccc; line-height:1.8;">
                    {content}
                </div>
                <div style="margin-top:25px; padding-top:20px; border-top:1px solid #1a1a1a; text-align:center;">
                    <p style="color:#666; font-size:12px;">
                        You received this email because you subscribed via our website.<br>
                        <a href="https://app.brevo.com/unsubscribe" style="color:#D4AF37;">Unsubscribe</a>
                    </p>
                </div>
            </div>
            """
        }
        
        send_response = requests.post(send_url, headers=send_headers, json=data, verify=False)
        
        if send_response.status_code in [200, 201]:
            success_count += 1
        else:
            print(f"Failed to send to {contact_email}: {send_response.status_code}")
    
    print(f"Newsletter sent to {success_count}/{len(contacts)} contacts.")
    return success_count > 0

def send_group_approval_email(email, name, group_name):
    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "accept": "application/json",
        "api-key": BREVO_API_KEY,
        "content-type": "application/json"
    }
    data = {
        "sender": {"name": BREVO_FROM_NAME, "email": BREVO_FROM_EMAIL},
        "to": [{"email": email, "name": name}],
        "subject": f"Welcome to {group_name}!",
        "htmlContent": f"""
        <div style="font-family: Arial, sans-serif; max-width:600px; margin:0 auto; background:#0a0a0a; color:#fff; padding:40px 30px; border-radius:12px;">
            <h1 style="color:#D4AF37; text-align:center;">Welcome to {group_name}!</h1>
            <p style="text-align:center; font-size:16px; color:#ccc;">Hi {name},</p>
            <p style="text-align:center; font-size:16px; color:#ccc;">Your request to join <strong style="color:#D4AF37;">{group_name}</strong> has been approved. You are now part of the family!</p>
            <div style="text-align:center; margin:30px 0;">
                <a href="https://generation-family.onrender.com/family-groups" style="background:#D4AF37; color:#000; padding:12px 30px; text-decoration:none; border-radius:50px; font-weight:bold;">View Your Groups</a>
            </div>
            <p style="color:#666; font-size:12px; text-align:center;">The Generation Family — Revival in me. Awakening through us.</p>
        </div>
        """
    }
    response = requests.post(url, headers=headers, json=data, verify=False)
    return response.status_code in [200, 201]

def send_new_sermon_notification(sermon_title, speaker, audio_url, description=''):
    """Send email to all subscribers when a new sermon is uploaded."""
    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "accept": "application/json",
        "api-key": BREVO_API_KEY,
        "content-type": "application/json"
    }
    
    data = {
        "sender": {
            "name": BREVO_FROM_NAME,
            "email": BREVO_FROM_EMAIL
        },
        "to": [{
            "email": BREVO_TO_EMAIL
        }],
        "subject": f"New Sermon: {sermon_title}",
        "htmlContent": f"""
        <div style="font-family: Arial, sans-serif; max-width:600px; margin:0 auto; background:#0a0a0a; color:#fff; padding:30px; border-radius:12px;">
            <div style="text-align:center; margin-bottom:20px;">
                <h2 style="color:#D4AF37;">The Generation Family</h2>
                <p style="color:#ccc; font-size:14px;">New Sermon Available</p>
            </div>
            <div style="background:#111; padding:25px; border-radius:8px; text-align:center;">
                <h3 style="color:#D4AF37; margin-bottom:10px;">{sermon_title}</h3>
                <p style="color:#999; margin-bottom:5px;">Speaker: {speaker}</p>
                <p style="color:#ccc; font-size:14px; line-height:1.6; margin:15px 0;">{description}</p>
                <div style="margin-top:20px;">
                    <a href="{audio_url}" style="background:#D4AF37; color:#000; padding:12px 30px; text-decoration:none; border-radius:50px; font-weight:bold; display:inline-block;">Listen Now</a>
                </div>
            </div>
            <p style="color:#666; font-size:12px; text-align:center; margin-top:20px;">
                You received this because you subscribed via our website.<br>
                <a href="https://app.brevo.com/unsubscribe" style="color:#D4AF37;">Unsubscribe</a>
            </p>
        </div>
        """
    }
    
    response = requests.post(url, headers=headers, json=data, verify=False)
    return response.status_code in [200, 201]