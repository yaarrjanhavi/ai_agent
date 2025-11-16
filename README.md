# 🤖 Action Item Automator Agent (AI-Powered Meeting Summary)

## 🌟 Project Overview

This project implements an intelligent agent designed to solve the common problem of **"Meeting Notes That Never Get Used."**

The **Action Item Automator Agent** uses the Gemini API to analyze raw meeting transcripts (or audio output), reliably extract critical information, and format it into a structured, project-ready document (Markdown table), simulating an automatic post to a project management tool (like Jira, Asana, or Trello).

The core value lies in transforming unstructured text into clean, actionable data points, complete with assigned owners, due dates, and priority levels.

-----

## ✨ Features

  * **Structured Data Extraction:** Utilizes the Gemini API's **structured output** capability (via Pydantic) to guarantee clean, machine-readable JSON output every time.
  * **Transcript File Input:** Reads the meeting content from an external text file (`meeting_transcript.txt`).
  * **Intelligent Due Date Estimation:** The agent uses the current date as context to interpret relative time phrases in the transcript (e.g., "next Friday," "tomorrow").
  * **Professional Output:** Generates a clean, human-readable **Markdown (`.md`) file** with action items presented in an easy-to-scan table format, ready for immediate use.
  * **Key Decision Highlighting:** Separately identifies and lists critical decisions made during the meeting.

-----

## ⚙️ Tech Stack

| Component | Technology | Role |
| :--- | :--- | :--- |
| **Agent Core** | Python 3.9+ | Main application logic and orchestration. |
| **AI/LLM** | **Google Gemini API (gemini-2.5-flash)** | Handles the complex natural language understanding and structured extraction. |
| **Data Schema** | Pydantic | Defines the strict data model for reliable JSON output. |
| **Environment** | `python-dotenv` (Optional) | Manages the API key securely. |

-----

## 🚀 Getting Started

Follow these steps to set up and run the agent locally.

### 1\. Prerequisites

  * **Python 3.9+** installed on your system.
  * A **Gemini API Key**.

### 2\. Setup and Installation

1.  **Clone the repository:**

    ```bash
    git clone [YOUR_REPOSITORY_URL]
    cd action-item-automator
    ```

2.  **Install dependencies:**

    ```bash
    pip install google-genai pydantic python-dotenv
    ```

3.  **Set your API Key:**
    The script requires your API key to be set as an environment variable.

      * **Secure Method (Recommended):** Create a file named **`.env`** in the project directory and add your key:
        ```
        GEMINI_API_KEY="YOUR_API_KEY_HERE"
        ```
      * **Direct Terminal (Temporary):**
        ```bash
        # Linux/macOS
        export GEMINI_API_KEY="YOUR_API_KEY_HERE"

        # Windows PowerShell
        $env:GEMINI_API_KEY="YOUR_API_KEY_HERE"
        ```

### 3\. Prepare the Input

1.  Create a file named **`meeting_transcript.txt`** in the same directory.
2.  Paste your meeting transcript into this file.

### 4\. Run the Agent

Execute the Python script:

```bash
python agent_v2.py
```

## 📂 Output

Upon successful execution, a file named **`action_items_output.md`** will be generated in the project directory, containing the fully structured and formatted summary, ready for use in any project management environment.

-----

## 📝 Data Model (Pydantic Schema)

The agent strictly adheres to this output schema to ensure consistent and reliable data extraction.

| Field | Type | Description |
| :--- | :--- | :--- |
| `task_description` | `str` | The specific action item (verb-first). |
| `owner` | `str` | The person responsible. |
| `type` | `str` | `Action Item`, `Decision`, or `Follow-up`. |
| `priority` | `str` | `High`, `Medium`, or `Low`. |
| `due_date` | `str` | Estimated date (YYYY-MM-DD) or `TBD`. |
| `confidence_score` | `int` | LLM's confidence (1-100) in the extraction. |

## 💡 Future Enhancements

  * **Direct PM Integration:** Implement API calls to create tickets directly in Jira, Asana, or Trello.
  * **Audio Input:** Integrate with a transcription service (like Whisper or Deepgram) to accept audio files directly.
  * **Web Interface:** Build a simple web front-end (using Flask/FastAPI) to allow users to upload files and view the results in a browser.
