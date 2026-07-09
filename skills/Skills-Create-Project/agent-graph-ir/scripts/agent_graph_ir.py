#!/usr/bin/env python3
"""Typed agent graph IR: models, validation, renderers, and trace export."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from time import perf_counter
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field


KST = timezone(timedelta(hours=9))


def _now_iso() -> str:
    return datetime.now(KST).isoformat(timespec="seconds")


class NodeKind(str, Enum):
    OBSERVE = "observe"
    ROUTER = "router"
    GROUND = "ground"
    PLAN = "plan"
    ACTION = "action"
    REFLECT = "reflect"
    STOP = "stop"


class ScopeKind(str, Enum):
    ROOT = "root"
    ROUTER = "router"
    LOOP = "loop"


class Severity(str, Enum):
    ERROR = "error"
    WARNING = "warning"


class CaptureMode(str, Enum):
    TOOL_SPECIFIC = "tool_specific"
    WINDOW = "window"
    REGION = "region"
    DESKTOP = "desktop"


class VarDef(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str
    meaning: str
    type: str
    scope_id: str
    unit: str | None = None


class VarExpr(BaseModel):
    model_config = ConfigDict(extra="forbid")
    kind: Literal["var"] = "var"
    name: str


class ConstExpr(BaseModel):
    model_config = ConfigDict(extra="forbid")
    kind: Literal["const"] = "const"
    value: Any


class RefExpr(BaseModel):
    model_config = ConfigDict(extra="forbid")
    kind: Literal["ref"] = "ref"
    id: str


class UnaryExpr(BaseModel):
    model_config = ConfigDict(extra="forbid")
    kind: Literal["unary"] = "unary"
    op: Literal["not", "neg"]
    arg: "Expr"


class BinaryExpr(BaseModel):
    model_config = ConfigDict(extra="forbid")
    kind: Literal["binary"] = "binary"
    op: Literal["eq", "neq", "lt", "lte", "gt", "gte", "in", "contains"]
    left: "Expr"
    right: "Expr"


class NaryExpr(BaseModel):
    model_config = ConfigDict(extra="forbid")
    kind: Literal["nary"] = "nary"
    op: Literal["and", "or", "add", "mul"]
    args: list["Expr"]


Expr = Annotated[
    VarExpr | ConstExpr | RefExpr | UnaryExpr | BinaryExpr | NaryExpr,
    Field(discriminator="kind"),
]


class Node(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    kind: NodeKind
    label: str
    scope_id: str
    tool: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class Edge(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    src: str
    dst: str
    scope_id: str
    route_id: str | None = None
    condition_id: str | None = None


class LoopMeta(BaseModel):
    model_config = ConfigDict(extra="forbid")
    loop_id: str
    max_iterations: int
    break_condition_id: str
    timeout_ms: int | None = None


class RouterMeta(BaseModel):
    model_config = ConfigDict(extra="forbid")
    router_id: str
    selection_policy: Literal["first_true", "llm_ranked", "majority_vote"]
    default_route_id: str | None = None


class Scope(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    kind: ScopeKind
    parent_scope_id: str | None = None
    loop: LoopMeta | None = None
    router: RouterMeta | None = None


class Formula(BaseModel):
    model_config = ConfigDict(extra="forbid")
    ast: Expr
    latex: str


class ValidationRule(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    severity: Severity
    message: str


class RouteDefinition(BaseModel):
    model_config = ConfigDict(extra="forbid")
    route_id: str
    condition_id: str


class RouterDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")
    router_id: str
    routes: list[RouteDefinition]
    selection_policy: Literal["first_true", "llm_ranked", "majority_vote"]


class ToolCall(BaseModel):
    model_config = ConfigDict(extra="forbid")
    tool_name: str
    input: dict[str, Any] = Field(default_factory=dict)
    output: dict[str, Any] = Field(default_factory=dict)
    latency_ms: int | None = None


class CaptureRegion(BaseModel):
    model_config = ConfigDict(extra="forbid")
    x: int
    y: int
    width: int
    height: int


class CaptureRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    target_app: str | None = None
    window_name: str | None = None
    tool_name: str | None = None
    region: CaptureRegion | None = None
    prefer_tool_specific: bool = True
    allow_desktop_fallback: bool = True


class CaptureRoute(BaseModel):
    model_config = ConfigDict(extra="forbid")
    route_id: str
    capture_mode: CaptureMode
    source: str
    priority: int
    reason: str


class CaptureArtifact(BaseModel):
    model_config = ConfigDict(extra="forbid")
    artifact_ref: str
    file_path: str
    sha256: str
    width: int
    height: int
    mime_type: str
    capture_mode: CaptureMode
    target_app: str | None = None
    window_name: str | None = None


class RunEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")
    step_id: str
    node_id: str
    scope_instance_id: str
    iteration_id: int = 0
    timestamp: str
    selected_route: str | None = None
    stop_reason: str | None = None
    input: dict[str, Any] = Field(default_factory=dict)
    output: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
    tool_call: ToolCall | None = None


class RunSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")
    trace_id: str
    session_id: str
    status: Literal["success", "failed", "cancelled", "partial"]
    stop_reason: str | None = None
    latency_ms: int | None = None
    raw_action_count: int = 0
    final_action_count: int = 0
    selected_routes: list[dict[str, str]] = Field(default_factory=list)
    loop_iterations: dict[str, int] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentRun(BaseModel):
    model_config = ConfigDict(extra="forbid")
    summary: RunSummary
    trace: list[RunEvent]


class AgentSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")
    spec_version: str
    agent_id: str
    title: str | None = None
    variables: list[VarDef]
    nodes: list[Node]
    edges: list[Edge]
    scopes: list[Scope]
    conditions: dict[str, Expr]
    formulae: dict[str, Formula] = Field(default_factory=dict)
    router_decisions: list[RouterDecision] = Field(default_factory=list)
    validation_rules: list[ValidationRule] = Field(default_factory=list)


class ValidationIssue(BaseModel):
    model_config = ConfigDict(extra="forbid")
    code: str
    severity: Severity
    message: str
    path: str | None = None


class JsonSpecParser:
    """Thin parser that validates JSON into the canonical Pydantic models."""

    @staticmethod
    def parse(raw: str | dict[str, Any]) -> AgentSpec:
        if isinstance(raw, str):
            return AgentSpec.model_validate(json.loads(raw))
        return AgentSpec.model_validate(raw)


class JsonRunParser:
    """Thin parser that validates run JSON into the canonical Pydantic models."""

    @staticmethod
    def parse(raw: str | dict[str, Any]) -> AgentRun:
        if isinstance(raw, str):
            return AgentRun.model_validate(json.loads(raw))
        return AgentRun.model_validate(raw)


def build_capture_run(
    *,
    trace_id: str,
    session_id: str,
    events: list[RunEvent],
    status: Literal["success", "failed", "cancelled", "partial"] = "partial",
    stop_reason: str = "capture_completed",
    latency_ms: int | None = None,
    metadata: dict[str, Any] | None = None,
) -> AgentRun:
    return AgentRun(
        summary=RunSummary(
            trace_id=trace_id,
            session_id=session_id,
            status=status,
            stop_reason=stop_reason,
            latency_ms=latency_ms,
            raw_action_count=len(events),
            final_action_count=len(events),
            loop_iterations={},
            metadata=metadata or {},
        ),
        trace=events,
    )


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_png_dimensions(path: Path) -> tuple[int, int]:
    with path.open("rb") as handle:
        header = handle.read(24)
    if len(header) < 24 or header[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"Only PNG screenshot artifacts are supported in the first slice: {path}")
    width, height = struct.unpack(">II", header[16:24])
    return width, height


class OpenAiScreenshotPolicyAdapter:
    """Minimal adapter that encodes the official capture priority into typed IR helpers."""

    @staticmethod
    def plan_routes(request: CaptureRequest) -> list[CaptureRoute]:
        routes: list[CaptureRoute] = []
        priority = 1

        if request.prefer_tool_specific and request.tool_name:
            routes.append(
                CaptureRoute(
                    route_id="route_tool_specific",
                    capture_mode=CaptureMode.TOOL_SPECIFIC,
                    source=request.tool_name,
                    priority=priority,
                    reason="tool_specific_capture_available",
                )
            )
            priority += 1

        if request.window_name or request.target_app:
            routes.append(
                CaptureRoute(
                    route_id="route_window_capture",
                    capture_mode=CaptureMode.WINDOW,
                    source="os_window_capture",
                    priority=priority,
                    reason="app_or_window_target_present",
                )
            )
            priority += 1

        if request.region:
            routes.append(
                CaptureRoute(
                    route_id="route_region_capture",
                    capture_mode=CaptureMode.REGION,
                    source="os_region_capture",
                    priority=priority,
                    reason="bounded_region_present",
                )
            )
            priority += 1

        if request.allow_desktop_fallback:
            routes.append(
                CaptureRoute(
                    route_id="route_desktop_fallback",
                    capture_mode=CaptureMode.DESKTOP,
                    source="os_desktop_capture",
                    priority=priority,
                    reason="global_fallback",
                )
            )

        return routes

    @staticmethod
    def build_artifact(
        artifact_path: Path,
        *,
        capture_mode: CaptureMode,
        artifact_ref: str | None = None,
        target_app: str | None = None,
        window_name: str | None = None,
    ) -> CaptureArtifact:
        width, height = _read_png_dimensions(artifact_path)
        resolved_ref = artifact_ref or f"artifact://screens/{artifact_path.name}"
        return CaptureArtifact(
            artifact_ref=resolved_ref,
            file_path=str(artifact_path),
            sha256=_sha256_file(artifact_path),
            width=width,
            height=height,
            mime_type="image/png",
            capture_mode=capture_mode,
            target_app=target_app,
            window_name=window_name,
        )

    @classmethod
    def build_observe_event(
        cls,
        *,
        request: CaptureRequest,
        artifact_path: Path,
        step_id: str = "s_observe",
        node_id: str = "n_observe",
        scope_instance_id: str = "root#0",
        iteration_id: int = 0,
        timestamp: str | None = None,
        capture_mode: CaptureMode | None = None,
        artifact_ref: str | None = None,
    ) -> RunEvent:
        routes = cls.plan_routes(request)
        selected_route = routes[0] if routes else CaptureRoute(
            route_id="route_desktop_fallback",
            capture_mode=CaptureMode.DESKTOP,
            source="os_desktop_capture",
            priority=1,
            reason="default_fallback",
        )
        artifact = cls.build_artifact(
            artifact_path,
            capture_mode=capture_mode or selected_route.capture_mode,
            artifact_ref=artifact_ref,
            target_app=request.target_app,
            window_name=request.window_name,
        )
        return RunEvent(
            step_id=step_id,
            node_id=node_id,
            scope_instance_id=scope_instance_id,
            iteration_id=iteration_id,
            timestamp=timestamp or _now_iso(),
            input=request.model_dump(mode="json", exclude_none=True),
            output=artifact.model_dump(mode="json"),
            metadata={
                "capture_route_id": selected_route.route_id,
                "capture_route_candidates": [route.route_id for route in routes],
                "capture_priority_policy": "tool_specific_first_then_os_fallback",
            },
        )

    @staticmethod
    def parse_screenshot_skill_output(stdout_text: str) -> list[Path]:
        paths: list[Path] = []
        for raw_line in stdout_text.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            paths.append(Path(line).expanduser())
        return paths

    @classmethod
    def build_observe_events_from_screenshot_skill_output(
        cls,
        *,
        request: CaptureRequest,
        stdout_text: str,
        step_prefix: str = "s_observe",
        node_id: str = "n_observe",
        scope_instance_id: str = "root#0",
        iteration_id: int = 0,
        timestamp: str | None = None,
    ) -> list[RunEvent]:
        artifact_paths = cls.parse_screenshot_skill_output(stdout_text)
        runtime_request = request.model_copy(update={"prefer_tool_specific": False})
        events: list[RunEvent] = []

        for index, artifact_path in enumerate(artifact_paths, start=1):
            step_id = step_prefix if len(artifact_paths) == 1 else f"{step_prefix}_{index:03d}"
            event = cls.build_observe_event(
                request=runtime_request,
                artifact_path=artifact_path,
                step_id=step_id,
                node_id=node_id,
                scope_instance_id=scope_instance_id,
                iteration_id=iteration_id,
                timestamp=timestamp,
            )
            event.tool_call = ToolCall(
                tool_name="openai_curated_screenshot_skill",
                input=runtime_request.model_dump(mode="json", exclude_none=True),
                output={"printed_path": str(artifact_path)},
            )
            event.metadata["capture_output_index"] = index
            event.metadata["capture_output_count"] = len(artifact_paths)
            event.metadata["capture_output_source"] = "stdout_path_list"
            events.append(event)

        return events

    @classmethod
    def run_screenshot_command_bridge(
        cls,
        *,
        request: CaptureRequest,
        command: list[str],
        trace_id: str,
        session_id: str,
        step_prefix: str = "s_observe",
        node_id: str = "n_observe",
        scope_instance_id: str = "root#0",
        iteration_id: int = 0,
        timestamp: str | None = None,
        cwd: Path | None = None,
    ) -> dict[str, Any]:
        started = perf_counter()
        completed = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            cwd=str(cwd) if cwd else None,
        )
        elapsed_ms = int((perf_counter() - started) * 1000)
        events = cls.build_observe_events_from_screenshot_skill_output(
            request=request,
            stdout_text=completed.stdout,
            step_prefix=step_prefix,
            node_id=node_id,
            scope_instance_id=scope_instance_id,
            iteration_id=iteration_id,
            timestamp=timestamp,
        )
        if not events:
            raise RuntimeError("Screenshot bridge command completed but produced no artifact paths.")

        run = build_capture_run(
            trace_id=trace_id,
            session_id=session_id,
            events=events,
            status="partial",
            stop_reason="capture_completed",
            latency_ms=elapsed_ms,
            metadata={
                "target_app": request.target_app,
                "window_name": request.window_name,
                "capture_output_count": len(events),
                "screenshot_command_argv": command,
            },
        )
        return {
            "command": command,
            "cwd": str(cwd) if cwd else None,
            "returncode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "run": run.model_dump(mode="json"),
        }


def _dedupe_issues(issues: list[ValidationIssue]) -> list[ValidationIssue]:
    seen: set[tuple[str, str | None, str]] = set()
    unique: list[ValidationIssue] = []
    for issue in issues:
        key = (issue.code, issue.path, issue.message)
        if key in seen:
            continue
        seen.add(key)
        unique.append(issue)
    return unique


def _expr_refs(expr: Expr) -> list[str]:
    refs: list[str] = []
    if isinstance(expr, RefExpr):
        return [expr.id]
    if isinstance(expr, UnaryExpr):
        return _expr_refs(expr.arg)
    if isinstance(expr, BinaryExpr):
        return _expr_refs(expr.left) + _expr_refs(expr.right)
    if isinstance(expr, NaryExpr):
        for arg in expr.args:
            refs.extend(_expr_refs(arg))
    return refs


def _is_ancestor_scope(scope_by_id: dict[str, Scope], ancestor_id: str, descendant_id: str) -> bool:
    current = scope_by_id.get(descendant_id)
    while current and current.parent_scope_id is not None:
        if current.parent_scope_id == ancestor_id:
            return True
        current = scope_by_id.get(current.parent_scope_id)
    return False


def validate_spec(spec: AgentSpec) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    node_ids = [node.id for node in spec.nodes]
    edge_ids = [edge.id for edge in spec.edges]
    scope_ids = [scope.id for scope in spec.scopes]
    condition_ids = set(spec.conditions)
    formula_ids = set(spec.formulae)
    router_ids = {scope.router.router_id for scope in spec.scopes if scope.router}

    def _check_unique(values: list[str], code: str, label: str) -> None:
        counts = Counter(values)
        for value, count in counts.items():
            if count > 1:
                issues.append(
                    ValidationIssue(
                        code=code,
                        severity=Severity.ERROR,
                        message=f"Duplicate {label}: {value}",
                        path=label,
                    )
                )

    _check_unique(node_ids, "VR001", "node_id")
    _check_unique(edge_ids, "VR002", "edge_id")
    _check_unique(scope_ids, "VR003", "scope_id")

    node_by_id = {node.id: node for node in spec.nodes}
    scope_by_id = {scope.id: scope for scope in spec.scopes}

    root_scopes = [scope for scope in spec.scopes if scope.kind == ScopeKind.ROOT]
    if len(root_scopes) != 1:
        issues.append(
            ValidationIssue(
                code="VR004",
                severity=Severity.ERROR,
                message="Exactly one root scope is required.",
                path="scopes",
            )
        )

    for variable in spec.variables:
        if variable.scope_id not in scope_by_id:
            issues.append(
                ValidationIssue(
                    code="VR005",
                    severity=Severity.ERROR,
                    message=f"Variable {variable.name} references missing scope {variable.scope_id}.",
                    path=f"variables/{variable.name}",
                )
            )

    for node in spec.nodes:
        if node.scope_id not in scope_by_id:
            issues.append(
                ValidationIssue(
                    code="VR006",
                    severity=Severity.ERROR,
                    message=f"Node {node.id} references missing scope {node.scope_id}.",
                    path=f"nodes/{node.id}",
                )
            )

    for edge in spec.edges:
        if edge.src not in node_by_id:
            issues.append(
                ValidationIssue(
                    code="VR007",
                    severity=Severity.ERROR,
                    message=f"Edge {edge.id} references missing source node {edge.src}.",
                    path=f"edges/{edge.id}",
                )
            )
        if edge.dst not in node_by_id:
            issues.append(
                ValidationIssue(
                    code="VR008",
                    severity=Severity.ERROR,
                    message=f"Edge {edge.id} references missing destination node {edge.dst}.",
                    path=f"edges/{edge.id}",
                )
            )
        if edge.scope_id not in scope_by_id:
            issues.append(
                ValidationIssue(
                    code="VR009",
                    severity=Severity.ERROR,
                    message=f"Edge {edge.id} references missing scope {edge.scope_id}.",
                    path=f"edges/{edge.id}",
                )
            )
        if edge.condition_id and edge.condition_id not in condition_ids:
            issues.append(
                ValidationIssue(
                    code="VR010",
                    severity=Severity.ERROR,
                    message=f"Edge {edge.id} references missing condition {edge.condition_id}.",
                    path=f"edges/{edge.id}",
                )
            )
        src_node = node_by_id.get(edge.src)
        dst_node = node_by_id.get(edge.dst)
        if src_node and dst_node:
            src_scope_id = src_node.scope_id
            dst_scope_id = dst_node.scope_id
            if (
                src_scope_id != dst_scope_id
                and not _is_ancestor_scope(scope_by_id, src_scope_id, dst_scope_id)
                and not _is_ancestor_scope(scope_by_id, dst_scope_id, src_scope_id)
            ):
                if src_node.kind != NodeKind.ROUTER and dst_node.kind not in {
                    NodeKind.STOP,
                    NodeKind.OBSERVE,
                }:
                    issues.append(
                        ValidationIssue(
                            code="VR023",
                            severity=Severity.ERROR,
                            message=(
                                f"Edge {edge.id} crosses sibling scopes {src_scope_id} -> {dst_scope_id} "
                                "without a boundary node."
                            ),
                            path=f"edges/{edge.id}",
                        )
                    )

    for scope in spec.scopes:
        if scope.parent_scope_id and scope.parent_scope_id not in scope_by_id:
            issues.append(
                ValidationIssue(
                    code="VR011",
                    severity=Severity.ERROR,
                    message=f"Scope {scope.id} references missing parent scope {scope.parent_scope_id}.",
                    path=f"scopes/{scope.id}",
                )
            )
        if scope.kind == ScopeKind.ROUTER:
            if not scope.router:
                issues.append(
                    ValidationIssue(
                        code="VR012",
                        severity=Severity.ERROR,
                        message=f"Router scope {scope.id} must define router metadata.",
                        path=f"scopes/{scope.id}",
                    )
                )
            route_edges = [edge for edge in spec.edges if edge.scope_id == scope.id and edge.route_id]
            if len(route_edges) < 2:
                issues.append(
                    ValidationIssue(
                        code="VR013",
                        severity=Severity.ERROR,
                        message=f"Router scope {scope.id} must expose at least two route edges.",
                        path=f"scopes/{scope.id}",
                    )
                )
        if scope.kind == ScopeKind.LOOP:
            if not scope.loop:
                issues.append(
                    ValidationIssue(
                        code="VR014",
                        severity=Severity.ERROR,
                        message=f"Loop scope {scope.id} must define loop metadata.",
                        path=f"scopes/{scope.id}",
                    )
                )
            else:
                if scope.loop.max_iterations < 1:
                    issues.append(
                        ValidationIssue(
                            code="VR015",
                            severity=Severity.ERROR,
                            message=f"Loop scope {scope.id} must have max_iterations >= 1.",
                            path=f"scopes/{scope.id}",
                        )
                    )
                if scope.loop.break_condition_id not in condition_ids:
                    issues.append(
                        ValidationIssue(
                            code="VR016",
                            severity=Severity.ERROR,
                            message=(
                                f"Loop scope {scope.id} references missing break condition "
                                f"{scope.loop.break_condition_id}."
                            ),
                            path=f"scopes/{scope.id}",
                        )
                    )

    for name, expr in spec.conditions.items():
        for ref_id in _expr_refs(expr):
            if ref_id not in condition_ids:
                issues.append(
                    ValidationIssue(
                        code="VR017",
                        severity=Severity.ERROR,
                        message=f"Condition {name} references missing condition {ref_id}.",
                        path=f"conditions/{name}",
                    )
                )

    for name, formula in spec.formulae.items():
        for ref_id in _expr_refs(formula.ast):
            if ref_id not in condition_ids and ref_id not in formula_ids:
                issues.append(
                    ValidationIssue(
                        code="VR018",
                        severity=Severity.WARNING,
                        message=(
                            f"Formula {name} references {ref_id}. "
                            "Only condition refs are checked in the first slice."
                        ),
                        path=f"formulae/{name}",
                    )
                )
        if not formula.latex.strip():
            issues.append(
                ValidationIssue(
                    code="VR019",
                    severity=Severity.WARNING,
                    message=f"Formula {name} has empty latex.",
                    path=f"formulae/{name}",
                )
            )

    for router_decision in spec.router_decisions:
        if router_decision.router_id not in router_ids:
            issues.append(
                ValidationIssue(
                    code="VR020",
                    severity=Severity.ERROR,
                    message=f"Router decision references missing router {router_decision.router_id}.",
                    path=f"router_decisions/{router_decision.router_id}",
                )
            )
        if len(router_decision.routes) < 2:
            issues.append(
                ValidationIssue(
                    code="VR021",
                    severity=Severity.ERROR,
                    message=f"Router {router_decision.router_id} must define at least two routes.",
                    path=f"router_decisions/{router_decision.router_id}",
                )
            )
        for route in router_decision.routes:
            if route.condition_id not in condition_ids:
                issues.append(
                    ValidationIssue(
                        code="VR022",
                        severity=Severity.ERROR,
                        message=(
                            f"Router {router_decision.router_id} route {route.route_id} "
                            f"references missing condition {route.condition_id}."
                        ),
                        path=f"router_decisions/{router_decision.router_id}",
                    )
                )

    return _dedupe_issues(issues)


def validate_run(spec: AgentSpec, run: AgentRun) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    node_by_id = {node.id: node for node in spec.nodes}
    scope_by_id = {scope.id: scope for scope in spec.scopes}
    router_scope_ids = {scope.id for scope in spec.scopes if scope.kind == ScopeKind.ROUTER}
    loop_scope_ids = {scope.id for scope in spec.scopes if scope.kind == ScopeKind.LOOP}
    loop_ids = {scope.loop.loop_id for scope in spec.scopes if scope.loop}

    by_scope_instance: dict[str, list[RunEvent]] = defaultdict(list)
    for event in run.trace:
        by_scope_instance[event.scope_instance_id].append(event)

    for event in run.trace:
        if event.node_id not in node_by_id:
            issues.append(
                ValidationIssue(
                    code="RR001",
                    severity=Severity.ERROR,
                    message=f"Run event {event.step_id} references missing node {event.node_id}.",
                    path=f"trace/{event.step_id}",
                )
            )
            continue

        scope_id = event.scope_instance_id.split("#", 1)[0]
        if scope_id not in scope_by_id:
            issues.append(
                ValidationIssue(
                    code="RR002",
                    severity=Severity.ERROR,
                    message=(
                        f"Run event {event.step_id} references missing scope instance "
                        f"prefix {scope_id}."
                    ),
                    path=f"trace/{event.step_id}",
                )
            )
            continue

        if event.iteration_id < 0:
            issues.append(
                ValidationIssue(
                    code="RR003",
                    severity=Severity.ERROR,
                    message=f"Run event {event.step_id} has negative iteration_id.",
                    path=f"trace/{event.step_id}",
                )
            )

        node = node_by_id[event.node_id]
        if node.kind == NodeKind.OBSERVE:
            required_output_fields = ["artifact_ref", "sha256", "width", "height", "capture_mode"]
            missing_fields = [field for field in required_output_fields if field not in event.output]
            if missing_fields:
                issues.append(
                    ValidationIssue(
                        code="RR009",
                        severity=Severity.ERROR,
                        message=(
                            f"Observe event {event.step_id} must record screenshot artifact fields: "
                            f"{', '.join(missing_fields)}."
                        ),
                        path=f"trace/{event.step_id}",
                    )
                )

        if scope_id in router_scope_ids and not event.selected_route:
            issues.append(
                ValidationIssue(
                    code="RR004",
                    severity=Severity.ERROR,
                    message=f"Router event {event.step_id} must record selected_route.",
                    path=f"trace/{event.step_id}",
                )
            )

    for scope_instance_id, events in by_scope_instance.items():
        scope_id = scope_instance_id.split("#", 1)[0]
        if scope_id not in loop_scope_ids:
            continue
        ordered = sorted(events, key=lambda item: (item.iteration_id, item.timestamp, item.step_id))
        iterations = [event.iteration_id for event in ordered]
        if iterations != sorted(iterations):
            issues.append(
                ValidationIssue(
                    code="RR005",
                    severity=Severity.ERROR,
                    message=f"Loop scope instance {scope_instance_id} has non-monotonic iteration_id.",
                    path=f"trace/{scope_instance_id}",
                )
            )
        last_event = ordered[-1]
        if not (last_event.stop_reason or run.summary.stop_reason):
            issues.append(
                ValidationIssue(
                    code="RR006",
                    severity=Severity.ERROR,
                    message=(
                        f"Loop scope instance {scope_instance_id} must end with stop_reason "
                        "on the event or run summary."
                    ),
                    path=f"trace/{scope_instance_id}",
                )
            )

    for loop_id, iteration_count in run.summary.loop_iterations.items():
        if loop_id not in loop_ids:
            issues.append(
                ValidationIssue(
                    code="RR007",
                    severity=Severity.WARNING,
                    message=f"Run summary references unknown loop_id {loop_id}.",
                    path=f"summary/loop_iterations/{loop_id}",
                )
            )
        if iteration_count < 0:
            issues.append(
                ValidationIssue(
                    code="RR008",
                    severity=Severity.ERROR,
                    message=f"Run summary loop iteration for {loop_id} must be >= 0.",
                    path=f"summary/loop_iterations/{loop_id}",
                )
            )

    return _dedupe_issues(issues)


class DotRenderer:
    """Render the canonical spec into Graphviz DOT text."""

    SHAPES = {
        NodeKind.ROUTER: "diamond",
        NodeKind.STOP: "doublecircle",
        NodeKind.ACTION: "box",
        NodeKind.OBSERVE: "box",
        NodeKind.GROUND: "box",
        NodeKind.PLAN: "box",
        NodeKind.REFLECT: "box",
    }

    @classmethod
    def render(cls, spec: AgentSpec) -> str:
        children_by_parent: dict[str | None, list[Scope]] = defaultdict(list)
        for scope in spec.scopes:
            children_by_parent[scope.parent_scope_id].append(scope)

        nodes_by_scope: dict[str, list[Node]] = defaultdict(list)
        for node in spec.nodes:
            nodes_by_scope[node.scope_id].append(node)

        lines = ["digraph AgentGraphIR {", "  rankdir=LR;", "  compound=true;"]

        def emit_scope(scope: Scope, indent: int = 1) -> None:
            prefix = "  " * indent
            cluster_name = f"cluster_{scope.id.replace('.', '_').replace('-', '_')}"
            lines.append(f"{prefix}subgraph {cluster_name} {{")
            lines.append(f'{prefix}  label="{scope.id}";')
            if scope.kind == ScopeKind.LOOP:
                lines.append(f"{prefix}  color=blue;")
            elif scope.kind == ScopeKind.ROUTER:
                lines.append(f"{prefix}  color=gray;")
            for node in nodes_by_scope.get(scope.id, []):
                shape = cls.SHAPES.get(node.kind, "box")
                safe_label = node.label.replace('"', '\\"')
                lines.append(f'{prefix}  {node.id} [shape={shape}, label="{safe_label}"];')
            for child in sorted(children_by_parent.get(scope.id, []), key=lambda item: item.id):
                emit_scope(child, indent + 1)
            lines.append(f"{prefix}}}")

        roots = sorted(children_by_parent.get(None, []), key=lambda item: item.id)
        for root in roots:
            emit_scope(root)

        for edge in spec.edges:
            label = edge.route_id or edge.condition_id
            attrs = [f'label="{label}"'] if label else []
            attr_text = f" [{', '.join(attrs)}]" if attrs else ""
            lines.append(f"  {edge.src} -> {edge.dst}{attr_text};")

        lines.append("}")
        return "\n".join(lines) + "\n"


class MermaidRenderer:
    """Render the canonical spec into a Mermaid flowchart."""

    @staticmethod
    def render(spec: AgentSpec) -> str:
        children_by_parent: dict[str | None, list[Scope]] = defaultdict(list)
        for scope in spec.scopes:
            children_by_parent[scope.parent_scope_id].append(scope)

        nodes_by_scope: dict[str, list[Node]] = defaultdict(list)
        for node in spec.nodes:
            nodes_by_scope[node.scope_id].append(node)

        lines = ["flowchart LR"]

        def emit_scope(scope: Scope, indent: int = 1) -> None:
            prefix = "  " * indent
            scope_token = scope.id.replace(".", "_").replace("-", "_")
            lines.append(f'{prefix}subgraph scope_{scope_token}["{scope.id}"]')
            for node in nodes_by_scope.get(scope.id, []):
                label = node.label.replace('"', "'")
                lines.append(f"{prefix}  {node.id}[{label}]")
            for child in sorted(children_by_parent.get(scope.id, []), key=lambda item: item.id):
                emit_scope(child, indent + 1)
            lines.append(f"{prefix}end")

        roots = sorted(children_by_parent.get(None, []), key=lambda item: item.id)
        for root in roots:
            emit_scope(root)

        for edge in spec.edges:
            label = edge.route_id or edge.condition_id
            if label:
                lines.append(f"  {edge.src} -->|{label}| {edge.dst}")
            else:
                lines.append(f"  {edge.src} --> {edge.dst}")
        return "\n".join(lines) + "\n"


def build_langfuse_trace(
    spec: AgentSpec,
    run: AgentRun,
    *,
    tags: list[str] | None = None,
    input_payload: dict[str, Any] | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    scope_by_id = {scope.id: scope for scope in spec.scopes}
    observations: list[dict[str, Any]] = []
    root_id = "obs_root"
    observations.append(
        {
            "id": root_id,
            "parent_id": None,
            "type": "span",
            "name": spec.agent_id,
            "scope_id": "root",
            "input": input_payload or {},
            "metadata": metadata or {},
        }
    )

    scope_observation_ids: dict[str, str] = {}
    last_seen_scope_instance: dict[str, str] = {}

    def ensure_scope_observation(scope_instance_id: str, timestamp: str) -> str:
        existing = scope_observation_ids.get(scope_instance_id)
        if existing:
            return existing

        scope_id, _, instance_suffix = scope_instance_id.partition("#")
        scope = scope_by_id.get(scope_id)
        parent_id = root_id

        if scope and scope.parent_scope_id:
            candidate_ids: list[str] = []
            if instance_suffix:
                candidate_ids.append(f"{scope.parent_scope_id}#{instance_suffix}")
            remembered = last_seen_scope_instance.get(scope.parent_scope_id)
            if remembered:
                candidate_ids.append(remembered)
            candidate_ids.append(f"{scope.parent_scope_id}#0")

            for candidate in candidate_ids:
                if candidate == scope_instance_id:
                    continue
                if candidate in scope_observation_ids:
                    parent_id = scope_observation_ids[candidate]
                    break
            else:
                if scope.parent_scope_id in scope_by_id:
                    synthetic_parent = f"{scope.parent_scope_id}#{instance_suffix or '0'}"
                    if synthetic_parent != scope_instance_id:
                        parent_id = ensure_scope_observation(synthetic_parent, timestamp)

        observation_id = f"scope::{scope_instance_id}"
        scope_observation_ids[scope_instance_id] = observation_id
        last_seen_scope_instance[scope_id] = scope_instance_id
        observations.append(
            {
                "id": observation_id,
                "parent_id": parent_id,
                "type": "span",
                "name": f"scope:{scope_id}",
                "scope_id": scope_id,
                "scope_instance_id": scope_instance_id,
                "timestamp": timestamp,
                "metadata": {
                    "scope_kind": scope.kind.value if scope else "unknown",
                },
            }
        )
        return observation_id

    for event in run.trace:
        scope_parent_id = ensure_scope_observation(event.scope_instance_id, event.timestamp)
        node = next((item for item in spec.nodes if item.id == event.node_id), None)
        scope_id = event.scope_instance_id.split("#", 1)[0]
        obs_type = "generation" if node and node.kind in {NodeKind.PLAN, NodeKind.REFLECT, NodeKind.ROUTER} else "span"
        if node and node.kind == NodeKind.OBSERVE:
            obs_type = "event"
        observation = {
            "id": event.step_id,
            "parent_id": scope_parent_id,
            "type": obs_type,
            "name": node.label if node else event.node_id,
            "scope_id": scope_id,
            "scope_instance_id": event.scope_instance_id,
            "iteration_id": event.iteration_id,
            "timestamp": event.timestamp,
            "input": event.input,
            "output": event.output,
            "metadata": event.metadata,
        }
        if event.selected_route:
            observation["selected_route"] = event.selected_route
        if event.stop_reason:
            observation["stop_reason"] = event.stop_reason
        if event.tool_call:
            observation["tool_call"] = event.tool_call.model_dump()
            if event.tool_call.latency_ms is not None:
                observation["latency_ms"] = event.tool_call.latency_ms
        observations.append(observation)

    scores = []
    if run.summary.status == "success":
        scores.append({"name": "task_completed", "data_type": "BOOLEAN", "value": True})
    elif run.summary.status in {"failed", "cancelled"}:
        scores.append({"name": "task_completed", "data_type": "BOOLEAN", "value": False})

    return {
        "trace_id": run.summary.trace_id,
        "session_id": run.summary.session_id,
        "name": spec.agent_id,
        "tags": tags or ["agent-graph-ir"],
        "metadata": metadata or {},
        "input": input_payload or {},
        "observations": observations,
        "scores": scores,
        "run_summary": run.summary.model_dump(),
    }


class LangfuseSdkAdapter:
    """Optional adapter. The core first slice emits JSON whether SDK is installed or not."""

    def __init__(self) -> None:
        try:
            from langfuse import get_client  # type: ignore
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise RuntimeError(
                "langfuse package is not installed. Emit JSON first or install langfuse."
            ) from exc
        self._client = get_client()

    def emit(self, payload: dict[str, Any]) -> None:  # pragma: no cover - optional dependency
        trace = self._client.trace(
            id=payload["trace_id"],
            session_id=payload["session_id"],
            name=payload["name"],
            input=payload["input"],
            metadata=payload["metadata"],
            tags=payload["tags"],
        )
        for observation in payload["observations"]:
            if observation["type"] == "generation":
                trace.generation(
                    name=observation["name"],
                    input=observation.get("input", {}),
                    output=observation.get("output", {}),
                    metadata=observation.get("metadata", {}),
                )
            else:
                trace.span(
                    name=observation["name"],
                    input=observation.get("input", {}),
                    output=observation.get("output", {}),
                    metadata=observation.get("metadata", {}),
                )
        for score in payload["scores"]:
            self._client.create_score(trace_id=payload["trace_id"], **score)
        self._client.flush()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_output(text: str, path: Path | None) -> None:
    if path is None:
        print(text)
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_json(payload: dict[str, Any], path: Path | None) -> None:
    text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    _write_output(text, path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="agent-graph-ir first-slice tooling")
    subparsers = parser.add_subparsers(dest="command", required=True)

    emit_schema = subparsers.add_parser("emit-json-schema", help="Emit AgentSpec JSON Schema")
    emit_schema.add_argument("--output-json", type=Path)

    validate_spec_parser = subparsers.add_parser("validate-spec", help="Validate AgentSpec JSON")
    validate_spec_parser.add_argument("--input", type=Path, required=True)
    validate_spec_parser.add_argument("--output-json", type=Path)

    validate_run_parser = subparsers.add_parser("validate-run", help="Validate AgentRun JSON")
    validate_run_parser.add_argument("--spec", type=Path, required=True)
    validate_run_parser.add_argument("--run", type=Path, required=True)
    validate_run_parser.add_argument("--output-json", type=Path)

    dot_parser = subparsers.add_parser("render-dot", help="Render AgentSpec as Graphviz DOT")
    dot_parser.add_argument("--input", type=Path, required=True)
    dot_parser.add_argument("--output", type=Path)

    mermaid_parser = subparsers.add_parser("render-mermaid", help="Render AgentSpec as Mermaid")
    mermaid_parser.add_argument("--input", type=Path, required=True)
    mermaid_parser.add_argument("--output", type=Path)

    trace_parser = subparsers.add_parser(
        "emit-trace-json", help="Emit Langfuse-compatible trace JSON from spec + run"
    )
    trace_parser.add_argument("--spec", type=Path, required=True)
    trace_parser.add_argument("--run", type=Path, required=True)
    trace_parser.add_argument("--output-json", type=Path)

    capture_plan_parser = subparsers.add_parser(
        "plan-capture",
        help="Plan screenshot capture routes using the OpenAI screenshot fallback policy",
    )
    capture_plan_parser.add_argument("--input", type=Path, required=True)
    capture_plan_parser.add_argument("--output-json", type=Path)

    observe_event_parser = subparsers.add_parser(
        "emit-observe-event",
        help="Build a typed observe event from a screenshot artifact and capture request",
    )
    observe_event_parser.add_argument("--request", type=Path, required=True)
    observe_event_parser.add_argument("--artifact", type=Path, required=True)
    observe_event_parser.add_argument("--step-id", default="s_observe")
    observe_event_parser.add_argument("--node-id", default="n_observe")
    observe_event_parser.add_argument("--scope-instance-id", default="root#0")
    observe_event_parser.add_argument("--iteration-id", type=int, default=0)
    observe_event_parser.add_argument("--timestamp")
    observe_event_parser.add_argument(
        "--capture-mode",
        choices=[mode.value for mode in CaptureMode],
    )
    observe_event_parser.add_argument("--artifact-ref")
    observe_event_parser.add_argument("--output-json", type=Path)

    observe_events_from_output_parser = subparsers.add_parser(
        "emit-observe-events-from-screenshot-output",
        help="Convert OpenAI screenshot skill stdout paths into typed observe events",
    )
    observe_events_from_output_parser.add_argument("--request", type=Path, required=True)
    observe_events_from_output_parser.add_argument(
        "--stdout-file",
        type=Path,
        required=True,
        help="Text file containing one screenshot path per line",
    )
    observe_events_from_output_parser.add_argument("--step-prefix", default="s_observe")
    observe_events_from_output_parser.add_argument("--node-id", default="n_observe")
    observe_events_from_output_parser.add_argument("--scope-instance-id", default="root#0")
    observe_events_from_output_parser.add_argument("--iteration-id", type=int, default=0)
    observe_events_from_output_parser.add_argument("--timestamp")
    observe_events_from_output_parser.add_argument("--output-json", type=Path)

    screenshot_bridge_parser = subparsers.add_parser(
        "run-screenshot-bridge",
        help="Run a screenshot helper command and convert stdout paths into a partial AgentRun",
    )
    screenshot_bridge_parser.add_argument("--request", type=Path, required=True)
    screenshot_bridge_parser.add_argument("--trace-id", required=True)
    screenshot_bridge_parser.add_argument("--session-id", required=True)
    screenshot_bridge_parser.add_argument("--step-prefix", default="s_observe")
    screenshot_bridge_parser.add_argument("--node-id", default="n_observe")
    screenshot_bridge_parser.add_argument("--scope-instance-id", default="root#0")
    screenshot_bridge_parser.add_argument("--iteration-id", type=int, default=0)
    screenshot_bridge_parser.add_argument("--timestamp")
    screenshot_bridge_parser.add_argument("--cwd", type=Path)
    screenshot_bridge_parser.add_argument("--output-json", type=Path)
    screenshot_bridge_parser.add_argument(
        "--command",
        dest="command_argv",
        nargs=argparse.REMAINDER,
        help="Command argv to execute after --command",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "emit-json-schema":
        payload = {
            "generated_at": _now_iso(),
            "schema_name": "AgentSpec",
            "schema": AgentSpec.model_json_schema(),
        }
        _write_json(payload, args.output_json)
        return 0

    if args.command == "validate-spec":
        spec = JsonSpecParser.parse(_load_json(args.input))
        issues = [issue.model_dump() for issue in validate_spec(spec)]
        payload = {
            "generated_at": _now_iso(),
            "input": str(args.input),
            "issue_count": len(issues),
            "issues": issues,
        }
        _write_json(payload, args.output_json)
        return 0

    if args.command == "validate-run":
        spec = JsonSpecParser.parse(_load_json(args.spec))
        run = JsonRunParser.parse(_load_json(args.run))
        issues = [issue.model_dump() for issue in validate_run(spec, run)]
        payload = {
            "generated_at": _now_iso(),
            "spec": str(args.spec),
            "run": str(args.run),
            "issue_count": len(issues),
            "issues": issues,
        }
        _write_json(payload, args.output_json)
        return 0

    if args.command == "render-dot":
        spec = JsonSpecParser.parse(_load_json(args.input))
        _write_output(DotRenderer.render(spec), args.output)
        return 0

    if args.command == "render-mermaid":
        spec = JsonSpecParser.parse(_load_json(args.input))
        _write_output(MermaidRenderer.render(spec), args.output)
        return 0

    if args.command == "emit-trace-json":
        spec = JsonSpecParser.parse(_load_json(args.spec))
        run = JsonRunParser.parse(_load_json(args.run))
        payload = build_langfuse_trace(spec, run)
        _write_json(payload, args.output_json)
        return 0

    if args.command == "plan-capture":
        request = CaptureRequest.model_validate(_load_json(args.input))
        payload = {
            "generated_at": _now_iso(),
            "request": request.model_dump(mode="json", exclude_none=True),
            "routes": [
                route.model_dump(mode="json")
                for route in OpenAiScreenshotPolicyAdapter.plan_routes(request)
            ],
        }
        _write_json(payload, args.output_json)
        return 0

    if args.command == "emit-observe-event":
        request = CaptureRequest.model_validate(_load_json(args.request))
        event = OpenAiScreenshotPolicyAdapter.build_observe_event(
            request=request,
            artifact_path=args.artifact,
            step_id=args.step_id,
            node_id=args.node_id,
            scope_instance_id=args.scope_instance_id,
            iteration_id=args.iteration_id,
            timestamp=args.timestamp,
            capture_mode=CaptureMode(args.capture_mode) if args.capture_mode else None,
            artifact_ref=args.artifact_ref,
        )
        _write_json(event.model_dump(mode="json"), args.output_json)
        return 0

    if args.command == "emit-observe-events-from-screenshot-output":
        request = CaptureRequest.model_validate(_load_json(args.request))
        stdout_text = args.stdout_file.read_text(encoding="utf-8")
        events = OpenAiScreenshotPolicyAdapter.build_observe_events_from_screenshot_skill_output(
            request=request,
            stdout_text=stdout_text,
            step_prefix=args.step_prefix,
            node_id=args.node_id,
            scope_instance_id=args.scope_instance_id,
            iteration_id=args.iteration_id,
            timestamp=args.timestamp,
        )
        payload = {
            "generated_at": _now_iso(),
            "event_count": len(events),
            "events": [event.model_dump(mode="json") for event in events],
        }
        _write_json(payload, args.output_json)
        return 0

    if args.command == "run-screenshot-bridge":
        if not args.command_argv:
            parser.error("run-screenshot-bridge requires argv after --command")
        request = CaptureRequest.model_validate(_load_json(args.request))
        payload = OpenAiScreenshotPolicyAdapter.run_screenshot_command_bridge(
            request=request,
            command=args.command_argv,
            trace_id=args.trace_id,
            session_id=args.session_id,
            step_prefix=args.step_prefix,
            node_id=args.node_id,
            scope_instance_id=args.scope_instance_id,
            iteration_id=args.iteration_id,
            timestamp=args.timestamp,
            cwd=args.cwd,
        )
        _write_json(payload, args.output_json)
        return 0

    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
