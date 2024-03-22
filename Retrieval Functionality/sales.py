

import os
import openai
import json
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ.get("OPENAI_API_KEY")


# Initialize the client
client = openai.Client()
#Step 1 Initialize the client 


assistant_instructions = """ You are an internal sales assistant employed by our chatbot company, tasked with analyzing and extracting valuable insights from our sales calls. Your primary role is to assist in enhancing our sales call analysis based on past interactions. You are also responsible for various call-related tasks, including sentiment analysis, providing detailed responses to questions and queries, and ensuring the utmost accuracy in your responses.

Your source of information is a document file containing transcripts of our previous sales calls. Your goal is to leverage this data to offer comprehensive and insightful answers to a wide range of questions and inquiries. Your responses should go beyond basic information, aiming for depth and precision when addressing the queries.

Your assistance will play a pivotal role in improving our sales strategies and customer interactions. Your expertise in extracting insights from our sales calls will help us better understand customer needs, objections, and preferences, ultimately leading to more successful sales outcomes. """




#if you dont specfiy the assitant seems openai will keep creating assitants 
def create_assistants():
    assistant_file_id="assistant_id_.txt"
    if os.path.exists(assistant_file_id):
        with open(assistant_file_id, "r") as file:
            assistant_id=file.read().strip()


    else:

        print("Creating an Assitant....")
        # Upload a file with an "assistants" purpose
        file = client.files.create(
            file=open("Sales.pdf", "rb"),
            purpose='assistants'
            )
        

        assistant = client.beta.assistants.create(
        name= "Sales Call Knowledgebot",
        instructions=assistant_instructions,
        tools=[{"type": "retrieval"}],
        model="gpt-4-1106-preview",
        file_ids=[file.id]
        )
        #write new assistant_id to a file 
        assistant_id= assistant.id
        with open(assistant_file_id, "w") as file:
            file.write(assistant_id)
        print(f"Assitant created with ID: {assistant_id}")
    
    #retrieve the assitant_id 
    assistant = client.beta.assistants.retrieve(assistant_id)  
    print(f"Assistant created with ID: {assistant_id}")  
    
    #step 2: Create a thread 
    print("Creating a Thread for a new user conversation.....")
    thread = client.beta.threads.create()
    print(f"Thread created with ID: {thread.id}")
    print("using existing thread")

    #Step 3 add a message to the thread 
    user_message="What are the most common objections we face in our sales call"
    print(f"Adding user's message to the Thread: {user_message}")
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_message
    )
    print("Message added to the Thread.")

    # Step 4: Run the Assistant
    print("Running the Assistant to generate a response...")
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
        instructions=assistant_instructions
    )
    print(f"Run created with ID: {run.id} and status: {run.status}")

    # Step 5: Display the Assistant's Response
    # Poll the Run status until it's completed
    while True:   
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
        if run.status == 'completed':
            print("Run completed. Retrieving the Assistant's responses...")
            break
        print("Waiting for the Assistant to complete the run...")

    messages = client.beta.threads.messages.list(
        thread_id=thread.id
    )
    with open("messages.json", "w") as f:
        messages_json = messages.model_dump()
        json.dump(messages_json, f, indent=4)
    print("Displaying the conversation:")
    for msg in messages.data:
        print(f"{msg.role.capitalize()}: {msg.content[0].text.value}")

    # save run steps to json file
    run_steps = client.beta.threads.runs.steps.list(
    thread_id=thread.id,
    run_id=run.id
    )

    with open("run_steps.json" , "w") as f:
        run_steps_json = run_steps.model_dump()
        json.dump(run_steps_json,f, indent=4)



if __name__ == "__main__":
    create_assistants()






# Add the file to the assistant



