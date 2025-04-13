
import requests
from django.http import HttpResponse
import mimetypes
import os
import yt_dlp
from django.http import StreamingHttpResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import uuid
from django.shortcuts import render, redirect
from .forms import ContactForm
from django.contrib import messages
from urllib.parse import urlparse, unquote
import traceback





def about(request):
    return render(request, 'about.html')


import os
import mimetypes
import requests
from urllib.parse import urlparse, unquote
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

# Supported image MIME types and extensions
VALID_IMAGE_MIME_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/gif": ".gif",
    "image/bmp": ".bmp",
    "image/webp": ".webp",
    "application/octet-stream": ".jpg",  # fallback if server doesn't set proper content-type
}

@csrf_exempt
def download_image(request):
    if request.method == "POST":
        image_url = request.POST.get("url", "").strip()

        if not image_url:
            return HttpResponse("❌ No URL provided", status=400)

        if not image_url.startswith(("http://", "https://")):
            return HttpResponse("❌ Invalid URL. Must start with http:// or https://", status=400)

        try:
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                )
            }

            response = requests.get(image_url, headers=headers, stream=True, timeout=10, allow_redirects=True)

            if response.status_code != 200:
                return HttpResponse("❌ Failed to download image. Server returned an error.", status=400)

            content_type = response.headers.get("Content-Type", "").lower()
            ext = VALID_IMAGE_MIME_TYPES.get(content_type)

            # Fallback using Python mimetypes if unknown content-type
            if not ext:
                ext = mimetypes.guess_extension(content_type) or ".jpg"

            # Get file name or use fallback
            parsed_url = urlparse(image_url)
            original_name = unquote(os.path.basename(parsed_url.path))
            file_base, file_ext = os.path.splitext(original_name)

            if file_ext.lower() not in VALID_IMAGE_MIME_TYPES.values():
                file_name = f"downloaded_image{ext}"
            else:
                file_name = original_name or f"image{ext}"

            return HttpResponse(
                response.content,
                content_type=content_type,
                headers={"Content-Disposition": f'attachment; filename="{file_name}"'}
            )

        except requests.exceptions.Timeout:
            return HttpResponse("❌ Request timed out while downloading the image.", status=408)
        except requests.exceptions.RequestException as e:
            return HttpResponse(f"❌ Error downloading image: {str(e)}", status=400)
        except Exception as e:
            return HttpResponse(f"❌ Unexpected error: {str(e)}", status=500)

    return render(request, "download_image.html")



# VALID_IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"]

# def download_image(request):
#     if request.method == "POST":
#         image_url = request.POST.get("url")

#         if not image_url:
#             return HttpResponse("No URL provided", status=400)

#         if not image_url.startswith(('http://', 'https://')):
#             return HttpResponse("Invalid URL. Please use http:// or https://", status=400)

#         # Validate file extension
#         parsed_url = urlparse(image_url)
#         file_name = os.path.basename(parsed_url.path)
#         file_ext = os.path.splitext(file_name)[1].lower()

#         if file_ext not in VALID_IMAGE_EXTENSIONS:
#             return HttpResponse("URL does not point to a valid image file.", status=400)

#         try:
#             headers = {
#                 "User-Agent": (
#                     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
#                     "AppleWebKit/537.36 (KHTML, like Gecko) "
#                     "Chrome/85.0.4183.121 Safari/537.36"
#                 )
#             }

#             response = requests.get(image_url, headers=headers, stream=True, timeout=10)

#             if response.status_code != 200:
#                 return HttpResponse("Failed to download image. Server returned error.", status=400)

#             file_name = unquote(file_name) or "image.jpg"
#             content_type = response.headers.get("Content-Type") or mimetypes.guess_type(file_name)[0] or "image/jpeg"

#             image_data = response.content
#             resp = HttpResponse(image_data, content_type=content_type)
#             resp['Content-Disposition'] = f'attachment; filename="{file_name}"'
#             return resp

#         except requests.exceptions.RequestException as e:
#             return HttpResponse(f"Error: {str(e)}", status=400)

#     return render(request, "download_image.html")



#working video, audio with 1440hd video downloading in browser 

class VideoDownloadView(View):
    def get(self, request):
        """Render download page."""
        return render(request, "download_video.html")

    @method_decorator(csrf_exempt)
    def post(self, request):
        """Handle supercharged video downloading."""
        video_url = request.POST.get("url", "").strip()
        if not video_url:
            return HttpResponse("❌ No video URL provided.", status=400)

        unique_id = uuid.uuid4().hex[:6]
        output_folder = "downloads"
        os.makedirs(output_folder, exist_ok=True)
        output_template = os.path.join(output_folder, f"%(title)s-{unique_id}.%(ext)s")

        try:
            # Step 1: Probe video info
            probe_opts = {
                'quiet': True,
                'noplaylist': True,
                'skip_download': True,
            }
            with yt_dlp.YoutubeDL(probe_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                protocol = info.get('protocol', '')
                title = info.get('title', f'video-{unique_id}')
                ext = info.get('ext', 'mp4')

            # Step 2: Choose download strategy
            if 'm3u8' in protocol or 'dash' in protocol:
                print(f"[INFO] HLS/DASH stream detected. Falling back to yt-dlp internal.")
                ydl_opts = self._yt_dlp_fallback_opts(output_template)
            else:
                print(f"[INFO] Using aria2c for fast and high-quality download.")
                ydl_opts = self._aria2c_opts(output_template)

            # Step 3: Download video
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=True)
                file_path = ydl.prepare_filename(info)

            if not os.path.exists(file_path):
                return HttpResponse("❌ File not found after download.", status=404)

            return self.serve_file(file_path, title, ext)

        except Exception as e:
            traceback.print_exc()
            return HttpResponse(f"❌ Error: {str(e)}", status=500)

    def _aria2c_opts(self, output_template):
        """Download using aria2c (fast, high quality, minimum 1440p)."""
        return {
            'format': '(bestvideo[height>=1440][ext=mp4]+bestaudio[ext=m4a])/bestvideo+bestaudio/best',
            'outtmpl': output_template,
            'noplaylist': True,
            'merge_output_format': 'mp4',
            'external_downloader': 'aria2c',
            'external_downloader_args': [
                '-x', '16',   # Connections
                '-s', '16',   # Segments
                '-k', '5M'    # Segment size
            ],
            'prefer_ffmpeg': True,
            'quiet': True,
            'no_warnings': True,
            'noprogress': True,
            'progress_hooks': [self.progress_hook],
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4'
            }],
            'extractor_args': {
                'generic': ['impersonate']
            }
        }

    def _yt_dlp_fallback_opts(self, output_template):
        """Fallback downloader for HLS/DASH or unsupported by aria2c."""
        return {
            'format': '(bestvideo[height>=1440][ext=mp4]+bestaudio[ext=m4a])/bestvideo+bestaudio/best',
            'outtmpl': output_template,
            'noplaylist': True,
            'merge_output_format': 'mp4',
            'prefer_ffmpeg': True,
            'quiet': True,
            'no_warnings': True,
            'noprogress': True,
            'progress_hooks': [self.progress_hook],
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4'
            }],
        }

    def progress_hook(self, d):
        """Logs progress."""
        if d['status'] == 'downloading':
            print(f"📥 Downloading: {d.get('_percent_str', '')} at {d.get('_speed_str', '')}")
        elif d['status'] == 'finished':
            print(f"✅ Finished: {d.get('_total_bytes_str', '')} in {d.get('_elapsed_str', '')}")

    def serve_file(self, file_path, title, ext):
        """Serve downloaded file."""
        def file_iterator(file_name, chunk_size=1024 * 1024):
            with open(file_name, 'rb') as f:
                while chunk := f.read(chunk_size):
                    yield chunk

        response = StreamingHttpResponse(file_iterator(file_path), content_type='video/mp4')
        response['Content-Disposition'] = f'attachment; filename="{title}.{ext}"'
        response['Content-Length'] = os.path.getsize(file_path)
        return response




@method_decorator(csrf_exempt, name='dispatch')
class MovieDownloadView(View):

    def get(self, request):
        # Renders the HTML template for movie download input
        return render(request, "download_movie.html")

    def post(self, request):
        movie_url = request.POST.get("url", "").strip()

        if not movie_url or not movie_url.startswith(("http://", "https://")):
            return HttpResponse("❌ Invalid movie URL. Please try again.", status=400)

        unique_id = uuid.uuid4().hex[:6]
        output_folder = "downloads"
        os.makedirs(output_folder, exist_ok=True)
        output_template = os.path.join(output_folder, f"%(title)s-{unique_id}.%(ext)s")

        try:
            print("🔍 Probing URL:", movie_url)
            with yt_dlp.YoutubeDL({'quiet': True, 'noplaylist': True, 'skip_download': True}) as ydl:
                info = ydl.extract_info(movie_url, download=False)
                protocol = info.get('protocol', '')
                title = info.get('title', f'movie-{unique_id}')
                ext = info.get('ext', 'mp4')

            print(f"🎯 Video Title: {title} | Protocol: {protocol}")

            # Select downloader
            if 'm3u8' in protocol or 'dash' in protocol:
                ydl_opts = self._yt_dlp_fallback_opts(output_template)
            else:
                ydl_opts = self._aria2c_opts(output_template)

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(movie_url, download=True)
                    file_path = ydl.prepare_filename(info)
            except Exception:
                print("⚠️ aria2c failed, falling back to yt-dlp...")
                ydl_opts = self._yt_dlp_fallback_opts(output_template)
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(movie_url, download=True)
                    file_path = ydl.prepare_filename(info)

            if not os.path.exists(file_path):
                return HttpResponse("❌ Download failed. File not found.", status=404)

            print("✅ Download successful! Serving file...")
            return self.serve_file(file_path, title, ext)

        except Exception as e:
            traceback_str = traceback.format_exc()
            print("🔥 Error during download:\n", traceback_str)
            return HttpResponse(f"❌ Unexpected error: {str(e)}", status=500)

    def _aria2c_opts(self, output_template):
        return {
            'format': '(bestvideo[height>=720][ext=mp4]+bestaudio[ext=m4a])/best',
            'outtmpl': output_template,
            'noplaylist': True,
            'merge_output_format': 'mp4',
            'external_downloader': 'aria2c',
            'external_downloader_args': ['-x', '16', '-s', '16', '-k', '5M'],
            'prefer_ffmpeg': True,
            'quiet': False,
            'no_warnings': True,
            'progress_hooks': [self.progress_hook],
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4'
            }],
        }

    def _yt_dlp_fallback_opts(self, output_template):
        return {
            'format': '(bestvideo[height>=720][ext=mp4]+bestaudio[ext=m4a])/best',
            'outtmpl': output_template,
            'noplaylist': True,
            'merge_output_format': 'mp4',
            'prefer_ffmpeg': True,
            'quiet': False,
            'no_warnings': True,
            'progress_hooks': [self.progress_hook],
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4'
            }],
        }

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            print(f"⬇️ Downloading: {d.get('_percent_str', '')} at {d.get('_speed_str', '')}")
        elif d['status'] == 'finished':
            print(f"✅ Finished downloading in {d.get('_elapsed_str', '')}")

    def serve_file(self, file_path, title, ext):
        def file_iterator(file_name, chunk_size=1024 * 1024):
            with open(file_name, 'rb') as f:
                while chunk := f.read(chunk_size):
                    yield chunk

        response = StreamingHttpResponse(file_iterator(file_path), content_type='video/mp4')
        response['Content-Disposition'] = f'attachment; filename="{title}.{ext}"'
        response['Content-Length'] = os.path.getsize(file_path)
        return response


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your message has been sent successfully!')
            return redirect('contact')  # make sure your URL name is 'contact'
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ContactForm()

    return render(request, 'contact.html', {'form': form})
