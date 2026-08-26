from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
import os
import tempfile
import traceback

app = Flask(__name__)
CORS(app)

@app.route('/api', methods=['GET'])
@app.route('/api/', methods=['GET'])
def get_tiktok_link():
    tiktok_url = request.args.get('url')
    if not tiktok_url:
        return jsonify({"code": 1, "message": "Thiếu tham số url!"}), 400

    # Lấy chuỗi cookie động do Extension từ trình duyệt người dùng truyền lên qua Header
    dynamic_cookie_string = request.headers.get('X-TikTok-Cookie')
    
    cookie_file_path = None
    cookie_path = 'cookies.txt' # Fallback phòng hờ nếu vẫn dùng file tĩnh
    
    ydl_opts = {
        'format': 'bv*[vcodec^=avc]+ba/b',  # Ép chọn chuẩn H.264/AVC tương thích 100% với thẻ video HTML5 trên trình duyệt
        'quiet': True,
        'no_warnings': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://www.tiktok.com/'
        }
    }

    # Ưu tiên sử dụng cookie động từ người dùng truyền lên
    if dynamic_cookie_string:
        try:
            fd, cookie_file_path = tempfile.mkstemp(suffix='.txt')
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                f.write("# Netscape HTTP Cookie File\n")
                for item in dynamic_cookie_string.split('; '):
                    if '=' in item:
                        parts = item.split('=', 1)
                        name, value = parts[0].strip(), parts[1].strip()
                        f.write(f".tiktok.com\tTRUE\t/\tTRUE\t0\t{name}\t{value}\n")
            ydl_opts['cookiefile'] = cookie_file_path
        except Exception as e:
            print("Lỗi tạo cookie tạm thời:", e)
    elif os.path.exists(cookie_path):
        # Nếu không có cookie động thì dùng tạm file cookies.txt sẵn có trên server (nếu còn)
        ydl_opts['cookiefile'] = cookie_path

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(tiktok_url, download=False)
            
            video_url = None
            if 'url' in info:
                video_url = info['url']
            elif 'formats' in info and len(info['formats']) > 0:
                # Lấy định dạng tốt nhất có hỗ trợ video đầy đủ
                for f in info['formats']:
                    if f.get('vcodec') != 'none' and f.get('acodec') != 'none' and f.get('ext') == 'mp4':
                        video_url = f.get('url')
                        break
                if not video_url:
                    video_url = info['formats'][-1].get('url')
                
            video_id = info.get('id', 'unknown')

            if video_url:
                return jsonify({
                    "code": 0,
                    "data": {
                        "id": video_id,
                        "play": video_url,
                        "hdplay": video_url
                    }
                })
            else:
                return jsonify({"code": 1, "message": "Không tìm thấy đường dẫn video từ yt-dlp!"}), 404

    except Exception as e:
        traceback.print_exc()
        return jsonify({"code": 1, "message": str(e)}), 500

    finally:
        # Dọn dẹp file cookie tạm thời trên RAM/Disk của server sau khi xử lý xong
        if cookie_file_path and os.path.exists(cookie_file_path):
            try:
                os.remove(cookie_file_path)
            except:
                pass

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
