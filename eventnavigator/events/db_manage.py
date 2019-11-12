from django.db import connection

accounts_table = '`rutgers-app`.accounts'

# RETURN VALUES:
#   -1 = Unsucessful attempt (username/email already exist, or PW != confirmPW)
#   1 = account successfully created within function
def register_account(request):

        inputUsername = request.POST.get("inputUsername")
        inputEmail = request.POST.get("inputEmail")
        inputPassword = request.POST.get("inputPassword")
        inputConfirmPassword = request.POST.get("inputConfirmPassword")

        print('[DEBUG] db_manage.register_account()')
        print('[DEBUG] inputUsername: {}'.format(inputUsername))
        print('[DEBUG] inputEmail: {}'.format(inputEmail))
        print('[DEBUG] inputPassword: {}'.format(inputPassword))
        print('[DEBUG] inputConfirmPassword: {}'.format(inputConfirmPassword))

        if inputPassword != inputConfirmPassword:
            print('[DEBUG] RETURN: -1 (Password != confirmPassword)')
            return -1

        connection.ensure_connection()
        cursor = connection.cursor()
        #checking for duplicates
        query = 'SELECT exists (SELECT 1 from {table_name} WHERE username = "{0}" OR email = "{1}");'
        query = query.format(inputUsername, inputEmail, table_name = accounts_table)

        cursor.execute(query)
        row = cursor.fetchone()
        if row[0] == 1:
            cursor.close()
            print('[DEBUG] RETURN: -1 (Username/Email exists)')
            return -1

        #inserting new account into db
        query = 'INSERT INTO {table_name} (username, password, email) VALUES ("{0}","{1}","{2}");'
        query = query.format(inputUsername, inputPassword, inputEmail, table_name = accounts_table)
        cursor.execute(query)
        cursor.close()
        print('[DEBUG] RETURN: 1')
        return 1
