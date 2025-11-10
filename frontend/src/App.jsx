import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { ThemeProvider } from 'styled-components';
import styled from 'styled-components';
import theme from './styles/theme';

// Components
import Header from './components/layout/Header';
import Footer from './components/layout/Footer';

// Pages
import HomePage from './pages/HomePage';
import SearchPage from './pages/SearchPage';
import ClinicDetailPage from './pages/ClinicDetailPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import MyPage from './pages/MyPage';
import PriceComparisonPage from './pages/PriceComparisonPage';
import ReviewAnalysisPage from './pages/ReviewAnalysisPage';
import AboutPage from './pages/AboutPage';
import FavoritesPage from './pages/FavoritesPage';
import HistoryPage from './pages/HistoryPage';

// Context
import { AuthProvider } from './contexts/AuthContext';

const AppContainer = styled.div`
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  width: 100%;
  max-width: 100vw;
  overflow-x: hidden;
`;

const MainContent = styled.main`
  flex: 1;
  width: 100%;
  box-sizing: border-box;
`;

function App() {
  return (
    <ThemeProvider theme={theme}>
      <AuthProvider>
        <AppContainer>
          <Header />
          <MainContent>
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/search" element={<SearchPage />} />
              <Route path="/clinic/:id" element={<ClinicDetailPage />} />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
              <Route path="/mypage" element={<MyPage />} />
              <Route path="/price-compare" element={<PriceComparisonPage />} />
              <Route path="/reviews" element={<ReviewAnalysisPage />} />
              <Route path="/about" element={<AboutPage />} />
              <Route path="/favorites" element={<FavoritesPage />} />
              <Route path="/history" element={<HistoryPage />} />
            </Routes>
          </MainContent>
          <Footer />
        </AppContainer>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;