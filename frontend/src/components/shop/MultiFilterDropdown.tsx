import { useState, useRef, useEffect } from 'react';
import { ChevronDown } from 'lucide-react';

interface MultiFilterDropdownProps {
  label: string;
  options: string[];
  values: string[];
  onChange: (values: string[]) => void;
}

export default function MultiFilterDropdown({ label, options, values, onChange }: MultiFilterDropdownProps) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const isActive = values.length > 0;
  const displayValue = isActive ? values.join(', ') : '全部';

  const toggle = (opt: string) => {
    if (values.includes(opt)) {
      onChange(values.filter((v) => v !== opt));
    } else {
      onChange([...values, opt]);
    }
  };

  return (
    <div ref={ref} className="relative">
      <button
        type="button"
        onClick={() => setOpen(!open)}
        className={`flex items-center gap-1 px-3 py-1.5 text-sm border rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-400 ${
          isActive
            ? 'border-orange-400 text-orange-600 bg-orange-50'
            : 'border-gray-300 text-gray-700 bg-white'
        }`}
      >
        <span className="max-w-[120px] truncate">
          {label}: {displayValue}
        </span>
        <ChevronDown size={14} className="flex-shrink-0" />
      </button>

      {open && (
        <div className="absolute left-0 mt-1 w-48 bg-white border border-gray-200 rounded-lg shadow-lg z-50 max-h-60 overflow-auto">
          {options.map((opt) => {
            const selected = values.includes(opt);
            return (
              <label
                key={opt}
                className={`flex items-center gap-2 px-3 py-2 text-sm cursor-pointer ${
                  selected ? 'bg-orange-50 text-orange-600' : 'text-gray-700 hover:bg-gray-50'
                }`}
              >
                <input
                  type="checkbox"
                  checked={selected}
                  onChange={() => toggle(opt)}
                  className="w-4 h-4 rounded border-gray-300 text-orange-500 focus:ring-orange-400"
                />
                {opt}
              </label>
            );
          })}
        </div>
      )}
    </div>
  );
}
