#%%
import os

import gradio as gr
import os
os.environ["LANGCHAIN_HANDLER"] = "langchain"
from langchain.agents import Tool
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI
from langchain.utilities import SerpAPIWrapper
from langchain.agents import initialize_agent
from langchain.agents import AgentType
from langchain.agents import ZeroShotAgent, Tool, AgentExecutor
from langchain import OpenAI, SerpAPIWrapper, LLMChain
from langchain import PromptTemplate, FewShotPromptTemplate
from langchain.chat_models import ChatOpenAI

def load_files_from_directory(directory_path):
    file_contents = {}

    # List all files in the specified directory
    for file_name in os.listdir(directory_path):
        file_path = os.path.join(directory_path, file_name)

        # Check if it's a file (and not a directory)
        if os.path.isfile(file_path) and file_name.endswith('.py'):
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                file_contents[file_name] = content
    
    #return [{'filename' : filename, 'content' : content} for filename, content in file_contents.items()]
    file_content_string = "\n".join([f"""
--- start file: {filename} ---
{content}
--- end file {filename} ---
""" for filename, content in file_contents.items()])
    return file_content_string



try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    Warning("Could not load .env file. But Birgir might have put it in env anyways so all good.")
    pass

from langchain.utilities import GoogleSearchAPIWrapper

#%%

#%%

#%%
class Agent:
    def __init__(self):
        # Configure tools
        search = GoogleSearchAPIWrapper(k=1)
        #search = SerpAPIWrapper()
        self.tools = [
            Tool(
                name = "Search",
                func=search.run,
                description="useful for when you need to answer questions about current events"
            )
        ]
    def __call__(self, text, model_name="gpt-4"):
        agent_executor = self.build_agent(model_name=model_name)
        return agent_executor.run(text)

    def build_agent(self, model_name="gpt-3.5-turbo"):
        file_contents = load_files_from_directory(".")

        prefix = f"""You are an excellent software developer that helps the user built their app for their need by suggesting changes to the existing code base. The current codebase looks like this:
        {file_contents}.
        You have access to the following tools, but should only use them in the last resort:"""
        suffix = """If the user request something that is unclear, please ask him to modify his question with the added information.".

        Question: {input}
        {agent_scratchpad}"""

        prompt = ZeroShotAgent.create_prompt(
            tools = self.tools, 
            prefix=prefix.replace('{',"{{").replace('}',"}}"), 
            suffix=suffix, 
            input_variables=["input", "agent_scratchpad"]
        )
        llm_chain = LLMChain(llm=ChatOpenAI(temperature=0,model_name=model_name), prompt=prompt)

        tool_names = [tool.name for tool in self.tools]
        agent = ZeroShotAgent(llm_chain=llm_chain, allowed_tools=tool_names)
        agent_executor = AgentExecutor.from_agent_and_tools(agent=agent, tools=self.tools, verbose=True)
        return agent_executor
# %%
if __name__ == "__main__":
    agent = Agent()
    agent("How can I get the codebase to be loaded from a directory specified in the gradio app?")
# %%