from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from functools import wraps
import os
from dotenv import load_dotenv
from supabase_client import (
    supabase_get,
    supabase_insert,
    supabase_update,
    supabase_delete,
    get_site_settings
)
from cloudinary_client import upload_image, upload_audio

load_dotenv()

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'generation2026')

# ==================== LOGIN DECORATOR ====================
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

# ==================== LOGIN ====================
@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin.dashboard'))
        error = 'Incorrect password.'
    return render_template('admin/login.html', error=error)

@admin_bp.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin.login'))

# ==================== DASHBOARD ====================
@admin_bp.route('/')
@login_required
def dashboard():
    return render_template('admin/dashboard.html')

# ==================== SITE SETTINGS ====================
@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        updates = {
            'mission': request.form.get('mission'),
            'vision': request.form.get('vision'),
            'values': request.form.get('values'),
            'lives_impacted': request.form.get('lives_impacted'),
            'years_in_existence': request.form.get('years_in_existence'),
            'cities': request.form.get('cities'),
            'meetings_held': request.form.get('meetings_held'),
            'year_theme': request.form.get('year_theme'),
            'hero_tagline': request.form.get('hero_tagline'),
            'church_address': request.form.get('church_address'),
            'church_phone': request.form.get('church_phone'),
            'church_email': request.form.get('church_email'),
        }
        
        for key, value in updates.items():
            if value:
                try:
                    # Check if setting exists
                    existing = supabase_get('site_settings', {'setting_key': f'eq.{key}'})
                    if existing:
                        supabase_update('site_settings', existing[0]['id'], {'setting_value': value})
                    else:
                        supabase_insert('site_settings', {'setting_key': key, 'setting_value': value})
                except Exception as e:
                    print(f"Error updating {key}: {e}")
        
        return redirect(url_for('admin.settings'))

    current_settings = get_site_settings()
    return render_template('admin/settings.html', settings=current_settings)

# ==================== SERMONS MANAGEMENT ====================
@admin_bp.route('/sermons', methods=['GET', 'POST'])
@login_required
def manage_sermons():
    if request.method == 'POST':
        title = request.form.get('title')
        speaker = request.form.get('speaker')
        date = request.form.get('date')
        series = request.form.get('series')
        description = request.form.get('description')
        audio_url = None

        # Handle audio upload
        audio_file = request.files.get('audio_file')
        if audio_file and audio_file.filename:
            result = upload_audio(audio_file, folder='generation/sermons')
            audio_url = result['url']

        supabase_insert('sermons', {
            'title': title,
            'speaker': speaker,
            'date': date,
            'series': series,
            'description': description,
            'audio_url': audio_url or request.form.get('audio_url') or ''
        })
        return redirect(url_for('admin.manage_sermons'))

    sermons = supabase_get('sermons', {'order': 'date.desc'})
    return render_template('admin/sermons.html', sermons=sermons)

@admin_bp.route('/newsletter', methods=['GET', 'POST'])
@login_required
def newsletter():
    message = None
    error = None
    
    if request.method == 'POST':
        subject = request.form.get('subject')
        content = request.form.get('content')
        
        if subject and content:
            try:
                from brevo_client import send_newsletter_to_all
                result = send_newsletter_to_all(subject, content)
                if result:
                    message = "Newsletter sent successfully to all subscribers!"
                else:
                    error = "Failed to send. Check your Brevo account limits."
            except Exception as e:
                error = f"Error: {str(e)}"
        else:
            error = "Subject and content are required."
    
    return render_template('admin/newsletter.html', message=message, error=error)

@admin_bp.route('/sermons/<int:sermon_id>/delete', methods=['POST'])
@login_required
def delete_sermon(sermon_id):
    supabase_delete('sermons', sermon_id)
    return redirect(url_for('admin.manage_sermons'))

# ==================== LEADERSHIP MANAGEMENT ====================
@admin_bp.route('/leadership', methods=['GET', 'POST'])
@login_required
def manage_leadership():
    if request.method == 'POST':
        name = request.form.get('name')
        title = request.form.get('title')
        bio = request.form.get('bio')
        display_order = request.form.get('display_order', 0)
        image_url = None

        image_file = request.files.get('image')
        if image_file and image_file.filename:
            result = upload_image(image_file, folder='generation/leadership')
            image_url = result['url']

        supabase_insert('leadership', {
            'name': name,
            'title': title,
            'bio': bio,
            'display_order': display_order,
            'image_url': image_url or ''
        })
        return redirect(url_for('admin.manage_leadership'))

    leaders = supabase_get('leadership', {'order': 'display_order.asc'})
    return render_template('admin/leadership.html', leaders=leaders)

@admin_bp.route('/leadership/<int:leader_id>/delete', methods=['POST'])
@login_required
def delete_leader(leader_id):
    supabase_delete('leadership', leader_id)
    return redirect(url_for('admin.manage_leadership'))

# ==================== TESTIMONIALS MANAGEMENT ====================
@admin_bp.route('/testimonials', methods=['GET', 'POST'])
@login_required
def manage_testimonials():
    if request.method == 'POST':
        name = request.form.get('name')
        quote = request.form.get('quote')
        supabase_insert('testimonials', {
            'name': name,
            'quote': quote,
            'is_approved': True
        })
        return redirect(url_for('admin.manage_testimonials'))

    testimonials = supabase_get('testimonials', {'order': 'created_at.desc'})
    return render_template('admin/testimonials.html', testimonials=testimonials)

@admin_bp.route('/testimonials/<int:id>/delete', methods=['POST'])
@login_required
def delete_testimonial(id):
    supabase_delete('testimonials', id)
    return redirect(url_for('admin.manage_testimonials'))

# ==================== EVENTS MANAGEMENT ====================
@admin_bp.route('/events', methods=['GET', 'POST'])
@login_required
def manage_events():
    if request.method == 'POST':
        title = request.form.get('title')
        event_date = request.form.get('event_date')
        event_time = request.form.get('event_time')
        location = request.form.get('location')
        description = request.form.get('description')
        image_url = None

        image_file = request.files.get('image')
        if image_file and image_file.filename:
            result = upload_image(image_file, folder='generation/events')
            image_url = result['url']

        supabase_insert('events', {
            'title': title,
            'event_date': event_date,
            'event_time': event_time,
            'location': location,
            'description': description,
            'image_url': image_url or ''
        })
        return redirect(url_for('admin.manage_events'))

    events = supabase_get('events', {'order': 'event_date.asc'})
    return render_template('admin/events.html', events=events)

@admin_bp.route('/events/<int:event_id>/delete', methods=['POST'])
@login_required
def delete_event(event_id):
    supabase_delete('events', event_id)
    return redirect(url_for('admin.manage_events'))