from datetime import datetime, timedelta
import grpc
from concurrent import futures
from accounts_pb2 import RegisterUserResponse, LoginUserResponse
from accounts_pb2_grpc import UsersServicer, add_UsersServicer_to_server
from mongoengine import connect, Document, StringField, EmailField, DoesNotExist, NotUniqueError
from jwt import decode, encode
from hashlib import md5

SECRET_KEY = "this is my secret key 123456"

"""Connect to mongo DB"""
connect('accounts')
"""If this database dose not exist mongo engine create DB"""


class Accounts(Document):
    """Accounts table with fields"""
    username = StringField(required=True, unique=True)
    email = EmailField(required=True, unique=True)
    password = StringField(required=True)


class UsersServicer(UsersServicer):
    """Register user function get Accounts fields"""
    def RegisterUser(self, request, context):
        try:
            """Hash password and save into database"""
            salt = "5gz"
            user_password = request.password
            db_password = user_password + salt
            hashed_password = md5(db_password.encode())
            hashed_password_digest = hashed_password.hexdigest()
            user_register = Accounts(username=request.username, email=request.email, password=hashed_password_digest)
            user_register.save()
            response = RegisterUserResponse()
            """if every things ok user get this message"""
            response.message = f"Register complete. your username is {request.username} and" \
                               f" your password is {request.password}"
            return response
        except NotUniqueError:
            """if username or email is not unique"""
            response = RegisterUserResponse()
            response.message = f"Username or email is repetitive"
            return response

    """Login user function"""
    def LoginUser(self, request, context):
        """Handle error if username or password True or False"""
        try:
            """Check hash password"""
            salt = "5gz"
            user_password = request.password
            db_password = user_password + salt
            hashed_password = md5(db_password.encode())
            hashed_password_digest = hashed_password.hexdigest()
            user_login = Accounts.objects(username=request.username, password=hashed_password_digest)
            user_login.get()
            """Generate jwt token"""
            token = encode({"user": request.username, "exp": datetime.utcnow() + timedelta(minutes=60)
                            }, SECRET_KEY, algorithm="HS256")
            """Decode jwt token"""
            decode(token, SECRET_KEY, algorithms=["HS256"])
            """If username and password True user get this message"""
            response = LoginUserResponse()
            response.message = f"Login complete. your username is {request.username} and your token is: {token}"
            return response
        except DoesNotExist:
            """If username or password wrong user get this message"""
            response = LoginUserResponse()
            response.message = f"Wrong username or password"
            return response


def main():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_UsersServicer_to_server(UsersServicer(), server)
    """Server port"""
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()


"""Run main function and then run server"""
main()
