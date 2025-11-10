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
  margin-bottom: 40px;
`;

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

const ClinicGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 25px;

  @media (max-width: ${props => props.theme.breakpoints.mobile}) {
    grid-template-columns: 1fr;
  }
`;

const ClinicCard = styled.div`
  background: ${props => props.theme.colors.white};
  border: 1px solid ${props => props.theme.colors.gray200};
  border-radius: ${props => props.theme.borderRadius.lg};
  padding: 25px;
  box-shadow: ${props => props.theme.shadows.sm};
  transition: all ${props => props.theme.transitions.fast};
  position: relative;

  &:hover {
    transform: translateY(-2px);
    box-shadow: ${props => props.theme.shadows.md};
  }
`;

const FavoriteButton = styled.button`
  position: absolute;
  top: 20px;
  right: 20px;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: ${props => props.theme.colors.white};
  border: 1px solid ${props => props.theme.colors.gray200};
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  color: ${props => props.theme.colors.error};
  transition: all ${props => props.theme.transitions.fast};

  &:hover {
    background: ${props => props.theme.colors.error};
    color: ${props => props.theme.colors.white};
  }
`;

const ClinicName = styled.h3`
  font-size: ${props => props.theme.fonts.sizes.xl};
  font-weight: ${props => props.theme.fonts.weights.bold};
  color: ${props => props.theme.colors.textPrimary};
  margin-bottom: 10px;
  padding-right: 50px;
`;

const ClinicInfo = styled.div`
  margin-bottom: 15px;
`;

const InfoItem = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  color: ${props => props.theme.colors.textSecondary};
  font-size: ${props => props.theme.fonts.sizes.sm};
`;

const InfoIcon = styled.span`
  font-size: 14px;
  width: 16px;
`;

const TagContainer = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 15px;
`;

const Tag = styled.span`
  background: ${props => props.theme.colors.primary}15;
  color: ${props => props.theme.colors.primary};
  padding: 4px 12px;
  border-radius: ${props => props.theme.borderRadius.full};
  font-size: ${props => props.theme.fonts.sizes.xs};
  font-weight: ${props => props.theme.fonts.weights.medium};
`;

const Rating = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 15px;
`;

const Stars = styled.div`
  color: ${props => props.theme.colors.warning};
  font-size: 16px;
`;

const RatingText = styled.span`
  color: ${props => props.theme.colors.textSecondary};
  font-size: ${props => props.theme.fonts.sizes.sm};
`;

const ActionButtons = styled.div`
  display: flex;
  gap: 10px;
`;

const ViewButton = styled(Link)`
  flex: 1;
  background: ${props => props.theme.colors.primary};
  color: ${props => props.theme.colors.white};
  padding: 12px;
  border-radius: ${props => props.theme.borderRadius.md};
  text-align: center;
  font-weight: ${props => props.theme.fonts.weights.medium};
  transition: background ${props => props.theme.transitions.fast};

  &:hover {
    background: ${props => props.theme.colors.primaryDark};
  }
`;

const CallButton = styled.button`
  background: ${props => props.theme.colors.success};
  color: ${props => props.theme.colors.white};
  padding: 12px 16px;
  border-radius: ${props => props.theme.borderRadius.md};
  font-weight: ${props => props.theme.fonts.weights.medium};
  transition: background ${props => props.theme.transitions.fast};

  &:hover {
    background: ${props => props.theme.colors.successDark};
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

function FavoritesPage() {
  const { user } = useContext(AuthContext);
  const [favorites, setFavorites] = useState([]);
  const [filter, setFilter] = useState('all');
  const [loading, setLoading] = useState(true);

  // 샘플 데이터 (실제로는 API에서 가져올 데이터)
  const sampleFavorites = [
    {
      id: 1,
      name: '서울대학교치과병원',
      address: '서울시 종로구 대학로 101',
      phone: '02-2072-2175',
      rating: 4.8,
      reviewCount: 1250,
      specialties: ['임플란트', '교정', '심미치료'],
      distance: '1.2km',
      addedDate: '2024-11-01'
    },
    {
      id: 2,
      name: '강남세브란스치과',
      address: '서울시 강남구 테헤란로 211',
      phone: '02-2019-3870',
      rating: 4.6,
      reviewCount: 890,
      specialties: ['임플란트', '보철', '구강외과'],
      distance: '2.5km',
      addedDate: '2024-10-28'
    },
    {
      id: 3,
      name: '연세대학교치과대학병원',
      address: '서울시 서대문구 연세로 50-1',
      phone: '02-2228-8900',
      rating: 4.7,
      reviewCount: 1100,
      specialties: ['교정', '소아치과', '치주치료'],
      distance: '3.1km',
      addedDate: '2024-10-25'
    }
  ];

  useEffect(() => {
    // 실제로는 API 호출
    setTimeout(() => {
      if (user) {
        setFavorites(sampleFavorites);
      }
      setLoading(false);
    }, 1000);
  }, [user]);

  const handleRemoveFavorite = (clinicId) => {
    setFavorites(favorites.filter(clinic => clinic.id !== clinicId));
  };

  const filteredFavorites = favorites.filter(clinic => {
    if (filter === 'all') return true;
    if (filter === 'recent') {
      const addedDate = new Date(clinic.addedDate);
      const weekAgo = new Date();
      weekAgo.setDate(weekAgo.getDate() - 7);
      return addedDate >= weekAgo;
    }
    return clinic.specialties.some(specialty => 
      specialty.toLowerCase().includes(filter.toLowerCase())
    );
  });

  const renderStars = (rating) => {
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 !== 0;
    const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);

    return (
      <>
        {'★'.repeat(fullStars)}
        {hasHalfStar && '☆'}
        {'☆'.repeat(emptyStars)}
      </>
    );
  };

  if (!user) {
    return (
      <PageContainer>
        <LoginPrompt>
          <EmptyIcon>❤️</EmptyIcon>
          <EmptyTitle>로그인이 필요합니다</EmptyTitle>
          <EmptyDescription>
            즐겨찾기 기능을 사용하려면 로그인해주세요.
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
        <Title>즐겨찾기</Title>
        <Subtitle>관심 있는 치과들을 모아서 쉽게 관리하세요</Subtitle>
      </Header>

      {favorites.length > 0 && (
        <FilterSection>
          <FilterButton 
            active={filter === 'all'} 
            onClick={() => setFilter('all')}
          >
            전체 ({favorites.length})
          </FilterButton>
          <FilterButton 
            active={filter === 'recent'} 
            onClick={() => setFilter('recent')}
          >
            최근 추가
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
            active={filter === '심미치료'} 
            onClick={() => setFilter('심미치료')}
          >
            심미치료
          </FilterButton>
        </FilterSection>
      )}

      {filteredFavorites.length > 0 ? (
        <ClinicGrid>
          {filteredFavorites.map(clinic => (
            <ClinicCard key={clinic.id}>
              <FavoriteButton onClick={() => handleRemoveFavorite(clinic.id)}>
                ❤️
              </FavoriteButton>
              
              <ClinicName>{clinic.name}</ClinicName>
              
              <ClinicInfo>
                <InfoItem>
                  <InfoIcon>📍</InfoIcon>
                  {clinic.address}
                </InfoItem>
                <InfoItem>
                  <InfoIcon>📞</InfoIcon>
                  {clinic.phone}
                </InfoItem>
                <InfoItem>
                  <InfoIcon>📏</InfoIcon>
                  {clinic.distance}
                </InfoItem>
              </ClinicInfo>

              <TagContainer>
                {clinic.specialties.map(specialty => (
                  <Tag key={specialty}>{specialty}</Tag>
                ))}
              </TagContainer>

              <Rating>
                <Stars>{renderStars(clinic.rating)}</Stars>
                <RatingText>
                  {clinic.rating} ({clinic.reviewCount}개 리뷰)
                </RatingText>
              </Rating>

              <ActionButtons>
                <ViewButton to={`/clinic/${clinic.id}`}>
                  상세보기
                </ViewButton>
                <CallButton onClick={() => window.open(`tel:${clinic.phone}`)}>
                  📞
                </CallButton>
              </ActionButtons>
            </ClinicCard>
          ))}
        </ClinicGrid>
      ) : (
        <EmptyState>
          <EmptyIcon>💔</EmptyIcon>
          <EmptyTitle>
            {filter === 'all' ? '즐겨찾기가 비어있습니다' : '해당 조건의 치과가 없습니다'}
          </EmptyTitle>
          <EmptyDescription>
            {filter === 'all' 
              ? '관심 있는 치과를 즐겨찾기에 추가해보세요.'
              : '다른 필터를 선택하거나 전체를 확인해보세요.'
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

export default FavoritesPage;