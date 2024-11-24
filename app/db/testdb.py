from surrealdb import Surreal


# Test database configuration
TEST_SURREAL_URL = "ws://localhost:8004/rpc"
TEST_DB_NAME = "test_db"
TEST_NAMESPACE = "test_namespace"


async def test_db():
    """Fixture to set up and tear down test database"""
    db = Surreal(TEST_SURREAL_URL)
    await db.connect()
    await db.signin({"user": "test", "pass": "test"})
    await db.use(TEST_NAMESPACE, TEST_DB_NAME)
    
    yield db
    
    # Cleanup after tests
    await db.query(f"REMOVE DATABASE {TEST_DB_NAME}")
    await db.close()