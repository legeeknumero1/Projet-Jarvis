import React from 'react';

const MessageItem = ({ role, text, timestamp }) => {
  const isUser = role === 'user';
  
  return (
    <div 
      className={`
        my-4 px-6 py-4 rounded-xl backdrop-blur-md relative
        ${isUser 
          ? 'ml-[20%] text-right bg-gradient-to-br from-cyan-500/10 to-blue-500/5 border border-cyan-500/30' 
          : 'mr-[20%] bg-gradient-to-br from-white/5 to-gray-200/2 border border-white/10'
        }
      `}
    >
      <div className="text-white leading-relaxed">
        {text}
      </div>
      
      {/* Bulle pointer */}
      <div 
        className={`
          absolute top-1/2 -translate-y-1/2 w-0 h-0 
          ${isUser 
            ? '-right-2 border-l-[8px] border-l-cyan-500/30 border-y-[8px] border-y-transparent' 
            : '-left-2 border-r-[8px] border-r-white/10 border-y-[8px] border-y-transparent'
          }
        `}
      />
    </div>
  );
};

export default MessageItem;