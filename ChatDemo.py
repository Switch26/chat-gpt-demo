from openai import OpenAI
import os
import panel as pn
pn.extension()
import time


client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
paynote_assistant_id = "asst_6wgVV1Fa1IzuwCsvVZvXjZSe"
pizza_assistant_id = "asst_DgPlIjjQuVSZGEbuljHHDYDi"

# Retrieve the assistant (based on the assistant id)
assistant = client.beta.assistants.retrieve(pizza_assistant_id)

# Create a new thread (one thread per conversation)
# No need to delete them, they are automatically deleted after 60 days
thread = client.beta.threads.create()

async def getCompletionForChat(contents: str, user: str, instance: pn.chat.ChatInterface):
    # create a new message and add it to the thread
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role='user',
        content=contents
    )
    # create a run and kick it off
    run = client.beta.threads.runs.create(
        assistant_id=assistant.id,
        thread_id=thread.id
    )
    # wait for the run to finish
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
        time.sleep(0.5)
    # get new message
    messagesArray = client.beta.threads.messages.list(
        thread_id=thread.id,
        order="asc",
        after=message.id
    )
    # find the last message
    message_text = messagesArray.data[0].content[0].text.value
    
    # send the messages to the chat interface
    instance.send(message_text, user="bot", respond=False)
    return

# start chat
chat_interface = pn.chat.ChatInterface(
    callback=getCompletionForChat, 
    show_rerun=False, 
    show_undo=False,
    callback_user="bot"
)
#chat_interface.send("Hello! Welcome to our pizza restaurant, what would you like to order?", user="ChatGPT", respond=False)
chat_interface.servable()





