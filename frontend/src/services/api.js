import axios from 'axios';

// API 기본 설정
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 요청 인터셉터 - 토큰 자동 추가
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 응답 인터셉터 - 토큰 만료 처리
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refreshToken');
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/auth/token/refresh/`, {
            refresh: refreshToken,
          });

          const { access } = response.data;
          localStorage.setItem('token', access);
          
          // 원래 요청 재시도
          originalRequest.headers.Authorization = `Bearer ${access}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        // 리프레시 토큰도 만료된 경우
        localStorage.removeItem('token');
        localStorage.removeItem('refreshToken');
        window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  }
);

// 인증 관련 API
export const authAPI = {
  login: (email, password) => 
    api.post('/auth/login/', { email, password }),
  
  register: (userData) => 
    api.post('/auth/register/', userData),
  
  logout: (refreshToken) => 
    api.post('/auth/logout/', { refresh_token: refreshToken }),
  
  getProfile: () => 
    api.get('/auth/profile/'),
  
  updateProfile: (profileData) => 
    api.patch('/auth/profile/', profileData),
  
  changePassword: (passwordData) => 
    api.post('/auth/change-password/', passwordData),
};

// 치과 관련 API
export const clinicAPI = {
  getList: (params) => 
    api.get('/clinics/', { params }),
  
  getDetail: (id) => 
    api.get(`/clinics/${id}/`),
  
  search: (searchParams) => {
    console.log('API: Searching clinics with params:', searchParams);
    return api.get('/clinics/search/', { params: searchParams })
      .then(response => {
        console.log('API: Search response received:', response.data);
        return response;
      })
      .catch(error => {
        console.error('API: Search failed:', error);
        throw error;
      });
  },
  
  // 위치 기반 검색
  getNearby: (locationParams) => 
    api.get('/clinics/nearby/', { params: locationParams }),
  
  getByDistrict: (districtParams) => 
    api.get('/clinics/by-district/', { params: districtParams }),
  
  // 추천 시스템
  getRecommendations: (recommendationParams) => 
    api.post('/recommendations/', recommendationParams),
  
  getPriceComparison: (comparisonParams) => 
    api.get('/recommendations/price-comparison/', { params: comparisonParams }),
  
  // 통계 및 정보
  getDistricts: () => 
    api.get('/clinics/districts/'),
  
  getSeoulDistricts: () => 
    api.get('/clinics/seoul-districts/'),
  
  getStats: () => 
    api.get('/clinics/stats/'),
  
  getNearbyDistricts: (district, radius) => 
    api.get('/clinics/nearby-districts/', { params: { district, radius } }),
};

// 리뷰 관련 API
export const reviewAPI = {
  getClinicReviews: (clinicId, params = {}) => {
    console.log(`Fetching reviews for clinic ${clinicId}`, params);
    return api.get(`/reviews/clinic/${clinicId}/`, { params });
  },
  
  getReviewStatistics: (clinicId) => 
    api.get(`/reviews/statistics/${clinicId}/`),
  
  searchReviews: (searchParams) => 
    api.get('/reviews/search/', { params: searchParams }),
};

// 가격 비교 API
export const priceAPI = {
  getComparison: (params) => 
    api.get('/price-comparison/', { params }),
  
  getRegionalStats: (params) => 
    api.get('/price-stats/', { params }),
  
  getTreatmentTypes: () => 
    api.get('/treatment-types/'),
};

// 분석 API
export const analysisAPI = {
  getClinicAnalysis: (clinicId) => 
    api.get(`/clinics/${clinicId}/analysis/`),
  
  getClinicReviewsWithAnalysis: (clinicId, params = {}) => 
    api.get(`/clinics/${clinicId}/reviews/`, { params }),
  
  getDistrictSummary: (params = {}) => 
    api.get('/district-analysis/', { params }),
};

// 관리자 API (관리자 권한 필요)
export const adminAPI = {
  triggerCrawling: (crawlingData) => 
    api.post('/reviews/crawl/', crawlingData),
  
  getCrawlingStatus: (clinicId) => 
    api.get(`/reviews/crawl/status/${clinicId}/`),
  
  batchCrawling: (batchData) => 
    api.post('/reviews/crawl/batch/', batchData),
  
  manageReviews: (managementData) => 
    api.post('/reviews/manage/', managementData),
  
  detectDuplicates: (clinicId, threshold) => 
    api.get(`/reviews/duplicates/${clinicId}/`, { params: { threshold } }),
};

// 위치 서비스 API
export const locationAPI = {
  // 주소 ↔ 좌표 변환
  geocodeAddress: (address) => 
    api.post('/clinics/geocode/', { address }),
  
  reverseGeocode: (lat, lng) => 
    api.post('/clinics/reverse-geocode/', { lat, lng }),
  
  // 현재 위치 기반 검색
  getCurrentLocation: () => {
    return new Promise((resolve, reject) => {
      if (!navigator.geolocation) {
        reject(new Error('Geolocation is not supported by this browser.'));
        return;
      }

      navigator.geolocation.getCurrentPosition(
        (position) => {
          resolve({
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
            accuracy: position.coords.accuracy,
          });
        },
        (error) => {
          reject(error);
        },
        {
          enableHighAccuracy: true,
          timeout: 10000,
          maximumAge: 300000, // 5분
        }
      );
    });
  },
  
  // 거리 계산
  calculateDistance: (lat1, lng1, lat2, lng2) => {
    const R = 6371; // 지구 반지름 (km)
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLng = (lng2 - lng1) * Math.PI / 180;
    const a = 
      Math.sin(dLat/2) * Math.sin(dLat/2) +
      Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * 
      Math.sin(dLng/2) * Math.sin(dLng/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c; // 거리 (km)
  },
  
  // 거리 포맷팅
  formatDistance: (distanceKm) => {
    if (distanceKm < 1) {
      return `${Math.round(distanceKm * 1000)}m`;
    } else if (distanceKm < 10) {
      return `${distanceKm.toFixed(1)}km`;
    } else {
      return `${Math.round(distanceKm)}km`;
    }
  },
};

// 유틸리티 API
export const utilAPI = {
  healthCheck: () => 
    api.get('/health/'),
  
  getTreatmentTypes: () => 
    api.get('/treatment-types/'),
};

// 메인 API 객체도 named export로 제공
export { api };

export default api;