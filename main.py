from flask import Flask, jsonify, request
import instaloader
import os
import json
import tempfile

app = Flask(__name__)

def get_loader():
    L = instaloader.Instaloader()
    
    cookies_json = os.environ.get('IG_COOKIES')
    if cookies_json:
        cookies = json.loads(cookies_json)
        import http.cookiejar
        for cookie in cookies:
            c = http.cookiejar.Cookie(
                version=0,
                name=cookie['name'],
                value=cookie['value'],
                port=None,
                port_specified=False,
                domain=cookie.get('domain', '.instagram.com'),
                domain_specified=True,
                domain_initial_dot=cookie.get('domain', '').startswith('.'),
                path=cookie.get('path', '/'),
                path_specified=True,
                secure=cookie.get('secure', False),
                expires=cookie.get('expirationDate'),
                discard=False,
                comment=None,
                comment_url=None,
                rest={}
            )
            L.context._session.cookies.set_cookie(c)
    
    return L

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

@app.route('/followers', methods=['POST'])
def get_followers():
    data = request.json
    target_username = data.get('username')
    max_count = data.get('maxCount', 100)
    min_followers = data.get('minFollowers', 1000)
    max_followers = data.get('maxFollowers', 50000)
    min_posts = data.get('minPosts', 12)

    try:
        L = get_loader()
        profile = instaloader.Profile.from_username(L.context, target_username)

        followers = []
        count = 0

        for follower in profile.get_followers():
            if count >= max_count:
                break
            if follower.is_private:
                continue
            if follower.followers < min_followers:
                continue
            if follower.followers > max_followers:
                continue
            if follower.mediacount < min_posts:
                continue

            followers.append({
                'username': follower.username,
                'fullName': follower.full_name,
                'biography': follower.biography,
                'followersCount': follower.followers,
                'followsCount': follower.followees,
                'postsCount': follower.mediacount,
                'verified': follower.is_verified,
                'private': follower.is_private,
                'externalUrl': follower.external_url or ''
            })

            count += 1

        return jsonify({
            'success': True,
            'count': len(followers),
            'followers': followers
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
