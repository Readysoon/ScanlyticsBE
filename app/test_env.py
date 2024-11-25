import pytest
import os

# this is a personal test - to be used online where the TESTING env has to be set in the test environment
@pytest.fixture(autouse=True)
def set_test_env():
    # Save original value if it exists
    original_value = os.environ.get('TESTING')
    
    # Set test environment
    os.environ['TESTING'] = 'True'
    
    yield
    
    # Restore original value
    if original_value is not None:
        os.environ['TESTING'] = original_value
    else:
        del os.environ['TESTING']

# Now all tests will have TESTING=True
def test_env():
    assert os.getenv('TESTING') == 'True'