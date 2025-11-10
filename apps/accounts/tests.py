from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

User = get_user_model()


class UserModelTest(TestCase):
    """사용자 모델 테스트"""
    
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'phone': '010-1234-5678',
            'preferred_district': '강남구'
        }
    
    def test_create_user(self):
        """일반 사용자 생성 테스트"""
        user = User.objects.create_user(**self.user_data)
        
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.username, 'testuser')
        self.assertTrue(user.check_password('testpass123'))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.is_active)
    
    def test_create_superuser(self):
        """슈퍼유저 생성 테스트"""
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        
        self.assertEqual(admin_user.email, 'admin@example.com')
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
        self.assertTrue(admin_user.is_active)
    
    def test_user_string_representation(self):
        """사용자 문자열 표현 테스트"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(str(user), 'test@example.com')
    
    def test_email_unique(self):
        """이메일 중복 방지 테스트"""
        User.objects.create_user(**self.user_data)
        
        with self.assertRaises(Exception):
            User.objects.create_user(
                username='testuser2',
                email='test@example.com',  # 중복 이메일
                password='testpass123'
            )


class UserAuthenticationAPITest(APITestCase):
    """사용자 인증 API 테스트"""
    
    def setUp(self):
        self.register_url = reverse('api:accounts:register')
        self.login_url = reverse('api:accounts:login')
        self.profile_url = reverse('api:accounts:profile')
        
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'phone': '010-1234-5678',
            'preferred_district': '강남구'
        }
    
    def test_user_registration(self):
        """사용자 회원가입 테스트"""
        response = self.client.post(self.register_url, self.user_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('tokens', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['email'], 'test@example.com')
    
    def test_user_registration_password_mismatch(self):
        """비밀번호 불일치 회원가입 테스트"""
        self.user_data['password_confirm'] = 'wrongpass'
        response = self.client.post(self.register_url, self.user_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_user_login(self):
        """사용자 로그인 테스트"""
        # 먼저 사용자 생성
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        login_data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        
        response = self.client.post(self.login_url, login_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)
        self.assertIn('user', response.data)
    
    def test_user_login_invalid_credentials(self):
        """잘못된 인증정보 로그인 테스트"""
        login_data = {
            'email': 'wrong@example.com',
            'password': 'wrongpass'
        }
        
        response = self.client.post(self.login_url, login_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_user_profile_access(self):
        """사용자 프로필 접근 테스트"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # 인증 없이 접근
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # 인증 후 접근
        self.client.force_authenticate(user=user)
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'test@example.com')