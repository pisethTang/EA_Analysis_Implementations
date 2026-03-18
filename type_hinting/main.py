from typing import NewType
# from typing import NewType, TypeVar 
# from typing import NewType, Any 
# from typing import NewType, TypedDict
from dataclasses import dataclass
import random 

import requests 


resp = requests.get("https://seth-tang.me", timeout=5)
status = resp.status_code
status = "ok"






RGB = NewType("RGB", tuple[int, int, int])
HSL = NewType("HSL", tuple[int, int, int])


# using `type alias`
# type User = dict[str, str | int | RGB | None] 
# `type` is optional (just to be explicit)


# inherits from TypeDict
# we can validate each argument's type 
# class User(TypedDict):
#     first_name: str
#     last_name: str
#     email :str
#     age: int | None 
#     fav_color: RGB | None 




# better to use dataclass when creating froms scratch 
@dataclass
class User:
    first_name: str
    last_name: str
    email :str
    age: int | None  = None
    fav_color: RGB | None = None 




def create_user(
        first_name: str, 
        last_name: str, 
        age: int | None = None,
        favorite_color: RGB | None =  None,
) -> User:
    email = f"{first_name.lower()}_{last_name.lower()}@example.com"

    # str_age = str(age)


    return User(
        first_name= first_name,
        last_name= last_name,
        email= email,
        age= age,
        fav_color= favorite_color
    )

# T = TypeVar("T")


def random_choice[T](items: list[T]) -> T: # newer python 3.12 syntax
    return random.choice(items)



user1 = create_user("Corey", "Scahfer", 39, RGB((109, 123, 134)))
user2 = create_user("Piseth", "Tang", 23, RGB((206, 10, 48)))

print(user1)
# print(user2)




users = [user1, user2]
rando_user = random_choice(users)
print(rando_user)

# rando_user. doesn't know that it's 

emails = [user.email for user in users]
rando_email = random_choice(emails)
print(rando_email)
# rando_email.




