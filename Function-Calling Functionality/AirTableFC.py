import os
import openai
import requests
import urllib.parse
import json
import time
import os
from dotenv import load_dotenv
load_dotenv()


def get_records_by_lead_name(lead_name: str):
    # Airtable settings
    base_id = os.environ.get("base_id")
    table_id = os.environ.get("table_id")
    api_key_airtable = os.environ.get("api_key_airtable")

    # Filter setup
    column_name = 'Leads Name'
    encoded_filter_formula = urllib.parse.quote(f"{{{column_name}}}='{lead_name}'")

    # Airtable API URL
    api_url = f"https://api.airtable.com/v0/{base_id}/{table_id}?filterByFormula={encoded_filter_formula}"

    # Headers for authentication
    headers = {
        'Authorization': f'Bearer {api_key_airtable}'
    }

    # Make the API request
    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        # Successful request
        records = response.json().get('records', [])
        return records
    else:
        # Failed request, log details
        error_info = response.text
        try:
            # Attempt to parse JSON error message
            error_info = json.loads(response.text)
        except json.JSONDecodeError:
            # Response is not JSON formatted
            pass
        
       
        print(f"Failed to retrieve data. Status Code: {response.status_code}. Response: {error_info}")
        return None


# OpenAI API Key
api_key = os.environ.get("OPENAI_API_KEY")



tools_list = [{
    "type": "function",
    "function": {

        "name": "get_records_by_lead_name",
        "description": "Retrieve infomation of the specfic lead like when's the next meeting with them, their email and etc",
        "parameters": {
            "type": "object",
            "properties": {
                "lead_name": {
                    "type": "string",
                    "description": "The lead's name"
                }
            },
            "required": ["lead_name"]
        }
    }
}]



# Initialize the client
client = openai.Client()



#if you dont specfiy the assitant seems openai will keep creating assitants 
def create_assistants():
    assistant_file_id="assitant_id1.txt"
    if os.path.exists(assistant_file_id):
        with open(assistant_file_id, "r") as file:
            assistant_id=file.read().strip()
    else:
        print("Creating an Assitant....")
        # Upload a file with an "assistants" purpose
        assistant = client.beta.assistants.create(
        name= "Airtable Func Call",
        instructions="You are a sale chatbot. Use the data you pull from our airtable database to answer question on our potential clients.",
        model="gpt-4-1106-preview",
        tools=tools_list
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

    #step add a message to the thread 
    user_message="What do we need to prepare for in our next meeting with David"
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
        instructions="You are a sale chatbot. Use the data you pull from our airtable database to answer question on our potential clients."
    )
    print(f"Run created with ID: {run.id} and status: {run.status}")
    print(run.model_dump_json(indent=4))

    # Step 5: Display the Assistant's Response
    # Poll the Run status until it's completed
    while True:
       # Wait for 5 seconds
        time.sleep(5)

         # Retrieve the run status
        run_status = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
        print(run_status.model_dump_json(indent=4))

    # If run is completed, get messages
        if run_status.status == 'completed':
            messages = client.beta.threads.messages.list(
                thread_id=thread.id
        )

        # Loop through messages and print content based on role
            for msg in messages.data:
                role = msg.role
                content = msg.content[0].text.value
                print(f"{role.capitalize()}: {content}")
            
              # save run steps to json file
            run_steps = client.beta.threads.runs.steps.list(
                thread_id=thread.id,
                run_id=run.id
            )
            print(run_steps)

            break
        elif run_status.status == 'requires_action':
            print("Function Calling")
            required_actions = run_status.required_action.submit_tool_outputs.model_dump()
            print( "Run Required Action State")
            print(required_actions)
            tool_outputs = []
            for action in required_actions["tool_calls"]:
                func_name = action['function']['name']
                arguments = json.loads(action['function']['arguments'])
         
                if func_name == "get_records_by_lead_name":
                    output = get_records_by_lead_name(lead_name=arguments['lead_name'])
                    output_string = json.dumps(output)
                    tool_outputs.append({
                    "tool_call_id": action['id'],
                    "output": output_string
                })
                else:
                    raise ValueError(f"Unknown function: {func_name}")
                
            print("Tool Outputs")
            print(tool_outputs)
            print("Submitting outputs back to the Assistant...")
            client.beta.threads.runs.submit_tool_outputs(
            thread_id=thread.id,
            run_id=run.id,
            tool_outputs=tool_outputs
            )
        else:
            print("Waiting for the Assistant to process...")
            time.sleep(5)

   


if __name__ == "__main__":
   create_assistants()
