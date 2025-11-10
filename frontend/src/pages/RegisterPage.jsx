import React, { useState, useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { AuthContext } from '../contexts/AuthContext';
import LoadingSpinner from '../components/common/LoadingSpinner';

const RegisterContainer = styled.div`
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

const RegisterCard = styled.div`
  background: ${props => props.theme.colors.white};
  border-radius: ${props => props.theme.borderRadius.xl};
  box-shadow: ${props => props.theme.shadows.lg};
  padding: 48px;
  width: 100%;
  max-width: 480px;

  @media (max-width: ${props => props.theme.breakpoints.mobile}) {
    padding: 32px 24px;
  }
`;

const RegisterHeader = styled.div`
  text-align: center;
  margin-bottom: 32px;
`;

const RegisterTitle = styled.h1`
  font-size: ${props => props.theme.fonts.sizes['2xl']};
  font-weight: ${props => props.theme.fonts.weights.bold};
  color: ${props => props.theme.colors.textPrimary};
  margin-bottom: 8px;
`;

const RegisterSubtitle = styled.p`
  color: ${props => props.theme.colors.textSecondary};
  font-size: ${props => props.theme.fonts.sizes.base};
`;

const RegisterForm = styled.form`
  display: flex;
  flex-direction: column;
  gap: 20px;
`;

const FormRow = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;

  @media (max-width: ${props => props.theme.breakpoints.mobile}) {
    grid-template-columns: 1fr;
    gap: 20px;
  }
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
  width: 100%;
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

const FormSelect = styled.select`
  padding: 16px 20px;
  border: 2px solid ${props => props.hasError ? props.theme.colors.error : props.theme.colors.gray200};
  border-radius: ${props => props.theme.borderRadius.lg};
  font-size: ${props => props.theme.fonts.sizes.base};
  color: ${props => props.theme.colors.textPrimary};
  background: ${props => props.theme.colors.white};
  transition: border-color ${props => props.theme.transitions.fast};

  &:focus {
    outline: none;
    border-color: ${props => props.hasError ? props.theme.colors.error : props.theme.colors.primary};
  }
`;

const ErrorMessage = styled.div`
  color: ${props => props.theme.colors.error};
  font-size: ${props => props.theme.fonts.sizes.sm};
  margin-top: 4px;
`;

const PasswordStrength = styled.div`
  margin-top: 8px;
`;

const StrengthBar = styled.div`
  height: 4px;
  background: ${props => props.theme.colors.gray200};
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: 4px;
`;

const StrengthFill = styled.div`
  height: 100%;
  width: ${props => props.strength}%;
  background: ${props => {
    if (props.strength < 30) return props.theme.colors.error;
    if (props.strength < 70) return props.theme.colors.warning;
    return props.theme.colors.success;
  }};
  transition: all ${props => props.theme.transitions.base};
`;

const StrengthText = styled.div`
  font-size: ${props => props.theme.fonts.sizes.xs};
  color: ${props => {
    if (props.strength < 30) return props.theme.colors.error;
    if (props.strength < 70) return props.theme.colors.warning;
    return props.theme.colors.success;
  }};
`;

const TermsCheckbox = styled.label`
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin: 16px 0;
  cursor: pointer;
  font-size: ${props => props.theme.fonts.sizes.sm};
  color: ${props => props.theme.colors.textSecondary};
  line-height: 1.5;

  input {
    width: 16px;
    height: 16px;
    margin-top: 2px;
    accent-color: ${props => props.theme.colors.primary};
  }

  a {
    color: ${props => props.theme.colors.primary};
    text-decoration: none;

    &:hover {
      text-decoration: underline;
    }
  }
`;

const RegisterButton = styled.button`
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

const LoginPrompt = styled.div`
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

function RegisterPage() {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    password_confirm: '',
    phone: '',
    preferred_district: '',
    agreeTerms: false
  });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [passwordStrength, setPasswordStrength] = useState(0);
  
  const { register } = useContext(AuthContext);
  const navigate = useNavigate();

  const calculatePasswordStrength = (password) => {
    let strength = 0;
    
    if (password.length >= 8) strength += 25;
    if (password.length >= 12) strength += 15;
    if (/[a-z]/.test(password)) strength += 15;
    if (/[A-Z]/.test(password)) strength += 15;
    if (/[0-9]/.test(password)) strength += 15;
    if (/[^A-Za-z0-9]/.test(password)) strength += 15;
    
    return Math.min(strength, 100);
  };

  const getPasswordStrengthText = (strength) => {
    if (strength < 30) return '약함';
    if (strength < 70) return '보통';
    return '강함';
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    const newValue = type === 'checkbox' ? checked : value;
    
    setFormData(prev => ({
      ...prev,
      [name]: newValue
    }));
    
    // 비밀번호 강도 계산
    if (name === 'password') {
      setPasswordStrength(calculatePasswordStrength(value));
    }
    
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

    if (!formData.username) {
      newErrors.username = '사용자명을 입력해주세요.';
    } else if (formData.username.length < 2) {
      newErrors.username = '사용자명은 2자 이상이어야 합니다.';
    }

    if (!formData.email) {
      newErrors.email = '이메일을 입력해주세요.';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = '올바른 이메일 형식이 아닙니다.';
    }

    if (!formData.password) {
      newErrors.password = '비밀번호를 입력해주세요.';
    } else if (formData.password.length < 8) {
      newErrors.password = '비밀번호는 8자 이상이어야 합니다.';
    }

    if (!formData.password_confirm) {
      newErrors.password_confirm = '비밀번호 확인을 입력해주세요.';
    } else if (formData.password !== formData.password_confirm) {
      newErrors.password_confirm = '비밀번호가 일치하지 않습니다.';
    }

    if (formData.phone && !/^010-?\d{4}-?\d{4}$/.test(formData.phone.replace(/\s/g, ''))) {
      newErrors.phone = '올바른 휴대폰 번호 형식이 아닙니다.';
    }

    if (!formData.agreeTerms) {
      newErrors.agreeTerms = '이용약관에 동의해주세요.';
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
      const { agreeTerms, ...registerData } = formData;
      const result = await register(registerData);
      
      if (result.success) {
        // 회원가입 성공
        navigate('/', { replace: true });
      } else {
        // 회원가입 실패
        setErrors({ general: result.error });
      }
    } catch (error) {
      setErrors({ general: '회원가입 중 오류가 발생했습니다.' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <RegisterContainer>
      <RegisterCard>
        <RegisterHeader>
          <RegisterTitle>회원가입</RegisterTitle>
          <RegisterSubtitle>치과AI와 함께 신뢰할 수 있는 치과를 찾아보세요</RegisterSubtitle>
        </RegisterHeader>

        <RegisterForm onSubmit={handleSubmit}>
          {errors.general && (
            <ErrorMessage>{errors.general}</ErrorMessage>
          )}

          <FormRow>
            <FormGroup>
              <FormLabel htmlFor="username">사용자명 *</FormLabel>
              <FormInput
                id="username"
                name="username"
                type="text"
                placeholder="사용자명을 입력하세요"
                value={formData.username}
                onChange={handleInputChange}
                hasError={!!errors.username}
                autoComplete="username"
              />
              {errors.username && <ErrorMessage>{errors.username}</ErrorMessage>}
            </FormGroup>

            <FormGroup>
              <FormLabel htmlFor="email">이메일 *</FormLabel>
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
          </FormRow>

          <FormGroup>
            <FormLabel htmlFor="password">비밀번호 *</FormLabel>
            <FormInput
              id="password"
              name="password"
              type="password"
              placeholder="비밀번호를 입력하세요 (8자 이상)"
              value={formData.password}
              onChange={handleInputChange}
              hasError={!!errors.password}
              autoComplete="new-password"
            />
            {formData.password && (
              <PasswordStrength>
                <StrengthBar>
                  <StrengthFill strength={passwordStrength} />
                </StrengthBar>
                <StrengthText strength={passwordStrength}>
                  비밀번호 강도: {getPasswordStrengthText(passwordStrength)}
                </StrengthText>
              </PasswordStrength>
            )}
            {errors.password && <ErrorMessage>{errors.password}</ErrorMessage>}
          </FormGroup>

          <FormGroup>
            <FormLabel htmlFor="password_confirm">비밀번호 확인 *</FormLabel>
            <FormInput
              id="password_confirm"
              name="password_confirm"
              type="password"
              placeholder="비밀번호를 다시 입력하세요"
              value={formData.password_confirm}
              onChange={handleInputChange}
              hasError={!!errors.password_confirm}
              autoComplete="new-password"
            />
            {errors.password_confirm && <ErrorMessage>{errors.password_confirm}</ErrorMessage>}
          </FormGroup>

          <FormRow>
            <FormGroup>
              <FormLabel htmlFor="phone">휴대폰 번호</FormLabel>
              <FormInput
                id="phone"
                name="phone"
                type="tel"
                placeholder="010-1234-5678"
                value={formData.phone}
                onChange={handleInputChange}
                hasError={!!errors.phone}
                autoComplete="tel"
              />
              {errors.phone && <ErrorMessage>{errors.phone}</ErrorMessage>}
            </FormGroup>

            <FormGroup>
              <FormLabel htmlFor="preferred_district">선호 지역</FormLabel>
              <FormSelect
                id="preferred_district"
                name="preferred_district"
                value={formData.preferred_district}
                onChange={handleInputChange}
                hasError={!!errors.preferred_district}
              >
                <option value="">지역 선택</option>
                <option value="강서구">강서구</option>
                <option value="강남구">강남구</option>
                <option value="영등포구">영등포구</option>
              </FormSelect>
            </FormGroup>
          </FormRow>

          <TermsCheckbox>
            <input
              type="checkbox"
              name="agreeTerms"
              checked={formData.agreeTerms}
              onChange={handleInputChange}
            />
            <span>
              <Link to="/terms">이용약관</Link> 및 <Link to="/privacy">개인정보처리방침</Link>에 동의합니다. *
            </span>
          </TermsCheckbox>
          {errors.agreeTerms && <ErrorMessage>{errors.agreeTerms}</ErrorMessage>}

          <RegisterButton type="submit" disabled={loading}>
            {loading ? (
              <LoadingSpinner size="small" />
            ) : (
              '회원가입'
            )}
          </RegisterButton>
        </RegisterForm>

        <LoginPrompt>
          이미 계정이 있으신가요?{' '}
          <Link to="/login">로그인</Link>
        </LoginPrompt>
      </RegisterCard>
    </RegisterContainer>
  );
}

export default RegisterPage;