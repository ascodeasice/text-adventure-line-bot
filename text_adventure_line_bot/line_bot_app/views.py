from django.shortcuts import render

# Create your views here.
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt

from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextSendMessage

from .Story.Story import Story
from .Story.functions import call_func_with_str
from .Story.state_text import state_text

line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)
story=Story()

@csrf_exempt
def callback(request):
    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')

        try:
            events = parser.parse(body, signature)
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()

        for event in events:
            if isinstance(event, MessageEvent):
                received_text=event.message.text
                if(received_text==''):
                    continue
                
                option_index=ord(received_text[0])-ord('A')
                current_triggers=story.get_current_triggers()
                message=[]

                if(option_index<0 or option_index>=len(current_triggers)):
                    continue # ignore if out of index

                if(story.user_acted_too_slow and (story.state=='bad_ending' or story.state=='saved_by_dog')):
                    message.append(TextSendMessage(text="你反應太慢了"))
                    story.user_acted_too_slow=False # prevent stuck in this if statement
                else:
                    # enter next state
                    call_func_with_str(story,story.get_current_triggers()[option_index])

                message.append(TextSendMessage(text=state_text[story.state]))
                message.append(TextSendMessage(text=story.get_current_options()))
                line_bot_api.reply_message(event.reply_token,message)

        return HttpResponse()
    else:
        return HttpResponseBadRequest()