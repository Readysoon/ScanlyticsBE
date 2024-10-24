from surrealdb import Surreal
from app.auth.authSchema import Token
from app.auth.authService import signup_service
from app.user.userSchema import UserSignup

async def SeedUserService(db: Surreal, response_model=Token):
    # Seed user information
    seed_user_data = UserSignup(
        user_email="admin@example.com",
        user_name="Admin User",
        user_password="securepassword123",
        user_role="admin",
        orga_address="123 Seed Lane, Example City, EX 12345",
        orga_email="orga@example.com",
        orga_name="Seed Organization"
    )

    # Use the existing signup service for user creation
    return await signup_service(
        seed_user_data.user_email,
        seed_user_data.user_name,
        seed_user_data.user_password,
        seed_user_data.user_role,
        seed_user_data.orga_address,
        seed_user_data.orga_email,
        seed_user_data.orga_name,
        db
    )
