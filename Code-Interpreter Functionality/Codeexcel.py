import pandas as pd
import json

excel_file = 'salessheet.xlsx'
data = pd.read_excel(excel_file, sheet_name='Sales Data', header=3)

# Convert DataFrame to JSON string
json_str = data.to_json(orient='records')

# Convert JSON string to Python object (list of dictionaries)
data_list = json.loads(json_str)

# Create a mapping based on the first row (header row)
header_mapping = data_list[0]
key_mapping = {f'Unnamed: {i}': header_mapping[f'Unnamed: {i}'] for i in range(len(header_mapping)) if header_mapping[f'Unnamed: {i}'] is not None}

# Cleaning the data and applying dynamic mapping
cleaned_data = []
for item in data_list[1:]:  # Skip the first row as it's used for mapping
    cleaned_item = {}
    for key, value in item.items():
        # Apply mapping and clean key
        new_key = key_mapping.get(key, key)
        if new_key is not None and value is not None:  # Exclude keys and values that are None
            cleaned_item[new_key.replace('Unnamed: ', '')] = value
    cleaned_data.append(cleaned_item)


json_data = json.dumps(cleaned_data, indent=4)
print(json_data)
# Optionally, write this list of dictionaries to a text file
with open('output.txt', 'w') as file:
    file.write(json_data)



import os
import openai
import json
from dotenv import load_dotenv
load_dotenv()


# OpenAI API Key
api_key = os.environ.get("OPENAI_API_KEY")



# Initialize the client
client = openai.Client()



#if you dont specfiy the assitant seems openai will keep creating assitants 
def create_assistants():
    assistant_file_id="assitant_id3.txt"
    if os.path.exists(assistant_file_id):
        with open(assistant_file_id, "r") as file:
            assistant_id=file.read().strip()
    else:
        print("Creating an Assitant....")
        # Upload a file with an "assistants" purpose
        file = client.files.create(
            file=open("output.txt", "rb"),
            purpose='assistants'
            )
        assistant = client.beta.assistants.create(
        name= "Data Analyst Sales Assistant",
        instructions="then follow these steps -Reading the JSON File: Utilize Python, specifically the json module, to open and parse the data from the text file. Employ the open() function to access the file, and json.load() to convert the contents into a Python dictionary or list, depending on the JSON structure.Understanding Data Structure: The JSON data encompasses fields like 'Deal Orders', 'Company', 'Status', 'Contact', along with financial metrics and other relevant details. Acquaint yourself with these key data points for accurate responses.Data Analysis and Insights: Provide comprehensive summaries, highlight key trends, and deduce insights from the data, including total sales figures, average deal sizes, status distributions, and more.Visualization of Data: Craft and present visual charts like bar graphs and pie charts to depict sales trends and patterns. Ensure these visualizations are both accurate and user-friendly, offering clear insights at a glance.Query Handling: Efficiently respond to a range of queries related to the sales data. This includes providing specific deal details, comparing time periods, and summarizing overall sales performance.Maintaining Data Accuracy: Always ensure the information you deliver is precise and reflects the most current data available in the text file.Your role is crucial in aiding users to comprehend our sales data thoroughly, enabling them to make well-informed decisions based on this insightful analysis. If it just requires you to answer basic questions based in the data given and doesnt need code to answer just use retrival fucntion",
        tools=[{"type": "code_interpreter"},{"type": "retrieval"},],
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

    #step add a message to the thread 
    user_message="create me a bar graph measuring the expensives of each deal in our data file"
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
        instructions="Please address the user respectfully. The user requires help with math."
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
    with open("messages1.json", "w") as f:
        messages_json = messages.model_dump()
        json.dump(messages_json, f, indent=4)
    print("Displaying the conversation:")
    
    
    for msg in messages.data:
        role = msg.role
        for content_item in msg.content:
            if content_item.type == "text":
                text_content = content_item.text.value
                print(f"{role.capitalize()}: {text_content}")
            elif content_item.type == "image_file":
                image_file_id = content_item.image_file.file_id
                print(f"Image File ID: {image_file_id}")

            # Retrieve the image content using the client's method
                image_data = client.files.content(image_file_id)
                image_data_bytes = image_data.read()

            # Save the image data to a file
            with open(f"./image_{image_file_id}.png", "wb") as file:
                file.write(image_data_bytes)
                print(f"Image {image_file_id} saved as image_{image_file_id}.png")
    # msg in messages.data:
     #   print(f"{msg.role.capitalize()}: {msg.content[0].text.value}")

    # save run steps to json file
   # run_steps = client.beta.threads.runs.steps.list(
  #  thread_id=thread.id,
  #  run_id=run.id
  #  )

   # with open("run_steps.json" , "w") as f:
      #  run_steps_json = run_steps.model_dump()
       # json.dump(run_steps_json,f, indent=4)



if __name__ == "__main__":
    create_assistants()
