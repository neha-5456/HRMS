import requests
import json

BASE_URL = "http://localhost:8000/api"

# Login first
def login():
    response = requests.post(f"{BASE_URL}/auth/login/", json={
        "email": "admin@company.com",
        "password": "your_password"
    })
    return response.json()['access']

# Test attendance check-in
def test_attendance(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/attendance/check_in/", headers=headers)
    print("Check-in:", response.json())

# Test leave request creation
def test_leave(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/leave/", 
        json={
            "leave_type": 1,
            "start_date": "2025-10-20",
            "end_date": "2025-10-22",
            "reason": "Personal"
        },
        headers=headers
    )
    print("Leave request:", response.json())

# Run tests
if __name__ == "__main__":
    token = login()
    test_attendance(token)
    test_leave(token)