import grpc
from concurrent import futures
import accounts_pb2
import accounts_pb2_grpc
from mongoengine import *

# connect to mongodb
connect('accounts')


class Accounts(Document):
    username = StringField(required=True, unique=True)
    email = EmailField(required=True, unique=True)
    password = IntField(required=True)


class UsersServicer(accounts_pb2_grpc.UsersServicer):
    def RegisterUser(self, request, context):
        print("registering user")
        user_register = Accounts(username=request.username, email=request.email, password=request.password)
        user_register.save()
        response = accounts_pb2.RegisterUserResponse()
        response.message = f"register complete. your username is {request.username} and" \
                           f" your password is {request.password}"
        print(request.username)
        print(request.password)
        return response

    def LoginUser(self, request, context):
        print("login user")
        user_login = Accounts.objects(username=request.username, password=request.password)
        user_login.get()
        response = accounts_pb2.LoginUserResponse()
        response.message = f"login complete. your username is {request.username}"
        print(request.username)
        print(request.password)
        return response


def main():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    accounts_pb2_grpc.add_UsersServicer_to_server(UsersServicer(), server)
    print('Server Started. Listening on port 50051')
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()


main()
