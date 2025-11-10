import React, { useState, useContext } from 'react';
import styled from 'styled-components';
import { AuthContext } from '../contexts/AuthContext';
import LoadingSpinner from '../components/common/LoadingSpinner';

const MyPageContainer = styled.div`
  min-height: calc(100vh - 140px);
  background: ${props => props.theme.colors.backgroundGray};
`;

const MyPageContent = styled.div`
  max-width: 1400px;
  width: 100%;
  margin: 0 auto;
  padding: 32px 24px;

  @media (max-width: 1200px) {
    max-width: 1200px;
  }

  @media (max-width: ${props => props.theme.breakpoints.tablet}) {
    padding: 24px 16px;
  }
`;

const PageHeader = styled.div`
  background: ${props => props.theme.colors.white};
  border-radius: ${props => props.theme.borderRadius.xl};
  box-shadow: ${props => props.theme.shadows.base};
  padding: 32px;
  margin-bottom: 32px;
  width: 100%;
  box-sizing: border-box;

  @media (max-width: ${props => props.theme.breakpoints.tablet}) {
    padding: 24px;
    margin-bottom: 24px;
  }
`;

const PageTitle = styled.h1`
  font-size: ${props => props.theme.fonts.sizes['2xl']};
  font-weight: ${props => props.theme.fonts.weights.bold};
  color: ${props => props.theme.colors.textPrimary};
  margin-bottom: 8px;
`;

const PageSubtitle = styled.p`
  color: ${props => props.theme.colors.textSecondary};
  font-size: ${props => props.theme.fonts.sizes.base};
`;

const ContentGrid = styled.div`
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 32px;
  width: 100%;

  @media (max-width: 1200px) {
    grid-template-columns: 280px 1fr;
    gap: 24px;
  }

  @media (max-width: ${props => props.theme.breakpoints.desktop}) {
    grid-template-columns: 1fr;
    gap: 20px;
  }
`;

const Sidebar = styled.div`
  @media (max-width: ${props => props.theme.breakpoints.desktop}) {
    order: 2;
  }
`;

const MainContent = styled.div`
  @media (max-width: ${props => props.theme.breakpoints.desktop}) {
    order: 1;
  }
`;

const MenuCard = styled.div`
  background: ${props => props.theme.colors.white};
  border-radius: ${props => props.theme.borderRadius.xl};
  box-shadow: ${props => props.theme.shadows.base};
  overflow: hidden;
  width: 100%;
  box-sizing: border-box;
`;

const MenuItem = styled.button`
  width: 100%;
  padding: 16px 20px;
  text-align: left;
  background: ${props => props.active ? props.theme.colors.backgroundLight : 'transparent'};
  color: ${props => props.active ? props.theme.colors.primary : props.theme.colors.textPrimary};
  font-size: ${props => props.theme.fonts.sizes.base};
  font-weight: ${props => props.active ? props.theme.fonts.weights.semibold : props.theme.fonts.weights.normal};
  border-bottom: 1px solid ${props => props.theme.colors.gray200};
  transition: all ${props => props.theme.transitions.fast};

  &:last-child {
    border-bottom: none;
  }

  &:hover {
    background: ${props => props.theme.colors.backgroundLight};
    color: ${props => props.theme.colors.primary};
  }
`;

const ContentCard = styled.div`
  background: ${props => props.theme.colors.white};
  border-radius: ${props => props.theme.borderRadius.xl};
  box-shadow: ${props => props.theme.shadows.base};
  padding: 32px;
  width: 100%;
  box-sizing: border-box;

  @media (max-width: ${props => props.theme.breakpoints.tablet}) {
    padding: 24px;
  }
`;

const SectionTitle = styled.h2`
  font-size: ${props => props.theme.fonts.sizes.xl};
  font-weight: ${props => props.theme.fonts.weights.semibold};
  color: ${props => props.theme.colors.textPrimary};
  margin-bottom: 24px;
  padding-bottom: 12px;
  border-bottom: 1px solid ${props => props.theme.colors.gray200};
`;

const Form = styled.form`
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
  width: 100%;
  padding: 12px 16px;
  border: 1px solid ${props => props.theme.colors.gray300};
  border-radius: ${props => props.theme.borderRadius.md};
  font-size: ${props => props.theme.fonts.sizes.base};
  color: ${props => props.theme.colors.textPrimary};
  transition: border-color ${props => props.theme.transitions.fast};
  box-sizing: border-box;

  &:focus {
    outline: none;
    border-color: ${props => props.theme.colors.primary};
  }

  &:disabled {
    background: ${props => props.theme.colors.gray100};
    color: ${props => props.theme.colors.textLight};
  }
`;

const FormSelect = styled.select`
  width: 100%;
  padding: 12px 16px;
  border: 1px solid ${props => props.theme.colors.gray300};
  border-radius: ${props => props.theme.borderRadius.md};
  font-size: ${props => props.theme.fonts.sizes.base};
  color: ${props => props.theme.colors.textPrimary};
  background: ${props => props.theme.colors.white};
  transition: border-color ${props => props.theme.transitions.fast};
  box-sizing: border-box;

  &:focus {
    outline: none;
    border-color: ${props => props.theme.colors.primary};
  }
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: 12px;
  margin-top: 8px;

  @media (max-width: ${props => props.theme.breakpoints.mobile}) {
    flex-direction: column;
  }
`;

const Button = styled.button`
  padding: 12px 24px;
  border-radius: ${props => props.theme.borderRadius.md};
  font-size: ${props => props.theme.fonts.sizes.base};
  font-weight: ${props => props.theme.fonts.weights.medium};
  transition: all ${props => props.theme.transitions.fast};
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;

  &.primary {
    background: ${props => props.theme.colors.primary};
    color: ${props => props.theme.colors.white};

    &:hover:not(:disabled) {
      background: ${props => props.theme.colors.primaryDark};
    }
  }

  &.secondary {
    background: ${props => props.theme.colors.gray200};
    color: ${props => props.theme.colors.textPrimary};

    &:hover:not(:disabled) {
      background: ${props => props.theme.colors.gray300};
    }
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`;

const ErrorMessage = styled.div`
  color: ${props => props.theme.colors.error};
  font-size: ${props => props.theme.fonts.sizes.sm};
  margin-top: 4px;
`;

const SuccessMessage = styled.div`
  color: ${props => props.theme.colors.success};
  font-size: ${props => props.theme.fonts.sizes.sm};
  margin-top: 4px;
`;

const StatCard = styled.div`
  background: ${props => props.theme.colors.backgroundLight};
  padding: 20px;
  border-radius: ${props => props.theme.borderRadius.lg};
  text-align: center;
  margin-bottom: 16px;

  h3 {
    font-size: ${props => props.theme.fonts.sizes['2xl']};
    font-weight: ${props => props.theme.fonts.weights.bold};
    color: ${props => props.theme.colors.primary};
    margin-bottom: 8px;
  }

  p {
    color: ${props => props.theme.colors.textSecondary};
    font-size: ${props => props.theme.fonts.sizes.base};
  }
`;

function MyPage() {
  const { user, updateProfile, changePassword } = useContext(AuthContext);
  const [activeTab, setActiveTab] = useState('profile');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });

  const [profileData, setProfileData] = useState({
    username: user?.username || '',
    email: user?.email || '',
    phone: user?.phone || '',
    preferred_district: user?.preferred_district || '',
    notification_enabled: user?.notification_enabled || true
  });

  const [passwordData, setPasswordData] = useState({
    old_password: '',
    new_password: '',
    new_password_confirm: ''
  });

  const handleProfileChange = (e) => {
    const { name, value, type, checked } = e.target;
    setProfileData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handlePasswordChange = (e) => {
    const { name, value } = e.target;
    setPasswordData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleProfileSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage({ type: '', text: '' });

    try {
      const result = await updateProfile(profileData);
      if (result.success) {
        setMessage({ type: 'success', text: '프로필이 성공적으로 업데이트되었습니다.' });
      } else {
        setMessage({ type: 'error', text: result.error });
      }
    } catch (error) {
      setMessage({ type: 'error', text: '프로필 업데이트 중 오류가 발생했습니다.' });
    } finally {
      setLoading(false);
    }
  };

  const handlePasswordSubmit = async (e) => {
    e.preventDefault();
    
    if (passwordData.new_password !== passwordData.new_password_confirm) {
      setMessage({ type: 'error', text: '새 비밀번호가 일치하지 않습니다.' });
      return;
    }

    setLoading(true);
    setMessage({ type: '', text: '' });

    try {
      const result = await changePassword(passwordData);
      if (result.success) {
        setMessage({ type: 'success', text: '비밀번호가 성공적으로 변경되었습니다.' });
        setPasswordData({
          old_password: '',
          new_password: '',
          new_password_confirm: ''
        });
      } else {
        setMessage({ type: 'error', text: result.error });
      }
    } catch (error) {
      setMessage({ type: 'error', text: '비밀번호 변경 중 오류가 발생했습니다.' });
    } finally {
      setLoading(false);
    }
  };

  const renderContent = () => {
    switch (activeTab) {
      case 'profile':
        return (
          <ContentCard>
            <SectionTitle>프로필 정보</SectionTitle>
            <Form onSubmit={handleProfileSubmit}>
              <FormGroup>
                <FormLabel>사용자명</FormLabel>
                <FormInput
                  name="username"
                  value={profileData.username}
                  onChange={handleProfileChange}
                  placeholder="사용자명을 입력하세요"
                />
              </FormGroup>

              <FormGroup>
                <FormLabel>이메일</FormLabel>
                <FormInput
                  name="email"
                  type="email"
                  value={profileData.email}
                  onChange={handleProfileChange}
                  disabled
                />
              </FormGroup>

              <FormGroup>
                <FormLabel>휴대폰 번호</FormLabel>
                <FormInput
                  name="phone"
                  type="tel"
                  value={profileData.phone}
                  onChange={handleProfileChange}
                  placeholder="010-1234-5678"
                />
              </FormGroup>

              <FormGroup>
                <FormLabel>선호 지역</FormLabel>
                <FormSelect
                  name="preferred_district"
                  value={profileData.preferred_district}
                  onChange={handleProfileChange}
                >
                  <option value="">지역 선택</option>
                  <option value="강서구">강서구</option>
                  <option value="강남구">강남구</option>
                  <option value="영등포구">영등포구</option>
                </FormSelect>
              </FormGroup>

              <FormGroup>
                <FormLabel>
                  <input
                    type="checkbox"
                    name="notification_enabled"
                    checked={profileData.notification_enabled}
                    onChange={handleProfileChange}
                    style={{ marginRight: '8px' }}
                  />
                  알림 수신 동의
                </FormLabel>
              </FormGroup>

              {message.text && (
                message.type === 'success' ? (
                  <SuccessMessage>{message.text}</SuccessMessage>
                ) : (
                  <ErrorMessage>{message.text}</ErrorMessage>
                )
              )}

              <ButtonGroup>
                <Button type="submit" className="primary" disabled={loading}>
                  {loading ? <LoadingSpinner size="small" /> : '저장하기'}
                </Button>
              </ButtonGroup>
            </Form>
          </ContentCard>
        );

      case 'password':
        return (
          <ContentCard>
            <SectionTitle>비밀번호 변경</SectionTitle>
            <Form onSubmit={handlePasswordSubmit}>
              <FormGroup>
                <FormLabel>현재 비밀번호</FormLabel>
                <FormInput
                  name="old_password"
                  type="password"
                  value={passwordData.old_password}
                  onChange={handlePasswordChange}
                  placeholder="현재 비밀번호를 입력하세요"
                />
              </FormGroup>

              <FormGroup>
                <FormLabel>새 비밀번호</FormLabel>
                <FormInput
                  name="new_password"
                  type="password"
                  value={passwordData.new_password}
                  onChange={handlePasswordChange}
                  placeholder="새 비밀번호를 입력하세요"
                />
              </FormGroup>

              <FormGroup>
                <FormLabel>새 비밀번호 확인</FormLabel>
                <FormInput
                  name="new_password_confirm"
                  type="password"
                  value={passwordData.new_password_confirm}
                  onChange={handlePasswordChange}
                  placeholder="새 비밀번호를 다시 입력하세요"
                />
              </FormGroup>

              {message.text && (
                message.type === 'success' ? (
                  <SuccessMessage>{message.text}</SuccessMessage>
                ) : (
                  <ErrorMessage>{message.text}</ErrorMessage>
                )
              )}

              <ButtonGroup>
                <Button type="submit" className="primary" disabled={loading}>
                  {loading ? <LoadingSpinner size="small" /> : '비밀번호 변경'}
                </Button>
              </ButtonGroup>
            </Form>
          </ContentCard>
        );

      case 'activity':
        return (
          <ContentCard>
            <SectionTitle>활동 내역</SectionTitle>
            <StatCard>
              <h3>12</h3>
              <p>검색한 치과 수</p>
            </StatCard>
            <StatCard>
              <h3>5</h3>
              <p>즐겨찾기한 치과</p>
            </StatCard>
            <StatCard>
              <h3>28</h3>
              <p>총 검색 횟수</p>
            </StatCard>
          </ContentCard>
        );

      default:
        return null;
    }
  };

  return (
    <MyPageContainer>
      <MyPageContent>
        <PageHeader>
          <PageTitle>마이페이지</PageTitle>
          <PageSubtitle>
            안녕하세요, {user?.username}님! 계정 정보를 관리하고 활동 내역을 확인하세요.
          </PageSubtitle>
        </PageHeader>

        <ContentGrid>
          <Sidebar>
            <MenuCard>
              <MenuItem
                active={activeTab === 'profile'}
                onClick={() => setActiveTab('profile')}
              >
                프로필 정보
              </MenuItem>
              <MenuItem
                active={activeTab === 'password'}
                onClick={() => setActiveTab('password')}
              >
                비밀번호 변경
              </MenuItem>
              <MenuItem
                active={activeTab === 'activity'}
                onClick={() => setActiveTab('activity')}
              >
                활동 내역
              </MenuItem>
              <MenuItem
                active={activeTab === 'favorites'}
                onClick={() => setActiveTab('favorites')}
              >
                즐겨찾기
              </MenuItem>
              <MenuItem
                active={activeTab === 'notifications'}
                onClick={() => setActiveTab('notifications')}
              >
                알림 설정
              </MenuItem>
            </MenuCard>
          </Sidebar>

          <MainContent>
            {renderContent()}
          </MainContent>
        </ContentGrid>
      </MyPageContent>
    </MyPageContainer>
  );
}

export default MyPage;