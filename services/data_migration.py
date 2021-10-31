import csv
from typing import Iterable, Optional
import pydantic
from pydantic.networks import EmailStr

from services.db.deta.userDB import get_all_users_from_db, permanently_delete_user_from_db

class User(pydantic.BaseModel):
    key: Optional[int] = None
    username: str
    first_name: str
    last_name: str
    department: str
    email: EmailStr
    contact_number: str
    gender: Optional[str]
    city: Optional[str]
    state: str = 'kerala'
    avatar: Optional[str] = None
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None
    password: str = 'password@123'
    repeat_password: str = 'password@123'

class Student(User):
    register_number: int
    year_of_passout: int
    type: str = 'student'
    password: str = 'student@123'
    repeat_password: str = 'student@123'

class Staff(User):
    designation: str
    type: str = 'staff'
    password: str = 'staff@123'
    repeat_password: str = 'staff@123'


def convert_students_csv_to_pydantic(csv_file: Iterable[str]):
    student_list = []
    csv_reader = csv.reader(csv_file)
    # TODO: Fetch the header from the csv file and strore it in a variable.
    next(csv_reader)
    for row in csv_reader:
        try:
            if row[10] == '' or int(row[10]) < 10000000:
                continue

            student = Student(
                username=int(row[3]), 
                email=row[2], 
                first_name=row[0], 
                last_name=row[4], 
                department=row[1], 
                year_of_passout=int(row[4][2:]), 
                contact_number=int(row[3]),
                city=row[8], 
                register_number=row[10]
                )
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


def convert_staffs_csv_to_pydantic(csv_file: Iterable[str]):
    staff_list = []
    csv_reader = csv.reader(csv_file)
    next(csv_reader)
    for row in csv_reader:
        print(f"{row[0]} Gender = {row[6]} Designation = {row[4]}")
        try:
            staff = Staff(
                username=row[0],
                email=row[1],
                first_name=row[2],
                last_name=row[3],
                designation=row[4],
                department=row[5],
                gender=row[6],
                contact_number=row[7],
                password=row[8],
                repeat_password=row[8],
                type='staff',
            )
            staff_list.append(staff)
        except Exception as e:
            print(e)
    return staff_list
