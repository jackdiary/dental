import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import styled from 'styled-components';
import { clinicAPI, reviewAPI } from '../services/api';
import { getTreatmentName } from '../constants/common';
import LoadingSpinner from '../components/common/LoadingSpinner';

const DetailContainer = styled.div`
  min-height: calc(100vh - 140px);
  background: ${props => props.theme.colors.backgroundGray};
`;

const DetailContent = styled.div`
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

const ClinicHeader = styled.div`
  background: ${props => props.theme.colors.white};
  border-radius: ${props => props.theme.borderRadius.xl};
  box-shadow: ${props => props.theme.shadows.base};
  padding: 32px;
  margin-bottom: 24px;

  @media (max-width: ${props => props.theme.breakpoints.tablet}) {
    padding: 24px;
  }
`;

const ClinicTitle = styled.h1`
  font-size: ${props => props.theme.fonts.sizes['3xl']};
  font-weight: ${props => props.theme.fonts.weights.bold};
  color: ${props => props.theme.colors.textPrimary};
  margin-bottom: 16px;

  @media (max-width: ${props => props.theme.breakpoints.tablet}) {
    font-size: ${props => props.theme.fonts.sizes['2xl']};
  }
`;

const ClinicInfo = styled.div`
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 32px;
  align-items: start;

  @media (max-width: ${props => props.theme.breakpoints.tablet}) {
    grid-template-columns: 1fr;
    gap: 24px;
  }
`;

const InfoSection = styled.div``;

const InfoItem = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
  font-size: ${props => props.theme.fonts.sizes.base};
  color: ${props => props.theme.colors.textSecondary};

  &:last-child {
    margin-bottom: 0;
  }
`;

const InfoIcon = styled.div`
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: ${props => props.theme.colors.primary};
  position: relative;

  &.location::before {
    content: '';
    width: 12px;
    height: 16px;
    border: 2px solid currentColor;
    border-radius: 6px 6px 6px 0;
    transform: rotate(-45deg);
  }

  &.location::after {
    content: '';
    width: 4px;
    height: 4px;
    background: currentColor;
    border-radius: 50%;
    position: absolute;
    top: 6px;
    left: 8px;
  }

  &.phone::before {
    content: '';
    width: 12px;
    height: 16px;
    border: 2px solid currentColor;
    border-radius: 3px;
  }

  &.phone::after {
    content: '';
    width: 6px;
    height: 1px;
    background: currentColor;
    position: absolute;
    bottom: 4px;
  }

  &.time::before {
    content: '';
    width: 16px;
    height: 16px;
    border: 2px solid currentColor;
    border-radius: 50%;
  }

  &.time::after {
    content: '';
    width: 6px;
    height: 1px;
    background: currentColor;
    position: absolute;
    box-shadow: 0 -4px 0 currentColor;
  }
`;

const ScoreSection = styled.div`
  text-align: center;
`;

const OverallScore = styled.div`
  background: ${props => props.theme.colors.primary};
  color: ${props => props.theme.colors.white};
  padding: 24px;
  border-radius: ${props => props.theme.borderRadius.xl};
  margin-bottom: 16px;
`;

const ScoreValue = styled.div`
  font-size: ${props => props.theme.fonts.sizes['4xl']};
  font-weight: ${props => props.theme.fonts.weights.bold};
  margin-bottom: 8px;
`;

const ScoreLabel = styled.div`
  font-size: ${props => props.theme.fonts.sizes.base};
  opacity: 0.9;
`;

const ReviewCount = styled.div`
  color: ${props => props.theme.colors.textSecondary};
  font-size: ${props => props.theme.fonts.sizes.sm};
`;

const ContentGrid = styled.div`
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;

  @media (max-width: ${props => props.theme.breakpoints.desktop}) {
    grid-template-columns: 1fr;
  }
`;

const MainContent = styled.div``;

const Sidebar = styled.div``;

const Section = styled.div`
  background: ${props => props.theme.colors.white};
  border-radius: ${props => props.theme.borderRadius.xl};
  box-shadow: ${props => props.theme.shadows.base};
  padding: 24px;
  margin-bottom: 24px;

  &:last-child {
    margin-bottom: 0;
  }
`;

const SectionTitle = styled.h2`
  font-size: ${props => props.theme.fonts.sizes.xl};
  font-weight: ${props => props.theme.fonts.weights.semibold};
  color: ${props => props.theme.colors.textPrimary};
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid ${props => props.theme.colors.gray200};
`;

const AspectScores = styled.div`
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;

  @media (max-width: ${props => props.theme.breakpoints.mobile}) {
    grid-template-columns: 1fr;
  }
`;

const AspectItem = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: ${props => props.theme.colors.backgroundLight};
  border-radius: ${props => props.theme.borderRadius.lg};
`;

const AspectLabel = styled.div`
  font-size: ${props => props.theme.fonts.sizes.base};
  color: ${props => props.theme.colors.textPrimary};
  font-weight: ${props => props.theme.fonts.weights.medium};
`;

const AspectScore = styled.div`
  font-size: ${props => props.theme.fonts.sizes.lg};
  font-weight: ${props => props.theme.fonts.weights.bold};
  color: ${props => {
    const score = parseFloat(props.score);
    if (score >= 4.0) return props.theme.colors.success;
    if (score >= 3.0) return props.theme.colors.warning;
    return props.theme.colors.error;
  }};
`;

const FeaturesList = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
`;

const FeatureTag = styled.div`
  background: ${props => props.positive ? props.theme.colors.success : props.theme.colors.gray200};
  color: ${props => props.positive ? props.theme.colors.white : props.theme.colors.textSecondary};
  padding: 8px 16px;
  border-radius: ${props => props.theme.borderRadius.md};
  font-size: ${props => props.theme.fonts.sizes.sm};
  font-weight: ${props => props.theme.fonts.weights.medium};
`;

const KeywordsSection = styled.div`
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid ${props => props.theme.colors.gray200};
`;

const KeywordsTitle = styled.h3`
  font-size: ${props => props.theme.fonts.sizes.lg};
  font-weight: ${props => props.theme.fonts.weights.semibold};
  color: ${props => props.theme.colors.textPrimary};
  margin-bottom: 16px;
`;

const KeywordTags = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
`;

const KeywordTag = styled.span`
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  background: ${props => props.theme.colors.primary}15;
  color: ${props => props.theme.colors.primary};
  border-radius: 20px;
  font-size: ${props => props.theme.fonts.sizes.sm};
  font-weight: ${props => props.theme.fonts.weights.medium};
  border: 1px solid ${props => props.theme.colors.primary}30;
`;

const KeywordCount = styled.span`
  background: ${props => props.theme.colors.primary};
  color: white;
  border-radius: 10px;
  padding: 2px 6px;
  font-size: ${props => props.theme.fonts.sizes.xs};
  font-weight: ${props => props.theme.fonts.weights.bold};
  min-width: 18px;
  text-align: center;
`;

const PriceTable = styled.div`
  overflow-x: auto;
`;

const Table = styled.table`
  width: 100%;
  border-collapse: collapse;

  th, td {
    padding: 12px 16px;
    text-align: left;
    border-bottom: 1px solid ${props => props.theme.colors.gray200};
  }

  th {
    background: ${props => props.theme.colors.backgroundLight};
    font-weight: ${props => props.theme.fonts.weights.semibold};
    color: ${props => props.theme.colors.textPrimary};
    font-size: ${props => props.theme.fonts.sizes.sm};
  }

  td {
    font-size: ${props => props.theme.fonts.sizes.sm};
    color: ${props => props.theme.colors.textSecondary};
  }

  .price {
    font-weight: ${props => props.theme.fonts.weights.semibold};
    color: ${props => props.theme.colors.primary};
  }
`;

const ReviewsList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

const ReviewItem = styled.div`
  padding: 20px;
  background: ${props => props.theme.colors.backgroundLight};
  border-radius: ${props => props.theme.borderRadius.lg};
`;

const ReviewHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
`;

const ReviewRating = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: ${props => props.theme.fonts.sizes.sm};
  color: ${props => props.theme.colors.textSecondary};
`;

const ReviewDate = styled.div`
  font-size: ${props => props.theme.fonts.sizes.xs};
  color: ${props => props.theme.colors.textLight};
`;

const ReviewText = styled.p`
  font-size: ${props => props.theme.fonts.sizes.base};
  color: ${props => props.theme.colors.textPrimary};
  line-height: 1.6;
`;

const LoadMoreButton = styled.button`
  width: 100%;
  padding: 12px 24px;
  background: ${props => props.theme.colors.gray100};
  color: ${props => props.theme.colors.textPrimary};
  border-radius: ${props => props.theme.borderRadius.md};
  font-size: ${props => props.theme.fonts.sizes.sm};
  font-weight: ${props => props.theme.fonts.weights.medium};
  transition: background ${props => props.theme.transitions.fast};
  margin-top: 16px;

  &:hover {
    background: ${props => props.theme.colors.gray200};
  }
`;

function ClinicDetailPage() {
  const { id } = useParams();
  const [clinic, setClinic] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [topKeywords, setTopKeywords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [reviewsLoading, setReviewsLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchClinicDetail();
    fetchReviews();
    fetchTopKeywords();
  }, [id]);

  const fetchClinicDetail = async () => {
    try {
      setLoading(true);
      const response = await clinicAPI.getDetail(id);
      setClinic(response.data);
    } catch (err) {
      console.error('Failed to fetch clinic detail:', err);
      setError('치과 정보를 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const fetchReviews = async () => {
    try {
      setReviewsLoading(true);
      console.log(`Fetching reviews for clinic ID: ${id}`);
      
      const response = await reviewAPI.getClinicReviews(id);
      console.log('Reviews API response:', response.data);
      
      if (response.data && response.data.reviews) {
        setReviews(response.data.reviews);
        console.log(`Loaded ${response.data.reviews.length} reviews`);
      } else {
        console.log('No reviews data in response');
        setReviews([]);
      }
    } catch (err) {
      console.error('Failed to fetch reviews:', err);
      console.error('Error details:', err.response?.data);
      setReviews([]);
    } finally {
      setReviewsLoading(false);
    }
  };

  const fetchTopKeywords = async () => {
    try {
      // 더미 키워드 데이터 (실제로는 API에서 가져와야 함)
      const dummyKeywords = [
        { keyword: '친절', count: 15 },
        { keyword: '깨끗', count: 12 },
        { keyword: '실력', count: 10 },
        { keyword: '빠름', count: 8 },
        { keyword: '합리적', count: 7 },
        { keyword: '꼼꼼', count: 6 }
      ];
      
      // 상위 3개만 선택
      setTopKeywords(dummyKeywords.slice(0, 3));
    } catch (err) {
      console.error('Failed to fetch keywords:', err);
      setTopKeywords([]);
    }
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('ko-KR').format(price) + '원';
  };

  const getAspectLabel = (key) => {
    const labels = {
      price: '가격 합리성',
      skill: '의료진 실력',
      kindness: '친절도',
      waiting: '대기시간',
      facility: '시설',
      overtreatment: '과잉진료 없음'
    };
    return labels[key] || key;
  };

  if (loading) {
    return (
      <DetailContainer>
        <DetailContent>
          <LoadingSpinner size="large" text="치과 정보를 불러오는 중..." />
        </DetailContent>
      </DetailContainer>
    );
  }

  if (error || !clinic) {
    return (
      <DetailContainer>
        <DetailContent>
          <Section>
            <h2>오류가 발생했습니다</h2>
            <p>{error || '치과 정보를 찾을 수 없습니다.'}</p>
          </Section>
        </DetailContent>
      </DetailContainer>
    );
  }

  // 실제 API 데이터 사용 (clinic 객체에서)
  const aspectScores = clinic.aspect_scores || {
    price: 0,
    skill: 0,
    kindness: 0,
    waiting: 0,
    facility: 0,
    overtreatment: 0
  };

  const priceEntries = (() => {
    if (!clinic.price_info) return [];
    if (Array.isArray(clinic.price_info)) {
      return clinic.price_info;
    }
    return Object.entries(clinic.price_info).map(([treatment, info]) => ({
      treatment: getTreatmentName(treatment),
      average_price: info?.average_price || info?.price || 0,
      price_count: info?.price_count || 0,
    })).filter(item => item.average_price > 0);
  })();

  const mockData = {
    comprehensive_score: clinic.average_rating || 0,
    aspect_scores: aspectScores
  };

  return (
    <DetailContainer>
      <DetailContent>
        <ClinicHeader>
          <ClinicTitle>{clinic.name}</ClinicTitle>
          <ClinicInfo>
            <InfoSection>
              <InfoItem>
                <InfoIcon className="location" />
                {clinic.address}
              </InfoItem>
              {clinic.phone && (
                <InfoItem>
                  <InfoIcon className="phone" />
                  {clinic.phone}
                </InfoItem>
              )}
              <InfoItem>
                <InfoIcon className="time" />
                평일 09:00-18:00 {clinic.night_service && '| 야간진료'} {clinic.weekend_service && '| 주말진료'}
              </InfoItem>
            </InfoSection>
            
            <ScoreSection>
              <OverallScore>
                <ScoreValue>{Number(clinic.average_rating ?? clinic.rating ?? 0).toFixed(1)}</ScoreValue>
                <ScoreLabel>종합 점수</ScoreLabel>
              </OverallScore>
              <ReviewCount>
                총 {clinic.total_reviews?.toLocaleString() || 0}개 리뷰
              </ReviewCount>
            </ScoreSection>
          </ClinicInfo>
        </ClinicHeader>

        <ContentGrid>
          <MainContent>
            <Section>
              <SectionTitle>측면별 평가</SectionTitle>
              <AspectScores>
                {Object.entries(aspectScores).map(([key, score]) => (
                  <AspectItem key={key}>
                    <AspectLabel>{getAspectLabel(key)}</AspectLabel>
                    <AspectScore score={score}>
                      {Number(score ?? 0).toFixed(1)}
                    </AspectScore>
                  </AspectItem>
                ))}
              </AspectScores>
            </Section>

            <Section>
              <SectionTitle>편의시설 및 특징</SectionTitle>
              <FeaturesList>
                {clinic.has_parking && (
                  <FeatureTag positive>주차 가능</FeatureTag>
                )}
                {clinic.night_service && (
                  <FeatureTag positive>야간 진료</FeatureTag>
                )}
                {clinic.weekend_service && (
                  <FeatureTag positive>주말 진료</FeatureTag>
                )}
                {aspectScores.overtreatment >= 4.0 && (
                  <FeatureTag positive>과잉진료 없음</FeatureTag>
                )}
                {aspectScores.price >= 4.0 && (
                  <FeatureTag positive>합리적 가격</FeatureTag>
                )}
                {aspectScores.skill >= 4.0 && (
                  <FeatureTag positive>실력 인정</FeatureTag>
                )}
              </FeaturesList>

              {topKeywords.length > 0 && (
                <KeywordsSection>
                  <KeywordsTitle>🏷️ 자주 언급되는 키워드 TOP 3</KeywordsTitle>
                  <KeywordTags>
                    {topKeywords.map((item, index) => (
                      <KeywordTag key={index}>
                        #{item.keyword}
                        <KeywordCount>{item.count}</KeywordCount>
                      </KeywordTag>
                    ))}
                  </KeywordTags>
                </KeywordsSection>
              )}
            </Section>

            <Section>
              <SectionTitle>
                실제 크롤링 리뷰 ({reviews.length}개)
                {process.env.NODE_ENV === 'development' && (
                  <span style={{ fontSize: '12px', color: '#666', fontWeight: 'normal' }}>
                    {' '}(치과 ID: {id})
                  </span>
                )}
              </SectionTitle>
              {reviewsLoading ? (
                <LoadingSpinner text="실제 리뷰 데이터를 불러오는 중..." />
              ) : reviews.length > 0 ? (
                <ReviewsList>
                  {reviews.slice(0, 10).map((review, index) => (
                    <ReviewItem key={review.id || index}>
                      <ReviewHeader>
                        <ReviewRating>
                          ⭐ {review.rating || '미평가'} / 5
                        </ReviewRating>
                        <ReviewDate>
                          {review.review_date 
                            ? new Date(review.review_date).toLocaleDateString('ko-KR')
                            : new Date(review.created_at).toLocaleDateString('ko-KR')
                          }
                        </ReviewDate>
                      </ReviewHeader>
                      <ReviewText>
                        {review.text || '리뷰 내용이 없습니다.'}
                      </ReviewText>
                      <div style={{ 
                        fontSize: '12px', 
                        color: '#999', 
                        marginTop: '8px',
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center'
                      }}>
                        <span>
                          📍 출처: {review.source === 'naver' ? '네이버 플레이스' : review.source}
                        </span>
                        <span>
                          👤 {review.reviewer_hash}
                        </span>
                      </div>
                    </ReviewItem>
                  ))}
                  {reviews.length > 10 && (
                    <LoadMoreButton onClick={() => {
                      alert(`총 ${reviews.length}개의 실제 리뷰가 있습니다. 더 많은 리뷰 기능은 추후 구현 예정입니다.`);
                    }}>
                      더 많은 리뷰 보기 ({reviews.length - 10}개 더)
                    </LoadMoreButton>
                  )}
                </ReviewsList>
              ) : (
                <div style={{ 
                  textAlign: 'center', 
                  padding: '40px 20px',
                  color: '#666'
                }}>
                  <p>🔍 실제 크롤링된 리뷰가 없습니다.</p>
                  <p style={{ fontSize: '14px', marginTop: '8px' }}>
                    이 치과는 아직 리뷰 크롤링이 완료되지 않았습니다.
                  </p>
                  {process.env.NODE_ENV === 'development' && (
                    <p style={{ fontSize: '12px', marginTop: '8px', color: '#999' }}>
                      개발자 정보: 치과 ID {id}의 리뷰를 확인해주세요.
                    </p>
                  )}
                </div>
              )}
            </Section>
          </MainContent>

          <Sidebar>
            <Section>
              <SectionTitle>가격 정보</SectionTitle>
              <PriceTable>
                <Table>
                  <thead>
                    <tr>
                      <th>치료</th>
                      <th>평균 가격</th>
                      <th>데이터 수</th>
                    </tr>
                  </thead>
                  <tbody>
                    {priceEntries.length > 0 ? (
                      priceEntries.map((item, index) => (
                        <tr key={index}>
                          <td>{item.treatment}</td>
                          <td className="price">{formatPrice(item.average_price)}</td>
                          <td>{item.price_count || 0}개</td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan="3" style={{ textAlign: 'center', color: '#666' }}>
                          등록된 가격 정보가 없습니다.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </Table>
              </PriceTable>
            </Section>

            <Section>
              <SectionTitle>위치 정보</SectionTitle>
              <InfoItem>
                <InfoIcon className="location" />
                {clinic.district}
              </InfoItem>
              {clinic.latitude && clinic.longitude && (
                <div style={{ 
                  width: '100%', 
                  height: '200px', 
                  background: '#f0f0f0', 
                  borderRadius: '8px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  marginTop: '16px',
                  color: '#666'
                }}>
                  지도 영역
                  <br />
                  (위도: {clinic.latitude}, 경도: {clinic.longitude})
                </div>
              )}
            </Section>
          </Sidebar>
        </ContentGrid>
      </DetailContent>
    </DetailContainer>
  );
}

export default ClinicDetailPage;
