import json
from fastapi import FastAPI, HTTPException, Request
import schemas
import tools

# MCP imports
from mcp.server import Server
from mcp.server.sse import SseServerTransport
import mcp.types as types

app = FastAPI(title="Demand MCP Server")

# ─── MCP Server Setup ─────────────────────────────────────────────────────────

mcp_server = Server("demand-mcp-server")
sse_transport = SseServerTransport("/messages")


@mcp_server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="create_demand",
            description="Create a new resource demand in the system",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_name":                   {"type": "string",  "description": "Name of the project"},
                    "crm_id":                         {"type": "string",  "description": "CRM identifier"},
                    "probability":                    {"type": "integer", "description": "Probability percentage (0-100)"},
                    "grade":                          {"type": "string",  "description": "Grade level"},
                    "start_date":                     {"type": "string",  "format": "date", "description": "Start date (YYYY-MM-DD)"},
                    "end_date":                       {"type": "string",  "format": "date", "description": "End date (YYYY-MM-DD)"},
                    "fte":                            {"type": "integer", "description": "Full-time equivalents required"},
                    "platform_type":                  {"type": "string",  "enum": ["EBS", "Fusion"], "description": "Platform type"},
                    "competency_track":               {"type": "string",  "description": "Competency track"},
                    "primary_mandatory_skill":        {"type": "string",  "description": "Primary mandatory skill"},
                    "good_to_have_skill":             {"type": "string",  "description": "Nice-to-have skill"},
                    "monthly_billing_rate_usd":       {"type": "number",  "description": "Monthly billing rate in USD"},
                    "minimum_gm_percent":             {"type": "number",  "description": "Minimum gross margin percentage"},
                    "specific_certification_required":{"type": "boolean", "description": "Whether a specific certification is required"},
                    "client_interview_flag":          {"type": "boolean", "description": "Whether a client interview is required"},
                    "job_description":                {"type": "string",  "description": "Full job description text"},
                    "required_count":                 {"type": "integer", "description": "Number of resources required", "default": 1}
                },
                "required": [
                    "project_name", "crm_id", "start_date", "end_date",
                    "fte", "platform_type", "primary_mandatory_skill",
                    "monthly_billing_rate_usd", "minimum_gm_percent"
                ]
            }
        ),
        types.Tool(
            name="get_demands",
            description="Fetch all existing resource demands, ordered by creation date (newest first)",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        types.Tool(
            name="update_demand",
            description="Update the status of an existing demand",
            inputSchema={
                "type": "object",
                "properties": {
                    "demand_id": {"type": "string", "description": "UUID of the demand to update"},
                    "status": {
                        "type": "string",
                        "enum": ["Draft", "Internal", "External", "Partial", "Fulfilled", "Closed"],
                        "description": "New status for the demand"
                    }
                },
                "required": ["demand_id", "status"]
            }
        )
    ]


@mcp_server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    try:
        if name == "create_demand":
            result = tools.create_demand_tool(arguments)
        elif name == "get_demands":
            result = tools.get_demands_tool()
        elif name == "update_demand":
            result = tools.update_demand_tool(
                demand_id=arguments["demand_id"],
                status=arguments["status"]
            )
        else:
            raise ValueError(f"Unknown tool: {name}")

        return [types.TextContent(type="text", text=json.dumps(result, default=str))]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]


# ─── MCP SSE Endpoints ─────────────────────────────────────────────────────────

@app.get("/sse")
async def handle_sse(request: Request):
    async with sse_transport.connect_sse(
        request.scope, request.receive, request._send
    ) as streams:
        await mcp_server.run(
            streams[0],
            streams[1],
            mcp_server.create_initialization_options()
        )


@app.post("/messages")
async def handle_messages(request: Request):
    await sse_transport.handle_post_message(request.scope, request.receive, request._send)


# ─── Legacy REST Endpoints (kept for backward compatibility) ───────────────────

@app.get("/")
def root():
    return {"message": "Demand MCP Server Running", "mcp_sse_endpoint": "/sse"}


@app.get("/tools")
def list_tools_rest():
    return [
        {"name": "create_demand", "description": "Create a new resource demand",  "endpoint": "/create-demand",             "method": "POST"},
        {"name": "get_demands",   "description": "Fetch all existing demands",    "endpoint": "/demands",                  "method": "GET"},
        {"name": "update_demand", "description": "Update demand status",           "endpoint": "/update-demand/{demand_id}", "method": "PUT"}
    ]


@app.post("/create-demand")
def create_demand(demand: schemas.CreateDemand):
    return tools.create_demand_tool(demand.dict())


@app.get("/demands")
def get_demands():
    return tools.get_demands_tool()


@app.put("/update-demand/{demand_id}")
def update_demand(demand_id: str, body: schemas.UpdateDemand):
    try:
        return tools.update_demand_tool(demand_id, body.status)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
