import yaml
from pocketflow import Node
from ..utils.call_llm import call_local_llm

class DecideToolNode(Node):
    def prep(self, shared):
        """Prepare the prompt for LLM to process the question"""
        tool_info = shared["tool_info"]
        question = shared["question"]

        prompt = f"""
### CONTEXT
You are an assistant that can use tools via Model Context Protocol (MCP).

### ACTION SPACE
{tool_info}

### TASK
Answer this question: "{question}"

## NEXT ACTION
Analyze the question, extract any numbers or parameters, and decide which tool to use.
Return your response in this format:

```yaml
thinking: |
    <your step-by-step reasoning about what the question is asking and what numbers to extract>
tool: <name of the tool to use>
reason: <why you chose this tool>
parameters:
    <parameter_name>: <parameter_value>
    <parameter_name>: <parameter_value>
```
IMPORTANT: 
1. Extract numbers from the question properly
2. Use proper indentation (4 spaces) for multi-line fields
3. Use the | character for multi-line text fields
"""
        return prompt

    def exec(self, prompt):
        """Call LLM to process the question and decide which tool to use"""
        print("🤔 Analyzing question and deciding which tool to use...")
        response = call_local_llm(prompt)
        return response

    def post(self, shared, prep_res, exec_res):
        """Extract decision from YAML and save to shared context"""
        try:
            yaml_str = exec_res.split("```yaml")[1].split("```")[0].strip()
            decision = yaml.safe_load(yaml_str)

            shared["tool_name"] = decision["tool"]
            shared["parameters"] = decision["parameters"]
            shared["thinking"] = decision.get("thinking", "")

            print(f"💡 Selected tool: {decision['tool']}")
            print(f"🔢 Extracted parameters: {decision['parameters']}")

            return "execute"
        except Exception as e:
            print(f"❌ Error parsing LLM response: {e}")
            print("Raw response:", exec_res)
            return None