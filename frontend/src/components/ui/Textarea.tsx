import { TextareaHTMLAttributes, forwardRef, useId } from 'react';
import { cn } from '@/cn';

export interface TextareaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
  helperText?: string;
  variant?: 'default' | 'filled' | 'outline';
  textareaSize?: 'sm' | 'md' | 'lg';
}

const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ 
    className, 
    label, 
    error, 
    helperText,
    variant = 'default',
    textareaSize = 'md',
    id,
    rows = 4,
    ...props 
  }, ref) => {
    const generatedId = useId();
    const textareaId = id || `textarea-${generatedId}`;
    
    const baseStyles = 'w-full transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-900 disabled:opacity-50 disabled:cursor-not-allowed resize-vertical';
    
    const variants = {
      default: 'bg-gray-800 border border-gray-600 text-white placeholder-gray-400 focus:ring-blue-500 focus:border-blue-500',
      filled: 'bg-gray-700 border-0 text-white placeholder-gray-400 focus:ring-blue-500',
      outline: 'bg-transparent border border-gray-600 text-white placeholder-gray-400 focus:ring-blue-500 focus:border-blue-500',
    };
    
    const sizes = {
      sm: 'px-3 py-2 text-sm rounded-md',
      md: 'px-4 py-2.5 text-sm rounded-lg',
      lg: 'px-4 py-3 text-base rounded-lg',
    };

    return (
      <div className="space-y-1">
        {label && (
          <label 
            htmlFor={textareaId}
            className="block text-sm font-medium text-gray-300"
          >
            {label}
            {props.required && <span className="text-red-400 ml-1">*</span>}
          </label>
        )}
        
        <textarea
          id={textareaId}
          rows={rows}
          className={cn(
            baseStyles,
            variants[variant],
            sizes[textareaSize],
            error && 'border-red-500 focus:ring-red-500 focus:border-red-500',
            className
          )}
          ref={ref}
          {...props}
        />
        
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

Textarea.displayName = 'Textarea';

export { Textarea };