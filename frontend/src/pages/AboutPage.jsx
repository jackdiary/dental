import React from 'react';
import styled from 'styled-components';

const PageContainer = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;

  @media (max-width: ${props => props.theme.breakpoints.tablet}) {
    padding: 30px 16px;
  }

  @media (max-width: ${props => props.theme.breakpoints.mobile}) {
    padding: 20px 12px;
  }
`;

const Hero = styled.section`
  text-align: center;
  margin-bottom: 60px;
  padding: 60px 0;
  background: linear-gradient(135deg, ${props => props.theme.colors.primary}10, ${props => props.theme.colors.secondary}10);
  border-radius: ${props => props.theme.borderRadius.xl};
`;

const Title = styled.h1`
  font-size: ${props => props.theme.fonts.sizes['4xl']};
  font-weight: ${props => props.theme.fonts.weights.bold};
  color: ${props => props.theme.colors.textPrimary};
  margin-bottom: 20px;

  @media (max-width: ${props => props.theme.breakpoints.tablet}) {
    font-size: ${props => props.theme.fonts.sizes['3xl']};
  }
`;

const Subtitle = styled.p`
  font-size: ${props => props.theme.fonts.sizes.xl};
  color: ${props => props.theme.colors.textSecondary};
  max-width: 600px;
  margin: 0 auto;
  line-height: 1.6;

  @media (max-width: ${props => props.theme.breakpoints.tablet}) {
    font-size: ${props => props.theme.fonts.sizes.lg};
  }
`;

const Section = styled.section`
  margin-bottom: 50px;
`;

const SectionTitle = styled.h2`
  font-size: ${props => props.theme.fonts.sizes['2xl']};
  font-weight: ${props => props.theme.fonts.weights.bold};
  color: ${props => props.theme.colors.textPrimary};
  margin-bottom: 20px;
  text-align: center;
`;

const FeatureGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 30px;
  margin-top: 40px;
`;

const FeatureCard = styled.div`
  background: ${props => props.theme.colors.white};
  border: 1px solid ${props => props.theme.colors.gray200};
  border-radius: ${props => props.theme.borderRadius.lg};
  padding: 30px;
  text-align: center;
  box-shadow: ${props => props.theme.shadows.sm};
  transition: transform ${props => props.theme.transitions.fast};

  &:hover {
    transform: translateY(-5px);
    box-shadow: ${props => props.theme.shadows.md};
  }
`;

const FeatureIcon = styled.div`
  width: 60px;
  height: 60px;
  background: ${props => props.theme.colors.primary};
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
  font-size: 24px;
  color: ${props => props.theme.colors.white};
`;

const FeatureTitle = styled.h3`
  font-size: ${props => props.theme.fonts.sizes.lg};
  font-weight: ${props => props.theme.fonts.weights.bold};
  color: ${props => props.theme.colors.textPrimary};
  margin-bottom: 15px;
`;

const FeatureDescription = styled.p`
  color: ${props => props.theme.colors.textSecondary};
  line-height: 1.6;
`;

const StatsSection = styled.section`
  background: ${props => props.theme.colors.gray50};
  border-radius: ${props => props.theme.borderRadius.xl};
  padding: 50px 30px;
  margin: 60px 0;
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 30px;
  text-align: center;
`;

const StatItem = styled.div``;

const StatNumber = styled.div`
  font-size: ${props => props.theme.fonts.sizes['3xl']};
  font-weight: ${props => props.theme.fonts.weights.bold};
  color: ${props => props.theme.colors.primary};
  margin-bottom: 10px;
`;

const StatLabel = styled.div`
  color: ${props => props.theme.colors.textSecondary};
  font-weight: ${props => props.theme.fonts.weights.medium};
`;

const ContactSection = styled.section`
  text-align: center;
  background: ${props => props.theme.colors.white};
  border: 1px solid ${props => props.theme.colors.gray200};
  border-radius: ${props => props.theme.borderRadius.xl};
  padding: 40px;
`;

const ContactButton = styled.button`
  background: ${props => props.theme.colors.primary};
  color: ${props => props.theme.colors.white};
  padding: 15px 30px;
  border-radius: ${props => props.theme.borderRadius.lg};
  font-size: ${props => props.theme.fonts.sizes.lg};
  font-weight: ${props => props.theme.fonts.weights.medium};
  margin-top: 20px;
  transition: background ${props => props.theme.transitions.fast};

  &:hover {
    background: ${props => props.theme.colors.primaryDark};
  }
`;

function AboutPage() {
  return (
    <PageContainer>
      <Hero>
        <Title>치과AI 서비스 소개</Title>
        <Subtitle>
          AI 기술로 더 나은 치과 선택을 도와드립니다. 
          정확한 정보와 개인 맞춤 추천으로 최적의 치과를 찾아보세요.
        </Subtitle>
      </Hero>

      <Section>
        <SectionTitle>주요 서비스</SectionTitle>
        <FeatureGrid>
          <FeatureCard>
            <FeatureIcon>🔍</FeatureIcon>
            <FeatureTitle>스마트 치과 검색</FeatureTitle>
            <FeatureDescription>
              위치, 진료과목, 가격대 등 다양한 조건으로 
              나에게 맞는 치과를 쉽고 빠르게 찾을 수 있습니다.
            </FeatureDescription>
          </FeatureCard>

          <FeatureCard>
            <FeatureIcon>💰</FeatureIcon>
            <FeatureTitle>가격 비교 서비스</FeatureTitle>
            <FeatureDescription>
              동일한 치료에 대한 여러 치과의 가격을 
              한눈에 비교하여 합리적인 선택을 할 수 있습니다.
            </FeatureDescription>
          </FeatureCard>

          <FeatureCard>
            <FeatureIcon>⭐</FeatureIcon>
            <FeatureTitle>AI 리뷰 분석</FeatureTitle>
            <FeatureDescription>
              실제 환자 리뷰를 AI가 분석하여 
              객관적이고 신뢰할 수 있는 평가 정보를 제공합니다.
            </FeatureDescription>
          </FeatureCard>

          <FeatureCard>
            <FeatureIcon>📱</FeatureIcon>
            <FeatureTitle>개인 맞춤 추천</FeatureTitle>
            <FeatureDescription>
              개인의 치료 이력과 선호도를 바탕으로 
              가장 적합한 치과를 추천해드립니다.
            </FeatureDescription>
          </FeatureCard>

          <FeatureCard>
            <FeatureIcon>🏥</FeatureIcon>
            <FeatureTitle>실시간 정보 업데이트</FeatureTitle>
            <FeatureDescription>
              치과 운영시간, 예약 가능 여부 등 
              실시간으로 업데이트되는 정확한 정보를 제공합니다.
            </FeatureDescription>
          </FeatureCard>

          <FeatureCard>
            <FeatureIcon>🔒</FeatureIcon>
            <FeatureTitle>안전한 개인정보 보호</FeatureTitle>
            <FeatureDescription>
              철저한 보안 시스템으로 개인정보를 안전하게 보호하며, 
              투명한 정보 처리 정책을 운영합니다.
            </FeatureDescription>
          </FeatureCard>
        </FeatureGrid>
      </Section>

      <StatsSection>
        <SectionTitle>치과AI 현황</SectionTitle>
        <StatsGrid>
          <StatItem>
            <StatNumber>15,000+</StatNumber>
            <StatLabel>등록된 치과</StatLabel>
          </StatItem>
          <StatItem>
            <StatNumber>50,000+</StatNumber>
            <StatLabel>누적 사용자</StatLabel>
          </StatItem>
          <StatItem>
            <StatNumber>200,000+</StatNumber>
            <StatLabel>리뷰 분석 건수</StatLabel>
          </StatItem>
          <StatItem>
            <StatNumber>98%</StatNumber>
            <StatLabel>사용자 만족도</StatLabel>
          </StatItem>
        </StatsGrid>
      </StatsSection>

      <Section>
        <SectionTitle>왜 치과AI를 선택해야 할까요?</SectionTitle>
        <FeatureGrid>
          <FeatureCard>
            <FeatureTitle>정확한 정보</FeatureTitle>
            <FeatureDescription>
              실시간으로 업데이트되는 정확한 치과 정보와 
              검증된 리뷰만을 제공합니다.
            </FeatureDescription>
          </FeatureCard>

          <FeatureCard>
            <FeatureTitle>시간 절약</FeatureTitle>
            <FeatureDescription>
              여러 치과를 일일이 찾아보는 시간을 절약하고 
              한 번에 최적의 선택을 할 수 있습니다.
            </FeatureDescription>
          </FeatureCard>

          <FeatureCard>
            <FeatureTitle>비용 절약</FeatureTitle>
            <FeatureDescription>
              가격 비교를 통해 동일한 치료를 
              더 합리적인 비용으로 받을 수 있습니다.
            </FeatureDescription>
          </FeatureCard>
        </FeatureGrid>
      </Section>

      <ContactSection>
        <SectionTitle>더 궁금한 점이 있으신가요?</SectionTitle>
        <p>치과AI 서비스에 대해 더 자세히 알고 싶으시거나 문의사항이 있으시면 언제든 연락해주세요.</p>
        <ContactButton>문의하기</ContactButton>
      </ContactSection>
    </PageContainer>
  );
}

export default AboutPage;