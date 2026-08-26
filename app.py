from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)  # Kích hoạt CORS cho phép extension gọi API thoải mái

@app.route('/api', methods=['GET'])
def get_tiktok_link():
    tiktok_url = request.args.get('url')
    if not tiktok_url:
        return jsonify({"code": 1, "message": "Thiếu tham số url!"}), 400

    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(tiktok_url, download=False)
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
