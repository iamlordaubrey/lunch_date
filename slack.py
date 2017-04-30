from flask import Flask, render_template, request, redirect, url_for

import lunchbot

lunchBot = lunchbot.Bot()
# slack = lunchBot.client

app = Flask(__name__)


@app.route("/")
def index():
    # lunchBot = lunchbot.Bot()
    return redirect(url_for('oauth_dance'))


@app.route("/install")
def oauth_dance():
    print('in oauth')
    """
    Renders installation page with "Add to Slack" button
    """
    code = request.args.get('code')
    print('code', code)
    if code:
        lunchBot.auth(code)
        return redirect(url_for('thanks'))

    print('in except')
    print(lunchBot.oauth)
    print(dir(lunchBot))
    client_id = lunchBot.oauth["client_id"]
    print('client_id: ', client_id)
    scope = lunchBot.oauth["scope"]
    print('scope: ', scope)
    return render_template("install.html", client_id=client_id, scope=scope)


@app.route("/thanks", methods=["GET"])
def thanks():
    lunchBot.runner()
    return render_template("thanks.html")


if __name__ == "__main__":
    app.run(debug=True)
