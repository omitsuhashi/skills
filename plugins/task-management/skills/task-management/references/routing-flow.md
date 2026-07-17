# Task Management Routing Flow

The public contract stays the same even when the host changes the task backend.
The caller supplies only a logical destination and backend-neutral filters. The
host route owns every provider-specific decision.

## Read Routing Overview

```mermaid
flowchart LR
    caller["Consumer<br/>Schedule Secretary / workflow"]
    hermes["Hermes<br/>task-management-read:task_query"]
    facade["Task-management facade<br/>validate public query"]
    route["Host-owned route<br/>resolve backend + destination"]
    mcp["ExternalToolAdapter<br/>fixed MCP tool"]
    plugin["ExternalToolAdapter<br/>fixed provider-plugin tool"]
    normalize["Facade normalization<br/>allowlist + limit + safety guards"]
    success["TaskSnapshotResult<br/>normalized snapshots"]
    failure["TaskSnapshotResult<br/>typed error, no raw payload"]

    caller -->|"destination_ref + TaskQuery"| hermes
    hermes --> facade
    facade -->|"valid"| route
    facade -.->|"invalid query"| failure
    route -->|"kind = mcp"| mcp
    route -->|"kind = plugin"| plugin
    route -.->|"missing / invalid route"| failure
    mcp -->|"adapter result v1"| normalize
    plugin -->|"adapter result v1"| normalize
    mcp -.->|"unavailable / provider error"| failure
    plugin -.->|"unavailable / provider error"| failure
    normalize -->|"safe"| success
    normalize -.->|"invalid / unsafe snapshot"| failure
    success --> caller
    failure --> caller
```

The two normal runtime backend branches rejoin before the response. Consumers
therefore never parse MCP or provider-plugin payloads directly.

## End-to-End Read Sequence

```mermaid
sequenceDiagram
    autonumber
    participant C as Consumer
    participant H as Hermes registry
    participant F as task_query facade
    participant R as Host route
    participant A as Bound adapter
    participant P as External provider tool

    C->>H: task_query(destination_ref, query)
    H->>F: invoke registered handler
    F->>F: validate neutral query and credential boundary
    F->>R: resolve(optional backend_key, destination_ref)
    R-->>F: fixed kind, provider_ref, and tool
    F->>A: query(ResolvedTaskReadRequest)
    A->>H: dispatch exact configured read-only tool
    H->>P: adapter contract v1 request
    P-->>H: adapter contract v1 + items/error
    H-->>A: result
    A-->>F: AdapterTaskSnapshotResult or typed error
    F->>F: apply limit, normalize, and fail closed
    F-->>H: TaskSnapshotResult
    H-->>C: same result shape for every backend
```

## Ownership at Each Hop

| Hop | Owner | May choose | Must not choose |
| --- | --- | --- | --- |
| Public request | Consumer | logical `destination_ref`, neutral filters, optional trusted `backend_key` | file path, provider tool, provider destination, credentials |
| Route resolution | Host configuration | default backend, adapter kind, fixed tool, opaque provider ref | task content or provider credentials |
| Adapter execution | External MCP/provider plugin | provider-specific read, internal pagination | public response shape |
| Public response | Task-management facade | canonical fields, public limit, typed error | raw IDs, unknown metadata, credentials, provider cursor |

## Backend Switch

Changing the backend is a host configuration change, not a consumer flow
change:

```mermaid
stateDiagram-v2
    [*] --> SamePublicCall: destination_ref + TaskQuery
    SamePublicCall --> MCPBackend: host route = mcp
    SamePublicCall --> ProviderPlugin: host route = plugin
    MCPBackend --> SamePublicResult: TaskSnapshotResult
    ProviderPlugin --> SamePublicResult: TaskSnapshotResult
    SamePublicResult --> [*]
```

## Test and Smoke Fixture

The test-only `local_json` adapter exercises the same facade and normalization
contract with a temporary route and local JSON file. Only plugin-owned tests and
the isolated Hermes smoke use this seam; it is not part of the normal runtime
branches above, an operator bootstrap route, or a persistent task store.

## State-Changing Boundary

The diagrams above describe the implemented read path. A create, update,
comment, or report flow remains separate:

```mermaid
flowchart LR
    intent["Consumer intent"] --> draft["TaskDraft / operation preview"]
    draft --> approval{"Explicit approval?"}
    approval -->|"no"| stop["Stop without dispatch"]
    approval -->|"yes"| external["MCP or provider plugin<br/>owns provider-specific write"]
    external --> result["Normalized TaskWriteResult"]
```

There is no local write adapter. The task-management plugin prepares the
backend-neutral review surface; the external backend owns authorization,
provider mutations, retries, and canonical mutable task state.
