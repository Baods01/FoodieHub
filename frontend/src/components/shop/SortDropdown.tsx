import { Fragment } from 'react';
import { Listbox, Transition } from '@headlessui/react';
import { ChevronDown } from 'lucide-react';

export interface SortOptionDef {
  value: string;
  label: string;
}

interface SortDropdownProps {
  value: string;
  options: SortOptionDef[];
  onChange: (value: string) => void;
}

export default function SortDropdown({ value, options, onChange }: SortDropdownProps) {
  const selected = options.find((o) => o.value === value);
  const displayValue = selected?.label || '排序';

  return (
    <Listbox value={value} onChange={onChange}>
      <div className="relative">
        <Listbox.Button className="flex items-center gap-1 px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-400 bg-white text-gray-700">
          <span>{displayValue}</span>
          <ChevronDown size={14} />
        </Listbox.Button>
        <Transition
          as={Fragment}
          leave="transition ease-in duration-100"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <Listbox.Options className="absolute left-0 mt-1 w-32 bg-white border border-gray-200 rounded-lg shadow-lg z-50 max-h-60 overflow-auto">
            {options.map((option) => (
              <Listbox.Option
                key={option.value}
                value={option.value}
                className={({ active }) =>
                  `px-3 py-2 text-sm cursor-pointer ${
                    active ? 'bg-orange-50 text-orange-600' : 'text-gray-700'
                  }`
                }
              >
                {option.label}
              </Listbox.Option>
            ))}
          </Listbox.Options>
        </Transition>
      </div>
    </Listbox>
  );
}
