from flask import Flask, redirect, url_for, session, request, render_template,jsonify
from flask_oauthlib.client import OAuth

app = Flask(__name__,static_folder='staticFiles')
app.secret_key = 'some_random_secret'
oauth = OAuth(app)

google = oauth.remote_app(
    'google',
    consumer_key='503356804278-a1nfimdlg8l5sk7ogkgf95fhuf3p799b.apps.googleusercontent.com',
    consumer_secret='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',
    request_token_params={
        'scope': 'email',
    },
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)
bg = ''
with open('indexbg.txt','r') as indexbg:
    content = indexbg.read()
    bg=content
bg2=''
with open('loginbg.txt','r') as indexbg:
    content2 = indexbg.read()
    bg2=content2
@app.route('/')
def index():
    return render_template('login_link.html',loginbg=bg2)

@app.route('/login')
def login():
    return google.authorize(callback="http://127.0.0.1:5000/login/authorized")

@app.route('/logout')
def logout():
    session.pop('google_token')
    return redirect(url_for('index'))


@app.route('/login/authorized')
def authorized():
    response = google.authorized_response()
    if response is None or response.get('access_token') is None:
        return 'Access denied: reason={} error={}'.format(
            request.args['error_reason'],
            request.args['error_description']
        )
    global user_info,email
    session['google_token'] = (response['access_token'], '')
    user_info = google.get('userinfo')
    email=google.get('userinfo').data['email']
    return redirect(url_for('main'))

@app.route('/main')
def main():
    return render_template('index.html',email=google.get('userinfo').data['email'],bg=content)
cards_db = {}
next_id = 0

@app.route('/add_card', methods=['POST'])
def add_card():
    global next_id
    title = request.form['card_title']  # Corrected to directly access the form data
    content = request.form['card_content']

    # Store the new card with an ID
    cards_db[next_id] = {'title': title, 'content': content}
    response = jsonify({'message': 'Card added successfully!', 'card_id': next_id})
    next_id += 1  # increment for the next card

    return response

@app.route('/delete_card', methods=['POST'])
def delete_card():
    card_id = int(request.form['card_id'])  # Convert the ID from string to integer

    # Delete the card with the corresponding ID
    if card_id in cards_db:
        del cards_db[card_id]
        return jsonify({'message': 'Card deleted!'})
    else:
        return jsonify({'message': 'Card not found!'}), 404

@app.route('/get_cards', methods=['GET'])
def get_cards():
    # Return the list of cards
    cards_list = [{'id': card_id, 'title': card['title'], 'content': card['content']} for card_id, card in cards_db.items()]
    return jsonify(cards_list)

@app.route('/news')
def news():
    # Render the news page. This can be more complex depending on your setup.
    return render_template('news.html',email=google.get('userinfo').data['email'],bg=content)
@app.route('/projects')
def projects():
    return render_template('projects.html',bg=content)

@app.route('/test')
def s():
    return render_template('test2.html',bg=content)

@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')

if __name__ == '__main__':
    app.run(debug=True)
