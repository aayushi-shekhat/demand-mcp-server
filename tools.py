import uuid
from datetime import datetime
from sqlalchemy import text
from fastapi import HTTPException


def create_demand_tool(db, demand):

    demand_id = str(uuid.uuid4())
    now = datetime.utcnow()

    # Build dict from demand, only include fields that exist in DB
    data = demand.dict()

    query = text("""
    INSERT INTO demands (
        demand_id,
        project_name,
        crm_id,
        probability,
        grade,
        start_date,
        end_date,
        fte,
        platform_type,
        competency_track,
        primary_mandatory_skill,
        good_to_have_skill,
        monthly_billing_rate_usd,
        minimum_gm_percent,
        specific_certification_required,
        client_interview_flag,
        job_description,
        required_count,
        created_at,
        updated_at
    )
    VALUES (
        :demand_id,
        :project_name,
        :crm_id,
        :probability,
        :grade,
        :start_date,
        :end_date,
        :fte,
        :platform_type,
        :competency_track,
        :primary_mandatory_skill,
        :good_to_have_skill,
        :monthly_billing_rate_usd,
        :minimum_gm_percent,
        :specific_certification_required,
        :client_interview_flag,
        :job_description,
        :required_count,
        :created_at,
        :updated_at
    )
    """)

    db.execute(query, {
        "demand_id": demand_id,
        **data,
        "created_at": now,
        "updated_at": now
    })

    db.commit()

    return {
        "message": "Demand created successfully",
        "demand_id": demand_id
    }


def get_demands_tool(db):

    query = text("SELECT * FROM demands ORDER BY created_at DESC")
    result = db.execute(query).fetchall()
    return [dict(row._mapping) for row in result]


def update_demand_tool(db, demand_id, status):

    # Check exists first
    check = text("SELECT demand_id FROM demands WHERE demand_id = :demand_id")
    row = db.execute(check, {"demand_id": demand_id}).fetchone()

    if not row:
        raise HTTPException(status_code=404, detail=f"Demand {demand_id} not found")

    query = text("""
    UPDATE demands
    SET status = :status,
        updated_at = :updated_at
    WHERE demand_id = :demand_id
    """)

    db.execute(query, {
        "status": status,
        "updated_at": datetime.utcnow(),
        "demand_id": demand_id
    })

    db.commit()

    return {
        "message": "Demand updated successfully",
        "demand_id": demand_id,
        "new_status": status
    }