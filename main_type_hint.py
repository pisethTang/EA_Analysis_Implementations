from pydantic import validate_call


@validate_call
def create_user(first_name: str, last_name: str, age: int) -> dict:
    email = f"{first_name.lower()}_{last_name.lower()}@example.com"

    ## Not scalable (too much manual validation code) 
    # if not isinstance(first_name, str):
    #     raise TypeError("first_name must be a string")
    # if not isinstance(last_name, str):
    #     raise TypeError("last_name must be a string")
    # if not isinstance(age, int):
    #     raise TypeError("age must be an integer")

    return {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "age": age
    }

# user_1: dict = create_user("Corey", "Schafer", "thirty-eight")
user_1: dict = create_user("Corey", "Schafer", "37")
print(user_1)