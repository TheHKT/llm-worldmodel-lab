from prompts.Prompt import Prompt

class Reflector:
    def __init__(self, client, model, prompt: Prompt):
        self.client = client
        self.model = model
        self.prompt = prompt
        
    def run(self, debug=False): 
        contextMessage = self.prompt.getReflectorPrompt()

        response = self.client.chat.completions.create(
            model=self.model,
            messages=contextMessage
        ).choices[0].message
        if debug:
            print(f"== Response: {response.content}")

        return response.content