import React from 'react';
import { Link } from 'react-router-dom';
import styled from 'styled-components';

const FooterContainer = styled.footer`
  background: ${props => props.theme.colors.gray900};
  color: ${props => props.theme.colors.gray300};
  padding: 48px 0 24px;
  margin-top: auto;
`;

const FooterContent = styled.div`
  max-width: 1400px;
  width: 100%;
  margin: 0 auto;
  padding: 0 24px;

  @media (max-width: 1200px) {
    max-width: 1200px;
  }

  @media (max-width: ${props => props.theme.breakpoints.tablet}) {
    padding: 0 16px;
  }
`;

const FooterTop = styled.div`
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr;
  gap: 48px;
  margin-bottom: 32px;

  @media (max-width: ${props => props.theme.breakpoints.desktop}) {
    grid-template-columns: 1fr 1fr;
    gap: 32px;
  }

  @media (max-width: ${props => props.theme.breakpoints.tablet}) {
    grid-template-columns: 1fr;
    gap: 24px;
  }
`;

const FooterSection = styled.div`
  h3 {
    color: ${props => props.theme.colors.white};
    font-size: ${props => props.theme.fonts.sizes.lg};
    font-weight: ${props => props.theme.fonts.weights.semibold};
    margin-bottom: 16px;
  }

  p {
    font-size: ${props => props.theme.fonts.sizes.sm};
    line-height: 1.6;
    margin-bottom: 8px;
  }
`;

const FooterLinks = styled.ul`
  li {
    margin-bottom: 8px;
  }

  a {
    color: ${props => props.theme.colors.gray400};
    font-size: ${props => props.theme.fonts.sizes.sm};
    transition: color ${props => props.theme.transitions.fast};

    &:hover {
      color: ${props => props.theme.colors.white};
    }
  }
`;

const CompanyInfo = styled.div`
  h3 {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 16px;
  }

  p {
    color: ${props => props.theme.colors.gray400};
    font-size: ${props => props.theme.fonts.sizes.sm};
    line-height: 1.6;
    margin-bottom: 16px;
  }
`;

const LogoIcon = styled.div`
  width: 24px;
  height: 24px;
  background: ${props => props.theme.colors.primary};
  border-radius: ${props => props.theme.borderRadius.md};
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;

  &::before {
    content: '';
    width: 12px;
    height: 12px;
    background: ${props => props.theme.colors.white};
    border-radius: 50%;
    position: absolute;
  }

  &::after {
    content: '';
    width: 6px;
    height: 6px;
    background: ${props => props.theme.colors.primary};
    border-radius: 50%;
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
  }
`;

const ContactInfo = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;

  div {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: ${props => props.theme.fonts.sizes.sm};
    color: ${props => props.theme.colors.gray400};
  }
`;

const ContactIcon = styled.div`
  width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;

  &.email::before {
    content: '';
    width: 14px;
    height: 10px;
    border: 1px solid currentColor;
    border-radius: 2px;
  }

  &.email::after {
    content: '';
    width: 8px;
    height: 1px;
    background: currentColor;
    position: absolute;
    top: 6px;
    left: 4px;
    transform: rotate(25deg);
    box-shadow: 2px 2px 0 currentColor;
  }

  &.phone::before {
    content: '';
    width: 10px;
    height: 14px;
    border: 1px solid currentColor;
    border-radius: 2px;
  }

  &.phone::after {
    content: '';
    width: 6px;
    height: 1px;
    background: currentColor;
    position: absolute;
    bottom: 3px;
  }
`;

const FooterBottom = styled.div`
  border-top: 1px solid ${props => props.theme.colors.gray700};
  padding-top: 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;

  @media (max-width: ${props => props.theme.breakpoints.tablet}) {
    flex-direction: column;
    text-align: center;
  }
`;

const Copyright = styled.p`
  font-size: ${props => props.theme.fonts.sizes.sm};
  color: ${props => props.theme.colors.gray500};
`;

const FooterBottomLinks = styled.div`
  display: flex;
  gap: 24px;

  a {
    font-size: ${props => props.theme.fonts.sizes.sm};
    color: ${props => props.theme.colors.gray400};
    transition: color ${props => props.theme.transitions.fast};

    &:hover {
      color: ${props => props.theme.colors.white};
    }
  }

  @media (max-width: ${props => props.theme.breakpoints.tablet}) {
    flex-wrap: wrap;
    justify-content: center;
    gap: 16px;
  }
`;

function Footer() {
  return (
    <FooterContainer>
      <FooterContent>
        <FooterTop>
          <CompanyInfo>
            <h3>
              <LogoIcon />
              치과AI
            </h3>
            <p>
              AI 기반 치과 추천 서비스로 합리적인 가격과 신뢰할 수 있는 치과를 찾아드립니다. 
              리뷰 분석을 통해 과잉진료 없는 양심적인 치과를 추천합니다.
            </p>
            <ContactInfo>
              <div>
                <ContactIcon className="email" />
                contact@dental-ai.com
              </div>
              <div>
                <ContactIcon className="phone" />
                1588-0000
              </div>
            </ContactInfo>
          </CompanyInfo>

          <FooterSection>
            <h3>서비스</h3>
            <FooterLinks>
              <li><Link to="/search">치과 찾기</Link></li>
              <li><Link to="/price-compare">가격 비교</Link></li>
              <li><Link to="/reviews">리뷰 분석</Link></li>
              <li><Link to="/recommendations">AI 추천</Link></li>
            </FooterLinks>
          </FooterSection>

          <FooterSection>
            <h3>고객지원</h3>
            <FooterLinks>
              <li><Link to="/help">도움말</Link></li>
              <li><Link to="/faq">자주 묻는 질문</Link></li>
              <li><Link to="/contact">문의하기</Link></li>
              <li><Link to="/feedback">피드백</Link></li>
            </FooterLinks>
          </FooterSection>

          <FooterSection>
            <h3>회사</h3>
            <FooterLinks>
              <li><Link to="/about">회사 소개</Link></li>
              <li><Link to="/news">보도자료</Link></li>
              <li><Link to="/careers">채용정보</Link></li>
              <li><Link to="/partners">파트너십</Link></li>
            </FooterLinks>
          </FooterSection>
        </FooterTop>

        <FooterBottom>
          <Copyright>
            © 2024 치과AI. All rights reserved.
          </Copyright>
          <FooterBottomLinks>
            <Link to="/privacy">개인정보처리방침</Link>
            <Link to="/terms">이용약관</Link>
            <Link to="/sitemap">사이트맵</Link>
          </FooterBottomLinks>
        </FooterBottom>
      </FooterContent>
    </FooterContainer>
  );
}

export default Footer;