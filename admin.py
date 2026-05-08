from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from functools import wraps
import os
from dotenv import load_dotenv
from supabase_client import (
    supabase_get,
    supabase_get_one,
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

def role_required(*allowed_roles):
    """Restrict access to specific roles. 'admin' can access everything."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not session.get('admin_logged_in'):
                return redirect(url_for('admin.login'))
            
            user = session.get('admin_user', {})
            user_roles = user.get('roles', [])
            
            # Admin role can access everything
            if 'admin' in user_roles:
                return f(*args, **kwargs)
            
            # Check if any of the user's roles match allowed roles
            for role in user_roles:
                if role in allowed_roles:
                    return f(*args, **kwargs)
            
            return redirect(url_for('admin.dashboard'))
        return decorated_function
    return decorator

# ==================== LOGIN ====================
@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        # Check against database
        users = supabase_get('admin_users', {'username': f'eq.{username}', 'is_active': 'eq.true'})
        
        if users and users[0]['password'] == password:
            user = users[0]
            
            # Parse roles from database
            roles = user.get('roles', [])
            if not roles or roles == '{}':
                if user.get('role'):
                    roles = [user['role']]
                else:
                    roles = ['user']
            elif isinstance(roles, str):
                # Convert Supabase array string to Python list
                roles = roles.strip('{}').split(',') if roles.strip('{}') else [user.get('role', 'user')]
            
            session['admin_logged_in'] = True
            session['admin_user'] = {
                'id': user['id'],
                'username': user['username'],
                'display_name': user['display_name'],
                'role': roles[0] if roles else 'user',
                'roles': roles,
                'department': user.get('department', '')
            }
            return redirect(url_for('admin.dashboard'))
        else:
            error = 'Invalid username or password.'
    
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
@role_required('admin')
def settings():
    message = None
    error = None
    
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
            'about_intro': request.form.get('about_intro'),
            'about_description': request.form.get('about_description'),
        }
        
        for key, value in updates.items():
            if value is not None:
                try:
                    existing = supabase_get('site_settings', {'setting_key': f'eq.{key}'})
                    if existing:
                        supabase_update('site_settings', existing[0]['id'], {'setting_value': value})
                    else:
                        supabase_insert('site_settings', {'setting_key': key, 'setting_value': value})
                except Exception as e:
                    print(f"Error updating {key}: {e}")
        
        message = "Settings saved successfully!"
    
    current_settings = get_site_settings()
    return render_template('admin/settings.html', settings=current_settings, message=message, error=error)

# ==================== PRAYER RHYTHMS ====================
@admin_bp.route('/prayer-rhythms', methods=['GET', 'POST'])
@role_required('admin')
def manage_prayer_rhythms():
    message = None
    if request.method == 'POST':
        supabase_insert('prayer_rhythms', {
            'title': request.form.get('title'),
            'description': request.form.get('description'),
            'icon': request.form.get('icon', 'fa-pray'),
            'schedule': request.form.get('schedule'),
            'display_order': int(request.form.get('display_order', 0))
        })
        message = "Prayer rhythm added!"
    rhythms = supabase_get('prayer_rhythms', {'order': 'display_order.asc'})
    return render_template('admin/prayer-rhythms.html', rhythms=rhythms, message=message)

@admin_bp.route('/prayer-rhythms/<int:id>/delete', methods=['POST'])
@role_required('admin')
def delete_prayer_rhythm(id):
    supabase_delete('prayer_rhythms', id)
    return redirect(url_for('admin.manage_prayer_rhythms'))

# ==================== FAMILY GROUPS ====================
@admin_bp.route('/family-groups', methods=['GET', 'POST'])
@role_required('admin')
def manage_family_groups():
    message = None
    if request.method == 'POST':
        supabase_insert('family_groups', {
            'name': request.form.get('name'),
            'city': request.form.get('city'),
            'leader': request.form.get('leader'),
            'meeting_time': request.form.get('meeting_time'),
            'description': request.form.get('description'),
            'contact_email': request.form.get('contact_email')
        })
        message = "Family group added!"
    groups = supabase_get('family_groups', {'order': 'city.asc'})
    return render_template('admin/family-groups-manage.html', groups=groups, message=message)

@admin_bp.route('/family-groups/<int:id>/delete', methods=['POST'])
@role_required('admin')
def delete_family_group(id):
    supabase_delete('family_groups', id)
    return redirect(url_for('admin.manage_family_groups'))

# ==================== MARKETPLACE ====================
@admin_bp.route('/marketplace', methods=['GET', 'POST'])
@role_required('admin')
def manage_marketplace():
    message = None
    if request.method == 'POST':
        image_url = ''
        image_file = request.files.get('image')
        if image_file and image_file.filename:
            result = upload_image(image_file, folder='generation/marketplace')
            image_url = result['url']
        
        supabase_insert('marketplace_items', {
            'title': request.form.get('title'),
            'category': request.form.get('category'),
            'description': request.form.get('description'),
            'price': request.form.get('price'),
            'seller_name': request.form.get('seller_name'),
            'seller_contact': request.form.get('seller_contact'),
            'image_url': image_url
        })
        message = "Marketplace item added!"
    items = supabase_get('marketplace_items', {'order': 'created_at.desc'})
    return render_template('admin/marketplace-manage.html', items=items, message=message)

@admin_bp.route('/marketplace/<int:id>/delete', methods=['POST'])
@role_required('admin')
def delete_marketplace_item(id):
    supabase_delete('marketplace_items', id)
    return redirect(url_for('admin.manage_marketplace'))

# ==================== RETREATS ====================
@admin_bp.route('/retreats', methods=['GET', 'POST'])
@role_required('admin')
def manage_retreats():
    message = None
    if request.method == 'POST':
        image_url = ''
        image_file = request.files.get('image')
        if image_file and image_file.filename:
            result = upload_image(image_file, folder='generation/retreats')
            image_url = result['url']
        
        supabase_insert('retreats', {
            'title': request.form.get('title'),
            'description': request.form.get('description'),
            'location': request.form.get('location'),
            'start_date': request.form.get('start_date'),
            'end_date': request.form.get('end_date'),
            'image_url': image_url,
            'is_upcoming': request.form.get('is_upcoming') == 'true'
        })
        message = "Retreat added!"
    retreats = supabase_get('retreats', {'order': 'start_date.desc'})
    return render_template('admin/retreats-manage.html', retreats=retreats, message=message)

@admin_bp.route('/retreats/<int:id>/delete', methods=['POST'])
@role_required('admin')
def delete_retreat(id):
    supabase_delete('retreats', id)
    return redirect(url_for('admin.manage_retreats'))

# ==================== SERMONS (CRUD) ====================
@admin_bp.route('/sermons', methods=['GET', 'POST'])
@role_required('admin', 'sermons')
def manage_sermons():
    message = None
    error = None
    
    if request.method == 'POST':
        sermon_id = request.form.get('sermon_id')
        title = request.form.get('title')
        speaker = request.form.get('speaker')
        date = request.form.get('date')
        series = request.form.get('series')
        description = request.form.get('description')
        audio_url = request.form.get('audio_url') or ''
        
        audio_file = request.files.get('audio_file')
        if audio_file and audio_file.filename:
            audio_file.seek(0, 2)
            file_size = audio_file.tell()
            audio_file.seek(0)
            
            if file_size > 40 * 1024 * 1024:
                error = "File too large. Max 40MB. Please compress the MP3."
                sermons = supabase_get('sermons', {'order': 'date.desc'})
                return render_template('admin/sermons.html', sermons=sermons, error=error, message=message)
            
            result = upload_audio(audio_file, folder='generation/sermons')
            audio_url = result['url']
        
        data = {
            'title': title,
            'speaker': speaker,
            'date': date,
            'series': series,
            'description': description,
            'audio_url': audio_url
        }
        
        if sermon_id:
            supabase_update('sermons', int(sermon_id), data)
            message = "Sermon updated!"
        else:
            supabase_insert('sermons', data)
            message = "Sermon added!"
            
            # Send notification for new sermons
            try:
                from brevo_client import send_new_sermon_notification
                send_new_sermon_notification(title, speaker or 'The Generation Family', audio_url, description or '')
            except Exception as e:
                print(f"Sermon notification failed: {e}")
        
    
    sermons = supabase_get('sermons', {'order': 'date.desc'})
    return render_template('admin/sermons.html', sermons=sermons, message=message, error=error)

@admin_bp.route('/sermons/<int:sermon_id>/edit')
@login_required
def edit_sermon(sermon_id):
    sermon = supabase_get_one('sermons', sermon_id)
    sermons = supabase_get('sermons', {'order': 'date.desc'})
    return render_template('admin/sermons.html', sermons=sermons, edit_sermon=sermon)

@admin_bp.route('/sermons/<int:sermon_id>/delete', methods=['POST'])
@login_required
def delete_sermon(sermon_id):
    supabase_delete('sermons', sermon_id)
    return redirect(url_for('admin.manage_sermons'))

# ==================== LEADERSHIP (CRUD) ====================
@admin_bp.route('/leadership', methods=['GET', 'POST'])
@role_required('admin', 'leadership')
def manage_leadership():
    message = None
    error = None
    
    if request.method == 'POST':
        leader_id = request.form.get('leader_id')
        name = request.form.get('name')
        title = request.form.get('title')
        bio = request.form.get('bio')
        display_order = request.form.get('display_order', 0)
        image_url = request.form.get('existing_image_url') or ''
        
        image_file = request.files.get('image')
        if image_file and image_file.filename:
            result = upload_image(image_file, folder='generation/leadership')
            image_url = result['url']
        
        data = {
            'name': name,
            'title': title,
            'bio': bio,
            'display_order': int(display_order),
            'image_url': image_url
        }
        
        if leader_id:
            supabase_update('leadership', int(leader_id), data)
            message = "Leader updated!"
        else:
            supabase_insert('leadership', data)
            message = "Leader added!"
    
    leaders = supabase_get('leadership', {'order': 'display_order.asc'})
    return render_template('admin/leadership.html', leaders=leaders, message=message, error=error)

@admin_bp.route('/leadership/<int:leader_id>/edit')
@login_required
def edit_leader(leader_id):
    leader = supabase_get_one('leadership', leader_id)
    leaders = supabase_get('leadership', {'order': 'display_order.asc'})
    return render_template('admin/leadership.html', leaders=leaders, edit_leader=leader)

@admin_bp.route('/leadership/<int:leader_id>/delete', methods=['POST'])
@login_required
def delete_leader(leader_id):
    supabase_delete('leadership', leader_id)
    return redirect(url_for('admin.manage_leadership'))

# ==================== MINISTRIES (CRUD) ====================
@admin_bp.route('/ministries', methods=['GET', 'POST'])
@role_required('admin', 'ministries')
def manage_ministries():
    message = None
    error = None
    
    if request.method == 'POST':
        ministry_id = request.form.get('ministry_id')
        name = request.form.get('name')
        description = request.form.get('description')
        icon = request.form.get('icon', 'fa-church')
        slug = request.form.get('slug')
        display_order = request.form.get('display_order', 0)
        image_url = request.form.get('existing_image_url') or ''
        
        image_file = request.files.get('image')
        if image_file and image_file.filename:
            result = upload_image(image_file, folder='generation/ministries')
            image_url = result['url']
        
        data = {
            'name': name,
            'description': description,
            'icon': icon,
            'slug': slug,
            'display_order': int(display_order),
            'image_url': image_url
        }
        
        if ministry_id:
            supabase_update('ministries', int(ministry_id), data)
            message = "Ministry updated!"
        else:
            supabase_insert('ministries', data)
            message = "Ministry added!"
    
    ministries = supabase_get('ministries', {'order': 'display_order.asc'})
    return render_template('admin/ministries.html', ministries=ministries, message=message, error=error)

@admin_bp.route('/ministries/<int:ministry_id>/edit')
@login_required
def edit_ministry(ministry_id):
    ministry = supabase_get_one('ministries', ministry_id)
    ministries = supabase_get('ministries', {'order': 'display_order.asc'})
    return render_template('admin/ministries.html', ministries=ministries, edit_ministry=ministry)

@admin_bp.route('/ministries/<int:ministry_id>/delete', methods=['POST'])
@login_required
def delete_ministry(ministry_id):
    supabase_delete('ministries', ministry_id)
    return redirect(url_for('admin.manage_ministries'))

# ==================== TESTIMONIALS (CRUD) ====================
@admin_bp.route('/testimonials', methods=['GET', 'POST'])
@role_required('admin', 'testimonials')
def manage_testimonials():
    message = None
    error = None
    
    if request.method == 'POST':
        testimonial_id = request.form.get('testimonial_id')
        name = request.form.get('name')
        quote = request.form.get('quote')
        
        data = {
            'name': name,
            'quote': quote,
            'is_approved': True
        }
        
        if testimonial_id:
            supabase_update('testimonials', int(testimonial_id), data)
            message = "Testimonial updated!"
        else:
            supabase_insert('testimonials', data)
            message = "Testimonial added!"
    
    testimonials = supabase_get('testimonials', {'order': 'created_at.desc'})
    return render_template('admin/testimonials.html', testimonials=testimonials, message=message, error=error)

@admin_bp.route('/testimonials/<int:id>/edit')
@login_required
def edit_testimonial(id):
    testimonial = supabase_get_one('testimonials', id)
    testimonials = supabase_get('testimonials', {'order': 'created_at.desc'})
    return render_template('admin/testimonials.html', testimonials=testimonials, edit_testimonial=testimonial)

@admin_bp.route('/testimonials/<int:id>/delete', methods=['POST'])
@login_required
def delete_testimonial(id):
    supabase_delete('testimonials', id)
    return redirect(url_for('admin.manage_testimonials'))

# ==================== EVENTS (CRUD) ====================
@admin_bp.route('/events', methods=['GET', 'POST'])
@role_required('admin', 'events')
def manage_events():
    message = None
    error = None
    
    if request.method == 'POST':
        event_id = request.form.get('event_id')
        title = request.form.get('title')
        event_date = request.form.get('event_date')
        event_time = request.form.get('event_time')
        location = request.form.get('location')
        description = request.form.get('description')
        image_url = request.form.get('existing_image_url') or ''
        
        image_file = request.files.get('image')
        if image_file and image_file.filename:
            result = upload_image(image_file, folder='generation/events')
            image_url = result['url']
        
        data = {
            'title': title,
            'event_date': event_date,
            'event_time': event_time,
            'location': location,
            'description': description,
            'image_url': image_url
        }
        
        if event_id:
            supabase_update('events', int(event_id), data)
            message = "Event updated!"
        else:
            supabase_insert('events', data)
            message = "Event added!"
    
    events = supabase_get('events', {'order': 'event_date.asc'})
    return render_template('admin/events.html', events=events, message=message, error=error)

@admin_bp.route('/events/<int:event_id>/edit')
@login_required
def edit_event(event_id):
    event = supabase_get_one('events', event_id)
    events = supabase_get('events', {'order': 'event_date.asc'})
    return render_template('admin/events.html', events=events, edit_event=event)

@admin_bp.route('/events/<int:event_id>/delete', methods=['POST'])
@login_required
def delete_event(event_id):
    supabase_delete('events', event_id)
    return redirect(url_for('admin.manage_events'))

# ==================== BLOG POSTS (CRUD) ====================
@admin_bp.route('/blog', methods=['GET', 'POST'])
@role_required('admin', 'blog')
def manage_blog():
    message = None
    error = None
    
    if request.method == 'POST':
        post_id = request.form.get('post_id')
        title = request.form.get('title')
        slug = request.form.get('slug') or title.lower().replace(' ', '-')
        excerpt = request.form.get('excerpt')
        content = request.form.get('content')
        category = request.form.get('category', 'General')
        published = request.form.get('published') == 'on'
        image_url = request.form.get('existing_image_url') or ''
        
        image_file = request.files.get('image')
        if image_file and image_file.filename:
            result = upload_image(image_file, folder='generation/blog')
            image_url = result['url']
        
        data = {
            'title': title,
            'slug': slug,
            'excerpt': excerpt,
            'content': content,
            'category': category,
            'published': published,
            'image_url': image_url
        }
        
        if post_id:
            supabase_update('blog_posts', int(post_id), data)
            message = "Post updated!"
        else:
            supabase_insert('blog_posts', data)
            message = "Post published!"
    
    posts = supabase_get('blog_posts', {'order': 'created_at.desc'})
    return render_template('admin/blog.html', posts=posts, message=message, error=error)

@admin_bp.route('/blog/<int:post_id>/edit')
@login_required
def edit_blog(post_id):
    post = supabase_get_one('blog_posts', post_id)
    posts = supabase_get('blog_posts', {'order': 'created_at.desc'})
    return render_template('admin/blog.html', posts=posts, edit_post=post)

@admin_bp.route('/blog/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_blog(post_id):
    supabase_delete('blog_posts', post_id)
    return redirect(url_for('admin.manage_blog'))

# ==================== NEWSLETTER ====================
@admin_bp.route('/newsletter', methods=['GET', 'POST'])
@role_required('admin')
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
                    error = "Failed to send. Check Brevo account limits."
            except Exception as e:
                error = f"Error: {str(e)}"
        else:
            error = "Subject and content are required."
    
    return render_template('admin/newsletter.html', message=message, error=error)

# ==================== CONTACT SUBMISSIONS ====================
@admin_bp.route('/messages')
@role_required('admin')
def messages():
    submissions = supabase_get('contact_submissions', {'order': 'created_at.desc'})
    return render_template('admin/messages.html', submissions=submissions)

@admin_bp.route('/messages/<int:id>/read', methods=['POST'])
@login_required
def mark_read(id):
    supabase_update('contact_submissions', id, {'is_read': True})
    return redirect(url_for('admin.messages'))

@admin_bp.route('/messages/<int:id>/delete', methods=['POST'])
@login_required
def delete_message(id):
    supabase_delete('contact_submissions', id)
    return redirect(url_for('admin.messages'))


# ==================== HERO IMAGES ====================
@admin_bp.route('/hero', methods=['GET', 'POST'])
@role_required('admin')
def manage_hero():
    message = None
    error = None
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add':
            image_file = request.files.get('hero_image')
            if image_file and image_file.filename:
                result = upload_image(image_file, folder='generation/hero')
                supabase_insert('hero_images', {
                    'image_url': result['url'],
                    'public_id': result['public_id'],
                    'is_active': True
                })
                message = "Hero image added!"
            else:
                error = "Please select an image."
        
        elif action == 'delete':
            image_id = request.form.get('image_id')
            if image_id:
                supabase_delete('hero_images', int(image_id))
                message = "Image removed."
    
    hero_images = supabase_get('hero_images', {'order': 'created_at.desc'})
    return render_template('admin/hero.html', hero_images=hero_images, message=message, error=error)

# ==================== CREATIVES MANAGEMENT ====================
@admin_bp.route('/creatives', methods=['GET', 'POST'])
@role_required('admin', 'creatives')
def manage_creatives():
    message = None
    error = None
    
    if request.method == 'POST':
        section = request.form.get('section')
        title = request.form.get('title')
        description = request.form.get('description')
        content_url = request.form.get('content_url') or ''
        
        # Handle file upload
        upload_file = request.files.get('content_file')
        if upload_file and upload_file.filename:
            result = upload_image(upload_file, folder=f'generation/creatives/{section}')
            content_url = result['url']
        
        supabase_insert('creatives', {
            'section': section,
            'title': title,
            'description': description,
            'content_url': content_url
        })
        message = "Content added!"
    
    creatives = supabase_get('creatives', {'order': 'created_at.desc'})
    return render_template('admin/creatives.html', creatives=creatives, message=message, error=error)

@admin_bp.route('/creatives/<int:id>/delete', methods=['POST'])
@role_required('admin', 'creatives')
def delete_creative(id):
    supabase_delete('creatives', id)
    return redirect(url_for('admin.manage_creatives'))

@admin_bp.route('/section-images', methods=['GET', 'POST'])
@role_required('admin')
def manage_section_images():
    message = None
    
    if request.method == 'POST':
        section = request.form.get('section')
        image_file = request.files.get('image')
        
        if image_file and image_file.filename:
            result = upload_image(image_file, folder='generation/sections')
            image_url = result['url']
            
            # Check if section already has an image
            existing = supabase_get('section_images', {'section_name': f'eq.{section}'})
            if existing:
                supabase_update('section_images', existing[0]['id'], {'image_url': image_url})
            else:
                supabase_insert('section_images', {'section_name': section, 'image_url': image_url})
            
            message = f"Image for {section} updated!"
    
    images = supabase_get('section_images')
    return render_template('admin/section-images.html', images=images, message=message)

# ==================== STORY SECTIONS ====================
@admin_bp.route('/story-sections', methods=['GET', 'POST'])
@role_required('admin')
def manage_story():
    message = None
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        display_order = request.form.get('display_order', 0)
        supabase_insert('story_sections', {
            'title': title,
            'content': content,
            'display_order': int(display_order)
        })
        message = "Story section added!"
    
    sections = supabase_get('story_sections', {'order': 'display_order.asc'})
    return render_template('admin/story-sections.html', sections=sections, message=message)

# ==================== GIVING INFO ====================
@admin_bp.route('/giving-info', methods=['GET', 'POST'])
@role_required('admin')
def manage_giving():
    message = None
    if request.method == 'POST':
        method = request.form.get('method')
        details = request.form.get('details')
        icon = request.form.get('icon', 'fa-hand-holding-heart')
        display_order = request.form.get('display_order', 0)
        supabase_insert('giving_info', {
            'method': method,
            'details': details,
            'icon': icon,
            'display_order': int(display_order)
        })
        message = "Giving method added!"
    
    methods = supabase_get('giving_info', {'order': 'display_order.asc'})
    return render_template('admin/giving-info.html', methods=methods, message=message)

# ==================== FAQS ====================
@admin_bp.route('/faqs-manage', methods=['GET', 'POST'])
@role_required('admin')
def manage_faqs():
    message = None
    if request.method == 'POST':
        question = request.form.get('question')
        answer = request.form.get('answer')
        display_order = request.form.get('display_order', 0)
        supabase_insert('faqs', {
            'question': question,
            'answer': answer,
            'display_order': int(display_order)
        })
        message = "FAQ added!"
    
    faqs = supabase_get('faqs', {'order': 'display_order.asc'})
    return render_template('admin/faqs-manage.html', faqs=faqs, message=message)

@admin_bp.route('/story-sections/<int:id>/delete', methods=['POST'])
@role_required('admin')
def delete_story(id):
    supabase_delete('story_sections', id)
    return redirect(url_for('admin.manage_story'))

@admin_bp.route('/giving-info/<int:id>/delete', methods=['POST'])
@role_required('admin')
def delete_giving(id):
    supabase_delete('giving_info', id)
    return redirect(url_for('admin.manage_giving'))

@admin_bp.route('/faqs-manage/<int:id>/delete', methods=['POST'])
@role_required('admin')
def delete_faq(id):
    supabase_delete('faqs', id)
    return redirect(url_for('admin.manage_faqs'))

# ==================== MEDIA MANAGEMENT ====================
@admin_bp.route('/media', methods=['GET', 'POST'])
@role_required('admin', 'media')
def manage_media():
    message = None
    error = None
    
    if request.method == 'POST':
        media_type = request.form.get('media_type')
        title = request.form.get('title')
        description = request.form.get('description')
        media_url = request.form.get('media_url') or ''
        
        upload_file = request.files.get('media_file')
        if upload_file and upload_file.filename:
            if media_type == 'audio':
                result = upload_audio(upload_file, folder='generation/media/audio')
            else:
                result = upload_image(upload_file, folder='generation/media/images')
            media_url = result['url']
        
        supabase_insert('media', {
            'media_type': media_type,
            'title': title,
            'description': description,
            'media_url': media_url
        })
        message = "Media added!"
    
    media_items = supabase_get('media', {'order': 'created_at.desc'})
    return render_template('admin/media.html', media_items=media_items, message=message, error=error)

@admin_bp.route('/media/<int:id>/delete', methods=['POST'])
@role_required('admin', 'media')
def delete_media(id):
    supabase_delete('media', id)
    return redirect(url_for('admin.manage_media'))

@admin_bp.route('/users', methods=['GET', 'POST'])
@role_required('admin')
def manage_users():
    message = None
    error = None
    
    if request.method == 'POST':
        action = request.form.get('action')
                
        if action == 'add':
            username = request.form.get('username')
            password = request.form.get('password')
            display_name = request.form.get('display_name')
            department = request.form.get('department', '')
            roles = request.form.getlist('roles')
            primary_role = roles[0] if roles else 'user'
            
            supabase_insert('admin_users', {
                'username': username,
                'password': password,
                'display_name': display_name,
                'role': primary_role,
                'roles': roles,
                'department': department
            })
            message = f"User {display_name} added!"
        
        elif action == 'delete':
            user_id = request.form.get('user_id')
            supabase_delete('admin_users', int(user_id))
            message = "User removed."
        
        elif action == 'toggle':
            user_id = request.form.get('user_id')
            user = supabase_get_one('admin_users', int(user_id))
            if user:
                supabase_update('admin_users', int(user_id), {'is_active': not user['is_active']})
                message = "User status updated."
    
    users = supabase_get('admin_users', {'order': 'created_at.asc'})
    return render_template('admin/users.html', users=users, message=message, error=error)