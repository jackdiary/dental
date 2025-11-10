import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { clinicAPI, locationAPI } from '../../services/api';

const LocationSearchContainer = styled.div`
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  margin-bottom: 24px;
  width: 100%;
  box-sizing: border-box;
  
  @media (max-width: ${props => props.theme.breakpoints.tablet}) {
    padding: 20px;
    margin-bottom: 20px;
  }
  
  @media (max-width: ${props => props.theme.breakpoints.mobile}) {
    padding: 16px;
    margin-bottom: 16px;
  }
`;

const SearchHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 12px;
  
  @media (max-width: ${props => props.theme.breakpoints.mobile}) {
    flex-direction: column;
    align-items: flex-start;
  }
`;

const SearchTitle = styled.h3`
  margin: 0;
  color: ${props => props.theme.colors.primary};
  font-size: 18px;
  font-weight: 600;
`;

const LocationButton = styled.button`
  background: ${props => props.theme.colors.primary};
  color: white;
  border: none;
  border-radius: 8px;
  padding: 8px 16px;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: auto;
  
  &:hover {
    background: ${props => props.theme.colors.primaryDark};
  }
  
  &:disabled {
    background: #ccc;
    cursor: not-allowed;
  }
`;

const SearchForm = styled.form`
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

const InputGroup = styled.div`
  display: flex;
  gap: 12px;
  align-items: end;
  flex-wrap: wrap;
  
  @media (max-width: ${props => props.theme.breakpoints.tablet}) {
    flex-direction: column;
    align-items: stretch;
    gap: 16px;
  }
`;

const InputWrapper = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
  
  @media (max-width: ${props => props.theme.breakpoints.tablet}) {
    flex: none;
    width: 100%;
  }
`;

const Label = styled.label`
  font-size: 14px;
  font-weight: 500;
  color: #333;
`;

const Input = styled.input`
  padding: 12px;
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  font-size: 14px;
  width: 100%;
  box-sizing: border-box;
  
  &:focus {
    outline: none;
    border-color: ${props => props.theme.colors.primary};
  }
`;

const Select = styled.select`
  padding: 12px;
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  font-size: 14px;
  background: white;
  width: 100%;
  box-sizing: border-box;
  
  &:focus {
    outline: none;
    border-color: ${props => props.theme.colors.primary};
  }
`;

const SearchButton = styled.button`
  background: ${props => props.theme.colors.secondary};
  color: white;
  border: none;
  border-radius: 8px;
  padding: 12px 24px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  height: fit-content;
  white-space: nowrap;
  
  &:hover {
    background: ${props => props.theme.colors.secondaryDark};
  }
  
  &:disabled {
    background: #ccc;
    cursor: not-allowed;
  }
  
  @media (max-width: ${props => props.theme.breakpoints.tablet}) {
    width: 100%;
    padding: 14px 24px;
  }
`;

const CurrentLocationInfo = styled.div`
  background: #f8f9fa;
  border-radius: 8px;
  padding: 12px;
  margin-top: 12px;
  font-size: 14px;
  color: #666;
`;

const ErrorMessage = styled.div`
  background: #fee;
  color: #c33;
  padding: 12px;
  border-radius: 8px;
  font-size: 14px;
  margin-top: 12px;
`;

const LocationSearch = ({ onSearchResults, onLoading }) => {
  const [searchType, setSearchType] = useState('district'); // 'district', 'nearby', 'address'
  const [district, setDistrict] = useState('');
  const [address, setAddress] = useState('');
  const [radius, setRadius] = useState(5);
  const [currentLocation, setCurrentLocation] = useState(null);
  const [districts, setDistricts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [locationLoading, setLocationLoading] = useState(false);

  // 지역구 목록 로드
  useEffect(() => {
    const loadDistricts = async () => {
      try {
        const response = await clinicAPI.getSeoulDistricts();
        setDistricts(response.data.districts);
      } catch (error) {
        console.error('지역구 목록 로드 실패:', error);
      }
    };

    loadDistricts();
  }, []);

  // 현재 위치 가져오기
  const getCurrentLocation = async () => {
    setLocationLoading(true);
    setError('');

    try {
      const location = await locationAPI.getCurrentLocation();
      setCurrentLocation(location);
      
      // 현재 위치의 주소 정보 가져오기
      try {
        const addressResponse = await locationAPI.reverseGeocode(
          location.latitude, 
          location.longitude
        );
        
        if (addressResponse.data.success) {
          setCurrentLocation(prev => ({
            ...prev,
            address: addressResponse.data.address,
            district: addressResponse.data.district
          }));
        }
      } catch (addressError) {
        console.error('주소 변환 실패:', addressError);
      }
      
    } catch (error) {
      setError('위치 정보를 가져올 수 없습니다. 브라우저 설정을 확인해주세요.');
    } finally {
      setLocationLoading(false);
    }
  };

  // 검색 실행
  const handleSearch = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    onLoading?.(true);

    try {
      let response;

      switch (searchType) {
        case 'district':
          if (!district) {
            throw new Error('지역구를 선택해주세요.');
          }
          
          const districtParams = { district, limit: 20 };
          if (currentLocation) {
            districtParams.lat = currentLocation.latitude;
            districtParams.lng = currentLocation.longitude;
            districtParams.radius = radius;
          }
          
          response = await clinicAPI.getByDistrict(districtParams);
          break;

        case 'nearby':
          if (!currentLocation) {
            throw new Error('현재 위치를 먼저 가져와주세요.');
          }
          
          response = await clinicAPI.getNearby({
            lat: currentLocation.latitude,
            lng: currentLocation.longitude,
            radius: radius,
            limit: 20
          });
          break;

        case 'address':
          if (!address) {
            throw new Error('주소를 입력해주세요.');
          }
          
          // 주소를 좌표로 변환
          const geocodeResponse = await locationAPI.geocodeAddress(address);
          if (!geocodeResponse.data.success) {
            throw new Error('주소를 찾을 수 없습니다.');
          }
          
          const coords = geocodeResponse.data.coordinates;
          response = await clinicAPI.getNearby({
            lat: coords.latitude,
            lng: coords.longitude,
            radius: radius,
            limit: 20
          });
          break;

        default:
          throw new Error('검색 방식을 선택해주세요.');
      }

      onSearchResults?.(response.data);

    } catch (error) {
      setError(error.message || '검색 중 오류가 발생했습니다.');
      onSearchResults?.({ results: [], count: 0 });
    } finally {
      setLoading(false);
      onLoading?.(false);
    }
  };

  return (
    <LocationSearchContainer>
      <SearchHeader>
        <SearchTitle>위치 기반 치과 검색</SearchTitle>
        <LocationButton 
          type="button"
          onClick={getCurrentLocation}
          disabled={locationLoading}
        >
          📍 {locationLoading ? '위치 확인 중...' : '현재 위치'}
        </LocationButton>
      </SearchHeader>

      <SearchForm onSubmit={handleSearch}>
        <InputGroup>
          <InputWrapper>
            <Label>검색 방식</Label>
            <Select 
              value={searchType} 
              onChange={(e) => setSearchType(e.target.value)}
            >
              <option value="district">지역구별 검색</option>
              <option value="nearby">현재 위치 기준</option>
              <option value="address">주소 기준</option>
            </Select>
          </InputWrapper>

          {searchType === 'district' && (
            <InputWrapper>
              <Label>지역구</Label>
              <Select 
                value={district} 
                onChange={(e) => setDistrict(e.target.value)}
                required
              >
                <option value="">지역구 선택</option>
                {districts.map(d => (
                  <option key={d.name} value={d.name}>
                    {d.name} ({d.clinic_count}개)
                  </option>
                ))}
              </Select>
            </InputWrapper>
          )}

          {searchType === 'address' && (
            <InputWrapper>
              <Label>주소</Label>
              <Input
                type="text"
                value={address}
                onChange={(e) => setAddress(e.target.value)}
                placeholder="예: 서울시 강남구 테헤란로 427"
                required
              />
            </InputWrapper>
          )}

          {(searchType === 'nearby' || searchType === 'address' || 
            (searchType === 'district' && currentLocation)) && (
            <InputWrapper>
              <Label>검색 반경</Label>
              <Select 
                value={radius} 
                onChange={(e) => setRadius(Number(e.target.value))}
              >
                <option value={1}>1km</option>
                <option value={3}>3km</option>
                <option value={5}>5km</option>
                <option value={10}>10km</option>
                <option value={20}>20km</option>
              </Select>
            </InputWrapper>
          )}

          <SearchButton type="submit" disabled={loading}>
            {loading ? '검색 중...' : '검색'}
          </SearchButton>
        </InputGroup>
      </SearchForm>

      {currentLocation && (
        <CurrentLocationInfo>
          📍 현재 위치: {currentLocation.address || 
            `위도 ${currentLocation.latitude.toFixed(4)}, 경도 ${currentLocation.longitude.toFixed(4)}`}
          {currentLocation.district && ` (${currentLocation.district})`}
        </CurrentLocationInfo>
      )}

      {error && (
        <ErrorMessage>
          {error}
        </ErrorMessage>
      )}
    </LocationSearchContainer>
  );
};

export default LocationSearch;