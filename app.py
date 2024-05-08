import os 
import random
import logging
import africastalking
from sarufi import Sarufi
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from starlette.datastructures import FormData
from mangum import Mangum

load_dotenv()

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize SDK
africastalking.initialize(
    username=os.getenv('AT_USERNAME'),
    api_key=os.getenv('AT_API_KEY_SECRET')
)
sarufi = Sarufi(os.getenv('SARUFI_API_KEY'))
sms = africastalking.SMS

app = FastAPI()
handler = Mangum(app)

@app.post("/")
async def form_data_endpoint(request: Request):
    form_data: FormData = await request.form()
    text = form_data['text']
    to = form_data['to']
    from_number = form_data['from']
    chat_id= from_number.replace('+', '')
    
    logging.info(f"Message received from {from_number}")
    
    # remove the keyword from the text
    if to =='15054':
        text_list = text.split(' ')
        text = ' '.join(text_list[1:])
    
    # Integrate Sarufi with sarufi here  and send the response to the user
    response = sarufi.chat(
        bot_id=os.getenv('SARUFI_BOT_ID'),
        chat_id=chat_id,
        message=text,
        message_type='text',
        channel='general'
    )
    
    if response:
        logging.info(response)
        message = response.get('message', 'Sorry, I did not understand that')
        if isinstance(message, list):
            if len(message) > 1:
                if isinstance(message[0], list):
                    message = random.choice(message)
            message = '\n'.join(message)
        sms.send(message = message, recipients=[from_number], sender_id=to)
        logging.info(f"Message sent to {from_number}")
    return {"status": "data received"}
    