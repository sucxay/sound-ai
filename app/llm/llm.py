from app.tools.browser_automation import open_website
from app.tools.macos import close_app, open_app
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import ToolMessage
from dotenv import load_dotenv

import os




load_dotenv()

tools = [
    open_app,
    close_app,
    open_website
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

        response = await self.model_with_tools.ainvoke(text)

        
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

            # Send tool result back to LLM
            messages = [
                {
                    "role": "user",
                    "content": text
                },
                response,
                *tool_messages
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