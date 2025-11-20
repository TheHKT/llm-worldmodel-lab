import json

from prompts.Prompt import Prompt

class Curator:
    def __init__(self, client, model, prompt: Prompt):
        self.client = client
        self.model = model
        self.prompt = prompt
        
        self.TOOL_MAPPING = {
          "ADD": self.prompt.addFromPlaybook,
          "REMOVE": self.prompt.removeFromPlaybook,
          "MODIFY": self.prompt.modifyFromPlaybook
      }

        
    def run(self, debug=False): 
        contextMessage = self.prompt.getCuratorPrompt()
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=contextMessage,
            tools=self.prompt.getCuratorTools()
        ).choices[0].message
        
        if debug:
            print(f"== Response: {response}")
            
        if response.tool_calls:
           
            if(debug):
                print(f"== Num_Tools: {len( response.tool_calls)}")
                        
            for tool_call in response.tool_calls:
                tool_name = tool_call.function.name
                tool_response = self.TOOL_MAPPING[tool_name](**(json.loads(tool_call.function.arguments))) if tool_call.function.arguments is not None else self.TOOL_MAPPING[tool_name]()
                
                if(debug):
                    print(f"== Tool: {tool_name}")
                    print(f"== Tool Parameters: {tool_call.function.arguments}")  

        return response.content