import os
from argparse import ArgumentParser
from flask import Flask, request, abort

from line_bot import (
    LineBotApi, MessageEvent, TextMessage, TextSendMessage,
    SignatureValidator, WebhookParser
)

app = Flask(__name__)

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as env.')
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as env.')

line_bot_api = LineBotApi(channel_access_token)
signature_validator = SignatureValidator(channel_secret)
parser = WebhookParser()


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # check signature
    if not signature_validator.validate(body, signature):
        abort(400)

    # parse webhook body
    events = parser.parse(body)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=event.message.text)
        )

    return ''


if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-p', '--port', default=8000, help='port')
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()

    app.run(debug=options.debug, port=options.port)