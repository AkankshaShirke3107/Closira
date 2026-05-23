import base64
import urllib.request
import json

def generate_mermaid_png(mermaid_code, output_filename):
    # Encode mermaid code to base64
    encoded_str = base64.urlsafe_b64encode(mermaid_code.encode('utf-8')).decode('utf-8')
    
    # URL for mermaid.ink
    # Use dark theme
    url = f"https://mermaid.ink/img/{encoded_str}?theme=dark"
    
    print(f"Downloading {output_filename} from {url}...")
    
    # Download the image
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response, open(output_filename, 'wb') as out_file:
            data = response.read()
            out_file.write(data)
        print(f"Successfully saved to {output_filename}")
    except Exception as e:
        print(f"Error downloading image: {e}")

architecture_code = """
graph TD
    %% Styling
    classDef client fill:#1e293b,stroke:#3b82f6,stroke-width:2px,color:#f8fafc,rx:10,ry:10;
    classDef router fill:#2563eb,stroke:#60a5fa,stroke-width:2px,color:#ffffff,rx:10,ry:10;
    classDef service fill:#7c3aed,stroke:#a78bfa,stroke-width:2px,color:#ffffff,rx:10,ry:10;
    classDef db fill:#059669,stroke:#34d399,stroke-width:2px,color:#ffffff,rx:10,ry:10;
    classDef async fill:#dc2626,stroke:#f87171,stroke-width:2px,color:#ffffff,rx:10,ry:10;
    classDef obs fill:#ea580c,stroke:#fb923c,stroke-width:2px,color:#ffffff,rx:10,ry:10;
    
    Client:::client -->|HTTP Request| Router[FastAPI Router Layer]:::router
    
    Router -->|Delegates| Service[Service Layer]:::service
    Service -->|Transactions| ORM[SQLAlchemy ORM]:::db
    ORM -->|Writes| DB[(SQLite Database)]:::db
    
    subgraph Async [Asynchronous Workflow]
        direction TB
        BG[Background Task Processor]:::async --> SOP[SOP Matching Engine]:::async
        SOP --> Event[Event Timeline Logger]:::async
    end
    
    Service -.->|Spawn| BG
    Event -->|Append| ORM
    
    subgraph Observability [Cross-Cutting Concerns]
        direction TB
        Log[Structured JSON Logging]:::obs
        Corr[Correlation ID Middleware]:::obs
        Exc[Global Exception Handlers]:::obs
    end
    
    Router -.-> Observability
"""

workflow_code = """
stateDiagram-v2
    %% State definitions
    [*] --> NEW: Enquiry Created
    
    NEW --> PROCESSING: Background Task Starts
    
    note right of PROCESSING
        SOP matching occurs here.
        Race Condition Guard Prevents
        Stale Background Updates.
    end note
    
    PROCESSING --> QUALIFIED: SOP Matched
    PROCESSING --> ESCALATED: No Match
    
    QUALIFIED --> FOLLOW_UP_SCHEDULED: Agent Schedules Follow-up
    QUALIFIED --> ESCALATED: Manual Escalation
    FOLLOW_UP_SCHEDULED --> ESCALATED: Manual Escalation
    
    note right of [*]
        All state changes append to
        immutable Event Timeline
    end note
"""

generate_mermaid_png(architecture_code, "Backend/docs/screenshots/architecture.png")
generate_mermaid_png(workflow_code, "Backend/docs/screenshots/workflow.png")
