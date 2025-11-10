import React, { useState, useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { AuthContext } from '../../contexts/AuthContext';

const HeaderContainer = styled.header`
  background: ${props => props.theme.colors.white};
  border-bottom: 1px solid ${props => props.theme.colors.gray200};
  position: sticky;
  top: 0;
  z-index: ${props => props.theme.zIndex.sticky};
  box-shadow: ${props => props.theme.shadows.sm};
`;

const HeaderContent = styled.div`
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 70px;
  width: 100%;
  box-sizing: border-box;

  @media (max-width: ${props => props.theme.breakpoints.desktop}) {
    max-width: 100%;
  }

  @media (max-width: ${props => props.theme.breakpoints.tablet}) {
    padding: 0 16px;
    height: 60px;
  }
  
  @media (max-width: ${props => props.theme.breakpoints.mobile}) {
    padding: 0 12px;
  }
`;

const Logo = styled(Link)`
  font-size: ${props => props.theme.fonts.sizes['2xl']};
  font-weight: ${props => props.theme.fonts.weights.bold};
  color: ${props => props.theme.colors.primary};
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 8px;

  &:hover {
    color: ${props => props.theme.colors.primaryDark};
  }

  @media (max-width: ${props => props.theme.breakpoints.tablet}) {
    font-size: ${props => props.theme.fonts.sizes.xl};
  }
`;

const LogoIcon = styled.div`
  width: 32px;
  height: 32px;
  background: ${props => props.theme.colors.primary};
  border-radius: ${props => props.theme.borderRadius.lg};
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;

  &::before {
    content: '';
    width: 16px;
    height: 16px;
    background: ${props => props.theme.colors.white};
    border-radius: 50%;
    position: absolute;
  }

  &::after {
    content: '';
    width: 8px;
    height: 8px;
    background: ${props => props.theme.colors.primary};
    border-radius: 50%;
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
  }

  @media (max-width: ${props => props.theme.breakpoints.tablet}) {
    width: 28px;
    height: 28px;

    &::before {
      width: 14px;
      height: 14px;
    }

    &::after {
      width: 6px;
      height: 6px;
    }
  }
`;

const Nav = styled.nav`
  display: flex;
  align-items: center;
  gap: 32px;

  @media (max-width: ${props => props.theme.breakpoints.tablet}) {
    display: none;
  }
`;

const NavLink = styled(Link)`
  color: ${props => props.theme.colors.textPrimary};
  font-weight: ${props => props.theme.fonts.weights.medium};
  font-size: ${props => props.theme.fonts.sizes.base};
  transition: color ${props => props.theme.transitions.fast};
  position: relative;

  &:hover {
    color: ${props => props.theme.colors.primary};
  }

  &.active {
    color: ${props => props.theme.colors.primary};

    &::after {
      content: '';
      position: absolute;
      bottom: -8px;
      left: 0;
      right: 0;
      height: 2px;
      background: ${props => props.theme.colors.primary};
      border-radius: 1px;
    }
  }
`;

const UserActions = styled.div`
  display: flex;
  align-items: center;
  gap: 16px;
`;

const LoginButton = styled(Link)`
  color: ${props => props.theme.colors.textSecondary};
  font-weight: ${props => props.theme.fonts.weights.medium};
  font-size: ${props => props.theme.fonts.sizes.sm};
  transition: color ${props => props.theme.transitions.fast};

  &:hover {
    color: ${props => props.theme.colors.primary};
  }
`;

const RegisterButton = styled(Link)`
  background: ${props => props.theme.colors.primary};
  color: ${props => props.theme.colors.white};
  padding: 8px 16px;
  border-radius: ${props => props.theme.borderRadius.md};
  font-weight: ${props => props.theme.fonts.weights.medium};
  font-size: ${props => props.theme.fonts.sizes.sm};
  transition: background ${props => props.theme.transitions.fast};

  &:hover {
    background: ${props => props.theme.colors.primaryDark};
  }
`;

const UserMenu = styled.div`
  position: relative;
`;

const UserButton = styled.button`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: ${props => props.theme.borderRadius.md};
  background: ${props => props.theme.colors.gray100};
  color: ${props => props.theme.colors.textPrimary};
  font-weight: ${props => props.theme.fonts.weights.medium};
  font-size: ${props => props.theme.fonts.sizes.sm};
  transition: background ${props => props.theme.transitions.fast};

  &:hover {
    background: ${props => props.theme.colors.gray200};
  }
`;

const UserAvatar = styled.div`
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: ${props => props.theme.colors.primary};
  display: flex;
  align-items: center;
  justify-content: center;
  color: ${props => props.theme.colors.white};
  font-size: ${props => props.theme.fonts.sizes.xs};
  font-weight: ${props => props.theme.fonts.weights.bold};
`;

const DropdownMenu = styled.div`
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 8px;
  background: ${props => props.theme.colors.white};
  border: 1px solid ${props => props.theme.colors.gray200};
  border-radius: ${props => props.theme.borderRadius.lg};
  box-shadow: ${props => props.theme.shadows.lg};
  min-width: 160px;
  overflow: hidden;
  z-index: ${props => props.theme.zIndex.dropdown};
  opacity: ${props => props.isOpen ? 1 : 0};
  visibility: ${props => props.isOpen ? 'visible' : 'hidden'};
  transform: translateY(${props => props.isOpen ? 0 : '-10px'});
  transition: all ${props => props.theme.transitions.fast};
`;

const DropdownItem = styled(Link)`
  display: block;
  padding: 12px 16px;
  color: ${props => props.theme.colors.textPrimary};
  font-size: ${props => props.theme.fonts.sizes.sm};
  transition: background ${props => props.theme.transitions.fast};

  &:hover {
    background: ${props => props.theme.colors.gray50};
  }
`;

const LogoutButton = styled.button`
  width: 100%;
  text-align: left;
  padding: 12px 16px;
  color: ${props => props.theme.colors.textPrimary};
  font-size: ${props => props.theme.fonts.sizes.sm};
  transition: background ${props => props.theme.transitions.fast};

  &:hover {
    background: ${props => props.theme.colors.gray50};
  }
`;

const MobileMenuButton = styled.button`
  display: none;
  flex-direction: column;
  gap: 4px;
  padding: 8px;

  @media (max-width: ${props => props.theme.breakpoints.tablet}) {
    display: flex;
  }
`;

const MenuLine = styled.div`
  width: 20px;
  height: 2px;
  background: ${props => props.theme.colors.textPrimary};
  border-radius: 1px;
  transition: all ${props => props.theme.transitions.fast};
`;

function Header() {
  const { user, logout } = useContext(AuthContext);
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    setIsUserMenuOpen(false);
    navigate('/');
  };

  const getUserInitial = (user) => {
    if (user?.username) {
      return user.username.charAt(0).toUpperCase();
    }
    return 'U';
  };

  return (
    <HeaderContainer>
      <HeaderContent>
        <Logo to="/">
          <LogoIcon />
          치과AI
        </Logo>

        <Nav>
          <NavLink to="/search">치과 찾기</NavLink>
          <NavLink to="/price-compare">가격 비교</NavLink>
          <NavLink to="/reviews">리뷰 분석</NavLink>
          <NavLink to="/about">서비스 소개</NavLink>
        </Nav>

        <UserActions>
          {user ? (
            <UserMenu>
              <UserButton 
                onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
                onBlur={() => setTimeout(() => setIsUserMenuOpen(false), 150)}
              >
                <UserAvatar>{getUserInitial(user)}</UserAvatar>
                {user.username}
              </UserButton>
              <DropdownMenu isOpen={isUserMenuOpen}>
                <DropdownItem to="/mypage">마이페이지</DropdownItem>
                <DropdownItem to="/favorites">즐겨찾기</DropdownItem>
                <DropdownItem to="/history">검색 기록</DropdownItem>
                <LogoutButton onClick={handleLogout}>로그아웃</LogoutButton>
              </DropdownMenu>
            </UserMenu>
          ) : (
            <>
              <LoginButton to="/login">로그인</LoginButton>
              <RegisterButton to="/register">회원가입</RegisterButton>
            </>
          )}

          <MobileMenuButton onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}>
            <MenuLine />
            <MenuLine />
            <MenuLine />
          </MobileMenuButton>
        </UserActions>
      </HeaderContent>
    </HeaderContainer>
  );
}

export default Header;