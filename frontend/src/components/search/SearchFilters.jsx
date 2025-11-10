import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { SEOUL_DISTRICTS, TREATMENT_TYPES, FACILITY_OPTIONS, RATING_OPTIONS } from '../../constants/common';

const FiltersContainer = styled.div`
  background: ${props => props.theme.colors.white};
  border-radius: ${props => props.theme.borderRadius.xl};
  box-shadow: ${props => props.theme.shadows.base};
  padding: 24px;
  position: sticky;
  top: 90px;
  width: 100%;
  box-sizing: border-box;

  @media (max-width: ${props => props.theme.breakpoints.desktop}) {
    position: static;
  }
  
  @media (max-width: ${props => props.theme.breakpoints.tablet}) {
    padding: 20px;
  }
  
  @media (max-width: ${props => props.theme.breakpoints.mobile}) {
    padding: 16px;
  }
`;

const FiltersTitle = styled.h3`
  font-size: ${props => props.theme.fonts.sizes.lg};
  font-weight: ${props => props.theme.fonts.weights.semibold};
  color: ${props => props.theme.colors.textPrimary};
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid ${props => props.theme.colors.gray200};
`;

const FilterGroup = styled.div`
  margin-bottom: 24px;

  &:last-child {
    margin-bottom: 0;
  }
`;

const FilterLabel = styled.label`
  display: block;
  font-size: ${props => props.theme.fonts.sizes.sm};
  font-weight: ${props => props.theme.fonts.weights.medium};
  color: ${props => props.theme.colors.textPrimary};
  margin-bottom: 8px;
`;

const FilterSelect = styled.select`
  width: 100%;
  padding: 12px 16px;
  border: 1px solid ${props => props.theme.colors.gray300};
  border-radius: ${props => props.theme.borderRadius.md};
  font-size: ${props => props.theme.fonts.sizes.sm};
  background: ${props => props.theme.colors.white};
  color: ${props => props.theme.colors.textPrimary};
  transition: border-color ${props => props.theme.transitions.fast};

  &:focus {
    outline: none;
    border-color: ${props => props.theme.colors.primary};
  }
`;

const CheckboxGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const CheckboxItem = styled.label`
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: ${props => props.theme.fonts.sizes.sm};
  color: ${props => props.theme.colors.textPrimary};
  transition: color ${props => props.theme.transitions.fast};

  &:hover {
    color: ${props => props.theme.colors.primary};
  }
`;

const Checkbox = styled.input`
  width: 16px;
  height: 16px;
  accent-color: ${props => props.theme.colors.primary};
`;

const RangeGroup = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
`;

const RangeInput = styled.input`
  width: 80%;
  flex: 1;
  padding: 8px 12px;
  border: 1px solid ${props => props.theme.colors.gray300};
  border-radius: ${props => props.theme.borderRadius.md};
  font-size: ${props => props.theme.fonts.sizes.sm};
  text-align: center;

  &:focus {
    outline: none;
    border-color: ${props => props.theme.colors.primary};
  }
`;

const RangeSeparator = styled.span`
  color: ${props => props.theme.colors.textSecondary};
  font-size: ${props => props.theme.fonts.sizes.sm};
`;

const FilterActions = styled.div`
  display: flex;
  gap: 8px;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid ${props => props.theme.colors.gray200};
`;

const ApplyButton = styled.button`
  flex: 1;
  background: ${props => props.theme.colors.primary};
  color: ${props => props.theme.colors.white};
  padding: 12px 16px;
  border-radius: ${props => props.theme.borderRadius.md};
  font-size: ${props => props.theme.fonts.sizes.sm};
  font-weight: ${props => props.theme.fonts.weights.medium};
  transition: background ${props => props.theme.transitions.fast};

  &:hover {
    background: ${props => props.theme.colors.primaryDark};
  }
`;

const ResetButton = styled.button`
  background: ${props => props.theme.colors.gray200};
  color: ${props => props.theme.colors.textSecondary};
  padding: 12px 16px;
  border-radius: ${props => props.theme.borderRadius.md};
  font-size: ${props => props.theme.fonts.sizes.sm};
  font-weight: ${props => props.theme.fonts.weights.medium};
  transition: all ${props => props.theme.transitions.fast};

  &:hover {
    background: ${props => props.theme.colors.gray300};
    color: ${props => props.theme.colors.textPrimary};
  }
`;

const ActiveFiltersCount = styled.div`
  background: ${props => props.theme.colors.primary};
  color: ${props => props.theme.colors.white};
  font-size: ${props => props.theme.fonts.sizes.xs};
  font-weight: ${props => props.theme.fonts.weights.bold};
  padding: 2px 6px;
  border-radius: ${props => props.theme.borderRadius.sm};
  min-width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
`;

function SearchFilters({ initialFilters = {}, onFilterChange }) {
  const [filters, setFilters] = useState({
    district: initialFilters.district || '',
    treatment: initialFilters.treatment || '',
    services: [],
    priceRange: { min: '', max: '' },
    rating: '',
    ...initialFilters
  });

  const [activeFiltersCount, setActiveFiltersCount] = useState(0);

  useEffect(() => {
    // 활성 필터 개수 계산
    let count = 0;
    if (filters.district) count++;
    if (filters.treatment) count++;
    if (filters.services.length > 0) count++;
    if (filters.priceRange.min || filters.priceRange.max) count++;
    if (filters.rating) count++;

    setActiveFiltersCount(count);
  }, [filters]);

  const handleSelectChange = (name, value) => {
    setFilters(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleCheckboxChange = (service, checked) => {
    setFilters(prev => ({
      ...prev,
      services: checked
        ? [...prev.services, service]
        : prev.services.filter(s => s !== service)
    }));
  };

  const handlePriceRangeChange = (type, value) => {
    setFilters(prev => ({
      ...prev,
      priceRange: {
        ...prev.priceRange,
        [type]: value
      }
    }));
  };

  const handleApplyFilters = () => {
    const cleanFilters = {};

    if (filters.district) cleanFilters.district = filters.district;
    if (filters.treatment) cleanFilters.treatment = filters.treatment;
    if (filters.services.length > 0) cleanFilters.services = filters.services.join(',');
    if (filters.priceRange.min) cleanFilters.priceMin = filters.priceRange.min;
    if (filters.priceRange.max) cleanFilters.priceMax = filters.priceRange.max;
    if (filters.rating) cleanFilters.rating = filters.rating;

    onFilterChange(cleanFilters);
  };

  const handleResetFilters = () => {
    const resetFilters = {
      district: '',
      treatment: '',
      services: [],
      priceRange: { min: '', max: '' },
      rating: ''
    };

    setFilters(resetFilters);
    onFilterChange({});
  };

  return (
    <FiltersContainer>
      <FiltersTitle>
        검색 필터
        {activeFiltersCount > 0 && (
          <ActiveFiltersCount>{activeFiltersCount}</ActiveFiltersCount>
        )}
      </FiltersTitle>

      <FilterGroup>
        <FilterLabel>지역</FilterLabel>
        <FilterSelect
          value={filters.district}
          onChange={(e) => handleSelectChange('district', e.target.value)}
        >
          <option value="">전체 지역</option>
          {SEOUL_DISTRICTS.map(district => (
            <option key={district} value={district}>{district}</option>
          ))}
        </FilterSelect>
      </FilterGroup>

      <FilterGroup>
        <FilterLabel>치료 종류</FilterLabel>
        <FilterSelect
          value={filters.treatment}
          onChange={(e) => handleSelectChange('treatment', e.target.value)}
        >
          <option value="">전체 치료</option>
          {TREATMENT_TYPES.map(treatment => (
            <option key={treatment} value={treatment}>{treatment}</option>
          ))}
        </FilterSelect>
      </FilterGroup>

      <FilterGroup>
        <FilterLabel>편의시설</FilterLabel>
        <CheckboxGroup>
          {FACILITY_OPTIONS.map(option => (
            <CheckboxItem key={option.key}>
              <Checkbox
                type="checkbox"
                checked={filters.services.includes(option.key)}
                onChange={(e) => handleCheckboxChange(option.key, e.target.checked)}
              />
              {option.label}
            </CheckboxItem>
          ))}
        </CheckboxGroup>
      </FilterGroup>

      <FilterGroup>
        <FilterLabel>가격 범위 (만원)</FilterLabel>
        <RangeGroup>
          <RangeInput
            type="number"
            placeholder="최소"
            value={filters.priceRange.min}
            onChange={(e) => handlePriceRangeChange('min', e.target.value)}
          />
          <RangeSeparator>~</RangeSeparator>
          <RangeInput
            type="number"
            placeholder="최대"
            value={filters.priceRange.max}
            onChange={(e) => handlePriceRangeChange('max', e.target.value)}
          />
        </RangeGroup>
      </FilterGroup>

      <FilterGroup>
        <FilterLabel>최소 평점</FilterLabel>
        <FilterSelect
          value={filters.rating}
          onChange={(e) => handleSelectChange('rating', e.target.value)}
        >
          <option value="">전체</option>
          {RATING_OPTIONS.map(option => (
            <option key={option.value} value={option.value}>{option.label}</option>
          ))}
        </FilterSelect>
      </FilterGroup>

      <FilterActions>
        <ResetButton onClick={handleResetFilters}>
          초기화
        </ResetButton>
        <ApplyButton onClick={handleApplyFilters}>
          적용하기
        </ApplyButton>
      </FilterActions>
    </FiltersContainer>
  );
}

export default SearchFilters;