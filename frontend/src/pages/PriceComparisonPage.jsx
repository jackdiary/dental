import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { priceAPI } from '../services/api';
import { SEOUL_DISTRICTS, TREATMENT_TYPES, getTreatmentName, getTreatmentCode } from '../constants/common';

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

const ResultsSection = styled.div`
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
`;

const ResultsHeader = styled.div`
  background: ${props => props.theme.colors.gray50};
  padding: 20px 24px;
  border-bottom: 1px solid ${props => props.theme.colors.gray200};
`;

const ResultsTitle = styled.h2`
  font-size: 1.3rem;
  font-weight: 600;
  color: ${props => props.theme.colors.textPrimary};
  margin-bottom: 8px;
`;

const ResultsCount = styled.p`
  color: ${props => props.theme.colors.textSecondary};
  font-size: 0.9rem;
`;

const PriceTable = styled.div`
  overflow-x: auto;
`;

const Table = styled.table`
  width: 100%;
  border-collapse: collapse;
`;

const TableHeader = styled.thead`
  background: ${props => props.theme.colors.gray50};
`;

const TableRow = styled.tr`
  border-bottom: 1px solid ${props => props.theme.colors.gray200};
  
  &:hover {
    background: ${props => props.theme.colors.gray50};
  }
`;

const TableHeaderCell = styled.th`
  padding: 16px;
  text-align: left;
  font-weight: 600;
  color: ${props => props.theme.colors.textPrimary};
  font-size: 0.9rem;
`;

const TableCell = styled.td`
  padding: 16px;
  color: ${props => props.theme.colors.textPrimary};
`;

const ClinicName = styled.div`
  font-weight: 600;
  margin-bottom: 4px;
`;

const ClinicInfo = styled.div`
  font-size: 0.8rem;
  color: ${props => props.theme.colors.textSecondary};
`;

const Price = styled.div`
  font-size: 1.1rem;
  font-weight: 600;
  color: ${props => props.theme.colors.primary};
`;

const PriceBadge = styled.span`
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: 600;
  margin-left: 8px;
  
  &.lowest {
    background: ${props => props.theme.colors.success}20;
    color: ${props => props.theme.colors.success};
  }
  
  &.highest {
    background: ${props => props.theme.colors.error}20;
    color: ${props => props.theme.colors.error};
  }
  
  &.average {
    background: ${props => props.theme.colors.warning}20;
    color: ${props => props.theme.colors.warning};
  }
`;

const StatsSection = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
`;

const StatCard = styled.div`
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  text-align: center;
`;

const StatValue = styled.div`
  font-size: 1.8rem;
  font-weight: bold;
  color: ${props => props.theme.colors.primary};
  margin-bottom: 8px;
`;

const StatLabel = styled.div`
  font-size: 0.9rem;
  color: ${props => props.theme.colors.textSecondary};
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

function PriceComparisonPage() {
  const [selectedDistrict, setSelectedDistrict] = useState('');
  const [selectedTreatment, setSelectedTreatment] = useState('');
  const [priceData, setPriceData] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);



  const handleSearch = async () => {
    if (!selectedDistrict || !selectedTreatment) {
      alert('지역과 치료 종류를 모두 선택해주세요.');
      return;
    }

    setLoading(true);
    setHasSearched(true);

    try {
      const response = await priceAPI.getComparison({
        district: selectedDistrict,
        treatment_type: selectedTreatment
      });

      setPriceData(response.data.prices || []);
      setStats(response.data.stats || null);
      
      // 결과가 없을 때 메시지 처리
      if (response.data.message) {
        console.log('Price comparison message:', response.data.message);
      }
    } catch (error) {
      console.error('가격 비교 데이터 로드 실패:', error);
      setPriceData([]);
      setStats(null);
    } finally {
      setLoading(false);
    }
  };

  const getPriceBadge = (price, stats) => {
    if (!stats) return null;
    
    const { min_price, max_price, avg_price } = stats;
    
    if (price === min_price) {
      return <PriceBadge className="lowest">최저가</PriceBadge>;
    } else if (price === max_price) {
      return <PriceBadge className="highest">최고가</PriceBadge>;
    } else if (Math.abs(price - avg_price) < avg_price * 0.1) {
      return <PriceBadge className="average">평균</PriceBadge>;
    }
    
    return null;
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('ko-KR').format(price) + '원';
  };



  return (
    <Container>
      <Header>
        <Title>치과 가격 비교</Title>
        <Subtitle>
          지역별, 치료별 가격을 비교하여 합리적인 선택을 도와드립니다.
        </Subtitle>
      </Header>

      <FilterSection>
        <FilterGrid>
          <FilterGroup>
            <Label>지역 선택</Label>
            <Select
              value={selectedDistrict}
              onChange={(e) => setSelectedDistrict(e.target.value)}
            >
              <option value="">지역을 선택하세요</option>
              {SEOUL_DISTRICTS.map(district => (
                <option key={district} value={district}>{district}</option>
              ))}
            </Select>
          </FilterGroup>

          <FilterGroup>
            <Label>치료 종류</Label>
            <Select
              value={selectedTreatment}
              onChange={(e) => setSelectedTreatment(e.target.value)}
            >
              <option value="">치료를 선택하세요</option>
              {TREATMENT_TYPES.map(treatment => (
                <option key={treatment} value={treatment}>
                  {treatment}
                </option>
              ))}
            </Select>
          </FilterGroup>

          <FilterGroup>
            <Label>&nbsp;</Label>
            <SearchButton 
              onClick={handleSearch}
              disabled={loading || !selectedDistrict || !selectedTreatment}
            >
              {loading ? '검색 중...' : '가격 비교'}
            </SearchButton>
          </FilterGroup>
        </FilterGrid>
      </FilterSection>

      {hasSearched && (
        <>
          {stats && (
            <StatsSection>
              <StatCard>
                <StatValue>{formatPrice(stats.min_price)}</StatValue>
                <StatLabel>최저가</StatLabel>
              </StatCard>
              <StatCard>
                <StatValue>{formatPrice(Math.round(stats.avg_price))}</StatValue>
                <StatLabel>평균가</StatLabel>
              </StatCard>
              <StatCard>
                <StatValue>{formatPrice(stats.max_price)}</StatValue>
                <StatLabel>최고가</StatLabel>
              </StatCard>
              <StatCard>
                <StatValue>{stats.sample_count}개</StatValue>
                <StatLabel>비교 대상</StatLabel>
              </StatCard>
            </StatsSection>
          )}

          <ResultsSection>
            <ResultsHeader>
              <ResultsTitle>
                {selectedDistrict} {getTreatmentName(selectedTreatment)} 가격 비교
              </ResultsTitle>
              <ResultsCount>
                {priceData.length}개 치과의 가격 정보
              </ResultsCount>
            </ResultsHeader>

            {loading ? (
              <LoadingSpinner />
            ) : priceData.length > 0 ? (
              <PriceTable>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHeaderCell>치과명</TableHeaderCell>
                      <TableHeaderCell>가격</TableHeaderCell>
                      <TableHeaderCell>주소</TableHeaderCell>
                      <TableHeaderCell>편의시설</TableHeaderCell>
                    </TableRow>
                  </TableHeader>
                  <tbody>
                    {priceData.map((item, index) => (
                      <TableRow key={index}>
                        <TableCell>
                          <ClinicName>{item.clinic_name}</ClinicName>
                          <ClinicInfo>⭐ {item.average_rating || 'N/A'}</ClinicInfo>
                        </TableCell>
                        <TableCell>
                          <Price>
                            {formatPrice(item.price)}
                            {getPriceBadge(item.price, stats)}
                          </Price>
                        </TableCell>
                        <TableCell>
                          <ClinicInfo>{item.address}</ClinicInfo>
                        </TableCell>
                        <TableCell>
                          <ClinicInfo>
                            {item.has_parking && '🅿️ 주차 '}
                            {item.night_service && '🌙 야간 '}
                            {item.weekend_service && '📅 주말'}
                          </ClinicInfo>
                        </TableCell>
                      </TableRow>
                    ))}
                  </tbody>
                </Table>
              </PriceTable>
            ) : (
              <EmptyState>
                <h3>검색 결과가 없습니다</h3>
                <p>선택하신 지역과 치료에 대한 가격 정보가 없습니다.</p>
              </EmptyState>
            )}
          </ResultsSection>
        </>
      )}
    </Container>
  );
}

export default PriceComparisonPage;