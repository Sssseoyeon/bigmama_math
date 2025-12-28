from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import DailyTask
from backend.schemas import DailyTaskResponse, DailyTaskUpdate

router = APIRouter(
    prefix="/daily-tasks",
    tags=["Daily Tasks"]
)

@router.put("/{task_id}")
def update_task_status(
    task_id: int,
    task: DailyTaskUpdate,
    db: Session = Depends(get_db)
):
    db_task = db.query(DailyTask).filter(DailyTask.id == task_id).first()

    if not db_task:
        raise HTTPException(status_code=404, detail="Task 없음")

    # ✅ 각각 개별적으로 업데이트
    if task.grading_done is not None:
        db_task.grading_done = task.grading_done

    if task.review_done is not None:
        db_task.review_done = task.review_done

    db.commit()
    db.refresh(db_task)

    return {
        "id": db_task.id,
        "content": db_task.content,
        "grading_done": db_task.grading_done,
        "review_done": db_task.review_done,
        "is_done": db_task.is_done
    }
