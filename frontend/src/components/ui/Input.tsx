import { InputHTMLAttributes, ReactNode, forwardRef, useId } from 'react';
import { cn } from '@/cn';

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  leftIcon?: ReactNode;
  rightIcon?: ReactNode;
  variant?: 'default' | 'filled' | 'outline';
  inputSize?: 'sm' | 'md' | 'lg';
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ 
    className, 
    label, 
    error, 
    helperText,
    leftIcon,
    rightIcon,
    variant = 'default',
    inputSize = 'md',
    id,
    ...props 
  }, ref) => {
    const generatedId = useId();
    const inputId = id || `input-${generatedId}`;
    
    const baseStyles = 'w-full transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-900 disabled:opacity-50 disabled:cursor-not-allowed';
    
    const variants = {
      default: 'bg-gray-800 border border-gray-600 text-white placeholder-gray-400 focus:ring-blue-500 focus:border-blue-500',
      filled: 'bg-gray-700 border-0 text-white placeholder-gray-400 focus:ring-blue-500',
      outline: 'bg-transparent border border-gray-600 text-white placeholder-gray-400 focus:ring-blue-500 focus:border-blue-500',
    };
    
    const sizes = {
      sm: 'px-3 py-2 text-sm rounded-md h-8',
      md: 'px-4 py-2.5 text-sm rounded-lg h-10',
      lg: 'px-4 py-3 text-base rounded-lg h-12',
    };

    const iconSizes = {
      sm: 'w-4 h-4',
      md: 'w-5 h-5',
      lg: 'w-5 h-5',
    };

    return (
      <div className="space-y-1">
        {label && (
          <label 
            htmlFor={inputId}
            className="block text-sm font-medium text-gray-300"
          >
            {label}
            {props.required && <span className="text-red-400 ml-1">*</span>}
          </label>
        )}
        
        <div className="relative">
          {leftIcon && (
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <span className={cn("text-gray-400", iconSizes[inputSize])}>
                {leftIcon}
              </span>
            </div>
          )}
          
          <input
            id={inputId}
            className={cn(
              baseStyles,
              variants[variant],
              sizes[inputSize],
              leftIcon && 'pl-10',
              rightIcon && 'pr-10',
              error && 'border-red-500 focus:ring-red-500 focus:border-red-500',
              className
            )}
            ref={ref}
            {...props}
          />
          
          {rightIcon && (
            <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
              <span className={cn("text-gray-400", iconSizes[inputSize])}>
                {rightIcon}
              </span>
            </div>
          )}
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

Input.displayName = 'Input';

export { Input };