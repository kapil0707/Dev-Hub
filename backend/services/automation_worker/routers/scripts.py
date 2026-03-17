"""
=============================================================================
Automation Worker — Scripts Router
=============================================================================
"""
import asyncio
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from devhub_shared.logging.logger import get_logger
from models import Execution
from schemas import ScriptRunRequest, ExecutionResponse

logger = get_logger(__name__, service_name="automation_worker")

router = APIRouter(tags=["Scripts"])


@router.post("/run", response_model=ExecutionResponse)
async def run_script(
    request: ScriptRunRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Executes a shell script via subprocess and records the result.
    """
    logger.info("Received script execution request", extra={"script_length": len(request.script_content)})

    # 1. Create a Pending execution record
    execution = Execution(
        script_content=request.script_content,
        status="Pending",
    )
    db.add(execution)
    await db.commit()
    await db.refresh(execution)
    
    logger.info(f"Created execution record {execution.id}")

    # 2. Execute the script via subprocess
    import subprocess
    output = ""
    exit_code = -1
    status = "Failed"
    
    try:
        def run_script_sync(cmd):
            # shell=True runs the command through the platform's shell
            return subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True
            )

        # Execute blocking subprocess in a separate thread so it doesn't block FastAPI
        completed_process = await asyncio.to_thread(run_script_sync, request.script_content)
        
        exit_code = completed_process.returncode
        output = completed_process.stdout
        
        # Merge stderr into output if any exists
        if completed_process.stderr:
            output += "\n[STDERR]\n" + completed_process.stderr

        status = "Success" if exit_code == 0 else "Failed"
        logger.info(f"Execution {execution.id} finished with status {status} and exit code {exit_code}")

    except Exception as e:
        import traceback
        status = "Failed"
        output = f"Internal Exception during execution:\n{traceback.format_exc()}"
        logger.error(f"Execution {execution.id} failed with exception: {e}")

    # 3. Update the execution record with results
    execution.status = status
    execution.exit_code = exit_code
    execution.output = output
    execution.updated_at = datetime.now(timezone.utc)
    
    await db.commit()
    await db.refresh(execution)

    return execution


@router.get("/executions", response_model=List[ExecutionResponse])
async def list_executions(db: AsyncSession = Depends(get_db)):
    """
    List all past executions, newest first.
    """
    stmt = select(Execution).order_by(Execution.created_at.desc())
    result = await db.execute(stmt)
    executions = result.scalars().all()
    return executions


@router.get("/executions/{execution_id}", response_model=ExecutionResponse)
async def get_execution(execution_id: str, db: AsyncSession = Depends(get_db)):
    """
    Get details of a specific execution.
    """
    stmt = select(Execution).where(Execution.id == execution_id)
    result = await db.execute(stmt)
    execution = result.scalar_one_or_none()
    
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
        
    return execution
