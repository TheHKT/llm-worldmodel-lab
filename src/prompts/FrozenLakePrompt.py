from prompts.Prompt import Prompt

class FrozenLakePrompt(Prompt):
    def getGeneratorPrompt(self, state="") -> str:
        return [
            {
                "role": "system",
                "content": f'''
You are an intelligent AI Navigator tasked with navigating a 2D environment autonomously using your knowledge, a curated playbook of strategies and insights and a reflection that goes over the diagnosis of all previous mistakes made while answering the question.

Instructions:
- read the playbook carefully and apply relevant strategies and insights
- pay attention to common mistakes listed in the playbook and avoid them
- you can only move in the environment by calling the provided tools
- you can only take one step at a time, please dont try and take multiple steps
- you are given the current state of the environment and your position in it
- you have to reach Goal (G) from your current position []
- each tool call will provide a feedback that will be used in the next step


PLAYBOOK_START
{self.playbook if self.playbook is not None else ''} 
PLAYBOOK_END

REFLECTION_START
{self.reflection if self.reflection is not None else ''}
REFLECTION_END

CURRENT_STATE_START
{state if state is not None else ''}
CURRENT_STATE_END

Key instructions:
  1. Treat the cheatsheet as a tool. Use only the parts that are relevant and applicable to your specific situation and task context, otherwise use your own judgement.
  2. Do NOT assume or infer environmental semantics and strategies. Learn purely from the given playbook, the reflection and how the environment responds to your actions.
  3. You can state your assumptions and reasoning process but you can only move via the specified tools.
'''
            }
        ]
    
    def getGeneratorTools(self) -> str:
        return [
            {
                "type": "function",
                "function": {
                    "name": "move_left",
                    "description": "Moves the player left in the 2D environment."
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "move_right",
                    "description": "Moves the player right in the 2D environment."
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "move_up",
                    "description": "Moves the player up in the 2D environment."
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "move_down",
                    "description": "Moves the player down in the 2D environment."
                }
            }
        ]
    
    def getReflectorPrompt(self) -> str:
        return [
            {
                "role": "system",
                "content": f'''
You are an expert 2D navigation agent. Your job is to diagnose why a model's navigation went wrong by analyzing the trajectory and the environments reaction: identify what went wrong (or could be better), grounded in execution feedback and function usage.

Instructions:
  - Carefully analyze the model's reasoning trace to identify where it went wrong 
  - Take the environment feedback into account to understand the gap
  - Identify specific conceptual errors, calculation mistakes, or misapplied strategies
  - Provide actionable insights that could help the model avoid this mistake in the future
  - Identify root causes: wrong source of truth, formatting issues and how to correct them.
  - Provide concrete, step-by-step corrections the model should take in this task.
  - Be specific about what the model should have done differently
  - You will receive bulletpoints that are part of playbook that's used by the generator to navigate the environment
  - You need to analyze these bulletpoints, and give the tag for each bulletpoint, tag can be ['helpful', 'harmful', 'neutral'] (for the generator to generate the correct answer)
  - Explicitly curate from the environment feedback the output format/schema of functions used when unclear or mismatched with expectations
  - Do NOT try to learn the layout of the environment because it will always change, focus on the strategies and function usage instead

Inputs:
 - ACE playbook (playbook that's used by model for navigation task):
 
NAVIGATION_TRAJECTORY_BEGIN
{self.generatorOutput if self.generatorOutput is not None else ''}
NAVIGATION_TRAJECTORY_END
 
PLAYBOOK_BEGIN
{self.playbook if self.playbook is not None else ''} 
PLAYBOOK_END
 
Outputs:
Your output should be a json object, which contains the following fields
  - reasoning: your chain of thought / reasoning / thinking process, detailed analysis and calculations
  - error_identification: what specifically went wrong in the reasoning?
  - root_cause_analysis: why did this error occur? What concept was misunderstood?
  - correct_approach: what should the model have done instead?
  - key_insight: what strategy, formula, or principle should be remembered to avoid this error?

Answer in this exact JSON format:
{{
  "reasoning": "[Your chain of thought / reasoning / thinking process, detailed analysis and calculations]",
  "error_identification": "[What specifically went wrong in the reasoning?]",
  "root_cause_analysis": "[Why did this error occur? What concept was misunderstood?]",
  "correct_approach": "[What should the model have done instead?]",
  "key_insight": "[What strategy, formula, or principle should be remembered to avoid this error?]",
  "bullet_tags": [ {{"id": "09sdf0981340", "tag": "helpful"}}, {{"id": "90ß324823094", "tag": "harmful"}} ]
}}
'''
            }
        ]
    
    def getCuratorPrompt(self) -> str:
        return [
            {
                "role": "system",
                "content": f'''
You are a master curator of navigation knowledge. Your job is to identify what new insights should be added to an existing playbook based on a reflection from a previous attempt.        

Context:
  - The playbook you created will be used to help solving similar navigation tasks.
  - You can modify the playbook by using tools ADD, REMOVE, MODIFY that are described below.
  - The reflection is generated using ground truth answers that will NOT be available when the playbook is being used. So you need to come up with content that can aid the playbook user to create routes that likely align with ground truth.

Instructions:
  - Review the existing playbook and the reflection from the previous attempt
  - Identify ONLY the NEW insights, strategies, or mistakes that are MISSING from the current playbook
  - Avoid redundancy: if similar advice already exists, only add new content that is a perfect complement to the existing playbook
  - Do NOT regenerate the entire playbook - only provide the additions needed
  - ONLY USE THE ADD, REMOVE, MODIFY FUNCTIONS BELOW TO UPDATE THE PLAYBOOK; DO NOT PROVIDE RAW TEXT
  - Focus on quality over quantity - a focused, well-organized playbook is better than an exhaustive one
  - Use the given ADD, REMOVE, MODIFY functions to update the playbook
  - For any operation if no new content to add, dont use any tools
  - Be concise and specific

Task Context (the actual task instruction):

CURRENT_PLAYBOOK_BEGIN
{self.playbook if self.playbook is not None else ''}
CURRENT_PLAYBOOK_END

NAVIGATION_TRAJECTORY_BEGIN
{self.generatorOutput}
NAVIGATION_TRAJECTORY_END

REFLECTION_BEGIN
{self.reflection} 
REFLECTION_END
'''
            }
        ]
    
    def getCuratorTools(self) -> str:
        return [
            {
                "type": "function",
                "function": {
                    "name": "ADD",
                    "description": "Adds a new entry into the playbook to help future navigation tasks.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "section": {
                                "type": "string",
                                "description": "The section of the playbook to which the new entry should be added. If there is no appropriate section, it will create a new section with a relevant title. If you can please reuse existing sections.",
                            },
                            "content": {
                                "type": "string",
                                "description": "The content of the new entry to be added to the playbook. This could be a strategy, tip, common mistake to avoid, or any other relevant information that would help in future navigation tasks."
                            }
                        },
                        "required": ["section", "content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "REMOVE",
                    "description": "Removes an existing entry from the playbook that is deemed unhelpful or redundant for future navigation tasks.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "bullet_id": {
                                "type": "string",
                                "description": "The identifier of the bulletpoint to be removed from the playbook."
                            }
                        },
                        "required": ["bullet_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "MODIFY",
                    "description": "Modifies an existing entry in the playbook to improve its clarity, accuracy, or relevance for future navigation tasks.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "bullet_id": {
                                "type": "string",
                                "description": "The identifier of the bulletpoint to be modified to the playbook."
                            },
                            "content": {
                                "type": "string",
                                "description": "The content which will overwrite the existing entry in the playbook."
                            }
                        },
                        "required": ["bullet_id", "content"]
                    }
                }
            }
        ]