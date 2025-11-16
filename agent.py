import os
import json
import datetime
from google import genai
from google.genai import types
from google.genai.errors import APIError
from pydantic import BaseModel, Field
from typing import List
from dotenv import load_dotenv # Used for local API key loading (optional but recommended)

# Load environment variables from a .env file if it exists
load_dotenv() 

# --- 1. Define the Advanced Structured Output Schema ---

class ActionItem(BaseModel):
    """Defines the structure for an advanced task extraction."""
    
    task_description: str = Field(
        description="The specific action item, task, or decision identified. Clear and concise, starting with a verb."
    )
    owner: str = Field(
        description="The person responsible for completing the item. Must be a name explicitly mentioned in the transcript."
    )
    type: str = Field(
        description="The category of the item (e.g., 'Action Item', 'Decision', 'Follow-up')."
    )
    priority: str = Field(
        description="The suggested priority for the item (must be 'High', 'Medium', or 'Low')."
    )
    due_date: str = Field(
        description="Estimate the required completion date based on temporal clues (e.g., 'tomorrow', 'next Friday') or use 'TBD' if no time frame is given. Format as YYYY-MM-DD if possible."
    )
    confidence_score: int = Field(
        description="A confidence score (1-100) indicating how certain you are that this is a definitive action item."
    )

class MeetingSummary(BaseModel):
    """The complete structured output for the meeting analysis."""
    
    action_items: List[ActionItem] = Field(
        description="A list of all structured action items extracted from the transcript."
    )
    overall_summary: str = Field(
        description="A brief, 2-3 sentence summary of the meeting's primary purpose, key discussion points, and outcome."
    )
    key_decisions_made: List[str] = Field(
        description="A list of 1-3 critical high-level decisions explicitly made during the meeting."
    )


# --- 2. Utility Functions ---

def read_transcript(filename: str) -> str:
    """Reads the transcript from a specified file."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"ERROR: Transcript file '{filename}' not found.")
        return ""

def format_and_save_results(data: MeetingSummary, meeting_date: str):
    """Formats the results into a professional and tidy Markdown file."""
    filename = "action_items_output.md"
    
    output = []
    output.append(f"# 📊 Meeting Summary & Action Items")
    output.append(f"") # Blank line for spacing
    output.append(f"---")
    output.append(f"**Meeting Date:** `{meeting_date}`")
    output.append(f"**Report Generated:** `{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`")
    output.append(f"---")
    output.append(f"") # Blank line
    
    # 1. Overall Summary
    output.append(f"## 📝 Key Meeting Overview")
    output.append(f"> {data.overall_summary}\n") # Use blockquote for summary
    
    # 2. Key Decisions
    if data.key_decisions_made: # Only show if there are decisions
        output.append(f"## 🛑 Critical Decisions Made")
        for i, decision in enumerate(data.key_decisions_made, 1):
            output.append(f"- **Decision {i}:** {decision}")
        output.append("") # Blank line
    
    # 3. Action Items (Structured Table)
    output.append(f"## ✅ Action Items & Follow-ups")
    
    # Table Header
    output.append("| Priority | Type | Task Description | Owner | Due Date |")
    output.append("| :------: | :--: | :--------------- | :----: | :--------: |") # Alignments
    
    # Table Rows
    for item in data.action_items:
        # Use emojis for a 'fancy' visual queue
        emoji = {"High": "🔥", "Medium": "🟡", "Low": "⚪"}.get(item.priority, "❓")
        priority_display = f"{emoji} {item.priority}"
        owner_display = f"@{item.owner}"
        
        # Ensure the task description doesn't break the table format
        task_desc_escaped = item.task_description.replace('|', '\\|')

        output.append(
            f"| {priority_display} | `{item.type}` | {task_desc_escaped} | {owner_display} | {item.due_date} |"
        )
    output.append("") # Blank line after table
    output.append("---\n")
    
    # 4. Agent Notes (Footnotes)
    output.append(f"") 
    output.append("### Agent Notes")
    output.append(f"*Confidence scores were used internally for extraction and are not displayed in this report.*")
    output.append(f"*Please verify all details and update your project management tool.*")


    # Write to file
    with open(filename, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output))
        
    print(f"\n✨ Successfully wrote professional output to: **{filename}**")


# --- 3. Agent Logic and Execution ---

def run_action_item_automator():
    """Main execution function for the enhanced agent."""
    
    # Check for API Key
    if 'GEMINI_API_KEY' not in os.environ:
        print("ERROR: Please set the GEMINI_API_KEY environment variable.")
        return

    # --- INPUT GATHERING ---
    TRANSCRIPT_FILE = 'meeting_transcript.txt'
    # Use today's date as context for relative due dates (e.g., 'next Friday')
    meeting_date_str = datetime.date.today().strftime('%Y-%m-%d')
    
    transcript = read_transcript(TRANSCRIPT_FILE)
    if not transcript:
        return

    try:
        # Initialize the Gemini Client
        client = genai.Client()

        # --- ADVANCED PROMPT ENGINEERING ---
        system_instruction = (
            "You are a professional Action Item Extraction and Project Management Agent. "
            "Your critical task is to analyze the meeting transcript and extract every required field "
            "into the specified JSON schema. Use the provided meeting date to help calculate the 'due_date' "
            "from relative phrases like 'tomorrow' or 'next week'. Be strict with the schema."
        )

        prompt = (
            f"MEETING DATE: {meeting_date_str}\n\n"
            f"Analyze the following transcript and extract all structured data:\n\n"
            f"TRANSCRIPT:\n---\n{transcript}\n---"
        )

        # Configure the model call for structured output using the Pydantic model
        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
            response_schema=MeetingSummary,
        )

        print("🧠 Analyzing transcript with Gemini...")
        
        # Call the Gemini API
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=config,
        )
        
        print("✅ Analysis complete.")

        # --- PROCESS AND DISPLAY ---
        parsed_data = MeetingSummary.model_validate_json(response.text)
        
        # Save the structured data to the professional Markdown file
        format_and_save_results(parsed_data, meeting_date_str)
        
    except APIError as e:
        print(f"An API error occurred: {e}")
    except json.JSONDecodeError:
        print(f"Error: The model returned invalid JSON. Response text:\n{response.text}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    run_action_item_automator()