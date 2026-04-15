from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.database import Base, get_db
from backend.main import app
from backend.models import Course, LearningPlan, PlanItem, User


def test_update_item_status_accepts_json_object(tmp_path):
    db_file = tmp_path / "test_plan_status.db"
    engine = create_engine(
        f"sqlite:///{db_file}",
        connect_args={"check_same_thread": False},
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    user = User(username="alice", password_hash="hash")
    course = Course(title="Python Basics", difficulty_level="Beginner")
    db.add_all([user, course])
    db.flush()

    plan = LearningPlan(user_id=user.id, status="active")
    db.add(plan)
    db.flush()

    item = PlanItem(
        learning_plan_id=plan.id,
        course_id=course.id,
        status="pending",
        sequence_order=1,
    )
    db.add(item)
    db.commit()

    def override_get_db():
        test_db = TestingSessionLocal()
        try:
            yield test_db
        finally:
            test_db.close()

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)
        response = client.put(
            f"/api/v1/plans/{plan.id}/items/{item.id}/status",
            json={"status": "completed"},
        )

        assert response.status_code == 200
        assert response.json()["new_status"] == "completed"

        refreshed_item = TestingSessionLocal().get(PlanItem, item.id)
        assert refreshed_item.status == "completed"
    finally:
        app.dependency_overrides.clear()
        db.close()
