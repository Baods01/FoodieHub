import { useState, useRef, useEffect } from 'react';
import { Search, X } from 'lucide-react';
import { useUiStore } from '../../store/uiStore';

interface SearchBarProps {
  value: string;
  onChange: (value: string) => void;
  onSearch: (keyword: string) => void;
}

export default function SearchBar({ value, onChange, onSearch }: SearchBarProps) {
  const { searchHistory, addSearchHistory } = useUiStore();
  const [showHistory, setShowHistory] = useState(false);
  const wrapperRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target as Node)) {
        setShowHistory(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (value.trim()) {
      addSearchHistory(value.trim());
      onSearch(value.trim());
    }
    setShowHistory(false);
  };

  const handleHistoryClick = (keyword: string) => {
    onChange(keyword);
    addSearchHistory(keyword);
    onSearch(keyword);
    setShowHistory(false);
  };

  const handleClear = () => {
    onChange('');
  };

  return (
    <div ref={wrapperRef} className="relative w-full">
      <form onSubmit={handleSubmit}>
        <div className="flex gap-2">
          <div className="relative flex-1">
            <Search
              className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"
              size={18}
            />
            <input
              type="text"
              placeholder="搜索店铺名称..."
              value={value}
              onChange={(e) => onChange(e.target.value)}
              onFocus={() => setShowHistory(true)}
              className="w-full pl-10 pr-10 py-2.5 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-orange-400 focus:border-transparent text-sm bg-gray-50/50"
            />
            {value && (
              <button
                type="button"
                onClick={handleClear}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
              >
                <X size={18} />
              </button>
            )}
          </div>
          <button
            type="submit"
            className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-[#FF7E3A] to-[#FF9A5C] text-white text-sm font-medium hover:shadow-lg hover:shadow-orange-200 transition-all duration-200 flex items-center gap-1.5"
          >
            <Search size={16} />
            搜索
          </button>
        </div>
      </form>

      {showHistory && searchHistory.length > 0 && (
        <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-200 rounded-lg shadow-lg z-50">
          {searchHistory.map((keyword) => (
            <button
              key={keyword}
              type="button"
              onClick={() => handleHistoryClick(keyword)}
              className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 first:rounded-t-lg last:rounded-b-lg"
            >
              {keyword}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
