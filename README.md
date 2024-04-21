# OpenAI---Assistant-API-Demo
 Repo for showcasing the  code for building an AI Sales Assistant using OpenAI Assistant's Retrieval, Function Calling, and Code Interpreter functionalities.

**Introduction**


This README provides detailed instructions for setting up and running the Python project that interfaces with the OpenAI API. The setup process includes installing Python, managing project dependencies, configuring environment variables, and obtaining an OpenAI API key.


**Prerequisites**

Note -  At least for windows might have to run as adminster when installing all of this to be able to run the commands/software packages  [How to run as admin] ( https://learn.microsoft.com/en-us/windows/terminal/faq)


Installing Python


Before proceeding, ensure that Python is installed on your system. We recommend using Homebrew on macOS and Chocolatey on Windows for a smooth installation experience.


macOS (using Homebrew):


Install Homebrew by running the following command in your terminal:


```sh
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Once Homebrew is installed, install Python by running:


```sh
brew install python
```

Windows (using Chocolatey):


Install Chocolatey by following the instructions on the [Chocolatey Installation page](https://chocolatey.org/install).
Once Chocolatey is installed, install Python by running the following command in your terminal (run as Administrator):


```powershell
choco install python
```

Note - For Windows it might have default aliases for Python that redirect the python command to the Microsoft Store which could cause the python command not to work. Disable these aliases as it might have default aliases for Python that redirect the python command to the Microsoft Store. Disable these.

Steps to disable app aliases
 Go to Settings > Apps > Advanced App settings.  Click on App execution aliases. [Here's is video also](https://www.google.com/search?q=windows+disable+app+aliases&oq=windows+disable+app+alis&gs_lcrp=EgZjaHJvbWUqCQgBECEYChigATIGCAAQRRg5MgkIARAhGAoYoAEyCQgCECEYChigATIJCAMQIRgKGKABMgkIBBAhGAoYoAEyCQgFECEYChigATIHCAYQIRifBTIHCAcQIRifBdIBCjEwMDI5ajBqMTWoAgiwAgE&sourceid=chrome&ie=UTF-8#kpvalbx=_0HkkZvS3KOvJp84P-fmw-AE_45)

**Dependency Management**


This project uses a requirements.txt file to manage dependencies. Ensure you have Python and pip installed before proceeding.


**Setup Instructions**


1. Clone the Repository

   
First, clone the project repository to your local machine using git:


```sh
git clone [repository URL]
cd [project directory]
```
Guide in how to install git if needed - [Guide](https://github.com/git-guides/install-git)

2. Install Dependencies

   
Navigate to the project directory and install the required Python packages using the following command:


```sh
pip install -r requirements.txt
```

3. Configure Environment Variables

   
Create a .env file in the project root directory. This file will store your OpenAI API key and any other sensitive information.


```sh
touch .env  # On macOS and Linux
type nul > .env  # On Windows in cmd or use New-Item .env -ItemType file in PowerShell
```

Add the following line to your .env file, replacing YOUR_API_KEY with your actual OpenAI API key:


```
OPENAI_API_KEY=YOUR_API_KEY
```

4. Obtaining an OpenAI API Key

   
To use the OpenAI API, you need an API key. If you do not have one, visit the [OpenAI API key page]((https://platform.openai.com/api-keys).to sign up for an account and obtain your API key.


5. Running the Project

   
With the setup complete, you can now run the project using the following command:


```sh
python main.py
```

Replace main.py with the name of your main Python script if different.


Additional Information
For more detailed information on the OpenAI API and its capabilities or other documention on how to setup OpenAI API in a python env, refer to the [OpenAI API documentation](https://platform.openai.com/docs/overview) and [Open API setup doc](https://platform.openai.com/docs/quickstart?context=python) 

IMPORTANT!

Open AI Assistant API V2

OpenAI just added a V2 version of the Opena Assitant API V2. This includes some breaking changes so if you want the current code to still work confirm that you are using the older version of openai lib(1.20.0)(you check your version using openai --version)(run pip install openai==1.20.0) or make the proper code changes need for the code to work with Open AI Assitant API V2. [Here is the documention for differences between V1 and V2](https://platform.openai.com/docs/assistants/migration/changing-beta-versions)

