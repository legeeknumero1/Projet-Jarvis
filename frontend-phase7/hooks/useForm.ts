/**
 * Hook personnalisé pour la gestion des formulaires avec validation
 */

'use client';

import { useState, useCallback } from 'react';
import { ValidationError } from '@/types';

export interface UseFormState<T> {
  values: T;
  errors: Record<keyof T, string | undefined>;
  touched: Record<keyof T, boolean>;
  isSubmitting: boolean;
}

export interface UseFormActions<T> {
  handleChange: (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => void;
  handleBlur: (e: React.FocusEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => void;
  handleSubmit: (onSubmit: (values: T) => Promise<void> | void) => (e: React.FormEvent) => Promise<void>;
  setFieldValue: (field: keyof T, value: any) => void;
  setErrors: (errors: Record<keyof T, string | undefined>) => void;
  resetForm: () => void;
  setSubmitting: (isSubmitting: boolean) => void;
}

export interface UseFormOptions<T> {
  initialValues: T;
  validate?: (values: T) => Record<keyof T, string | undefined>;
  onSubmit?: (values: T) => Promise<void> | void;
}

/**
 * Hook pour gérer les formulaires avec validation
 */
export function useForm<T extends Record<string, any>>(
  options: UseFormOptions<T>,
): UseFormState<T> & UseFormActions<T> {
  const [values, setValues] = useState<T>(options.initialValues);
  const [errors, setErrors] = useState<Record<keyof T, string | undefined>>({} as any);
  const [touched, setTouched] = useState<Record<keyof T, boolean>>({} as any);
  const [isSubmitting, setIsSubmitting] = useState(false);

  /**
   * Gérer le changement d'un champ
   */
  const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    const fieldValue = type === 'checkbox' ? (e.target as HTMLInputElement).checked : value;

    setValues((prev) => ({
      ...prev,
      [name]: fieldValue,
    }));

    // Valider le champ en direct si des erreurs existent
    if (errors[name as keyof T]) {
      const fieldErrors = options.validate?.({ ...values, [name]: fieldValue }) || {};
      setErrors((prev) => ({
        ...prev,
        [name]: fieldErrors[name as keyof T],
      }));
    }
  }, [errors, options, values]);

  /**
   * Gérer la perte de focus
   */
  const handleBlur = useCallback((e: React.FocusEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name } = e.target;

    setTouched((prev) => ({
      ...prev,
      [name]: true,
    }));

    // Valider le champ
    if (options.validate) {
      const fieldErrors = options.validate(values);
      setErrors((prev) => ({
        ...prev,
        [name]: fieldErrors[name as keyof T],
      }));
    }
  }, [options, values]);

  /**
   * Gérer l'envoi du formulaire
   */
  const handleSubmit = useCallback(
    (onSubmit: (values: T) => Promise<void> | void) =>
      async (e: React.FormEvent) => {
        e.preventDefault();

        // Valider tous les champs
        if (options.validate) {
          const fieldErrors = options.validate(values);
          setErrors(fieldErrors);

          const hasErrors = Object.values(fieldErrors).some((error) => error !== undefined);
          if (hasErrors) {
            return;
          }
        }

        setIsSubmitting(true);
        try {
          await Promise.resolve(onSubmit ? onSubmit(values) : options.onSubmit?.(values));
        } catch (error) {
          console.error('Erreur lors de la soumission du formulaire:', error);
        } finally {
          setIsSubmitting(false);
        }
      },
    [options, values],
  );

  /**
   * Définir la valeur d'un champ
   */
  const setFieldValue = useCallback((field: keyof T, value: any) => {
    setValues((prev) => ({
      ...prev,
      [field]: value,
    }));
  }, []);

  /**
   * Réinitialiser le formulaire
   */
  const resetForm = useCallback(() => {
    setValues(options.initialValues);
    setErrors({} as any);
    setTouched({} as any);
    setIsSubmitting(false);
  }, [options.initialValues]);

  return {
    values,
    errors,
    touched,
    isSubmitting,
    handleChange,
    handleBlur,
    handleSubmit,
    setFieldValue,
    setErrors,
    resetForm,
    setSubmitting: setIsSubmitting,
  };
}
