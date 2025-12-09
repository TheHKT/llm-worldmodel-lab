from prompts.Prompt import Prompt

class FrozenLakePrompt(Prompt):
    def getGeneratorPrompt(self, state="") -> str:
        return [
            {
                "role": "system",
                "content": f'''
You are a multi-turn LLM Agent Navigator in a dynamic 2D environment. Your goal: reach position G from current position [] using the provided tools for movement.

## Multi-Turn Operation
You receive a NAVIGATION TRAJECTORY containing:
- All your previous decisions and reasoning
- Environment responses after each action
- Current state resulting from your last move

Your output becomes input for your next iteration. Each decision builds on this growing trace, so reason clearly to help your future self.

## Core Task
Analyze the trajectory → Determine current state → Read the playbook and the reflection → Decide one move from the given context

## Decision Process
1. **Extract Current State** (from trajectory)
   - Your position: []
   - Goal position: G
   - Obstacles, boundaries, patterns observed

2. **Apply Learning**
   - PLAYBOOK: Proven strategies for similar situations, common failure patterns, environment dynamics
   - REFLECTION: What worked and what failed, corrected approaches

3. **Execute Single Move**
   - Reason concisely (this persists in your trace)
   - Call exactly ONE tool: move_left, move_right, move_up, move_down
   - Environment responds → new state → next iteration begins

## Critical Constraints
✓ One tool call per turn (you're multi-turn, not multi-action)
✓ State only updates after environment processes your move
✓ Your reasoning propagates forward—be clear and useful
✗ Never call multiple movement tools
✗ Don't assume behaviors not observed in the trajectory

## Input Context
PLAYBOOK_START
{self.playbook if self.playbook is not None else 'No playbook available'}
PLAYBOOK_END

REFLECTION_START
{self.reflection if self.reflection is not None else 'No prior mistakes recorded'}
REFLECTION_END

STATE_START
{state if state is not None else 'State unavailable'}
STATE_END
'''
            }
        ]
    
    def getGeneratorTools(self) -> str:
        return [
            {
                "type": "function",
                "function": {
                    "name": "move_left",
                    "description": "Moves the player left in the 2D environment. It returns the new state after the move was executed, the reward obtained and whether the task is terminated."
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "move_right",
                    "description": "Moves the player right in the 2D environment. It returns the new state after the move was executed, the reward obtained and whether the task is terminated."
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "move_up",
                    "description": "Moves the player up in the 2D environment. It returns the new state after the move was executed, the reward obtained and whether the task is terminated."
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "move_down",
                    "description": "Moves the player down in the 2D environment. It returns the new state after the move was executed, the reward obtained and whether the task is terminated."
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