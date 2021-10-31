import csv
from typing import Iterable, Optional
import pydantic
from pydantic.networks import EmailStr

from services.db.deta.userDB import get_all_users_from_db, permanently_delete_user_from_db

class Student(pydantic.BaseModel):
    key: Optional[int] = None
    username: str
    first_name: str
    last_name: str
    department: str
    year_of_passout: int
    email: EmailStr
    contact_number: str
    register_number: int
    city: str
    type: str = 'student'
    state: str = 'kerala'
    password: str = 'student@123'
    repeat_password: str = 'student@123'
    avatar: Optional[str] = None
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None

def convert_students_csv_to_pydantic(csv_file: Iterable[str]):
    student_list = []
    csv_reader = csv.reader(csv_file)
    # TODO: Fetch the header from the csv file and strore it in a variable.
    next(csv_reader)
    for row in csv_reader:
        try:
            if row[10] == '' or int(row[10]) < 10000000:
                continue

            student = Student(first_name=row[0], last_name=row[4], department=row[1], year_of_passout=int(row[4][2:]), email=row[2], username=int(row[3]), contact_number=int(row[3]),city=row[8], register_number=row[10])
            student_list.append(student)
        except: 
            continue
    return student_list


async def remove_all_users_from_db():
    users = await get_all_users_from_db()
    for user in users:
        if user.type == 'student':
            await permanently_delete_user_from_db(user)
            print(f'Deleted user {user.username}')
        else:
            print(f'User {user.username} is not a student')
