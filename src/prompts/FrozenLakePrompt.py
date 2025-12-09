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
You are an expert reflection agent analyzing a multi-turn navigation trajectory. The navigation agent operated iteratively: it received a trace, made ONE decision using guidance from a PLAYBOOK, got environment feedback, then was called again with the updated trace. Your job is to diagnose what went wrong across these iterations AND evaluate the playbook's effectiveness.

## Understanding the Multi-Turn Trace
The NAVIGATION_TRAJECTORY shows:
- Agent's reasoning at each turn (based on accumulated context and playbook)
- Single action executed per turn
- Environment's response after each action
- How errors compounded or were corrected across iterations

## Your Analysis Task
1. **Trace the Decision Chain**: Follow how the agent interpreted its growing trace at each step
2. **Analyze Playbook Usage**: 
   - Which playbook strategies did the agent apply or ignore?
   - Were strategies applied correctly in context?
   - Did playbook guidance lead to success or failure?
3. **Identify Breaking Points**: Where did reasoning diverge from optimal strategy?
4. **Diagnose Root Causes**:
   - Misinterpretation of previous feedback in the trace
   - Incorrect state extraction from trajectory
   - Misapplied or ignored playbook strategies
   - Tool usage errors or format mismatches
5. **Evaluate Each Playbook Bulletpoint**: Tag as 'helpful', 'harmful', or dont tag (skip) it if it was neutral based on:
   - Did it guide the agent toward correct decisions?
   - Did it cause errors or confusion?
   - Was it irrelevant to the observed failure?

## Critical Constraints
✓ Explicitly assess each playbook item's impact on navigation
✓ Focus on strategy and tool usage patterns (not environment layout—it changes)
✓ Ground analysis in actual environment feedback, not assumptions
✓ Provide actionable corrections applicable to future multi-turn episodes
✗ Don't learn specific positions or obstacle locations

## Inputs
NAVIGATION_TRAJECTORY_BEGIN
{self.generatorOutput if self.generatorOutput is not None else ''}
NAVIGATION_TRAJECTORY_END

PLAYBOOK_BEGIN
{self.playbook if self.playbook is not None else ''}
PLAYBOOK_END

## Required Output (JSON only)
{{
  "reasoning": "[Trace the multi-turn decision chain: what did the agent observe, decide, and receive as feedback at each iteration? Which playbook strategies were applied? Where did the reasoning break down?]",
  "error_identification": "[Specific mistakes in trace interpretation, playbook application, tool usage, or strategy selection across turns]",
  "root_cause_analysis": "[Why did the agent fail to learn from its growing trace? What concept about multi-turn operation was misunderstood? Were playbook strategies misleading or misapplied?]",
  "correct_approach": "[Step-by-step: how should the agent have processed the trace, applied playbook guidance, and made decisions differently?]",
  "key_insight": "[Generalizable strategy for multi-turn navigation: principles for trace interpretation, feedback integration, playbook usage, or tool usage]",
  "bullet_tags": [{{"id": "example_id", "tag": "helpful|harmful"}}]
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