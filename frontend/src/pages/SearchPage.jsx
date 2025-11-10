import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import styled from 'styled-components';
import { clinicAPI } from '../services/api';
import ClinicCard from '../components/clinic/ClinicCard';
import SearchFilters from '../components/search/SearchFilters';
import LocationSearch from '../components/search/LocationSearch';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { getTreatmentName, SORT_OPTIONS } from '../constants/common';

const SearchContainer = styled.div`
  min-height: calc(100vh - 140px);
  background: ${props => props.theme.colors.backgroundGray};
`;

const SearchContent = styled.div`
  max-width: 1400px;
  margin: 0 auto;
  padding: 32px 20px;
  display: grid;
  grid-template-columns: 350px 1fr;
  gap: 32px;
  width: 100%;
  box-sizing: border-box;

  @media (max-width: ${props => props.theme.breakpoints.desktop}) {
    grid-template-columns: 1fr;
    gap: 24px;
    max-width: 100%;
  }

  @media (max-width: ${props => props.theme.breakpoints.tablet}) {
    padding: 24px 16px;
    gap: 20px;
  }

  @media (max-width: ${props => props.theme.breakpoints.mobile}) {
    padding: 16px 12px;
    gap: 16px;
  }
`;

const FiltersSection = styled.aside`
  width: 100%;
  min-width: 0;
  
  @media (max-width: ${props => props.theme.breakpoints.desktop}) {
    order: 2;
  }
`;

const ResultsSection = styled.main`
  width: 100%;
  min-width: 0;
  overflow: hidden;
  
  @media (max-width: ${props => props.theme.breakpoints.desktop}) {
    order: 1;
  }
`;

const SearchHeader = styled.div`
  background: ${props => props.theme.colors.white};
  padding: 24px;
  border-radius: ${props => props.theme.borderRadius.xl};
  box-shadow: ${props => props.theme.shadows.base};
  margin-bottom: 24px;
`;

const SearchTitle = styled.h1`
  font-size: ${props => props.theme.fonts.sizes['2xl']};
  font-weight: ${props => props.theme.fonts.weights.bold};
  color: ${props => props.theme.colors.textPrimary};
  margin-bottom: 8px;
`;

const SearchInfo = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;

  @media (max-width: ${props => props.theme.breakpoints.mobile}) {
    flex-direction: column;
    align-items: flex-start;
  }
`;

const ResultCount = styled.p`
  color: ${props => props.theme.colors.textSecondary};
  font-size: ${props => props.theme.fonts.sizes.base};
`;

const SortOptions = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
`;

const SortLabel = styled.span`
  color: ${props => props.theme.colors.textSecondary};
  font-size: ${props => props.theme.fonts.sizes.sm};
`;

const SortSelect = styled.select`
  padding: 8px 12px;
  border: 1px solid ${props => props.theme.colors.gray300};
  border-radius: ${props => props.theme.borderRadius.md};
  font-size: ${props => props.theme.fonts.sizes.sm};
  background: ${props => props.theme.colors.white};
  color: ${props => props.theme.colors.textPrimary};

  &:focus {
    outline: none;
    border-color: ${props => props.theme.colors.primary};
  }
`;

const ResultsList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

const NoResults = styled.div`
  background: ${props => props.theme.colors.white};
  padding: 48px 24px;
  border-radius: ${props => props.theme.borderRadius.xl};
  box-shadow: ${props => props.theme.shadows.base};
  text-align: center;

  h3 {
    font-size: ${props => props.theme.fonts.sizes.xl};
    font-weight: ${props => props.theme.fonts.weights.semibold};
    color: ${props => props.theme.colors.textPrimary};
    margin-bottom: 16px;
  }

  p {
    color: ${props => props.theme.colors.textSecondary};
    font-size: ${props => props.theme.fonts.sizes.base};
    line-height: 1.6;
    margin-bottom: 24px;
  }
`;

const NoResultsIcon = styled.div`
  width: 80px;
  height: 80px;
  background: ${props => props.theme.colors.gray200};
  border-radius: 50%;
  margin: 0 auto 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;

  &::before {
    content: '';
    width: 40px;
    height: 40px;
    border: 3px solid ${props => props.theme.colors.gray400};
    border-radius: 50%;
  }

  &::after {
    content: '';
    width: 3px;
    height: 16px;
    background: ${props => props.theme.colors.gray400};
    transform: rotate(45deg);
    position: absolute;
    bottom: 16px;
    right: 16px;
  }
`;

const RetryButton = styled.button`
  background: ${props => props.theme.colors.primary};
  color: ${props => props.theme.colors.white};
  padding: 12px 24px;
  border-radius: ${props => props.theme.borderRadius.md};
  font-weight: ${props => props.theme.fonts.weights.medium};
  transition: background ${props => props.theme.transitions.fast};

  &:hover {
    background: ${props => props.theme.colors.primaryDark};
  }
`;

const LoadingContainer = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 200px;
`;

const Pagination = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  margin-top: 32px;
`;

const PageButton = styled.button`
  padding: 8px 12px;
  border: 1px solid ${props => props.theme.colors.gray300};
  border-radius: ${props => props.theme.borderRadius.md};
  background: ${props => props.active ? props.theme.colors.primary : props.theme.colors.white};
  color: ${props => props.active ? props.theme.colors.white : props.theme.colors.textPrimary};
  font-size: ${props => props.theme.fonts.sizes.sm};
  transition: all ${props => props.theme.transitions.fast};

  &:hover:not(:disabled) {
    background: ${props => props.active ? props.theme.colors.primaryDark : props.theme.colors.gray50};
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

function SearchPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [clinics, setClinics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [totalCount, setTotalCount] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [sortBy, setSortBy] = useState('recommended');

  const district = searchParams.get('district') || '';
  const treatment = searchParams.get('treatment') || '';

  useEffect(() => {
    fetchClinics();
  }, [searchParams, currentPage, sortBy]);

  const fetchClinics = async () => {
    try {
      setLoading(true);
      setError(null);

      const params = {
        page: currentPage,
        sort: sortBy,
        page_size: 4,
      };

      if (district) params.district = district;
      if (treatment) params.treatment = treatment;

      console.log('Searching clinics with params:', params);
      const response = await clinicAPI.search(params);
      console.log('Search response:', response.data);

      setClinics(response.data.results || []);
      setTotalCount(response.data.count || 0);
    } catch (err) {
      console.error('Failed to fetch clinics:', err);
      console.error('Error details:', err.response?.data);

      if (err.response?.status === 404) {
        setError('검색 결과가 없습니다.');
      } else if (err.response?.status >= 500) {
        setError('서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.');
      } else if (err.code === 'NETWORK_ERROR' || !err.response) {
        setError('네트워크 연결을 확인해주세요.');
      } else {
        setError('치과 정보를 불러오는데 실패했습니다.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (newFilters) => {
    const newSearchParams = new URLSearchParams();

    Object.entries(newFilters).forEach(([key, value]) => {
      if (value) {
        newSearchParams.append(key, value);
      }
    });

    setSearchParams(newSearchParams);
    setCurrentPage(1);
  };

  const handleSortChange = (e) => {
    setSortBy(e.target.value);
    setCurrentPage(1);
  };

  const handlePageChange = (page) => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const getSearchTitle = () => {
    if (district && treatment) {
      return `${district} ${getTreatmentName(treatment)} 치과`;
    } else if (district) {
      return `${district} 치과`;
    } else if (treatment) {
      return `${getTreatmentName(treatment)} 치과`;
    }
    return '치과 검색 결과';
  };



  const totalPages = Math.ceil(totalCount / 10);

  return (
    <SearchContainer>
      <SearchContent>
        <FiltersSection>
          <LocationSearch
            onSearchResults={(results) => {
              setClinics(results.results || []);
              setTotalCount(results.count || 0);
              setCurrentPage(1);
            }}
            onLoading={setLoading}
          />
          <SearchFilters
            initialFilters={{ district, treatment }}
            onFilterChange={handleFilterChange}
          />
        </FiltersSection>

        <ResultsSection>
          <SearchHeader>
            <SearchTitle>{getSearchTitle()}</SearchTitle>
            <SearchInfo>
              <ResultCount>
                총 {totalCount.toLocaleString()}개의 치과를 찾았습니다
              </ResultCount>
              <SortOptions>
                <SortLabel>정렬:</SortLabel>
                <SortSelect value={sortBy} onChange={handleSortChange}>
                  {SORT_OPTIONS.map(option => (
                    <option key={option.value} value={option.value}>{option.label}</option>
                  ))}
                </SortSelect>
              </SortOptions>
            </SearchInfo>
          </SearchHeader>

          {loading ? (
            <LoadingContainer>
              <LoadingSpinner />
            </LoadingContainer>
          ) : error ? (
            <NoResults>
              <NoResultsIcon />
              <h3>오류가 발생했습니다</h3>
              <p>{error}</p>
              <RetryButton onClick={fetchClinics}>
                다시 시도
              </RetryButton>
            </NoResults>
          ) : clinics.length === 0 ? (
            <NoResults>
              <NoResultsIcon />
              <h3>검색 결과가 없습니다</h3>
              <p>
                다른 지역이나 치료 종류로 검색해보시거나,<br />
                검색 조건을 변경해보세요.
              </p>
              <RetryButton onClick={() => handleFilterChange({})}>
                전체 보기
              </RetryButton>
            </NoResults>
          ) : (
            <>
              <ResultsList>
                {clinics.map((clinic) => (
                  <ClinicCard key={clinic.id} clinic={clinic} />
                ))}
              </ResultsList>

              {totalPages > 1 && (
                <Pagination>
                  <PageButton
                    onClick={() => handlePageChange(currentPage - 1)}
                    disabled={currentPage === 1}
                  >
                    이전
                  </PageButton>

                  {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                    const page = Math.max(1, Math.min(totalPages - 4, currentPage - 2)) + i;
                    return (
                      <PageButton
                        key={page}
                        active={page === currentPage}
                        onClick={() => handlePageChange(page)}
                      >
                        {page}
                      </PageButton>
                    );
                  })}

                  <PageButton
                    onClick={() => handlePageChange(currentPage + 1)}
                    disabled={currentPage === totalPages}
                  >
                    다음
                  </PageButton>
                </Pagination>
              )}
            </>
          )}
        </ResultsSection>
      </SearchContent>
    </SearchContainer>
  );
}

export default SearchPage;