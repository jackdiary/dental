import React from 'react';
import styled, { keyframes } from 'styled-components';

const spin = keyframes`
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
`;

const SpinnerContainer = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  padding: ${props => props.size === 'large' ? '48px' : '24px'};
`;

const Spinner = styled.div`
  width: ${props => {
    switch (props.size) {
      case 'small': return '20px';
      case 'large': return '48px';
      default: return '32px';
    }
  }};
  height: ${props => {
    switch (props.size) {
      case 'small': return '20px';
      case 'large': return '48px';
      default: return '32px';
    }
  }};
  border: ${props => {
    switch (props.size) {
      case 'small': return '2px';
      case 'large': return '4px';
      default: return '3px';
    }
  }} solid ${props => props.theme.colors.gray200};
  border-top: ${props => {
    switch (props.size) {
      case 'small': return '2px';
      case 'large': return '4px';
      default: return '3px';
    }
  }} solid ${props => props.theme.colors.primary};
  border-radius: 50%;
  animation: ${spin} 1s linear infinite;
`;

const LoadingText = styled.p`
  margin-top: 16px;
  color: ${props => props.theme.colors.textSecondary};
  font-size: ${props => props.theme.fonts.sizes.sm};
  text-align: center;
`;

function LoadingSpinner({ size = 'medium', text, className }) {
  return (
    <SpinnerContainer className={className}>
      <div>
        <Spinner size={size} />
        {text && <LoadingText>{text}</LoadingText>}
      </div>
    </SpinnerContainer>
  );
}

export default LoadingSpinner;