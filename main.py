from flask import Flask, jsonify, request
import instaloader
import os

app = Flask(__name__)

L = instaloader.Instaloader()

USERNAME = os.environ.get('IG_USERNAME')
PASSWORD = os.environ.get('IG_PASSWORD')

try:
    L.login(USERNAME, PASSWORD)
    print(f"Залогинились как {USERNAME}")
except Exception as e:
    print(f"Ошибка логина: {e}")

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
