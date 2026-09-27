from app.tools.browser_automation import open_website
from app.tools.macos import close_app, open_app
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import ToolMessage
from dotenv import load_dotenv
from app.tools.media import (
    play_music,
    pause_music,
    next_track,
    previous_track,
    play_album,
    play_song,
)


import os




load_dotenv()

tools = [
    open_app,
    close_app,
    open_website,
    play_music,
    pause_music,
    next_track,
    previous_track,
    play_album,
    play_song,
]


class LLM:

    def __init__(self):

        groq = ChatGroq(
            model="openai/gpt-oss-120b",
            api_key=os.getenv("GROQ_API_KEY"),
            temperature=0.7
        )

        gemini = ChatGoogleGenerativeAI(
            model="gemini-3.6-flash",
            google_api_key=os.getenv("GEMINI_API_KEY"),
            temperature=0.7
        )

        # Plain models (no tools) — used for final response after tool execution
        self._groq_plain = groq
        self._gemini_plain = gemini

        # Plain fallback model — used for normal (non-tool) responses
        self.model = groq.with_fallbacks([gemini])

        # Tool-bound model — used only for the initial invocation to decide if a tool should be called
        self.model_with_tools = groq.bind_tools(tools).with_fallbacks([gemini.bind_tools(tools)])

        self.tool_map = {
            tool.name: tool
            for tool in tools
        }

    async def generate_answer(self, text: str):

        system_prompt = (
            "You are a helpful voice assistant running on macOS. "
            "You have tools to control Apple Music (play, pause, next track, previous track, play a specific song or album). "
            "When the user asks you to play a song or album, ALWAYS use the play_song or play_album tool — never suggest YouTube links or external URLs. "
            "If the tool indicates a song was played from the library, confirm that it is playing. "
            "If the tool indicates a song was not in the library and search was opened, inform the user that it was not in their library and you opened Apple Music search for it. "
            "When the user asks to open or close an app, use the open_app or close_app tool. "
            "When the user asks to open a website, use the open_website tool. "
            "Keep your spoken responses short and natural, since they will be read aloud."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text},
        ]

        response = await self.model_with_tools.ainvoke(messages)

        
        if response.tool_calls:

            tool_messages = []

            for tool_call in response.tool_calls:

                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                tool_id = tool_call["id"]

                tool = self.tool_map[tool_name]

                result = tool.invoke(tool_args)

                tool_messages.append(
                    ToolMessage(
                        content=str(result),
                        tool_call_id=tool_id
                    )
                )

            # Send tool result back to LLM (include system prompt for context)
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
                response,
                *tool_messages,
            ]

            # Stream the final response. Groq sometimes raises a tool-choice
            # APIError even on a plain model when the history contains tool
            # messages, so we collect any streamed chunks and fall back to
            # Gemini streaming if that happens.
            try:
                async for chunk in self._groq_plain.astream(messages):
                    if chunk.content:
                        yield chunk.content
            except Exception:
                async for chunk in self._gemini_plain.astream(messages):
                    if chunk.content:
                        yield chunk.content

        else:

            # Normal response — no tool calls, stream directly.
            async for chunk in self.model.astream(text):
                if chunk.content:
                    yield chunk.content