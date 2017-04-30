from flask import Flask, render_template, request, redirect, url_for

import lunchbot

lunchBot = lunchbot.Bot()

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
    # import pdb; pdb.set_trace()
    print(lunchBot.oauth)
    print(dir(lunchBot))
    client_id = lunchBot.oauth["client_id"]
    print('client_id: ', client_id)
    scope = lunchBot.oauth["scope"]
    print('scope: ', scope)
    return render_template("install.html", client_id=client_id, scope=scope)
    # try:
    #     print('in try')
    #     code = request.args.get('code')
    #     print('code', code)
    #     return redirect(url_for('thanks'))
    # except NameError:
    #     print('in except')
    #     lunchBot = lunchbot.Bot()
    #     client_id = lunchBot.oauth["client_id"]
    #     print('client_id: ', client_id)
    #     scope = lunchBot.oauth["scope"]
    #     print('scope: ', scope)
    #     return render_template("install.html", client_id=client_id, scope=scope)


@app.route("/thanks", methods=["GET"])
def thanks():
    return render_template("thanks.html")


# @app.route("/thanks")
# def thanks():
#     """
#     Exchange temp auth code for OAuth token
#     Render a thank you page
#     """
#     # Get temp auth code from request params
#     code_arg = request.args.get('code')

#     # The bot's auth method that exchanges code for OAuth token
#     lunchBot.auth(code_arg)
#     return redirect(url_for('thanks_page'))


if __name__ == "__main__":
    app.run(debug=True)
