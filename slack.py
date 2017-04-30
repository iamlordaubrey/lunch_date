from flask import Flask, render_template, request, redirect, url_for
import lunchbot

app = Flask(__name__)


@app.route("/")
def index():
    """
    Renders installation page with "Add to Slack" button
    """
    # Bot = lunchbot.Bot()
    client_id = lunchbot.oauth["client_id"]
    print(client_id)
    scope = lunchbot.oauth["scope"]

    return render_template("install.html", client_id=client_id, scope=scope)


@app.route("/thanks")
def thanks():
    """
    Exchange temp auth code for OAuth token
    Render a thank you page
    """
    # Get temp auth code from request params
    code_arg = request.args.get('code')

    # The bot's auth method that exchanges code for OAuth token
    lunchbot.auth(code_arg)
    return redirect(url_for('thanks_page'))


if __name__ == "__main__":
    app.run()
