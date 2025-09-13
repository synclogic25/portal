#!/usr/bin/env python3
"""
SyncLogic Portal Backend API Tests
Tests all backend endpoints for JWT authentication, user management, and applications API
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "https://app-gateway-3.preview.emergentagent.com/api"
TEST_USER = {
    "username": "admin",
    "password": "password"
}

# Test user for registration
NEW_TEST_USER = {
    "username": "testuser_" + str(int(datetime.now().timestamp())),
    "email": "test@synclogic.com",
    "full_name": "Test User",
    "password": "testpassword123"
}

class BackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        
    def log_test(self, test_name, success, message, details=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if details:
            print(f"   Details: {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "details": details
        })
    
    def test_register_endpoint(self):
        """Test user registration endpoint"""
        print("\n=== Testing User Registration ===")
        
        try:
            response = self.session.post(
                f"{BASE_URL}/register",
                json=NEW_TEST_USER,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if "id" in data and "username" in data:
                    self.log_test("User Registration", True, "Successfully registered new user", 
                                f"User ID: {data.get('id')}, Username: {data.get('username')}")
                else:
                    self.log_test("User Registration", False, "Invalid response format", 
                                f"Response: {data}")
            else:
                self.log_test("User Registration", False, f"HTTP {response.status_code}", 
                            f"Response: {response.text}")
                
        except Exception as e:
            self.log_test("User Registration", False, "Request failed", str(e))
    
    def test_login_endpoint(self):
        """Test user login endpoint"""
        print("\n=== Testing User Login ===")
        
        try:
            response = self.session.post(
                f"{BASE_URL}/login",
                json=TEST_USER,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data and "user" in data:
                    self.auth_token = data["access_token"]
                    user_info = data["user"]
                    self.log_test("User Login", True, "Successfully logged in", 
                                f"Token received, User: {user_info.get('username')}")
                    return True
                else:
                    self.log_test("User Login", False, "Invalid response format", 
                                f"Response: {data}")
            else:
                self.log_test("User Login", False, f"HTTP {response.status_code}", 
                            f"Response: {response.text}")
                
        except Exception as e:
            self.log_test("User Login", False, "Request failed", str(e))
        
        return False
    
    def test_me_endpoint(self):
        """Test /me endpoint with authentication"""
        print("\n=== Testing /me Endpoint ===")
        
        if not self.auth_token:
            self.log_test("Get User Info", False, "No auth token available", "Login first")
            return
        
        try:
            headers = {
                "Authorization": f"Bearer {self.auth_token}",
                "Content-Type": "application/json"
            }
            
            response = self.session.get(f"{BASE_URL}/me", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if "username" in data and "email" in data:
                    self.log_test("Get User Info", True, "Successfully retrieved user info", 
                                f"Username: {data.get('username')}, Email: {data.get('email')}")
                else:
                    self.log_test("Get User Info", False, "Invalid response format", 
                                f"Response: {data}")
            else:
                self.log_test("Get User Info", False, f"HTTP {response.status_code}", 
                            f"Response: {response.text}")
                
        except Exception as e:
            self.log_test("Get User Info", False, "Request failed", str(e))
    
    def test_applications_endpoint(self):
        """Test /applications endpoint"""
        print("\n=== Testing Applications Endpoint ===")
        
        if not self.auth_token:
            self.log_test("Get Applications", False, "No auth token available", "Login first")
            return
        
        try:
            headers = {
                "Authorization": f"Bearer {self.auth_token}",
                "Content-Type": "application/json"
            }
            
            response = self.session.get(f"{BASE_URL}/applications", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    total_apps = len(data)
                    native_apps = [app for app in data if app.get("category") == "native"]
                    portal_apps = [app for app in data if app.get("category") == "portal"]
                    
                    if total_apps == 16 and len(native_apps) == 8 and len(portal_apps) == 8:
                        self.log_test("Get Applications", True, "Successfully retrieved applications", 
                                    f"Total: {total_apps}, Native: {len(native_apps)}, Portal: {len(portal_apps)}")
                    else:
                        self.log_test("Get Applications", False, "Incorrect application count", 
                                    f"Expected 16 total (8 native + 8 portal), got {total_apps} ({len(native_apps)} native + {len(portal_apps)} portal)")
                else:
                    self.log_test("Get Applications", False, "Invalid response format", 
                                f"Expected list, got: {type(data)}")
            else:
                self.log_test("Get Applications", False, f"HTTP {response.status_code}", 
                            f"Response: {response.text}")
                
        except Exception as e:
            self.log_test("Get Applications", False, "Request failed", str(e))
    
    def test_token_generation_endpoint(self):
        """Test token generation for portal apps"""
        print("\n=== Testing Token Generation ===")
        
        if not self.auth_token:
            self.log_test("Generate Portal Token", False, "No auth token available", "Login first")
            return
        
        try:
            headers = {
                "Authorization": f"Bearer {self.auth_token}",
                "Content-Type": "application/json"
            }
            
            # Test with a portal app ID
            app_id = "portal1"
            response = self.session.post(f"{BASE_URL}/applications/{app_id}/access-token", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data and "app_id" in data:
                    self.log_test("Generate Portal Token", True, "Successfully generated portal token", 
                                f"App ID: {data.get('app_id')}, Token generated")
                else:
                    self.log_test("Generate Portal Token", False, "Invalid response format", 
                                f"Response: {data}")
            else:
                self.log_test("Generate Portal Token", False, f"HTTP {response.status_code}", 
                            f"Response: {response.text}")
                
        except Exception as e:
            self.log_test("Generate Portal Token", False, "Request failed", str(e))
    
    def test_unauthorized_access(self):
        """Test unauthorized access to protected endpoints"""
        print("\n=== Testing Unauthorized Access ===")
        
        endpoints_to_test = ["/me", "/applications", "/applications/portal1/access-token"]
        
        for endpoint in endpoints_to_test:
            try:
                if endpoint.endswith("/access-token"):
                    response = self.session.post(f"{BASE_URL}{endpoint}")
                else:
                    response = self.session.get(f"{BASE_URL}{endpoint}")
                
                if response.status_code == 401:
                    self.log_test(f"Unauthorized Access {endpoint}", True, "Correctly rejected unauthorized request", 
                                f"HTTP 401 returned")
                else:
                    self.log_test(f"Unauthorized Access {endpoint}", False, f"Expected 401, got {response.status_code}", 
                                f"Response: {response.text}")
                    
            except Exception as e:
                self.log_test(f"Unauthorized Access {endpoint}", False, "Request failed", str(e))
    
    def test_invalid_credentials(self):
        """Test login with invalid credentials"""
        print("\n=== Testing Invalid Credentials ===")
        
        try:
            invalid_user = {
                "username": "invalid_user",
                "password": "wrong_password"
            }
            
            response = self.session.post(
                f"{BASE_URL}/login",
                json=invalid_user,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 401:
                self.log_test("Invalid Credentials", True, "Correctly rejected invalid credentials", 
                            f"HTTP 401 returned")
            else:
                self.log_test("Invalid Credentials", False, f"Expected 401, got {response.status_code}", 
                            f"Response: {response.text}")
                
        except Exception as e:
            self.log_test("Invalid Credentials", False, "Request failed", str(e))
    
    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting SyncLogic Portal Backend API Tests")
        print(f"📍 Testing against: {BASE_URL}")
        print(f"👤 Test user: {TEST_USER['username']}")
        
        # Test registration
        self.test_register_endpoint()
        
        # Test login (required for subsequent tests)
        login_success = self.test_login_endpoint()
        
        if login_success:
            # Test authenticated endpoints
            self.test_me_endpoint()
            self.test_applications_endpoint()
            self.test_token_generation_endpoint()
        
        # Test security
        self.test_unauthorized_access()
        self.test_invalid_credentials()
        
        # Summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("📊 TEST SUMMARY")
        print("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n🔍 FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  • {result['test']}: {result['message']}")
                    if result["details"]:
                        print(f"    Details: {result['details']}")
        
        print("\n" + "="*60)

if __name__ == "__main__":
    tester = BackendTester()
    tester.run_all_tests()