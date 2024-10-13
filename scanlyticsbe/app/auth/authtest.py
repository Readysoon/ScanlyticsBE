import datetime
from jose import jwt
import os


def create_access_token(data: dict or str, SECRET_KEY):
    if type(data) == str:
        # If data is a string (already a JWT), decode it first
        payload = jwt.decode(data, SECRET_KEY, algorithms=["HS256"])
        to_encode = payload.copy()
    else:
        # If data is a dictionary, proceed as normal
        to_encode = data.copy()

    expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=15)

    # Only try to split 'sub' if it contains a colon
    if ":" in to_encode['sub']:
        to_encode['sub'] = to_encode['sub'].split(":")[1].strip("⟨⟩")

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")

    return encoded_jwt


def main():
    # Example user data to encode
    user_data = {
        "sub": "user:⟨12345⟩",
        "name": "John Doe",
        "email": "johndoe@example.com"
    }

    # Set the SECRET_KEY environment variable (in a real scenario, this should be set securely in your environment)
    SECRET_KEY = "hjahash"
    
    # Create an access token
    access_token = create_access_token(user_data, SECRET_KEY)

    # Print the generated token
    print("Generated Access Token:")
    print(access_token)

    # Decode the token to get the payload
    payload = jwt.decode(access_token, SECRET_KEY, algorithms=["HS256"])
    id = payload.get("sub")

    print(f"payload: {payload}")

    print(f"id: {id}")

    # Generate another token based on the payload, not on the token itself
    access_token_2 = create_access_token(access_token, SECRET_KEY)
    print("Generated Access Token 2:")
    print(access_token_2)

    # Decode the second token and retrieve the sub again
    payload_2 = jwt.decode(access_token_2, SECRET_KEY, algorithms=["HS256"])
    id_2 = payload_2.get("sub")
    print(f"payload_2: {payload_2}")

    print(f"id from second token: {id_2}")

if __name__ == "__main__":
    main()


