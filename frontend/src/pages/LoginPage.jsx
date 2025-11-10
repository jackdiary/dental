import React, { useState, useContext } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import styled from 'styled-components';
import { AuthContext } from '../contexts/AuthContext';
import LoadingSpinner from '../components/common/LoadingSpinner';

const LoginContainer = styled.div`
  min-height: calc(100vh - 140px);
  display: flex;
  align-items: center;
  justify-content: center;
  background: ${props => props.theme.colors.backgroundGray};
  padding: 32px 24px;

  @media (max-width: ${props => props.theme.breakpoints.tablet}) {
    padding: 24px 16px;
  }
`;

const LoginCard = styled.div`
  background: ${props => props.theme.colors.white};
  border-radius: ${props => props.theme.borderRadius.xl};
  box-shadow: ${props => props.theme.shadows.lg};
  padding: 48px;
  width: 100%;
  max-width: 400px;

  @media (max-width: ${props => props.theme.breakpoints.mobile}) {
    padding: 32px 24px;
  }
`;

const LoginHeader = styled.div`
  text-align: center;
  margin-bottom: 32px;
`;

const LoginTitle = styled.h1`
  font-size: ${props => props.theme.fonts.sizes['2xl']};
  font-weight: ${props => props.theme.fonts.weights.bold};
  color: ${props => props.theme.colors.textPrimary};
  margin-bottom: 8px;
`;

const LoginSubtitle = styled.p`
  color: ${props => props.theme.colors.textSecondary};
  font-size: ${props => props.theme.fonts.sizes.base};
`;

const LoginForm = styled.form`
  display: flex;
  flex-direction: column;
  gap: 20px;
`;

const FormGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const FormLabel = styled.label`
  font-size: ${props => props.theme.fonts.sizes.sm};
  font-weight: ${props => props.theme.fonts.weights.medium};
  color: ${props => props.theme.colors.textPrimary};
`;

const FormInput = styled.input`
  padding: 16px 20px;
  border: 2px solid ${props => props.hasError ? props.theme.colors.error : props.theme.colors.gray200};
  border-radius: ${props => props.theme.borderRadius.lg};
  font-size: ${props => props.theme.fonts.sizes.base};
  color: ${props => props.theme.colors.textPrimary};
  transition: border-color ${props => props.theme.transitions.fast};

  &:focus {
    outline: none;
    border-color: ${props => props.hasError ? props.theme.colors.error : props.theme.colors.primary};
  }

  &::placeholder {
    color: ${props => props.theme.colors.textLight};
  }
`;

const ErrorMessage = styled.div`
  color: ${props => props.theme.colors.error};
  font-size: ${props => props.theme.fonts.sizes.sm};
  margin-top: 4px;
`;

const LoginButton = styled.button`
  background: ${props => props.theme.colors.primary};
  color: ${props => props.theme.colors.white};
  padding: 16px 24px;
  border-radius: ${props => props.theme.borderRadius.lg};
  font-size: ${props => props.theme.fonts.sizes.base};
  font-weight: ${props => props.theme.fonts.weights.semibold};
  transition: background ${props => props.theme.transitions.fast};
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 8px;

  &:hover:not(:disabled) {
    background: ${props => props.theme.colors.primaryDark};
  }

  &:disabled {
    background: ${props => props.theme.colors.gray400};
    cursor: not-allowed;
  }
`;

const LoginOptions = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 16px 0;
  font-size: ${props => props.theme.fonts.sizes.sm};
`;

const RememberMe = styled.label`
  display: flex;
  align-items: center;
  gap: 8px;
  color: ${props => props.theme.colors.textSecondary};
  cursor: pointer;

  input {
    width: 16px;
    height: 16px;
    accent-color: ${props => props.theme.colors.primary};
  }
`;

const ForgotPassword = styled(Link)`
  color: ${props => props.theme.colors.primary};
  text-decoration: none;
  transition: color ${props => props.theme.transitions.fast};

  &:hover {
    color: ${props => props.theme.colors.primaryDark};
  }
`;

const Divider = styled.div`
  display: flex;
  align-items: center;
  margin: 24px 0;
  
  &::before,
  &::after {
    content: '';
    flex: 1;
    height: 1px;
    background: ${props => props.theme.colors.gray200};
  }

  span {
    padding: 0 16px;
    color: ${props => props.theme.colors.textLight};
    font-size: ${props => props.theme.fonts.sizes.sm};
  }
`;

const SignupPrompt = styled.div`
  text-align: center;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid ${props => props.theme.colors.gray200};
  color: ${props => props.theme.colors.textSecondary};
  font-size: ${props => props.theme.fonts.sizes.sm};

  a {
    color: ${props => props.theme.colors.primary};
    font-weight: ${props => props.theme.fonts.weights.medium};
    text-decoration: none;
    transition: color ${props => props.theme.transitions.fast};

    &:hover {
      color: ${props => props.theme.colors.primaryDark};
    }
  }
`;

function LoginPage() {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    rememberMe: false
  });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  
  const { login } = useContext(AuthContext);
  const navigate = useNavigate();
  const location = useLocation();
  
  const from = location.state?.from?.pathname || '/';

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
    
    // 입력 시 해당 필드의 에러 제거
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.email) {
      newErrors.email = '이메일을 입력해주세요.';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = '올바른 이메일 형식이 아닙니다.';
    }

    if (!formData.password) {
      newErrors.password = '비밀번호를 입력해주세요.';
    } else if (formData.password.length < 6) {
      newErrors.password = '비밀번호는 6자 이상이어야 합니다.';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setLoading(true);
    
    try {
      const result = await login(formData.email, formData.password);
      
      if (result.success) {
        // 로그인 성공
        navigate(from, { replace: true });
      } else {
        // 로그인 실패
        setErrors({ general: result.error });
      }
    } catch (error) {
      setErrors({ general: '로그인 중 오류가 발생했습니다.' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <LoginContainer>
      <LoginCard>
        <LoginHeader>
          <LoginTitle>로그인</LoginTitle>
          <LoginSubtitle>치과AI에 오신 것을 환영합니다</LoginSubtitle>
        </LoginHeader>

        <LoginForm onSubmit={handleSubmit}>
          {errors.general && (
            <ErrorMessage>{errors.general}</ErrorMessage>
          )}

          <FormGroup>
            <FormLabel htmlFor="email">이메일</FormLabel>
            <FormInput
              id="email"
              name="email"
              type="email"
              placeholder="이메일을 입력하세요"
              value={formData.email}
              onChange={handleInputChange}
              hasError={!!errors.email}
              autoComplete="email"
            />
            {errors.email && <ErrorMessage>{errors.email}</ErrorMessage>}
          </FormGroup>

          <FormGroup>
            <FormLabel htmlFor="password">비밀번호</FormLabel>
            <FormInput
              id="password"
              name="password"
              type="password"
              placeholder="비밀번호를 입력하세요"
              value={formData.password}
              onChange={handleInputChange}
              hasError={!!errors.password}
              autoComplete="current-password"
            />
            {errors.password && <ErrorMessage>{errors.password}</ErrorMessage>}
          </FormGroup>

          <LoginOptions>
            <RememberMe>
              <input
                type="checkbox"
                name="rememberMe"
                checked={formData.rememberMe}
                onChange={handleInputChange}
              />
              로그인 상태 유지
            </RememberMe>
            <ForgotPassword to="/forgot-password">
              비밀번호 찾기
            </ForgotPassword>
          </LoginOptions>

          <LoginButton type="submit" disabled={loading}>
            {loading ? (
              <LoadingSpinner size="small" />
            ) : (
              '로그인'
            )}
          </LoginButton>
        </LoginForm>

        <SignupPrompt>
          아직 계정이 없으신가요?{' '}
          <Link to="/register">회원가입</Link>
        </SignupPrompt>
      </LoginCard>
    </LoginContainer>
  );
}

export default LoginPage;