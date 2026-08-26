from flask import Flask, request, jsonify
import yt_dlp

app = Flask(__name__)

@app.route('/api', methods=['GET'])
def get_tiktok_link():
    tiktok_url = request.args.get('url')
    if not tiktok_url:
        return jsonify({"code": 1, "message": "Thiếu tham số url!"}), 400

    # Cấu hình yt-dlp để lấy link video không logo trực tiếp từ TikTok
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Trích xuất thông tin video dạng JSON
            info = ydl.extract_info(tiktok_url, download=False)
            
            # Lấy link stream video gốc (không watermark)
            video_url = info.get('url') or info.get('formats')[0].get('url')
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
                return jsonify({"code": 1, "message": "Không tìm thấy đường dẫn video!"}), 404

    except Exception as e:
        return jsonify({"code": 1, "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)