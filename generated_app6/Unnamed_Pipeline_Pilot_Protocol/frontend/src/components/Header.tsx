import React from 'react';
import headerImg from '../assets/blank-header.png';
import subHeaderImg from '../assets/blank-page-header.png';
interface HeaderProps {
  className?: string;
  title?: string;
}

export const Header: React.FC<HeaderProps> = ({
  className = '',
  title = 'Import from External Model',
}) => {
  return (
    <header
      className={`fixed top-0 left-0 right-0 z-50 bg-white/95 backdrop-blur-md border-b border-slate-200/80 shadow-xs transition-all flex flex-col ${className}`}
    >
    
      <div className="w-full max-w-none flex flex-col">
        {/* Tier 1 (Top Pic): blank-page-header.png with text "Import from External Model" */}
        <div className="relative flex items-center justify-end pt-1 sm:pt-1.5 overflow-hidden">
          <img
            src={subHeaderImg}
            alt="Top Header Ribbon"
            className="h-6 sm:h-8 md:h-10 w-full max-w-full object-contain sm:object-cover md:object-contain object-right select-none transition-transform duration-200"
            //className="w-full block"

            loading="eager"
          />
          {/* Text inside top picture shifted rightwards to remain comfortably within the banner */}
          <div className="absolute inset-0 flex items-center justify-start pl-16 sm:pl-24 md:pl-32 lg:pl-40 pr-6 pointer-events-none">
            <span className="text-white font-bold text-xs sm:text-sm md:text-base tracking-wide drop-shadow-xs select-none">
              <div
                style={{
                    position: 'absolute',
                    top: '25px',
                    left: '220px',
                    color: 'white',
                    fontSize: '35px',
                    fontWeight: 'bold'
                }}
            >
                {title}
            </div>  
            </span>
          </div>
        </div>

        {/* Tier 2 (Bottom Pic): blank-header.png positioned directly below */}
        <div className="flex items-center justify-end pb-1 sm:pb-1.5 translate-x-6">
          <img
            src={headerImg}
            alt="Bottom Header Ribbon"
            className="h-5 sm:h-7 md:h-9  border-2 border-red- max-w-full object-cover object-right select-none -mt-0.5 sm:-mt-1 -mr-10"
            loading="eager"
            style={{
              height: '50px',
              width: '1000px',
              transform: 'translateX(100px)'
            }}
          />
        </div>
      </div>
    </header>
  );
};

export default Header;
