import json

from prompts.Prompt import Prompt

class Generator:
    def __init__(self, client, model, game_environment, prompt: Prompt):
        self.client = client
        self.model = model
        self.prompt = prompt
        self.game_environment = game_environment
        
    def run(self, debug=False): 
        contextMessage = self.prompt.getGeneratorPrompt(self.game_environment.get_state_description())

        counter = 1     
        isTerminated = False
        
        while not isTerminated:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=contextMessage,
                tools=self.prompt.getGeneratorTools()
            ).choices[0].message
            if debug:
                print(f"== Step {counter} ==")
                print(f"== Response: {response.content}")

            contextMessage.append({"role": response.role, "content": response.content})

            # Handle tool calls
            if response.tool_calls:
                
                try:
                    if(debug):
                            print(f"== Num_Tools: {len( response.tool_calls)}")

                    for tool_call in response.tool_calls:
                        tool_name = tool_call.function.name
                        tool_response = self.game_environment.ACTION_MAP[tool_name](**(json.loads(tool_call.function.arguments))) if tool_call.function.arguments is not None else self.game_environment.ACTION_MAP[tool_name]()
                        isTerminated = tool_response["isTerminated"]
                        contextMessage.append({
                          "role": "tool",
                          "tool_call_id": tool_call.id,
                          "tool_name": tool_name,
                          "tool_arguments": tool_call.function.arguments,
                          "content": json.dumps(tool_response),
                        })

                        if(debug):
                            print(f"== Tool: {tool_name}")
                            print(f"== Tool Parameters: {tool_call.function.arguments}")  
                            print(f'== New State:\n {tool_response["state"]}')   
                            print("======")  
                except Exception as e:
                    contextMessage.append({
                        "role": "system",
                        "content": f"An error occurred during tool execution: {str(e)}"
                    })
                    if(debug):
                        print(f"== Error occurred during tool execution! Terminating this iteration!")
                        print(f"== {str(e)}")

                    return contextMessage, counter

            if isTerminated:
                return contextMessage, counter

            counter+=1