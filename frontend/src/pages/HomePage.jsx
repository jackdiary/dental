import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import backgroundImage from '../assets/1920.jpg';
import { SEOUL_DISTRICTS, TREATMENT_TYPES } from '../constants/common';

const HomeContainer = styled.div`
  min-height: calc(100vh - 140px);
`;

const HeroSection = styled.section`
  background: 
    linear-gradient(135deg, rgba(44, 90, 160, 0.2) 0%, rgba(30, 63, 115, 0.8) 100%),
    url(${backgroundImage});
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  color: ${props => props.theme.colors.white};
  padding: 80px 0;
  text-align: center;

  @media (max-width: ${props => props.theme.breakpoints.tablet}) {
    padding: 60px 0;
  }
`;

const HeroContent = styled.div`
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

const HeroTitle = styled.h1`
  font-size: ${props => props.theme.fonts.sizes['5xl']};
  font-weight: ${props => props.theme.fonts.weights.bold};
  margin-bottom: 24px;
  line-height: 1.2;

  @media (max-width: ${props => props.theme.breakpoints.tablet}) {
    font-size: ${props => props.theme.fonts.sizes['3xl']};
  }

  @media (max-width: ${props => props.theme.breakpoints.mobile}) {
    font-size: ${props => props.theme.fonts.sizes['2xl']};
  }
`;

const HeroSubtitle = styled.p`
  font-size: ${props => props.theme.fonts.sizes.xl};
  margin-bottom: 48px;
  opacity: 0.9;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;

  @media (max-width: ${props => props.theme.breakpoints.tablet}) {
    font-size: ${props => props.theme.fonts.sizes.lg};
    margin-bottom: 32px;
  }
`;

const SearchContainer = styled.div`
  background: ${props => props.theme.colors.white};
  border-radius: ${props => props.theme.borderRadius['2xl']};
  padding: 32px;
  box-shadow: ${props => props.theme.shadows.xl};
  max-width: 700px;
  width: 100%;
  margin: 0 auto;
  box-sizing: border-box;

  @media (max-width: ${props => props.theme.breakpoints.tablet}) {
    padding: 24px;
    margin: 0 16px;
    max-width: calc(100% - 32px);
  }
`;

const SearchForm = styled.form`
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

const SearchInputGroup = styled.div`
  display: flex;
  gap: 12px;
  width: 100%;

  @media (max-width: 768px) {
    flex-direction: column;
    gap: 16px;
  }
`;

const SearchInput = styled.input`
  flex: 1;
  padding: 16px 20px;
  border: 2px solid ${props => props.theme.colors.gray200};
  border-radius: ${props => props.theme.borderRadius.lg};
  font-size: ${props => props.theme.fonts.sizes.base};
  color: ${props => props.theme.colors.textPrimary};
  transition: border-color ${props => props.theme.transitions.fast};

  &:focus {
    border-color: ${props => props.theme.colors.primary};
  }

  &::placeholder {
    color: ${props => props.theme.colors.textLight};
  }
`;

const SearchSelect = styled.select`
  flex: 1;
  padding: 16px 20px;
  border: 2px solid ${props => props.theme.colors.gray200};
  border-radius: ${props => props.theme.borderRadius.lg};
  font-size: ${props => props.theme.fonts.sizes.base};
  color: ${props => props.theme.colors.textPrimary};
  background: ${props => props.theme.colors.white};
  min-width: 160px;
  transition: border-color ${props => props.theme.transitions.fast};
  box-sizing: border-box;

  &:focus {
    border-color: ${props => props.theme.colors.primary};
  }

  @media (max-width: 768px) {
    min-width: 100%;
    width: 100%;
  }
`;

const SearchButton = styled.button`
  background: ${props => props.theme.colors.primary};
  color: ${props => props.theme.colors.white};
  padding: 16px 32px;
  border-radius: ${props => props.theme.borderRadius.lg};
  font-size: ${props => props.theme.fonts.sizes.base};
  font-weight: ${props => props.theme.fonts.weights.semibold};
  transition: background ${props => props.theme.transitions.fast};
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  min-height: 56px;
  white-space: nowrap;

  &:hover {
    background: ${props => props.theme.colors.primaryDark};
  }

  &:disabled {
    background: ${props => props.theme.colors.gray400};
    cursor: not-allowed;
  }
`;

const SearchIcon = styled.div`
  width: 20px;
  height: 20px;
  position: relative;

  &::before {
    content: '';
    position: absolute;
    width: 14px;
    height: 14px;
    border: 2px solid currentColor;
    border-radius: 50%;
    top: 0;
    left: 0;
  }

  &::after {
    content: '';
    position: absolute;
    width: 2px;
    height: 8px;
    background: currentColor;
    transform: rotate(45deg);
    bottom: 0;
    right: 0;
  }
`;

const FeaturesSection = styled.section`
  padding: 80px 0;
  background: ${props => props.theme.colors.backgroundGray};

  @media (max-width: ${props => props.theme.breakpoints.tablet}) {
    padding: 60px 0;
  }
`;

const FeaturesContainer = styled.div`
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

const SectionTitle = styled.h2`
  font-size: ${props => props.theme.fonts.sizes['3xl']};
  font-weight: ${props => props.theme.fonts.weights.bold};
  text-align: center;
  margin-bottom: 16px;
  color: ${props => props.theme.colors.textPrimary};

  @media (max-width: ${props => props.theme.breakpoints.tablet}) {
    font-size: ${props => props.theme.fonts.sizes['2xl']};
  }
`;

const SectionSubtitle = styled.p`
  font-size: ${props => props.theme.fonts.sizes.lg};
  text-align: center;
  margin-bottom: 64px;
  color: ${props => props.theme.colors.textSecondary};
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;

  @media (max-width: ${props => props.theme.breakpoints.tablet}) {
    margin-bottom: 48px;
  }
`;

const FeaturesGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 32px;
  width: 100%;

  @media (max-width: 1024px) {
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 24px;
  }

  @media (max-width: ${props => props.theme.breakpoints.tablet}) {
    grid-template-columns: 1fr;
    gap: 20px;
  }
`;

const FeatureCard = styled.div`
  background: ${props => props.theme.colors.white};
  padding: 32px;
  border-radius: ${props => props.theme.borderRadius.xl};
  box-shadow: ${props => props.theme.shadows.base};
  text-align: center;
  transition: transform ${props => props.theme.transitions.base}, box-shadow ${props => props.theme.transitions.base};
  width: 100%;
  box-sizing: border-box;

  &:hover {
    transform: translateY(-4px);
    box-shadow: ${props => props.theme.shadows.lg};
  }

  @media (max-width: ${props => props.theme.breakpoints.tablet}) {
    padding: 24px;
  }

  @media (max-width: 480px) {
    padding: 20px;
  }
`;

const FeatureIcon = styled.div`
  width: 64px;
  height: 64px;
  background: ${props => props.color || props.theme.colors.primary};
  border-radius: ${props => props.theme.borderRadius.xl};
  margin: 0 auto 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;

  &.ai::before {
    content: '';
    width: 32px;
    height: 32px;
    border: 3px solid ${props => props.theme.colors.white};
    border-radius: 50%;
  }

  &.ai::after {
    content: '';
    width: 16px;
    height: 16px;
    background: ${props => props.theme.colors.white};
    border-radius: 50%;
    position: absolute;
  }

  &.price::before {
    content: '';
    width: 24px;
    height: 32px;
    border: 3px solid ${props => props.theme.colors.white};
    border-radius: 4px;
  }

  &.price::after {
    content: '';
    width: 12px;
    height: 2px;
    background: ${props => props.theme.colors.white};
    position: absolute;
    box-shadow: 0 6px 0 ${props => props.theme.colors.white}, 0 12px 0 ${props => props.theme.colors.white};
  }

  &.review::before {
    content: '';
    width: 32px;
    height: 24px;
    border: 3px solid ${props => props.theme.colors.white};
    border-radius: 4px;
  }

  &.review::after {
    content: '';
    width: 16px;
    height: 2px;
    background: ${props => props.theme.colors.white};
    position: absolute;
    box-shadow: 0 4px 0 ${props => props.theme.colors.white}, 0 8px 0 ${props => props.theme.colors.white};
  }
`;

const FeatureTitle = styled.h3`
  font-size: ${props => props.theme.fonts.sizes.xl};
  font-weight: ${props => props.theme.fonts.weights.semibold};
  margin-bottom: 16px;
  color: ${props => props.theme.colors.textPrimary};
`;

const FeatureDescription = styled.p`
  font-size: ${props => props.theme.fonts.sizes.base};
  color: ${props => props.theme.colors.textSecondary};
  line-height: 1.6;
`;

const StatsSection = styled.section`
  padding: 80px 0;
  background: ${props => props.theme.colors.white};

  @media (max-width: ${props => props.theme.breakpoints.tablet}) {
    padding: 60px 0;
  }
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 48px;
  text-align: center;
  width: 100%;

  @media (max-width: 1024px) {
    grid-template-columns: repeat(2, 1fr);
    gap: 32px;
  }

  @media (max-width: ${props => props.theme.breakpoints.tablet}) {
    grid-template-columns: repeat(2, 1fr);
    gap: 24px;
  }

  @media (max-width: 480px) {
    grid-template-columns: 1fr;
    gap: 20px;
  }
`;

const StatItem = styled.div`
  h3 {
    font-size: ${props => props.theme.fonts.sizes['4xl']};
    font-weight: ${props => props.theme.fonts.weights.bold};
    color: ${props => props.theme.colors.primary};
    margin-bottom: 8px;

    @media (max-width: ${props => props.theme.breakpoints.tablet}) {
      font-size: ${props => props.theme.fonts.sizes['3xl']};
    }
  }

  p {
    font-size: ${props => props.theme.fonts.sizes.lg};
    color: ${props => props.theme.colors.textSecondary};
  }
`;

function HomePage() {
  const [searchData, setSearchData] = useState({
    district: '',
    treatment: '',
  });
  const navigate = useNavigate();

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setSearchData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSearch = (e) => {
    e.preventDefault();
    const searchParams = new URLSearchParams();

    if (searchData.district) {
      searchParams.append('district', searchData.district);
    }
    if (searchData.treatment) {
      searchParams.append('treatment', searchData.treatment);
    }

    navigate(`/search?${searchParams.toString()}`);
  };

  return (
    <HomeContainer>
      <HeroSection>
        <HeroContent>
          <HeroTitle>AI가 추천하는 신뢰할 수 있는 치과</HeroTitle>
          <HeroSubtitle>
            리뷰 분석을 통해 가격이 합리적이고 과잉진료 없는 치과를 찾아드립니다
          </HeroSubtitle>

          <SearchContainer>
            <SearchForm onSubmit={handleSearch}>
              <SearchInputGroup>
                <SearchSelect
                  name="district"
                  value={searchData.district}
                  onChange={handleInputChange}
                >
                  <option value="">지역 선택</option>
                  {SEOUL_DISTRICTS.map(district => (
                    <option key={district} value={district}>{district}</option>
                  ))}
                </SearchSelect>

                <SearchSelect
                  name="treatment"
                  value={searchData.treatment}
                  onChange={handleInputChange}
                >
                  <option value="">치료 종류</option>
                  {TREATMENT_TYPES.map(treatment => (
                    <option key={treatment} value={treatment}>{treatment}</option>
                  ))}
                </SearchSelect>
              </SearchInputGroup>

              <SearchButton type="submit">
                <SearchIcon />
                치과 찾기
              </SearchButton>
            </SearchForm>
          </SearchContainer>
        </HeroContent>
      </HeroSection>

      <FeaturesSection>
        <FeaturesContainer>
          <SectionTitle>왜 치과AI를 선택해야 할까요?</SectionTitle>
          <SectionSubtitle>
            AI 기반 분석으로 더 정확하고 신뢰할 수 있는 치과 정보를 제공합니다
          </SectionSubtitle>

          <FeaturesGrid>
            <FeatureCard>
              <FeatureIcon className="ai" color="#2c5aa0" />
              <FeatureTitle>AI 기반 분석</FeatureTitle>
              <FeatureDescription>
                수천 개의 리뷰를 AI가 분석하여 객관적이고 정확한 평가를 제공합니다.
                감성 분석을 통해 숨겨진 의미까지 파악합니다.
              </FeatureDescription>
            </FeatureCard>

            <FeatureCard>
              <FeatureIcon className="price" color="#00c851" />
              <FeatureTitle>투명한 가격 비교</FeatureTitle>
              <FeatureDescription>
                지역별, 치료별 가격을 투명하게 비교할 수 있습니다.
                합리적인 가격의 치과를 쉽게 찾아보세요.
              </FeatureDescription>
            </FeatureCard>

            <FeatureCard>
              <FeatureIcon className="review" color="#ff6b35" />
              <FeatureTitle>과잉진료 방지</FeatureTitle>
              <FeatureDescription>
                리뷰 분석을 통해 과잉진료 위험도를 평가합니다.
                양심적이고 신뢰할 수 있는 치과를 추천받으세요.
              </FeatureDescription>
            </FeatureCard>
          </FeaturesGrid>
        </FeaturesContainer>
      </FeaturesSection>

      <StatsSection>
        <FeaturesContainer>
          <SectionTitle>치과AI 현황</SectionTitle>
          <SectionSubtitle>
            많은 사용자들이 치과AI를 통해 만족스러운 치과를 찾고 있습니다
          </SectionSubtitle>

          <StatsGrid>
            <StatItem>
              <h3>15,000+</h3>
              <p>등록된 치과</p>
            </StatItem>
            <StatItem>
              <h3>50,000+</h3>
              <p>누적 사용자</p>
            </StatItem>
            <StatItem>
              <h3>200,000+</h3>
              <p>분석된 리뷰</p>
            </StatItem>
            <StatItem>
              <h3>98%</h3>
              <p>사용자 만족도</p>
            </StatItem>
          </StatsGrid>
        </FeaturesContainer>
      </StatsSection>
    </HomeContainer>
  );
}

export default HomePage;