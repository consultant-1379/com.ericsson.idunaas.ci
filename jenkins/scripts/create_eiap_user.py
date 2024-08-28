import requests
import json
import argparse
import logging
import sys

LOG = logging.getLogger('Create EIAP User')
handler = logging.StreamHandler()
formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] - %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
handler.setFormatter(formatter)
LOG.addHandler(handler)
LOG.setLevel(logging.INFO)


def process_command_args():
    """
    Function to process command line arguments.

    Returns:
         (options, args) -- tuple with parameters provided to the script
    """

    description = 'Create EIAP user'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--url',
                        help='GAS URL of the environment',
                        required=True)
    parser.add_argument('--gas-user',
                        help='GAS User to be used for login',
                        required=False,
                        default='gas-user')
    parser.add_argument('--gas-password',
                        help='GAS Password to be used for login',
                        required=True)

    args = parser.parse_args()
    return args


def login(url: str, gas_user: str, gas_password: str) -> str:
    """Function to log in to the GAS
    Args:
        url: Environment GAS url
        gas_user: GAS user to login
        gas_password: GAS password of GAS user
    Returns:
        Session ID token
    """
    formatted_url = f'https://{url}/auth/v1/login'
    headers = {
        'X-Login': f'{gas_user}',
        'X-password': f'{gas_password}',
        'X-tenant': 'master',
    }
    try:
        response = requests.request('POST', url=formatted_url, headers=headers, verify='intermediate-ca.crt',
                                    timeout=20)
    except requests.exceptions.ConnectTimeout:
        LOG.error('Connection timed out. Host is down or unavailable')
        sys.exit(1)
    except requests.exceptions.ConnectionError:
        LOG.error(f'Hostname {formatted_url} doesn\'t exist')
        sys.exit(1)
    except requests.exceptions.HTTPError:
        LOG.error('Oops... Something went wrong')
        sys.exit(1)
    else:
        session_id = response.text
        return session_id


def get_users_username(url: str, session_id: str) -> list:
    """ Function to get all the users
            Args:
                url: Environment GAS url
                session_id: Session ID that we get from login() function
            Returns:
                List of Usernames
            """
    formatted_url = f'https://{url}/idm/usermgmt/v1/users'
    headers = {
        'Content-Type': 'application/json',
        'Cookie': f'JSESSIONID={session_id}'
    }
    response = requests.request('GET', url=formatted_url, headers=headers, verify='intermediate-ca.crt', timeout=20)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        LOG.error(f'{response.status_code} {response.reason}')
        LOG.error(response.text)
    else:
        users = json.loads(response.text)
        usernames = []
        for user in users:
            usernames.append(user["username"])
        return usernames


def update_user(url: str, session_id: str, user: str, roles: list) -> bool:
    """ Function to update the user with the given roles
        Args:
            url: Environment GAS url
            session_id: Session ID that we get from login() function
            user: User to be created
            roles: Role privileges for the created user
        """
    formatted_url = f'https://{url}/idm/usermgmt/v1/users/{user}'
    headers = {
        'Content-Type': 'application/json',
        'Cookie': f'JSESSIONID={session_id}'
    }
    payload = json.dumps({
        'username': f'{user}',
        'privileges': roles
    })
    response = requests.request('PUT', url=formatted_url, headers=headers, data=payload, verify='intermediate-ca.crt',
                                timeout=20)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        LOG.error(f'{response.status_code} {response.reason}')
        LOG.error(f'User {user} was not updated due to {response.text}')
        return True
    else:
        LOG.info(f'{response.status_code} {response.reason}')
        LOG.info(response.text)
        LOG.info(f'User {user} updated with privileges {roles}')
        return False


def create_user(url: str, session_id: str, user: str, password: str, roles: list, pw_reset: bool) -> bool:
    """ Function to create the user with the given roles
    Args:
        url: Environment GAS url
        session_id: Session ID that we get from login() function
        user: User to be created
        password: Password that we set to the created user
        roles: Role privileges for the created user
        pw_reset: Flag to force the password reset
    """
    formatted_url = f'https://{url}/idm/usermgmt/v1/users'

    payload = json.dumps({
        'user': {
            'username': f'{user}',
            'privileges': roles
        },
        'passwordResetFlag': f'{pw_reset}',
        'password': f'{password}',
        'tenant': 'master'
    })
    headers = {
        'Content-Type': 'application/json',
        'Cookie': f'JSESSIONID={session_id}'
    }

    response = requests.request('POST', url=formatted_url, headers=headers, data=payload, verify='intermediate-ca.crt',
                                timeout=20)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        LOG.error(f'{response.status_code} {response.reason}')
        LOG.error(f'User {user} was not created due to {response.text}')
        return True
    else:
        LOG.info(f'{response.status_code} {response.reason}')
        LOG.info(response.text)
        LOG.info(f'User {user} Created with privileges {roles}')
        return False


def main():
    """Main Function to create EIAP user
    """
    any_errors = False
    args = process_command_args()
    session_id = login(url=args.url, gas_user=args.gas_user, gas_password=args.gas_password)
    if session_id is not None:
        all_users_username = get_users_username(args.url, session_id)
        file = "users.json"
        with open(file, "r") as f:
            users = json.load(f)
        for user in users["users"]:
            user_name = user["name"]
            password = user["password"]
            roles = user["roles"]
            pw_reset = user["pwreset"]
            if user_name in all_users_username:
                LOG.info(f"Updating user {user_name}")
                any_error = update_user(url=args.url, session_id=session_id, user=user_name, roles=roles)
                any_errors = any_errors or any_error
            else:
                LOG.info(f"Creating user {user_name}")
                any_error = create_user(url=args.url, session_id=session_id, user=user_name, password=password,
                                        roles=roles, pw_reset=pw_reset)
                any_errors = any_errors or any_error
    if any_errors is True:
        sys.exit(1)


if __name__ == '__main__':
    main()
