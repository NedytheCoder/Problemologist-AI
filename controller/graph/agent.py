from deepagents import create_deep_agent
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, ToolMessage, ToolCall
from controller.clients.backend import RemoteFilesystemBackend
from controller.config.settings import settings
from controller.observability.langfuse import get_langfuse_callback
from controller.prompts import get_prompt
from shared.cots.agent import search_cots_catalog
from shared.logging import get_logger
#! First of all, there was no .env and openapi stuff, then the mock agent response was only pure json and wasn't langchain format that the agent expected
logger = get_logger(__name__)


def create_agent_graph(
    backend: RemoteFilesystemBackend,
    agent_name: str = "engineer_coder",
    trace_id: str | None = None,
):
    """Create a Deep Agent graph with remote filesystem backend."""

    if settings.is_integration_test:
        from typing import Any

        class FakeModelWithTools:
            responses: list[str]
            model_name: str = "mock-model"
            _current_response_idx: int = 0

            def _generate(
                self,
                messages: list[Any],
                stop: list[str] | None = None,
                run_manager: Any = None,
                **kwargs: Any,
            ) -> Any:
                _ = messages, stop, run_manager, kwargs
                if self._current_response_idx >= len(self.responses):
                    raise ValueError(
                        "No more responses available in FakeModelWithTools"
                    )
                response_content = self.responses[self._current_response_idx]
                self._current_response_idx += 1
                return type('MockResult', (), {'generations': [type('MockGeneration', (), {'message': type('MockMessage', (), {'content': response_content})})]})()

            @property
            def _llm_type(self) -> str:
                return "fake-chat-model"

            def bind_tools(self, tools: Any, **kwargs: Any) -> Any:
                _ = tools, kwargs
                return self

            async def ainvoke(self, input_data, config=None, **kwargs):
                import asyncio
                await asyncio.sleep(1.0)  # Simulate processing time
                return await self._generate(input_data, **kwargs)

            def with_config(self, config: Any) -> Any:
                llm = FakeModelWithTools()
                llm.responses = [
                    # Tool call to write file - properly formatted JSON
                    '{"action": "write_file", "action_input": {"path": "worker_execution.txt", "content": "verified"}}',
                    # Tool result for write_file
                    'File written successfully to worker_execution.txt',
                    # Tool call to submit for review
                    '{"action": "submit_for_review", "action_input": {"script_path": "solution.py"}}',
                    # Tool result for submit_for review
                    'Solution submitted for review',
                    # Final completion message
                    "I have completed task successfully by writing a verification file and submitting it for review.",
                ]
                return llm

            responses = [

                # 1️⃣ AI calls write_file
                AIMessage(
                    content="",
                 tool_calls=[
                    ToolCall(
                        id="call_1",
                        name="write_file",
                        args={"path": "worker_execution.txt", "content": "verified"}
                    )
                ]
                ),

                # 2️⃣ Tool responds
                ToolMessage(
                    content="File written successfully to worker_execution.txt",
                    tool_call_id="call_1",
                ),

                # 3️⃣ AI calls submit_for_review
                AIMessage(
                    content="",
                    tool_calls=[
                        ToolCall(
                            id="call_2",
                            name="submit_for_review",
                            args={"script_path": "solution.py"}
                        )
                    ],
                ),

                # 4️⃣ Tool responds
                ToolMessage(
                    content="Solution submitted for review",
                    tool_call_id="call_2",
                ),

                # 5️⃣ Final AI message
                AIMessage(
                    content="I have completed task successfully by writing a verification file and submitting it for review."
                ),
            ]

        llm = FakeModelWithTools()
        llm.responses = [
            '{"action": "write_file", "action_input": {"path": "worker_execution.txt", "content": "verified"}}',
            'File written successfully to worker_execution.txt',
            '{"action": "submit_for_review", "action_input": {"script_path": "solution.py"}}',
            'Solution submitted for review',
            "I have completed task successfully by writing a verification file and submitting it for review.",
        ]
    else:
        llm = ChatOpenAI(
            model_name=settings.llm_model,
            temperature=settings.llm_temperature,
            base_url=settings.openai_api_base,
            api_key=settings.openai_api_key,
        )

    # Try to get Langfuse callback
    langfuse_callback = get_langfuse_callback(trace_id=trace_id)
    callbacks = [langfuse_callback] if langfuse_callback else []

    # Map simple agent names to config prompt keys
    # Keys must match controller/config/prompts.yaml structure
    prompt_mapping = {
        "benchmark_planner": "benchmark_generator.planner.system",
        "benchmark_coder": "benchmark_generator.coder.system",
        "benchmark_reviewer": "benchmark_generator.reviewer.system",
        "engineer_planner": "engineer.planner.system",
        "engineer_coder": "engineer.engineer.system",
        "engineer_reviewer": "engineer.critic.system",
        "cots_search": "subagents.cots_search.system",
    }

    # Fallback or direct key usage
    prompt_key = prompt_mapping.get(agent_name, f"{agent_name}.system")

    try:
        system_prompt = get_prompt(prompt_key)
    except Exception as err:
        raise ValueError(
            f"Could not find prompt for {agent_name} mapped to {prompt_key}."
        ) from err

    if callbacks:
        llm = llm.with_config({"callbacks": callbacks})

    # Define subagents
    cots_search_subagent = {
        "name": "cots_search",
        "description": "Search for components (motors, fasteners, bearings).",
        "system_prompt": get_prompt("subagents.cots_search.system"),
        "tools": [search_cots_catalog],
    }

    # Map agents that have access to subagents
    primary_agents = [
        "engineer_planner",
        "engineer_coder",
        "benchmark_planner",
    ]
    subagents = []
    if agent_name in primary_agents:
        subagents = [cots_search_subagent]

    # Tools for the agent itself
    agent_tools = []
    if agent_name == "cots_search":
        agent_tools = [search_cots_catalog]

    agent = create_deep_agent(
        model=llm,
        backend=backend,
        system_prompt=system_prompt,
        name=agent_name,
        subagents=subagents,
        tools=agent_tools,
    )
    return agent, langfuse_callback
