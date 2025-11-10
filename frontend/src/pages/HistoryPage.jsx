import React, { useState, useEffect, useContext } from 'react';
import styled from 'styled-components';
import { Link } from 'react-router-dom';
import { AuthContext } from '../contexts/AuthContext';

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

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 40px;

  @media (max-width: ${props => props.theme.breakpoints.mobile}) {
    flex-direction: column;
    align-items: flex-start;
    gap: 20px;
  }
`;

const HeaderLeft = styled.div``;

const Title = styled.h1`
  font-size: ${props => props.theme.fonts.sizes['3xl']};
  font-weight: ${props => props.theme.fonts.weights.bold};
  color: ${props => props.theme.colors.textPrimary};
  margin-bottom: 10px;
`;

const Subtitle = styled.p`
  color: ${props => props.theme.colors.textSecondary};
  font-size: ${props => props.theme.fonts.sizes.lg};
`;

const HeaderActions = styled.div`
  display: flex;
  gap: 15px;

  @media (max-width: ${props => props.theme.breakpoints.mobile}) {
    width: 100%;
  }
`;

const ClearButton = styled.button`
  background: ${props => props.theme.colors.error};
  color: ${props => props.theme.colors.white};
  padding: 10px 20px;
  border-radius: ${props => props.theme.borderRadius.md};
  font-weight: ${props => props.theme.fonts.weights.medium};
  transition: background ${props => props.theme.transitions.fast};

  &:hover {
    background: ${props => props.theme.colors.errorDark};
  }

  &:disabled {
    background: ${props => props.theme.colors.gray300};
    cursor: not-allowed;
  }
`;

const FilterSection = styled.div`
  display: flex;
  gap: 15px;
  margin-bottom: 30px;
  flex-wrap: wrap;

  @media (max-width: ${props => props.theme.breakpoints.mobile}) {
    flex-direction: column;
  }
`;

const FilterButton = styled.button`
  padding: 10px 20px;
  border: 1px solid ${props => props.active ? props.theme.colors.primary : props.theme.colors.gray300};
  background: ${props => props.active ? props.theme.colors.primary : props.theme.colors.white};
  color: ${props => props.active ? props.theme.colors.white : props.theme.colors.textSecondary};
  border-radius: ${props => props.theme.borderRadius.lg};
  font-weight: ${props => props.theme.fonts.weights.medium};
  transition: all ${props => props.theme.transitions.fast};

  &:hover {
    border-color: ${props => props.theme.colors.primary};
    color: ${props => props.active ? props.theme.colors.white : props.theme.colors.primary};
  }
`;

const HistoryList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 20px;
`;

const HistoryItem = styled.div`
  background: ${props => props.theme.colors.white};
  border: 1px solid ${props => props.theme.colors.gray200};
  border-radius: ${props => props.theme.borderRadius.lg};
  padding: 25px;
  box-shadow: ${props => props.theme.shadows.sm};
  transition: all ${props => props.theme.transitions.fast};

  &:hover {
    box-shadow: ${props => props.theme.shadows.md};
  }
`;

const HistoryHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;

  @media (max-width: ${props => props.theme.breakpoints.mobile}) {
    flex-direction: column;
    gap: 10px;
  }
`;

const SearchInfo = styled.div`
  flex: 1;
`;

const SearchQuery = styled.h3`
  font-size: ${props => props.theme.fonts.sizes.lg};
  font-weight: ${props => props.theme.fonts.weights.bold};
  color: ${props => props.theme.colors.textPrimary};
  margin-bottom: 8px;
`;

const SearchDetails = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  color: ${props => props.theme.colors.textSecondary};
  font-size: ${props => props.theme.fonts.sizes.sm};
`;

const SearchDetail = styled.span`
  display: flex;
  align-items: center;
  gap: 5px;
`;

const SearchTime = styled.div`
  color: ${props => props.theme.colors.textSecondary};
  font-size: ${props => props.theme.fonts.sizes.sm};
  white-space: nowrap;
`;

const ResultsSection = styled.div`
  margin-top: 15px;
`;

const ResultsHeader = styled.div`
  display: flex;
  justify-content: between;
  align-items: center;
  margin-bottom: 15px;
`;

const ResultsCount = styled.span`
  color: ${props => props.theme.colors.textSecondary};
  font-size: ${props => props.theme.fonts.sizes.sm};
`;

const ResultsList = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 15px;

  @media (max-width: ${props => props.theme.breakpoints.mobile}) {
    grid-template-columns: 1fr;
  }
`;

const ResultItem = styled.div`
  background: ${props => props.theme.colors.gray50};
  border: 1px solid ${props => props.theme.colors.gray200};
  border-radius: ${props => props.theme.borderRadius.md};
  padding: 15px;
`;

const ResultName = styled.h4`
  font-size: ${props => props.theme.fonts.sizes.base};
  font-weight: ${props => props.theme.fonts.weights.bold};
  color: ${props => props.theme.colors.textPrimary};
  margin-bottom: 8px;
`;

const ResultInfo = styled.div`
  color: ${props => props.theme.colors.textSecondary};
  font-size: ${props => props.theme.fonts.sizes.sm};
  margin-bottom: 10px;
`;

const ResultActions = styled.div`
  display: flex;
  gap: 10px;
`;

const ViewButton = styled(Link)`
  background: ${props => props.theme.colors.primary};
  color: ${props => props.theme.colors.white};
  padding: 8px 16px;
  border-radius: ${props => props.theme.borderRadius.sm};
  font-size: ${props => props.theme.fonts.sizes.xs};
  font-weight: ${props => props.theme.fonts.weights.medium};
  transition: background ${props => props.theme.transitions.fast};

  &:hover {
    background: ${props => props.theme.colors.primaryDark};
  }
`;

const RepeatButton = styled.button`
  background: ${props => props.theme.colors.gray200};
  color: ${props => props.theme.colors.textPrimary};
  padding: 8px 16px;
  border-radius: ${props => props.theme.borderRadius.sm};
  font-size: ${props => props.theme.fonts.sizes.xs};
  font-weight: ${props => props.theme.fonts.weights.medium};
  transition: background ${props => props.theme.transitions.fast};

  &:hover {
    background: ${props => props.theme.colors.gray300};
  }
`;

const EmptyState = styled.div`
  text-align: center;
  padding: 80px 20px;
  color: ${props => props.theme.colors.textSecondary};
`;

const EmptyIcon = styled.div`
  font-size: 64px;
  margin-bottom: 20px;
`;

const EmptyTitle = styled.h3`
  font-size: ${props => props.theme.fonts.sizes.xl};
  font-weight: ${props => props.theme.fonts.weights.bold};
  color: ${props => props.theme.colors.textPrimary};
  margin-bottom: 10px;
`;

const EmptyDescription = styled.p`
  margin-bottom: 30px;
  line-height: 1.6;
`;

const SearchButton = styled(Link)`
  background: ${props => props.theme.colors.primary};
  color: ${props => props.theme.colors.white};
  padding: 15px 30px;
  border-radius: ${props => props.theme.borderRadius.lg};
  font-weight: ${props => props.theme.fonts.weights.medium};
  transition: background ${props => props.theme.transitions.fast};

  &:hover {
    background: ${props => props.theme.colors.primaryDark};
  }
`;

const LoginPrompt = styled.div`
  text-align: center;
  padding: 80px 20px;
  background: ${props => props.theme.colors.gray50};
  border-radius: ${props => props.theme.borderRadius.xl};
`;

const LoginButton = styled(Link)`
  background: ${props => props.theme.colors.primary};
  color: ${props => props.theme.colors.white};
  padding: 15px 30px;
  border-radius: ${props => props.theme.borderRadius.lg};
  font-weight: ${props => props.theme.fonts.weights.medium};
  margin-top: 20px;
  display: inline-block;
  transition: background ${props => props.theme.transitions.fast};

  &:hover {
    background: ${props => props.theme.colors.primaryDark};
  }
`;

function HistoryPage() {
  const { user } = useContext(AuthContext);
  const [history, setHistory] = useState([]);
  const [filter, setFilter] = useState('all');
  const [loading, setLoading] = useState(true);

  // 샘플 데이터 (실제로는 API에서 가져올 데이터)
  const sampleHistory = [
    {
      id: 1,
      query: '강남구 임플란트',
      location: '강남구',
      treatment: '임플란트',
      priceRange: '100-200만원',
      searchTime: '2024-11-07 14:30',
      resultCount: 15,
      results: [
        { id: 101, name: '강남세브란스치과', address: '강남구 테헤란로 211', rating: 4.6 },
        { id: 102, name: '삼성서울병원 치과', address: '강남구 일원로 81', rating: 4.8 },
        { id: 103, name: '강남성심병원 치과', address: '강남구 선릉로 259', rating: 4.5 }
      ]
    },
    {
      id: 2,
      query: '서초구 교정치과',
      location: '서초구',
      treatment: '교정',
      priceRange: '300-500만원',
      searchTime: '2024-11-06 16:45',
      resultCount: 12,
      results: [
        { id: 201, name: '서초교정치과', address: '서초구 서초대로 294', rating: 4.7 },
        { id: 202, name: '강남교정전문의원', address: '서초구 반포대로 222', rating: 4.6 }
      ]
    },
    {
      id: 3,
      query: '종로구 스케일링',
      location: '종로구',
      treatment: '스케일링',
      priceRange: '5-10만원',
      searchTime: '2024-11-05 10:20',
      resultCount: 8,
      results: [
        { id: 301, name: '서울대학교치과병원', address: '종로구 대학로 101', rating: 4.8 },
        { id: 302, name: '종로치과의원', address: '종로구 종로 123', rating: 4.4 }
      ]
    }
  ];

  useEffect(() => {
    // 실제로는 API 호출
    setTimeout(() => {
      if (user) {
        setHistory(sampleHistory);
      }
      setLoading(false);
    }, 1000);
  }, [user]);

  const handleClearHistory = () => {
    if (window.confirm('검색 기록을 모두 삭제하시겠습니까?')) {
      setHistory([]);
    }
  };

  const handleRepeatSearch = (searchData) => {
    // 검색 페이지로 이동하면서 검색 조건 전달
    const searchParams = new URLSearchParams({
      location: searchData.location,
      treatment: searchData.treatment,
      priceRange: searchData.priceRange
    });
    window.location.href = `/search?${searchParams.toString()}`;
  };

  const filteredHistory = history.filter(item => {
    if (filter === 'all') return true;
    if (filter === 'today') {
      const today = new Date().toDateString();
      const itemDate = new Date(item.searchTime).toDateString();
      return today === itemDate;
    }
    if (filter === 'week') {
      const weekAgo = new Date();
      weekAgo.setDate(weekAgo.getDate() - 7);
      return new Date(item.searchTime) >= weekAgo;
    }
    return item.treatment.toLowerCase().includes(filter.toLowerCase());
  });

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays === 1) return '오늘';
    if (diffDays === 2) return '어제';
    if (diffDays <= 7) return `${diffDays - 1}일 전`;
    return date.toLocaleDateString('ko-KR');
  };

  if (!user) {
    return (
      <PageContainer>
        <LoginPrompt>
          <EmptyIcon>📋</EmptyIcon>
          <EmptyTitle>로그인이 필요합니다</EmptyTitle>
          <EmptyDescription>
            검색 기록을 확인하려면 로그인해주세요.
          </EmptyDescription>
          <LoginButton to="/login">로그인하기</LoginButton>
        </LoginPrompt>
      </PageContainer>
    );
  }

  if (loading) {
    return (
      <PageContainer>
        <div style={{ textAlign: 'center', padding: '100px 0' }}>
          <div>로딩 중...</div>
        </div>
      </PageContainer>
    );
  }

  return (
    <PageContainer>
      <Header>
        <HeaderLeft>
          <Title>검색 기록</Title>
          <Subtitle>이전 검색 결과를 다시 확인하고 재검색할 수 있습니다</Subtitle>
        </HeaderLeft>
        <HeaderActions>
          <ClearButton 
            onClick={handleClearHistory}
            disabled={history.length === 0}
          >
            전체 삭제
          </ClearButton>
        </HeaderActions>
      </Header>

      {history.length > 0 && (
        <FilterSection>
          <FilterButton 
            active={filter === 'all'} 
            onClick={() => setFilter('all')}
          >
            전체 ({history.length})
          </FilterButton>
          <FilterButton 
            active={filter === 'today'} 
            onClick={() => setFilter('today')}
          >
            오늘
          </FilterButton>
          <FilterButton 
            active={filter === 'week'} 
            onClick={() => setFilter('week')}
          >
            최근 7일
          </FilterButton>
          <FilterButton 
            active={filter === '임플란트'} 
            onClick={() => setFilter('임플란트')}
          >
            임플란트
          </FilterButton>
          <FilterButton 
            active={filter === '교정'} 
            onClick={() => setFilter('교정')}
          >
            교정
          </FilterButton>
          <FilterButton 
            active={filter === '스케일링'} 
            onClick={() => setFilter('스케일링')}
          >
            스케일링
          </FilterButton>
        </FilterSection>
      )}

      {filteredHistory.length > 0 ? (
        <HistoryList>
          {filteredHistory.map(item => (
            <HistoryItem key={item.id}>
              <HistoryHeader>
                <SearchInfo>
                  <SearchQuery>{item.query}</SearchQuery>
                  <SearchDetails>
                    <SearchDetail>📍 {item.location}</SearchDetail>
                    <SearchDetail>🦷 {item.treatment}</SearchDetail>
                    <SearchDetail>💰 {item.priceRange}</SearchDetail>
                  </SearchDetails>
                </SearchInfo>
                <SearchTime>{formatDate(item.searchTime)}</SearchTime>
              </HistoryHeader>

              <ResultsSection>
                <ResultsHeader>
                  <ResultsCount>검색 결과 {item.resultCount}개</ResultsCount>
                </ResultsHeader>
                
                <ResultsList>
                  {item.results.map(result => (
                    <ResultItem key={result.id}>
                      <ResultName>{result.name}</ResultName>
                      <ResultInfo>
                        📍 {result.address}<br/>
                        ⭐ {result.rating}
                      </ResultInfo>
                      <ResultActions>
                        <ViewButton to={`/clinic/${result.id}`}>
                          상세보기
                        </ViewButton>
                        <RepeatButton onClick={() => handleRepeatSearch(item)}>
                          재검색
                        </RepeatButton>
                      </ResultActions>
                    </ResultItem>
                  ))}
                </ResultsList>
              </ResultsSection>
            </HistoryItem>
          ))}
        </HistoryList>
      ) : (
        <EmptyState>
          <EmptyIcon>📋</EmptyIcon>
          <EmptyTitle>
            {filter === 'all' ? '검색 기록이 없습니다' : '해당 기간의 검색 기록이 없습니다'}
          </EmptyTitle>
          <EmptyDescription>
            {filter === 'all' 
              ? '치과를 검색해보시면 여기에 기록이 남습니다.'
              : '다른 기간을 선택하거나 전체를 확인해보세요.'
            }
          </EmptyDescription>
          {filter === 'all' && (
            <SearchButton to="/search">치과 찾기</SearchButton>
          )}
        </EmptyState>
      )}
    </PageContainer>
  );
}

export default HistoryPage;