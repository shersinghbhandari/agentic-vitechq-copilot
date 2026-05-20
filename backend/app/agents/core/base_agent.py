# backend/app/agents/core/base_agent.py

from abc import ABC, abstractmethod
from time import perf_counter
from typing import Any

from app.agents.core.agent_context import AgentContext


class BaseAgent(ABC):
    """
    Canonical execution wrapper for all agents.

    Architectural Purpose
    ---------------------
    Standardizes:
        - execution lifecycle
        - tracing
        - timing
        - token observability
        - failure handling

    Design Principles
    -----------------
    1. Cross-agent consistency
       - Every agent follows same execution contract.

    2. Centralized observability
       - Timing, tracing, and token tracking handled once.

    3. Thin orchestration layer
       - Business logic stays inside run() only.

    4. Future extensible
       - Supports retries, metrics, evaluation,
         guardrails, and distributed tracing.
    """

    name: str = "BaseAgent"

    def execute(
        self,
        context: AgentContext,
    ) -> AgentContext:
        """
        Standardized agent execution entrypoint.
        """

        start_time = perf_counter()

        try:
            self.trace(
                context,
                "Started.",
            )

            result = self.run(context)

            duration_ms = round(
                (perf_counter() - start_time) * 1000,
                2,
            )

            self.trace(
                result,
                f"Completed. duration_ms={duration_ms}.",
            )

            return result

        except Exception as ex:
            self.trace(
                context,
                f"Failed. error={str(ex)}",
            )
            raise

    @abstractmethod
    def run(
        self,
        context: AgentContext,
    ) -> AgentContext:
        """
        Agent-specific implementation.
        """
        pass

    def trace(
        self,
        context: AgentContext,
        message: str,
    ) -> None:
        """
        Lightweight orchestration tracing.

        Future Direction
        ----------------
        Can evolve into structured telemetry
        with OpenTelemetry integration.
        """

        context.add_trace(
            f"{self.name}: {message}"
        )

    def track_token_usage(
        self,
        context: AgentContext,
        response: Any,
    ) -> None:
        """
        Centralized LLM token tracking.

        Architectural Purpose
        ---------------------
        Enables:
            - cost monitoring
            - model optimization
            - prompt efficiency analysis
            - tenant-level AI observability
        """

        usage = self._extract_token_usage(response)

        if not usage:
            return

        existing_usage = context.token_usage.get(
            self.name,
            {
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
            },
        )

        existing_usage["input_tokens"] += usage.get(
            "input_tokens",
            0,
        )

        existing_usage["output_tokens"] += usage.get(
            "output_tokens",
            0,
        )

        existing_usage["total_tokens"] += usage.get(
            "total_tokens",
            0,
        )

        context.token_usage[self.name] = existing_usage

        self.trace(
            context,
            (
                "Token usage tracked. "
                f"input={usage.get('input_tokens', 0)}, "
                f"output={usage.get('output_tokens', 0)}, "
                f"total={usage.get('total_tokens', 0)}."
            ),
        )

    def _extract_token_usage(
        self,
        response: Any,
    ) -> dict[str, int]:
        """
        Provider-agnostic token extraction.

        Design Principle
        ----------------
        Different LLM providers expose token
        metadata differently.

        This method normalizes usage tracking
        into a unified internal contract.
        """

        response_metadata = getattr(
            response,
            "response_metadata",
            {},
        ) or {}

        usage = (
            response_metadata.get("token_usage")
            or response_metadata.get("usage")
            or {}
        )

        usage_metadata = getattr(
            response,
            "usage_metadata",
            {},
        ) or {}

        input_tokens = (
            usage.get("prompt_tokens")
            or usage.get("input_tokens")
            or usage_metadata.get("input_tokens")
            or 0
        )

        output_tokens = (
            usage.get("completion_tokens")
            or usage.get("output_tokens")
            or usage_metadata.get("output_tokens")
            or 0
        )

        total_tokens = (
            usage.get("total_tokens")
            or usage_metadata.get("total_tokens")
            or input_tokens + output_tokens
        )

        return {
            "input_tokens": int(input_tokens or 0),
            "output_tokens": int(output_tokens or 0),
            "total_tokens": int(total_tokens or 0),
        }