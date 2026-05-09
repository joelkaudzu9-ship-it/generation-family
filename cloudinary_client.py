import os
import cloudinary
import cloudinary.uploader
import cloudinary.api
from dotenv import load_dotenv

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET'),
    secure=True
)

MAX_IMAGE_SIZE = 10 * 1024 * 1024
MAX_AUDIO_SIZE = 40 * 1024 * 1024

def _check_size(file, max_size, label):
    if hasattr(file, 'seek'):
        file.seek(0, 2)
        size = file.tell()
        file.seek(0)
        if size > max_size:
            raise ValueError(f"File too large. {label} limit is {max_size/(1024*1024):.0f}MB. Your file is {size/(1024*1024):.1f}MB.")

def upload_image(file, folder="generation", public_id=None):
    _check_size(file, MAX_IMAGE_SIZE, "Image")
    options = {
        'folder': folder,
        'resource_type': 'image',
        'transformation': [{'quality': 'auto', 'fetch_format': 'auto'}]
    }
    if public_id:
        options['public_id'] = public_id
    result = cloudinary.uploader.upload(file, **options)
    return {'url': result['secure_url'], 'public_id': result['public_id'], 'width': result['width'], 'height': result['height']}

def upload_audio(file, folder="generation/sermons", public_id=None):
    _check_size(file, MAX_AUDIO_SIZE, "Audio")
    options = {'folder': folder, 'resource_type': 'video', 'format': 'mp3'}
    if public_id:
        options['public_id'] = public_id
    result = cloudinary.uploader.upload(file, **options)
    return {'url': result['secure_url'], 'public_id': result['public_id'], 'duration': result.get('duration', 0)}

def delete_upload(public_id, resource_type='image'):
    result = cloudinary.uploader.destroy(public_id, resource_type=resource_type)
    return result.get('result') == 'ok'

def get_optimized_url(public_id, width=400, height=400, crop='fill'):
    return cloudinary.CloudinaryImage(public_id).build_url(width=width, height=height, crop=crop, gravity='face', quality='auto', fetch_format='auto')