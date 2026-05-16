import os
import requests
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

def supabase_get(table, params=None):
    """Fetch records from a Supabase table."""
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()
    return response.json()

def supabase_get_one(table, record_id):
    """Fetch a single record by ID."""
    url = f"{SUPABASE_URL}/rest/v1/{table}?id=eq.{record_id}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    data = response.json()
    return data[0] if data else None

def supabase_insert(table, data):
    """Insert a record into a Supabase table."""
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    
    # Convert any Python lists to PostgreSQL array format
    processed_data = {}
    for key, value in data.items():
        if isinstance(value, list):
            processed_data[key] = '{' + ','.join(str(v) for v in value) + '}'
        else:
            processed_data[key] = value
    
    print(f"Inserting into {table}: {processed_data}")  # Debug
    
    response = requests.post(url, headers=HEADERS, json=processed_data)
    
    if response.status_code not in [200, 201]:
        print(f"Supabase insert error: {response.status_code} - {response.text}")
    
    response.raise_for_status()
    return response.json()

def supabase_update(table, record_id, data):
    """Update a record by ID."""
    url = f"{SUPABASE_URL}/rest/v1/{table}?id=eq.{record_id}"
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal'
    }
    
    # Convert any Python lists to PostgreSQL array format
    processed_data = {}
    for key, value in data.items():
        if isinstance(value, list):
            processed_data[key] = '{' + ','.join(str(v) for v in value) + '}'
        else:
            processed_data[key] = value
    
    response = requests.patch(url, headers=headers, json=processed_data)
    if response.status_code not in [200, 201, 204]:
        print(f"Supabase update error: {response.status_code} - {response.text}")
        response.raise_for_status()
    return True

def get_prayer_rhythms():
    return supabase_get('prayer_rhythms', {'order': 'display_order.asc'})

def get_family_groups():
    return supabase_get('family_groups', {'is_active': 'eq.true', 'order': 'city.asc'})

def get_marketplace_items():
    return supabase_get('marketplace_items', {'is_available': 'eq.true', 'order': 'created_at.desc'})

def get_retreats():
    return supabase_get('retreats', {'order': 'start_date.desc'})

def get_upcoming_retreat():
    retreats = supabase_get('retreats', {'is_upcoming': 'eq.true', 'order': 'start_date.asc', 'limit': '1'})
    return retreats[0] if retreats else None

def get_creatives(section=None):
    params = {'order': 'created_at.desc'}
    if section:
        params['section'] = f'eq.{section}'
    return supabase_get('creatives', params)

def get_media(media_type=None):
    params = {'order': 'created_at.desc'}
    if media_type:
        params['media_type'] = f'eq.{media_type}'
    return supabase_get('media', params)

def get_section_images():
    images = supabase_get('section_images')
    return {item['section_name']: item['image_url'] for item in images}

def get_story_sections():
    return supabase_get('story_sections', {'order': 'display_order.asc'})

def get_giving_info():
    return supabase_get('giving_info', {'order': 'display_order.asc'})

def get_faqs():
    return supabase_get('faqs', {'order': 'display_order.asc'})

def supabase_delete(table, record_id):
    """Delete a record by ID."""
    url = f"{SUPABASE_URL}/rest/v1/{table}?id=eq.{record_id}"
    response = requests.delete(url, headers=HEADERS)
    response.raise_for_status()
    return True

# Time-saving shortcuts
def get_leadership():
    return supabase_get('leadership', {'order': 'display_order.asc'})

def get_ministries():
    return supabase_get('ministries', {'order': 'display_order.asc'})

def get_sermons():
    return supabase_get('sermons', {'order': 'date.desc'})

def get_testimonials():
    return supabase_get('testimonials', {'is_approved': 'eq.true'})

def get_events():
    return supabase_get('events', {'order': 'event_date.asc'})

def get_site_settings():
    settings = supabase_get('site_settings')
    return {item['setting_key']: item['setting_value'] for item in settings}

def get_blog_posts():
    return supabase_get('blog_posts', {'published': 'eq.true', 'order': 'created_at.desc'})

def get_group_announcements(group_id):
    return supabase_get('group_announcements', {'group_id': f'eq.{group_id}', 'order': 'created_at.desc', 'limit': '5'})

def get_group_members(group_id):
    return supabase_get('group_members', {'group_id': f'eq.{group_id}', 'is_visible': 'eq.true'})

def get_group_gallery(group_id):
    return supabase_get('group_gallery', {'group_id': f'eq.{group_id}', 'order': 'uploaded_at.desc', 'limit': '12'})

def get_group_posts(group_id):
    return supabase_get('group_posts', {'group_id': f'eq.{group_id}', 'order': 'created_at.desc', 'limit': '10'})