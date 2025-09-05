import { SelectHTMLAttributes, forwardRef, ReactNode, useId } from 'react';
import { cn } from '@/cn';

export interface SelectOption {
  value: string;
  label: string;
  disabled?: boolean;
}

export interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  error?: string;
  helperText?: string;
  variant?: 'default' | 'filled' | 'outline';
  selectSize?: 'sm' | 'md' | 'lg';
  options?: SelectOption[];
  placeholder?: string;
  children?: ReactNode;
}

const Select = forwardRef<HTMLSelectElement, SelectProps>(
  ({ 
    className, 
    label, 
    error, 
    helperText,
    variant = 'default',
    selectSize = 'md',
    options = [],
    placeholder,
    children,
    id,
    ...props 
  }, ref) => {
    const generatedId = useId();
    const selectId = id || `select-${generatedId}`;
    
    const baseStyles = 'w-full transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-900 disabled:opacity-50 disabled:cursor-not-allowed appearance-none';
    
    const variants = {
      default: 'bg-gray-800 border border-gray-600 text-white focus:ring-blue-500 focus:border-blue-500',
      filled: 'bg-gray-700 border-0 text-white focus:ring-blue-500',
      outline: 'bg-transparent border border-gray-600 text-white focus:ring-blue-500 focus:border-blue-500',
    };
    
    const sizes = {
      sm: 'px-3 py-2 pr-8 text-sm rounded-md h-8',
      md: 'px-4 py-2.5 pr-10 text-sm rounded-lg h-10',
      lg: 'px-4 py-3 pr-10 text-base rounded-lg h-12',
    };

    return (
      <div className="space-y-1">
        {label && (
          <label 
            htmlFor={selectId}
            className="block text-sm font-medium text-gray-300"
          >
            {label}
            {props.required && <span className="text-red-400 ml-1">*</span>}
          </label>
        )}
        
        <div className="relative">
          <select
            id={selectId}
            className={cn(
              baseStyles,
              variants[variant],
              sizes[selectSize],
              error && 'border-red-500 focus:ring-red-500 focus:border-red-500',
              className
            )}
            ref={ref}
            {...props}
          >
            {placeholder && (
              <option value="" disabled>
                {placeholder}
              </option>
            )}
            
            {options.map((option) => (
              <option 
                key={option.value} 
                value={option.value} 
                disabled={option.disabled}
              >
                {option.label}
              </option>
            ))}
            
            {children}
          </select>
          
          {/* Custom dropdown arrow */}
          <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
            <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 9l4-4 4 4m0 6l-4 4-4-4" />
            </svg>
          </div>
        </div>
        
        {error && (
          <p className="text-sm text-red-400 flex items-center space-x-1">
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            <span>{error}</span>
          </p>
        )}
        
        {helperText && !error && (
          <p className="text-sm text-gray-400">{helperText}</p>
        )}
      </div>
    );
  }
);

Select.displayName = 'Select';

export { Select };