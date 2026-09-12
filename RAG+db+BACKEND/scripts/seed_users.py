import sys
from pathlib import Path

# Add backend root to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.models.database import SessionLocal
from app.models.user import User
from app.utils.security import hash_password


USERS = [
    {
        "name": "System Admin",
        "email": "admin@company.com",
        "password": "Admin@123",
        "role": "admin",
    },
    {
        "name": "Support Employee",
        "email": "employee@company.com",
        "password": "Employee@123",
        "role": "employee",
    },
    {
        "name": "Customer User",
        "email": "customer@company.com",
        "password": "Customer@123",
        "role": "customer",
    },
]


def seed_users():
    db = SessionLocal()

    try:
        for user_data in USERS:
            existing_user = (
                db.query(User)
                .filter(User.email == user_data["email"])
                .first()
            )

            if existing_user:
                print(
                    f"User already exists: "
                    f"{user_data['email']} "
                    f"({existing_user.role})"
                )
                continue

            user = User(
                name=user_data["name"],
                email=user_data["email"],
                password_hash=hash_password(user_data["password"]),
                role=user_data["role"],
                is_active=True,
            )

            db.add(user)

            print(
                f"Created user: "
                f"{user_data['email']} "
                f"({user_data['role']})"
            )

        db.commit()

        print("User seeding completed successfully.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_users()