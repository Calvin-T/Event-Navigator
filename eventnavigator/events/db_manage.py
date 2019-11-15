from django.db import connection
from django.contrib import messages
from .forms import RegisterForm
from django.shortcuts import render

accounts_table = '`rutgers-app`.accounts'

# RETURN VALUES:
#   -1 = Unsucessful attempt (username/email already exist, or PW != confirmPW)
#   1 = account successfully created within function
def register_account(request):
        inputUsername = request.POST.get("inputUsername")
        inputEmail = request.POST.get("inputEmail")
        inputPassword = request.POST.get("inputPassword")
        inputConfirmPassword = request.POST.get("inputConfirmPassword")
        isOrg = 1 if request.POST.get("isOrg") == "on" else 0

        print('[DEBUG] db_manage.register_account()')
        print('[DEBUG] inputUsername: {}'.format(inputUsername))
        print('[DEBUG] inputEmail: {}'.format(inputEmail))
        print('[DEBUG] inputPassword: {}'.format(inputPassword))
        print('[DEBUG] inputConfirmPassword: {}'.format(inputConfirmPassword))
        print('[DEBUG] isOrg {}'.format(isOrg))

        if inputPassword != inputConfirmPassword:
            messages.error(request,'Error: password and confirmPassword does not match! Please try again')
            print('[DEBUG] RETURN: -1 (Password != confirmPassword)')
            return render(request, 'register.html')

        connection.ensure_connection()
        cursor = connection.cursor()
        #checking for duplicates
        query = 'SELECT exists (SELECT 1 from {table_name} WHERE username = "{0}" OR email = "{1}");'
        query = query.format(inputUsername, inputEmail, table_name = accounts_table)

        cursor.execute(query)
        row = cursor.fetchone()
        if row[0] == 1:
            cursor.close()
            messages.error(request,'Error: username/email already exists! Please try again')
            print('[DEBUG] RETURN: -1 (Username/Email exists)')
            return render(request, 'register.html')
        #inserting new account into db
        query = 'INSERT INTO {table_name} (username, password, email, isOrg) VALUES ("{0}","{1}","{2}", "{3}");'
        query = query.format(inputUsername, inputPassword, inputEmail, isOrg, table_name = accounts_table)
        cursor.execute(query)
        cursor.close()
    
        print('[DEBUG] RETURN: 1')
        return render(request, 'register.html')
