from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash, make_response
from supabase_client import (
    get_leadership,
    get_ministries,
    get_sermons,
    get_testimonials,
    get_events,
    get_site_settings,
    get_blog_posts,
    get_prayer_rhythms,
    get_family_groups,
    get_marketplace_items,
    get_retreats,
    get_creatives,
    get_media,
    get_section_images,
    get_group_announcements,
    get_group_members,
    get_group_gallery,
    get_story_sections,
    get_giving_info,
    get_faqs,
    supabase_insert,
    supabase_get
)

from functools import wraps

from admin import admin_bp
import os
port = int(os.environ.get('PORT', 5000))
app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'generation-family-secret-key-2026')
app.register_blueprint(admin_bp)

@app.context_processor
def inject_settings():
    return {
        'settings': get_site_settings(),
        'section_images': get_section_images()
    }

@app.context_processor
def inject_member():
    member = None
    if session.get('member_id'):
        members = supabase_get('members', {'id': f'eq.{session["member_id"]}'})
        member = members[0] if members else None
    return {'current_member': member}


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('member_id'):
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('member_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.template_filter('linebreaks')
def linebreaks_filter(value):
    """Convert newlines to <br> tags, preserve paragraphs"""
    if not value:
        return ''
    # Split into paragraphs by double newlines
    paragraphs = value.split('\n\n')
    result = []
    for para in paragraphs:
        if para.strip():
            # Replace single newlines with <br> inside paragraph
            para = para.replace('\n', '<br>')
            result.append(f'<p>{para}</p>')
    return ''.join(result)

@app.route('/')
def home():
    settings = get_site_settings()
    leadership = get_leadership()
    ministries = get_ministries()
    testimonials = get_testimonials()
    hero_images = supabase_get('hero_images', {'is_active': 'eq.true', 'order': 'created_at.desc'})
    events = get_events()
    
    # Get the next upcoming event
    next_event = events[0] if events else None
    
    return render_template(
        'index.html',
        settings=settings,
        leadership=leadership,
        ministries=ministries,
        testimonials=testimonials,
        hero_images=hero_images,
        next_event=next_event
    )

@app.route('/debug-email')
def debug_email():
    import requests
    import json
    
    # Test Brevo API directly
    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "accept": "application/json",
        "api-key": os.getenv('BREVO_API_KEY'),
        "content-type": "application/json"
    }
    
    data = {
        "sender": {"name": "Test", "email": "gizmokzu@gmail.com"},
        "to": [{"email": "gizmokzu@gmail.com"}],
        "subject": "Test Email from Fly.io",
        "htmlContent": "<h1>Test</h1><p>This is a test email from Fly.io deployment.</p>"
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        return f"""
        <h2>Email Test Results</h2>
        <p>Status Code: {response.status_code}</p>
        <p>Response: {response.text}</p>
        <p>Headers: {dict(response.headers)}</p>
        """
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/podcast.xml')
def podcast_rss():
    sermons_list = get_sermons()
    settings = get_site_settings()
    
    rss = f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" xmlns:content="http://purl.org/rss/1.0/modules/content/">
<channel>
    <title>The Generation Family Sermons</title>
    <link>https://generation.fly.dev</link>
    <description>Life-changing messages from The Generation Family. A spiritual and growth family raising a generation rooted in faith.</description>
    <language>en</language>
    <itunes:author>The Generation Family</itunes:author>
    <itunes:owner>
    <itunes:email>joelkaudzu9@gmail.com</itunes:email>
    <itunes:name>The Generation Family</itunes:name>
    </itunes:owner>
    <itunes:summary>{settings.get('hero_tagline', 'A Spiritual & Growth Family')}</itunes:summary>
    <itunes:image href="{url_for('static', filename='images/og-image.jpg', _external=True)}"/>
    <itunes:category text="Religion &amp; Spirituality"/>
    <itunes:category text="Christianity"/>
    <itunes:explicit>no</itunes:explicit>
'''
    
    for sermon in sermons_list:
        if sermon.get('audio_url'):
            pub_date = sermon.get('date', '')
            rss += f'''
    <item>
        <title>{sermon.get('title', 'Sermon')}</title>
        <description>{sermon.get('description', '')}</description>
        <itunes:summary>{sermon.get('description', '')}</itunes:summary>
        <itunes:author>{sermon.get('speaker', 'The Generation Family')}</itunes:author>
        <enclosure url="{sermon.get('audio_url')}" length="0" type="audio/mpeg"/>
        <guid>{sermon.get('audio_url')}</guid>
        <pubDate>{pub_date}</pubDate>
    </item>'''
    
    rss += '''
</channel>
</rss>'''
    
    response = make_response(rss)
    response.headers['Content-Type'] = 'application/xml'
    return response

# ==================== ABOUT ====================
@app.route('/about')
def about():
    settings = get_site_settings()
    leadership = get_leadership()
    return render_template('about.html', settings=settings, leadership=leadership)

@app.route('/story')
def story():
    sections = get_story_sections()
    return render_template('story.html', story_sections=sections)

@app.route('/giving')
def giving():
    giving_methods = get_giving_info()
    return render_template('giving.html', giving_methods=giving_methods)

@app.route('/faqs')
def faqs():
    faqs = get_faqs()
    return render_template('faqs.html', faqs=faqs)

# ==================== MINISTRIES ====================
@app.route('/ministries')
def ministries():
    ministries = get_ministries()
    return render_template('ministries.html', ministries=ministries)


@app.route('/ministries/<slug>')
def ministry_detail(slug):
    from supabase_client import get_ministries, supabase_get
    
    ministries = get_ministries()
    ministry = next((m for m in ministries if m['slug'] == slug), None)
    
    if not ministry:
        return render_template('404.html'), 404
    
    # Get posts
    posts = supabase_get('ministry_posts', {'ministry_slug': f'eq.{slug}', 'order': 'created_at.desc'})
    
    # Get attachments
    attachments = supabase_get('ministry_attachments', {'ministry_slug': f'eq.{slug}', 'order': 'created_at.desc'})
    
    return render_template('ministry-detail.html', 
                         ministry=ministry, 
                         posts=posts,
                         attachments=attachments)


# ==================== PROGRAMS / EVENTS ====================
@app.route('/programs')
def programs():
    events = get_events()
    return render_template('programs.html', events=events)


# ==================== SERMONS ====================
@app.route('/sermons')
def sermons():
    sermons_list = get_sermons()
    return render_template('sermons.html', sermons=sermons_list)



# ==================== PRAYER RHYTHMS ====================
@app.route('/prayer-rhythms')
def prayer_rhythms():
    rhythms = get_prayer_rhythms()
    return render_template('prayer-rhythms.html', rhythms=rhythms)

# ==================== FAMILY GROUPS ====================
@app.route('/family-groups')
def family_groups():
    groups = get_family_groups()
    
    # Get current member if logged in
    current_member = None
    pending_requests = {}
    
    if session.get('member_id'):
        members = supabase_get('members', {'id': f'eq.{session["member_id"]}'})
        current_member = members[0] if members else None
        
        if current_member:
            requests = supabase_get('group_join_requests', {'email': f'eq.{current_member["email"]}', 'is_contacted': 'eq.false'})
            for req in requests:
                pending_requests[req['group_id']] = True
    
    return render_template('family-groups.html', 
                         groups=groups, 
                         current_member=current_member,
                         pending_requests=pending_requests)

@app.route('/debug-requests')
@login_required
def debug_requests():
    member_id = session['member_id']
    members = supabase_get('members', {'id': f'eq.{member_id}'})
    member = members[0] if members else None
    
    if not member:
        return jsonify({'error': 'Member not found'})
    
    requests = supabase_get('group_join_requests', {'email': f'eq.{member["email"]}'})
    
    return jsonify({
        'member': member,
        'requests': requests
    })

# ==================== MARKETPLACE ====================
@app.route('/marketplace')
def marketplace():
    items = get_marketplace_items()
    return render_template('marketplace.html', items=items)

# ==================== RETREATS ====================
@app.route('/retreats')
def retreats():
    retreats = get_retreats()
    return render_template('retreats.html', retreats=retreats)

# ==================== CREATIVES ====================
@app.route('/creatives')
def creatives():
    creatives = get_creatives()
    return render_template('creatives.html', creatives=creatives)

# ==================== RESOURCES ====================
@app.route('/resources')
def resources():
    return render_template('resources.html')

@app.route('/resources/canvas')
def resources_canvas():
    return render_template('canvas.html')

@app.route('/resources/tgf-music')
def tgf_music():
    music = get_creatives(section='music')
    return render_template('tgf-music.html', items=music)

@app.route('/resources/tgf-drama')
def tgf_drama():
    drama = get_creatives(section='drama')
    return render_template('tgf-drama.html', items=drama)

@app.route('/resources/tgf-poems')
def tgf_poems():
    poems = get_creatives(section='poems')
    return render_template('tgf-poems.html', items=poems)

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/resources/media')
def resources_media():
    media_items = get_media()
    return render_template('media.html', media_items=media_items)

@app.route('/resources/apparel')
def apparel():
    apparel_items = get_marketplace_items()
    return render_template('apparel.html', items=apparel_items)

@app.route('/resources/books')
def books():
    books_items = get_marketplace_items()
    return render_template('books.html', items=books_items)

@app.route('/blog')
def blog():
    posts = get_blog_posts()
    return render_template('blog.html', posts=posts)

# ==================== BLOG ====================
@app.route('/blog/<slug>')
def blog_post(slug):
    posts = supabase_get('blog_posts', {'slug': f'eq.{slug}', 'published': 'eq.true'})
    post = posts[0] if posts else None
    if not post:
        return render_template('404.html'), 404
    recent_posts = supabase_get('blog_posts', {'published': 'eq.true', 'order': 'created_at.desc', 'limit': '3'})
    return render_template('blog-detail.html', post=post, recent_posts=recent_posts)


# ==================== TESTIMONIALS PAGE ====================
# PHASE 4: Added /testimonials route
@app.route('/testimonials')
def testimonies_page():
    testimonials = get_testimonials()
    return render_template('testimonials-page.html', testimonials=testimonials)


# ==================== LEADERSHIP PAGE ====================
# PHASE 4: Added /leadership route
@app.route('/leadership')
def leadership_page():
    leaders = get_leadership()
    return render_template('leadership-page.html', leaders=leaders)


# ==================== CONTACT ====================
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    settings = get_site_settings()
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        supabase_insert('contact_submissions', {
            'name': name,
            'email': email,
            'subject': subject,
            'message': message
        })
        
        try:
            from brevo_client import send_contact_notification
            send_contact_notification(name, email, subject, message)
        except Exception as e:
            print(f"Brevo failed: {e}")
        
        return redirect(url_for('contact') + '?success=1')
    
    success = request.args.get('success') == '1'
    return render_template('contact.html', settings=settings, success=success)

@app.route('/family-groups/<int:group_id>/join', methods=['POST'])
def submit_join_request(group_id):
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    message = request.form.get('message')
    
    if name:
        supabase_insert('group_join_requests', {
            'group_id': group_id,
            'name': name,
            'email': email,
            'phone': phone,
            'message': message
        })
        flash('Join request sent! The group leader will contact you.', 'success')
    return redirect(url_for('family_groups'))

@app.route('/family-groups/<int:group_id>/request-join', methods=['POST'])
@login_required
def request_join_group(group_id):
    member_id = session['member_id']
    
    # Get member details
    members = supabase_get('members', {'id': f'eq.{member_id}'})
    member = members[0] if members else None
    
    if not member:
        flash('Member not found.', 'error')
        return redirect(url_for('family_groups'))
    
    # Check if already has a group
    if member.get('group_id'):
        flash('You are already a member of a family group.', 'error')
        return redirect(url_for('family_groups'))
    
    # Check if already requested this group
    existing = supabase_get('group_join_requests', {
        'email': f'eq.{member["email"]}',
        'group_id': f'eq.{group_id}'
    })
    
    if existing and len(existing) > 0:
        flash('You already have a pending request for this group.', 'info')
        return redirect(url_for('family_groups'))
    
    # Get group info for the flash message
    group = supabase_get_one('family_groups', group_id)
    group_name = group['name'] if group else 'the group'
    
    # Create join request
    supabase_insert('group_join_requests', {
        'group_id': group_id,
        'name': member['full_name'],
        'email': member['email'],
        'phone': member.get('phone', ''),
        'member_id': member_id,
        'message': f'Member {member["full_name"]} requested to join {group_name}.',
        'is_contacted': False
    })
    
    flash(f'Join request sent to {group_name}! The group leader will review your request.', 'success')
    return redirect(url_for('family_groups'))

@app.route('/family-groups/<int:group_id>')
def family_group_detail(group_id):
    groups = get_family_groups()
    group = None
    for g in groups:
        if g['id'] == group_id:
            group = g
            break
    
    if not group:
        return render_template('404.html'), 404
    
    announcements = supabase_get('group_announcements', {'group_id': f'eq.{group_id}', 'order': 'created_at.desc', 'limit': '5'})
    posts = supabase_get('group_posts', {'group_id': f'eq.{group_id}', 'order': 'created_at.desc', 'limit': '10'})
    gallery = supabase_get('group_gallery', {'group_id': f'eq.{group_id}', 'order': 'uploaded_at.desc', 'limit': '12'})
    
    # Get members directly from members table (one-to-one)
    members = supabase_get('members', {'group_id': f'eq.{group_id}', 'is_active': 'eq.true'})
    
    return render_template('family-group-detail.html',
                         group=group,
                         announcements=announcements,
                         members=members,
                         gallery=gallery,
                         posts=posts)

# ==================== MEMBER AUTH ====================
@app.route('/member/signup', methods=['GET', 'POST'])
def member_signup():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email', '')
        phone = request.form.get('phone', '')
        password = request.form.get('password')
        group_id = request.form.get('group_id')
        
        if email:
            existing = supabase_get('members', {'email': f'eq.{email}'})
            if existing:
                groups = get_family_groups()
                return render_template('member-signup.html', groups=groups, error='Email already registered.')
        
        # DON'T add member to members table yet
        # Instead, create a join request first
        
        # Create join request
        join_result = supabase_insert('group_join_requests', {
            'group_id': int(group_id) if group_id else None,
            'name': full_name,
            'email': email,
            'phone': phone,
            'message': f'New member {full_name} requested to join the group.',
            'is_contacted': False
        })
        
        if group_id:
            flash('Join request sent! The group leader will review and approve your membership.', 'info')
        else:
            flash('Welcome to the family! Browse groups to join one.', 'success')
        
        # Log them in but with no group (pending approval)
        # We'll create a member record but keep them inactive until approved
        result = supabase_insert('members', {
            'full_name': full_name,
            'email': email,
            'phone': phone,
            'password': password,
            'group_id': None,  # No group until approved
            'status': 'pending',
            'is_active': False
        })
        
        member_id = result[0]['id']
        session['member_id'] = member_id
        session['member_name'] = full_name
        
        return redirect(url_for('member_dashboard'))
    
    groups = get_family_groups()
    return render_template('member-signup.html', groups=groups)

@app.route('/member/login', methods=['GET', 'POST'])
def member_login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        
        members = supabase_get('members', {'email': f'eq.{email}', 'is_active': 'eq.true'})
        
        if members and members[0]['password'] == password:
            member = members[0]
            session['member_id'] = member['id']
            session['member_name'] = member['full_name']
            flash(f'Welcome back, {member["full_name"]}!', 'success')
            return redirect(url_for('member_dashboard'))
        
        return render_template('member-login.html', error='Invalid email or password.')
    
    return render_template('member-login.html')


@app.route('/member/logout')
def member_logout():
    session.pop('member_id', None)
    session.pop('member_name', None)
    flash('You have been logged out.', 'info')
    return redirect('/')

@app.route('/member/dashboard')
def member_dashboard():
    if not session.get('member_id'):
        return redirect(url_for('member_login'))
    
    member_id = session['member_id']
    
    members = supabase_get('members', {'id': f'eq.{member_id}'})
    member = members[0] if members else None
    
    # Check if member has a pending join request
    if member:
        pending_requests = supabase_get('group_join_requests', {
            'email': f'eq.{member["email"]}',
            'is_contacted': 'eq.false'
        })
        
        if pending_requests and member.get('status') == 'pending':
            flash('Your membership request is pending approval by the group leader.', 'warning')
            return render_template('member-pending.html', member=member, pending_request=pending_requests[0])
    
    # Check if member is approved
    if member and member.get('status') != 'active':
        flash('Your membership is pending approval by the group leader.', 'warning')
        return render_template('member-pending.html', member=member)
    
    group = None
    announcements = []
    posts = []
    gallery = []
    
    if member and member.get('group_id'):
        groups = supabase_get('family_groups', {'id': f'eq.{member["group_id"]}'})
        group = groups[0] if groups else None
        
        if group:
            announcements = supabase_get('group_announcements', {'group_id': f'eq.{group["id"]}', 'order': 'created_at.desc', 'limit': '10'})
            posts = supabase_get('group_posts', {'group_id': f'eq.{group["id"]}', 'order': 'created_at.desc', 'limit': '20'})
            gallery = supabase_get('group_gallery', {'group_id': f'eq.{group["id"]}', 'order': 'uploaded_at.desc', 'limit': '12'})
    
    return render_template('member-dashboard.html', 
                         group=group,
                         announcements=announcements,
                         posts=posts,
                         gallery=gallery)
    
@app.route('/subscribe', methods=['POST'])
def subscribe():
    email = request.form.get('email')
    
    if email:
        try:
            supabase_insert('newsletter_subscribers', {'email': email})
        except:
            pass
        
        try:
            from brevo_client import add_subscriber_to_brevo
            add_subscriber_to_brevo(email)
        except Exception as e:
            print(f"Brevo add subscriber failed: {e}")
        
        try:
            from brevo_client import send_subscriber_welcome
            send_subscriber_welcome(email)
        except Exception as e:
            print(f"Brevo welcome email failed: {e}")
        
        return jsonify({'status': 'success', 'message': 'Subscribed!'})
    
    return jsonify({'status': 'error', 'message': 'Email required.'})


if __name__ == '__main__':
    app.run(debug=True)