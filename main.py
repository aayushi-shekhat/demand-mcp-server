from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import get_db
import schemas
import tools

app = FastAPI(title="Demand MCP Server")


@app.get("/")
def root():
    return {"message": "Demand MCP Server Running"}


@app.get("/tools")
def list_tools():
    return [
        {
            "name": "create_demand",
            "description": "Create a new resource demand",
            "endpoint": "/create-demand",
            "method": "POST"
        },
        {
            "name": "get_demands",
            "description": "Fetch all existing demands",
            "endpoint": "/demands",
            "method": "GET"
        },
        {
            "name": "update_demand",
            "description": "Update demand status",
            "endpoint": "/update-demand/{demand_id}",
            "method": "PUT"
        }
    ]


@app.post("/create-demand")
def create_demand(demand: schemas.CreateDemand, db: Session = Depends(get_db)):
    return tools.create_demand_tool(db, demand)


@app.get("/demands")
def get_demands(db: Session = Depends(get_db)):
    return tools.get_demands_tool(db)


@app.put("/update-demand/{demand_id}")
def update_demand(demand_id: str, body: schemas.UpdateDemand, db: Session = Depends(get_db)):
    return tools.update_demand_tool(db, demand_id, body.status)