import React from 'react';
import footerImg from '../assets/page-footer-with-logo.png';

interface FooterProps {
  className?: string;
  version?: string;
  classification?: string;
}

export const Footer: React.FC<FooterProps> = ({ className = '' }) => {
  return (
    <footer className={`fixed bottom-0 left-0 right-0 z-50 bg-white/95 backdrop-blur-md border-t border-slate-200/80 shadow-xs transition-all ${className}`}>
      <div className="w-full max-w-[800px] mx-auto">
        <div className="flex items-center justify-end h-14 sm:h-16 md:h-18 overflow-hidden">
          {/* Fixed Footer Graphic with Unilever Logo - Fully Responsive across all screens */}
          <img
            src={footerImg}
            alt="Footer Wave and Logo"
            className="h-9 sm:h-11 md:h-13 w-full max-w-full object-contain object-right select-none transition-transform duration-200"
            loading="eager"
          />
        </div>
      </div>
    </footer>
  );
};

export default Footer;
