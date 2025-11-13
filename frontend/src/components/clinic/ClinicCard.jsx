import React from 'react';
import { Link } from 'react-router-dom';
import styled from 'styled-components';
import { getTreatmentName } from '../../constants/common';

const CardContainer = styled.div`
  background: ${props => props.theme.colors.white};
  border-radius: ${props => props.theme.borderRadius.xl};
  box-shadow: ${props => props.theme.shadows.base};
  overflow: hidden;
  transition: all ${props => props.theme.transitions.base};
  width: 100%;
  box-sizing: border-box;

  &:hover {
    transform: translateY(-2px);
    box-shadow: ${props => props.theme.shadows.lg};
  }
`;

const CardContent = styled.div`
  padding: 24px;
  
  @media (max-width: ${props => props.theme.breakpoints.tablet}) {
    padding: 20px;
  }
  
  @media (max-width: ${props => props.theme.breakpoints.mobile}) {
    padding: 16px;
  }
`;

const CardHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
  gap: 16px;
  flex-wrap: wrap;
  
  @media (max-width: ${props => props.theme.breakpoints.mobile}) {
    flex-direction: column;
    gap: 12px;
  }
`;

const ClinicInfo = styled.div`
  flex: 1;
  min-width: 0;
  
  @media (max-width: ${props => props.theme.breakpoints.mobile}) {
    width: 100%;
  }
`;

const ClinicName = styled(Link)`
  font-size: ${props => props.theme.fonts.sizes.xl};
  font-weight: ${props => props.theme.fonts.weights.semibold};
  color: ${props => props.theme.colors.textPrimary};
  text-decoration: none;
  display: block;
  margin-bottom: 8px;
  transition: color ${props => props.theme.transitions.fast};

  &:hover {
    color: ${props => props.theme.colors.primary};
  }
`;

const ClinicAddress = styled.p`
  color: ${props => props.theme.colors.textSecondary};
  font-size: ${props => props.theme.fonts.sizes.sm};
  margin-bottom: 4px;
`;

const ClinicDistrict = styled.span`
  background: ${props => props.theme.colors.gray100};
  color: ${props => props.theme.colors.textSecondary};
  padding: 4px 8px;
  border-radius: ${props => props.theme.borderRadius.sm};
  font-size: ${props => props.theme.fonts.sizes.xs};
  font-weight: ${props => props.theme.fonts.weights.medium};
`;

const ScoreSection = styled.div`
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 6px;
`;

const OverallScore = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
`;

const ScoreValue = styled.div`
  font-size: ${props => props.theme.fonts.sizes['2xl']};
  font-weight: ${props => props.theme.fonts.weights.bold};
  color: ${props => {
    const score = parseFloat(props.score);
    if (score >= 4.0) return props.theme.colors.success;
    if (score >= 3.0) return props.theme.colors.warning;
    return props.theme.colors.error;
  }};
`;

const ScoreLabel = styled.span`
  font-size: ${props => props.theme.fonts.sizes.sm};
  color: ${props => props.theme.colors.textSecondary};
`;

const SecondaryScore = styled.div`
  font-size: ${props => props.theme.fonts.sizes.sm};
  color: ${props => props.theme.colors.textSecondary};
`;

const ReviewCount = styled.div`
  font-size: ${props => props.theme.fonts.sizes.sm};
  color: ${props => props.theme.colors.textLight};
`;

const AspectScores = styled.div`
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin: 16px 0;

  @media (max-width: ${props => props.theme.breakpoints.mobile}) {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }
`;

const AspectScore = styled.div`
  text-align: center;
`;

const AspectLabel = styled.div`
  font-size: ${props => props.theme.fonts.sizes.xs};
  color: ${props => props.theme.colors.textSecondary};
  margin-bottom: 4px;
`;

const AspectValue = styled.div`
  font-size: ${props => props.theme.fonts.sizes.sm};
  font-weight: ${props => props.theme.fonts.weights.semibold};
  color: ${props => {
    const score = parseFloat(props.score);
    if (score >= 4.0) return props.theme.colors.success;
    if (score >= 3.0) return props.theme.colors.warning;
    return props.theme.colors.error;
  }};
`;

const Features = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 16px 0;
`;

const FeatureTag = styled.span`
  background: ${props => props.positive ? props.theme.colors.success : props.theme.colors.gray200};
  color: ${props => props.positive ? props.theme.colors.white : props.theme.colors.textSecondary};
  padding: 4px 8px;
  border-radius: ${props => props.theme.borderRadius.sm};
  font-size: ${props => props.theme.fonts.sizes.xs};
  font-weight: ${props => props.theme.fonts.weights.medium};
`;

const PriceInfo = styled.div`
  background: ${props => props.theme.colors.backgroundLight};
  padding: 12px;
  border-radius: ${props => props.theme.borderRadius.md};
  margin-top: 16px;
`;

const PriceTitle = styled.div`
  font-size: ${props => props.theme.fonts.sizes.sm};
  font-weight: ${props => props.theme.fonts.weights.medium};
  color: ${props => props.theme.colors.textPrimary};
  margin-bottom: 8px;
`;

const PriceList = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
`;

const PriceItem = styled.div`
  font-size: ${props => props.theme.fonts.sizes.xs};
  color: ${props => props.theme.colors.textSecondary};

  .treatment {
    font-weight: ${props => props.theme.fonts.weights.medium};
  }

  .price {
    color: ${props => props.theme.colors.primary};
    font-weight: ${props => props.theme.fonts.weights.semibold};
  }
`;

const CardFooter = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid ${props => props.theme.colors.gray200};
`;

const ViewButton = styled(Link)`
  background: ${props => props.theme.colors.primary};
  color: ${props => props.theme.colors.white};
  padding: 8px 16px;
  border-radius: ${props => props.theme.borderRadius.md};
  font-size: ${props => props.theme.fonts.sizes.sm};
  font-weight: ${props => props.theme.fonts.weights.medium};
  text-decoration: none;
  transition: background ${props => props.theme.transitions.fast};

  &:hover {
    background: ${props => props.theme.colors.primaryDark};
  }
`;

const Distance = styled.div`
  font-size: ${props => props.theme.fonts.sizes.sm};
  color: ${props => props.theme.colors.textLight};
`;

function ClinicCard({ clinic }) {
  const {
    id,
    name,
    address,
    district,
    total_reviews,
    average_rating,
    has_parking,
    night_service,
    weekend_service,
    // 실제 API에서 받아올 데이터들 (현재는 mock)
    comprehensive_score = 4.2,
    aspect_scores = {
      price: 4.1,
      skill: 4.3,
      kindness: 4.0,
      waiting: 3.8,
      facility: 4.2,
      overtreatment: 4.5
    },
    price_info
  } = clinic;

  const ratingValue = Number(average_rating ?? 0);
  const comprehensiveValue = Number(comprehensive_score ?? ratingValue);

  const buildPriceEntries = () => {
    if (!price_info) return [];
    return Object.entries(price_info)
      .map(([treatment, info]) => ({
        treatment: getTreatmentName(treatment),
        price: info?.average_price || 0,
      }))
      .filter(item => item.price > 0)
      .sort((a, b) => a.price - b.price)
      .slice(0, 3);
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('ko-KR').format(price) + '원';
  };

  const getAspectLabel = (key) => {
    const labels = {
      price: '가격',
      skill: '실력',
      kindness: '친절도',
      waiting: '대기시간',
      facility: '시설',
      overtreatment: '과잉진료'
    };
    return labels[key] || key;
  };

  return (
    <CardContainer>
      <CardContent>
        <CardHeader>
          <ClinicInfo>
            <ClinicName to={`/clinic/${id}`}>
              {name}
            </ClinicName>
            <ClinicAddress>{address}</ClinicAddress>
            <ClinicDistrict>{district}</ClinicDistrict>
          </ClinicInfo>

          <ScoreSection>
            <OverallScore>
              <ScoreValue score={ratingValue}>
                {ratingValue.toFixed(1)}
              </ScoreValue>
              <ScoreLabel>평균 평점</ScoreLabel>
            </OverallScore>
            <SecondaryScore>
              종합점수 {comprehensiveValue.toFixed(1)}
            </SecondaryScore>
            <ReviewCount>
              리뷰 {(total_reviews || 0).toLocaleString()}개
            </ReviewCount>
          </ScoreSection>
        </CardHeader>

        <AspectScores>
          {Object.entries(aspect_scores).map(([key, score]) => (
            <AspectScore key={key}>
              <AspectLabel>{getAspectLabel(key)}</AspectLabel>
              <AspectValue score={score}>
                {Number(score ?? 0).toFixed(1)}
              </AspectValue>
            </AspectScore>
          ))}
        </AspectScores>

        <Features>
          {has_parking && (
            <FeatureTag positive>주차가능</FeatureTag>
          )}
          {night_service && (
            <FeatureTag positive>야간진료</FeatureTag>
          )}
          {weekend_service && (
            <FeatureTag positive>주말진료</FeatureTag>
          )}
          {aspect_scores.overtreatment >= 4.0 && (
            <FeatureTag positive>과잉진료 없음</FeatureTag>
          )}
          {aspect_scores.price >= 4.0 && (
            <FeatureTag positive>합리적 가격</FeatureTag>
          )}
          {aspect_scores.skill >= 4.2 && (
            <FeatureTag positive>실력 우수</FeatureTag>
          )}
          {aspect_scores.kindness >= 4.0 && (
            <FeatureTag positive>친절함</FeatureTag>
          )}
          {aspect_scores.facility >= 4.0 && (
            <FeatureTag positive>시설 좋음</FeatureTag>
          )}
          {aspect_scores.waiting <= 3.5 && (
            <FeatureTag positive>대기시간 짧음</FeatureTag>
          )}
        </Features>

        {(() => {
          const priceEntries = buildPriceEntries();
          return priceEntries.length > 0 && (
            <PriceInfo>
              <PriceTitle>주요 치료 평균 가격</PriceTitle>
              <PriceList>
                {priceEntries.map((item, index) => (
                  <PriceItem key={index}>
                    <span className="treatment">{item.treatment}</span>
                    {' '}
                    <span className="price">{formatPrice(item.price)}</span>
                  </PriceItem>
                ))}
              </PriceList>
            </PriceInfo>
          );
        })()}

        <CardFooter>
          <Distance>
            {/* 거리 정보가 있다면 표시 */}
            {clinic.distance && `${clinic.distance}km`}
          </Distance>
          <ViewButton to={`/clinic/${id}`}>
            상세보기
          </ViewButton>
        </CardFooter>
      </CardContent>
    </CardContainer>
  );
}

export default ClinicCard;
