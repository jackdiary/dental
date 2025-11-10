import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { clinicAPI, analysisAPI } from '../services/api';
import { SEOUL_DISTRICTS, ASPECT_LABELS } from '../constants/common';

const Container = styled.div`
  max-width: 1400px;
  margin: 0 auto;
  padding: 40px 20px;
`;

const Header = styled.div`
  text-align: center;
  margin-bottom: 40px;
`;

const Title = styled.h1`
  font-size: 2.5rem;
  font-weight: bold;
  color: ${props => props.theme.colors.textPrimary};
  margin-bottom: 16px;
`;

const Subtitle = styled.p`
  font-size: 1.1rem;
  color: ${props => props.theme.colors.textSecondary};
  max-width: 600px;
  margin: 0 auto;
`;

const FilterSection = styled.div`
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 32px;
`;

const FilterGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
`;

const FilterGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const Label = styled.label`
  font-weight: 600;
  color: ${props => props.theme.colors.textPrimary};
  font-size: 0.9rem;
`;

const Select = styled.select`
  padding: 12px;
  border: 1px solid ${props => props.theme.colors.gray300};
  border-radius: 8px;
  font-size: 1rem;
  background: white;
  
  &:focus {
    outline: none;
    border-color: ${props => props.theme.colors.primary};
    box-shadow: 0 0 0 3px ${props => props.theme.colors.primary}20;
  }
`;

const SearchButton = styled.button`
  background: ${props => props.theme.colors.primary};
  color: white;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 600;
  transition: background 0.2s;
  
  &:hover {
    background: ${props => props.theme.colors.primaryDark};
  }
  
  &:disabled {
    background: ${props => props.theme.colors.gray400};
    cursor: not-allowed;
  }
`;

const AnalysisGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
`;

const AnalysisCard = styled.div`
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
`;

const CardTitle = styled.h3`
  font-size: 1.2rem;
  font-weight: 600;
  color: ${props => props.theme.colors.textPrimary};
  margin-bottom: 16px;
`;

const AspectScore = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
`;

const AspectName = styled.span`
  font-size: 0.9rem;
  color: ${props => props.theme.colors.textSecondary};
`;

const ScoreBar = styled.div`
  flex: 1;
  height: 8px;
  background: ${props => props.theme.colors.gray200};
  border-radius: 4px;
  margin: 0 12px;
  overflow: hidden;
`;

const ScoreFill = styled.div`
  height: 100%;
  background: ${props => {
    if (props.score > 0.3) return props.theme.colors.success;
    if (props.score > -0.3) return props.theme.colors.warning;
    return props.theme.colors.error;
  }};
  width: ${props => Math.abs(props.score) * 100}%;
  transition: width 0.3s ease;
`;

const ScoreValue = styled.span`
  font-size: 0.9rem;
  font-weight: 600;
  color: ${props => {
    if (props.score > 0.3) return props.theme.colors.success;
    if (props.score > -0.3) return props.theme.colors.warning;
    return props.theme.colors.error;
  }};
`;

const KeywordsSection = styled.div`
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 32px;
`;

const KeywordGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 24px;
`;

const KeywordCategory = styled.div`
  h4 {
    font-size: 1rem;
    font-weight: 600;
    color: ${props => props.theme.colors.textPrimary};
    margin-bottom: 12px;
  }
`;

const KeywordList = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
`;

const KeywordTag = styled.span`
  display: inline-block;
  padding: 6px 12px;
  background: ${props => props.theme.colors.primary}15;
  color: ${props => props.theme.colors.primary};
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
`;

const ReviewsSection = styled.div`
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
`;

const ReviewsHeader = styled.div`
  background: ${props => props.theme.colors.gray50};
  padding: 20px 24px;
  border-bottom: 1px solid ${props => props.theme.colors.gray200};
  border-radius: 12px 12px 0 0;
`;

const ReviewsTitle = styled.h2`
  font-size: 1.3rem;
  font-weight: 600;
  color: ${props => props.theme.colors.textPrimary};
  margin-bottom: 8px;
`;

const ReviewsCount = styled.p`
  color: ${props => props.theme.colors.textSecondary};
  font-size: 0.9rem;
`;

const ReviewItem = styled.div`
  padding: 20px 24px;
  border-bottom: 1px solid ${props => props.theme.colors.gray200};
  
  &:last-child {
    border-bottom: none;
  }
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
`;

const Stars = styled.div`
  color: ${props => props.theme.colors.warning};
`;

const ReviewDate = styled.span`
  font-size: 0.8rem;
  color: ${props => props.theme.colors.textSecondary};
`;

const ReviewText = styled.p`
  color: ${props => props.theme.colors.textPrimary};
  line-height: 1.6;
  margin-bottom: 12px;
`;



const LoadingSpinner = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40px;
  
  &::after {
    content: '';
    width: 40px;
    height: 40px;
    border: 4px solid ${props => props.theme.colors.gray300};
    border-top: 4px solid ${props => props.theme.colors.primary};
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

const EmptyState = styled.div`
  text-align: center;
  padding: 60px 20px;
  color: ${props => props.theme.colors.textSecondary};
`;

function ReviewAnalysisPage() {
  const [selectedDistrict, setSelectedDistrict] = useState('');
  const [selectedClinic, setSelectedClinic] = useState('');
  const [clinics, setClinics] = useState([]);
  const [analysisData, setAnalysisData] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);



  useEffect(() => {
    if (selectedDistrict) {
      loadClinics();
    }
  }, [selectedDistrict]);

  const loadClinics = async () => {
    try {
      const response = await clinicAPI.getList({
        district: selectedDistrict
      });
      setClinics(response.data.results || []);
    } catch (error) {
      console.error('치과 목록 로드 실패:', error);
      setClinics([]);
    }
  };

  const handleSearch = async () => {
    if (!selectedClinic) {
      alert('치과를 선택해주세요.');
      return;
    }

    setLoading(true);
    setHasSearched(true);

    try {
      const [analysisResponse, reviewsResponse] = await Promise.all([
        analysisAPI.getClinicAnalysis(selectedClinic),
        analysisAPI.getClinicReviewsWithAnalysis(selectedClinic)
      ]);

      setAnalysisData(analysisResponse.data);
      setReviews(reviewsResponse.data.results || []);
    } catch (error) {
      console.error('리뷰 분석 데이터 로드 실패:', error);
      setAnalysisData(null);
      setReviews([]);
    } finally {
      setLoading(false);
    }
  };

  const getScoreLabel = (score) => {
    if (score > 0.3) return '긍정적';
    if (score > -0.3) return '보통';
    return '부정적';
  };

  const getAspectClass = (score) => {
    if (score > 0.3) return 'positive';
    if (score > -0.3) return 'neutral';
    return 'negative';
  };

  const renderStars = (rating) => {
    return '★'.repeat(rating) + '☆'.repeat(5 - rating);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('ko-KR');
  };

  return (
    <Container>
      <Header>
        <Title>리뷰 분석</Title>
        <Subtitle>
          AI 기반 감성 분석으로 치과의 실제 평가를 확인해보세요.
        </Subtitle>
      </Header>

      <FilterSection>
        <FilterGrid>
          <FilterGroup>
            <Label>지역 선택</Label>
            <Select
              value={selectedDistrict}
              onChange={(e) => {
                setSelectedDistrict(e.target.value);
                setSelectedClinic('');
              }}
            >
              <option value="">지역을 선택하세요</option>
              {SEOUL_DISTRICTS.map(district => (
                <option key={district} value={district}>{district}</option>
              ))}
            </Select>
          </FilterGroup>

          <FilterGroup>
            <Label>치과 선택</Label>
            <Select
              value={selectedClinic}
              onChange={(e) => setSelectedClinic(e.target.value)}
              disabled={!selectedDistrict}
            >
              <option value="">치과를 선택하세요</option>
              {clinics.map(clinic => (
                <option key={clinic.id} value={clinic.id}>
                  {clinic.name}
                </option>
              ))}
            </Select>
          </FilterGroup>

          <FilterGroup>
            <Label>&nbsp;</Label>
            <SearchButton 
              onClick={handleSearch}
              disabled={loading || !selectedClinic}
            >
              {loading ? '분석 중...' : '리뷰 분석'}
            </SearchButton>
          </FilterGroup>
        </FilterGrid>
      </FilterSection>

      {hasSearched && (
        <>
          {loading ? (
            <LoadingSpinner />
          ) : analysisData ? (
            <>
              <AnalysisGrid>
                <AnalysisCard>
                  <CardTitle>측면별 감성 분석</CardTitle>
                  {Object.entries(ASPECT_LABELS).map(([key, label]) => (
                    <AspectScore key={key}>
                      <AspectName>{label}</AspectName>
                      <ScoreBar>
                        <ScoreFill score={analysisData.aspect_scores?.[key] || 0} />
                      </ScoreBar>
                      <ScoreValue score={analysisData.aspect_scores?.[key] || 0}>
                        {getScoreLabel(analysisData.aspect_scores?.[key] || 0)}
                      </ScoreValue>
                    </AspectScore>
                  ))}
                </AnalysisCard>

                <AnalysisCard>
                  <CardTitle>리뷰 통계</CardTitle>
                  <AspectScore>
                    <AspectName>총 리뷰 수</AspectName>
                    <ScoreValue>{analysisData.total_reviews || 0}개</ScoreValue>
                  </AspectScore>
                  <AspectScore>
                    <AspectName>평균 평점</AspectName>
                    <ScoreValue>{analysisData.average_rating || 0}점</ScoreValue>
                  </AspectScore>
                  <AspectScore>
                    <AspectName>긍정 리뷰</AspectName>
                    <ScoreValue>{analysisData.positive_ratio || 0}%</ScoreValue>
                  </AspectScore>
                  <AspectScore>
                    <AspectName>분석 신뢰도</AspectName>
                    <ScoreValue>{analysisData.confidence || 0}%</ScoreValue>
                  </AspectScore>
                </AnalysisCard>
              </AnalysisGrid>

              {analysisData.top_keywords && (
                <KeywordsSection>
                  <CardTitle>자주 언급되는 키워드</CardTitle>
                  <KeywordGrid>
                    {Object.entries(analysisData.top_keywords).map(([category, keywords]) => (
                      <KeywordCategory key={category}>
                        <h4>{ASPECT_LABELS[category] || category}</h4>
                        <KeywordList>
                          {keywords.map((keyword, index) => (
                            <KeywordTag key={index}>{keyword}</KeywordTag>
                          ))}
                        </KeywordList>
                      </KeywordCategory>
                    ))}
                  </KeywordGrid>
                </KeywordsSection>
              )}

              <ReviewsSection>
                <ReviewsHeader>
                  <ReviewsTitle>최근 리뷰</ReviewsTitle>
                  <ReviewsCount>{reviews.length}개의 리뷰</ReviewsCount>
                </ReviewsHeader>

                {reviews.length > 0 ? (
                  reviews.slice(0, 10).map((review, index) => (
                    <ReviewItem key={index}>
                      <ReviewHeader>
                        <ReviewRating>
                          <Stars>{renderStars(review.original_rating)}</Stars>
                          <span>{review.original_rating}점</span>
                        </ReviewRating>
                        <ReviewDate>{formatDate(review.review_date)}</ReviewDate>
                      </ReviewHeader>
                      
                      <ReviewText>{review.original_text}</ReviewText>

                    </ReviewItem>
                  ))
                ) : (
                  <EmptyState>
                    <h3>리뷰가 없습니다</h3>
                    <p>아직 분석할 리뷰가 없습니다.</p>
                  </EmptyState>
                )}
              </ReviewsSection>
            </>
          ) : (
            <EmptyState>
              <h3>분석 결과가 없습니다</h3>
              <p>선택하신 치과의 리뷰 분석 데이터가 없습니다.</p>
            </EmptyState>
          )}
        </>
      )}
    </Container>
  );
}

export default ReviewAnalysisPage;