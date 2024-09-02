import os
import openai
import requests
import urllib.parse
import json
import time
import re


def json_to_readable_summary(json_data, indent_level=0, max_depth=2):
    """
    Convert JSON data into a readable string format.
    :param json_data: The JSON data to convert.
    :param indent_level: Current indentation level for nested structures.
    :param max_depth: Maximum depth to traverse in nested structures.
    :return: A string representing the readable summary of the JSON data.
    """
    summary = []
    indent = "  " * indent_level

    if isinstance(json_data, dict):
        for key, value in json_data.items():
            if isinstance(value, (dict, list)) and indent_level < max_depth:
                summary.append(f"{indent}{key}:")
                summary.extend(json_to_readable_summary(value, indent_level + 1, max_depth))
            else:
                summary.append(f"{indent}{key}: {value}")
    elif isinstance(json_data, list):
        for item in json_data:
            summary.extend(json_to_readable_summary(item, indent_level + 1, max_depth))
    else:
        summary.append(f"{indent}{json_data}")

    return summary

# Example usage
company_data = {
    # ... (your JSON data)
}

readable_summary = json_to_readable_summary(company_data)
print('\n'.join(readable_summary))


def search_linkedin_profile(name):
    api_key = ""
    search_engine_id = ""
    search_query = f"{name} linkedin"  
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": api_key,
        "cx": search_engine_id,
        "q":  search_query ,
    }

    url = f"https://www.googleapis.com/customsearch/v1?q={search_query}&cx={search_engine_id}&key={api_key}"
    url_pattern = re.compile(r'https://www\.linkedin\.com/in/[\w-]+/?$')
    url_pattern2 = re.compile(r'(https://www\.linkedin\.com/in/[\w-]+/?$|linkedin\.com/in/([\w-]+)/?)')
    
    response = requests.get(url)

    if response.status_code == 200:
        search_results = response.json()
        print("Search Results:")
        search_links = [item.get("link") for item in search_results.get("items", [])]
        valid_links = [link for link in search_links if url_pattern.match(link)]
        for link in search_links:
            print(link)

        for link in valid_links:
            print(link)
         # Check if the list of links is not empty
        if valid_links:
        # Assuming the first result is the desired one (you might need more logic here)
             linkedin_url = valid_links[0]
        elif search_links:
              for link in search_links:
                match = url_pattern2.search(link)
                if match:
                # Extract username and create standard LinkedIn URL
                    username = match.group(2) if match.group(2) else match.group(1).split('/')[-1]
                    linkedin_url = f"https://www.linkedin.com/in/{username}"
                    break
        else:
                print("No LinkedIn profiles found in the search results.")
                linkedin_url = None
    else:
     print(f"Failed to retrieve search results. Status Code: {response.status_code}")
     linkedin_url = None
    print(linkedin_url)
    return linkedin_url


def get_linkedin_profile_and_company_data(name):
    linkedin_url = search_linkedin_profile(name)
    print(linkedin_url)
    if not linkedin_url:
        print("LinkedIn profile not found.")
        return

    api_key = ''
    headers = {'Authorization': 'Bearer ' + api_key}

    # First API Call - LinkedIn Profile Data
    api_endpoint_1 = 'https://nubela.co/proxycurl/api/v2/linkedin'
    params_1 = {
        'linkedin_profile_url': linkedin_url,
         'extra': 'exclude',
        'github_profile_id': 'exclude',
        'facebook_profile_id': 'exclude',
        'twitter_profile_id': 'exclude',
        'personal_contact_number': 'exclude',
        'personal_email': 'exclude',
        'inferred_salary': 'exclude',
        'skills': 'exclude',
        'use_cache': 'if-present',
        'fallback_to_cache': 'on-error',
    }
    response_1 = requests.get(api_endpoint_1, params=params_1, headers=headers)

    if response_1.status_code == 200:
        json_response_1 = response_1.json()
        readable_summary = json_to_readable_summary(json_response_1)
        occupation = json_response_1.get("occupation", "")
        # Initialize variables for current job details
       
        # Process the LinkedIn profile data...
        # Extract current job company URL for the second API call
          # Loop through experiences to find the current job
        for job in json_response_1.get("experiences", []):
            company_name = job.get("company", "")
            if company_name in occupation and job.get("ends_at") is None:
                current_job_company_url = job.get("company_linkedin_profile_url", "")

        if current_job_company_url:
            # Second API Call - LinkedIn Company Data
          api_endpoint_2 = 'https://nubela.co/proxycurl/api/linkedin/company'
          params_2 = {
                'url': current_job_company_url,
                'resolve_numeric_id': 'true',
                'categories': 'include',
                'funding_data': 'include',
                'extra': 'include',
                'exit_data': 'include',
                'acquisitions': 'include',
                'use_cache': 'if-present',
            }
          response_2 = requests.get(api_endpoint_2, params=params_2, headers=headers)

           
          if response_2.status_code == 200:
                json_response_2 = response_2.json()
                readable_summary_2 = json_to_readable_summary(json_response_2)
                # Process the LinkedIn company data...
                print("Company Data:", json_response_2)
          else:
                print("Failed to retrieve company data.")
    else:
        print("Failed to retrieve LinkedIn profile data.")
    
    
    print(readable_summary)
    print(readable_summary_2)
    return readable_summary, readable_summary_2
OPENAI_API_TOKEN = ""
# OpenAI API Key
api_key =  os.environ["OPENAI_API_KEY"] = OPENAI_API_TOKEN

tools_list = [{
    "type": "function",
    "function": {

        "name": "get_linkedin_profile_and_company_data",
        "description": "Retrieve infomation of the specfic lead like company they worked for, what thier company does , company size , website and etc from scraping linkedin",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "The lead's name"
                }
            },
            "required": ["name"]
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
        name= "Find Lead Info",
        instructions="You are a sale chatbot. Use your ability to pull info from linkedin to anwer question about potential leads.",
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
    user_message=""" During an AI conference I attended last week, I had the opportunity to meet a gentleman named Liam Ottely, who mentioned he runs an AI automation agency and expressed interest in a potential partnership. Could you please conduct some research for me to find out more about his company? Specifically, I'd like to know the name of his company, its official website, and a brief overview of what services or products his company offers.
 """
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

            break
        elif run_status.status == 'requires_action':
            print("required run")
            print(run_status.model_dump_json(indent=4))
            print("Function Calling")
            required_actions = run_status.required_action.submit_tool_outputs.model_dump()
            print(required_actions)
            tool_outputs = []
            import json
            for action in required_actions["tool_calls"]:
                func_name = action['function']['name']
                arguments = json.loads(action['function']['arguments'])
         
                if func_name == "get_linkedin_profile_and_company_data":
                    output = get_linkedin_profile_and_company_data(name=arguments['name'])
                    output_string = json.dumps(output)
                    tool_outputs.append({
                    "tool_call_id": action['id'],
                    "output": output_string
                })
                else:
                    raise ValueError(f"Unknown function: {func_name}")
            
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