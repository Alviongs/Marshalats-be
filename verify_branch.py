#!/usr/bin/env python3

import requests

# Login and get token
token_response = requests.post('http://localhost:8003/api/auth/login', 
                              json={'email': 'superadmin@test.com', 'password': 'SuperAdmin123!'})
token = token_response.json()['access_token']

# Get all branches
branches_response = requests.get('http://localhost:8003/api/branches', 
                                headers={'Authorization': f'Bearer {token}'})
branches = branches_response.json()['branches']

print(f'Total branches in database: {len(branches)}')
if branches:
    latest_branch = branches[-1]
    print(f'Latest branch: {latest_branch["branch"]["name"]} (ID: {latest_branch["id"]})')
    print(f'Manager ID: {latest_branch["manager_id"]}')
    print(f'Created at: {latest_branch["created_at"]}')
