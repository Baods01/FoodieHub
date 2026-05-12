import { Fragment } from 'react';
import { Listbox, Transition } from '@headlessui/react';
import { ChevronDown } from 'lucide-react';

interface FilterDropdownProps {
  label: string;
  options: string[];
  value: string;
  onChange: (value: string) => void;
}

export default function FilterDropdown({ label, options, value, onChange }: FilterDropdownProps) {
  const allOptions = ['全部', ...options];
  const displayValue = value || '全部';
  const isActive = value !== '';

  return (
    <Listbox value={value} onChange={onChange}>
      <div className="relative">
        <Listbox.Button
          className={`flex items-center gap-1 px-3 py-1.5 text-sm border rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-400 ${
            isActive
              ? 'border-orange-400 text-orange-600 bg-orange-50'
              : 'border-gray-300 text-gray-700 bg-white'
          }`}
        >
          <span>
            {label}: {displayValue}
          </span>
          <ChevronDown size={14} />
        </Listbox.Button>
        <Transition
          as={Fragment}
          leave="transition ease-in duration-100"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <Listbox.Options className="absolute right-0 mt-1 w-32 bg-white border border-gray-200 rounded-lg shadow-lg z-50 max-h-60 overflow-auto">
            {allOptions.map((option) => (
              <Listbox.Option
                key={option}
                value={option === '全部' ? '' : option}
                className={({ active }) =>
                  `px-3 py-2 text-sm cursor-pointer ${
                    active ? 'bg-orange-50 text-orange-600' : 'text-gray-700'
                  }`
                }
              >
                {option}
              </Listbox.Option>
            ))}
          </Listbox.Options>
        </Transition>
      </div>
    </Listbox>
  );
}
