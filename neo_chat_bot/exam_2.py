import telegram

# 토큰을 지정해서 bot을 선언해 줍시다! (물론 이 토큰은 dummy!)
# chii_token = '535111053:AAHmeNTq88auY7BR9XnCyvGcBGJkLqqHI_E'
# ictk_token = '649283772:AAElSi9wuksWFEdRTf2Ucvv721iY8qNlD5g'
#https://api.telegram.org/bot535111053:AAHIL89_ZsQUjy43-a4JWmsvtGfuxLRKb-o/sendMessage?chat_id=61951841&text=test
#https://api.telegram.org/bot535111053:AAHIL89_ZsQUjy43-a4JWmsvtGfuxLRKb-o/getUpdates
from neo_chat_bot.api_token import neo_bot_token

bot = telegram.Bot(token=neo_bot_token)
# 우선 테스트 봇이니까 가장 마지막으로 bot에게 말을 건 사람의 id를 지정해줄게요.
# 만약 IndexError 에러가 난다면 봇에게 메시지를 아무거나 보내고 다시 테스트해보세요.
print(bot)
#bot.sendMessage(chat_id="61951841", text='/start')
bot.sendMessage(chat_id="61951841", text='안녕')
print(bot.getUpdates())
#https://api.telegram.org/bot{token}/sendMessage?chat_id=<chat_id>&text=<Enter your text here>
chat_id = bot.getUpdates()[-1].message.chat.id

print(chat_id)