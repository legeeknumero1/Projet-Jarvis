/**
 * Formulaire d'enregistrement
 */

'use client';

import React from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useForm } from '@/hooks';
import { useUserStore } from '@/store';
import { authApi } from '@/lib/api';
import { Eye, EyeOff, Loader } from 'lucide-react';

interface RegisterFormData {
  name: string;
  email: string;
  password: string;
  confirmPassword: string;
}

export function RegisterForm() {
  const router = useRouter();
  const { setUser, setToken } = useUserStore();
  const [showPassword, setShowPassword] = React.useState(false);
  const [showConfirm, setShowConfirm] = React.useState(false);
  const [apiError, setApiError] = React.useState<string | null>(null);

  const { values, errors, touched, isSubmitting, handleChange, handleBlur, handleSubmit } = useForm<RegisterFormData>({
    initialValues: {
      name: '',
      email: '',
      password: '',
      confirmPassword: '',
    },
    validate: (values) => {
      const errors: Record<string, string | undefined> = {};

      if (!values.name?.trim()) {
        errors.name = 'Nom requis';
      } else if (values.name.length < 2) {
        errors.name = 'Au moins 2 caractères';
      }

      if (!values.email) {
        errors.email = 'Email requis';
      } else if (!/^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i.test(values.email)) {
        errors.email = 'Email invalide';
      }

      if (!values.password) {
        errors.password = 'Mot de passe requis';
      } else if (values.password.length < 8) {
        errors.password = 'Au moins 8 caractères';
      } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(values.password)) {
        errors.password = 'Doit contenir majuscule, minuscule et chiffre';
      }

      if (!values.confirmPassword) {
        errors.confirmPassword = 'Confirmation requise';
      } else if (values.password !== values.confirmPassword) {
        errors.confirmPassword = 'Les mots de passe ne correspondent pas';
      }

      return errors;
    },
  });

  /**
   * Gérer l'enregistrement
   */
  const onSubmit = handleSubmit(async (values) => {
    try {
      setApiError(null);
      const response = await authApi.register(values.email, values.password, values.name);

      // Sauvegarder l'utilisateur et le token
      setUser(response.user);
      setToken(response.token);
      localStorage.setItem('auth_token', response.token);

      // Rediriger
      router.push('/chat');
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Erreur d\'enregistrement';
      setApiError(errorMessage);
    }
  });

  return (
    <form onSubmit={onSubmit} className="space-y-6">
      {/* Titre */}
      <div>
        <h1 className="text-2xl font-bold">Créer un compte</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          Rejoignez Jarvis pour commencer
        </p>
      </div>

      {/* Erreur globale */}
      {apiError && (
        <div className="rounded-lg bg-destructive/10 p-3 text-sm text-destructive">
          {apiError}
        </div>
      )}

      {/* Nom */}
      <div>
        <label htmlFor="name" className="block text-sm font-medium">
          Nom complet
        </label>
        <input
          id="name"
          type="text"
          name="name"
          value={values.name}
          onChange={handleChange}
          onBlur={handleBlur}
          className={`mt-2 w-full rounded-lg border px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary ${
            touched.name && errors.name ? 'border-destructive' : 'border-input'
          }`}
          placeholder="Jean Dupont"
        />
        {touched.name && errors.name && (
          <p className="mt-1 text-xs text-destructive">{errors.name}</p>
        )}
      </div>

      {/* Email */}
      <div>
        <label htmlFor="email" className="block text-sm font-medium">
          Email
        </label>
        <input
          id="email"
          type="email"
          name="email"
          value={values.email}
          onChange={handleChange}
          onBlur={handleBlur}
          className={`mt-2 w-full rounded-lg border px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary ${
            touched.email && errors.email ? 'border-destructive' : 'border-input'
          }`}
          placeholder="nom@exemple.com"
        />
        {touched.email && errors.email && (
          <p className="mt-1 text-xs text-destructive">{errors.email}</p>
        )}
      </div>

      {/* Mot de passe */}
      <div>
        <label htmlFor="password" className="block text-sm font-medium">
          Mot de passe
        </label>
        <div className="relative mt-2">
          <input
            id="password"
            type={showPassword ? 'text' : 'password'}
            name="password"
            value={values.password}
            onChange={handleChange}
            onBlur={handleBlur}
            className={`w-full rounded-lg border px-4 py-2 pr-10 text-sm focus:outline-none focus:ring-2 focus:ring-primary ${
              touched.password && errors.password
                ? 'border-destructive'
                : 'border-input'
            }`}
            placeholder="••••••••"
          />
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
          >
            {showPassword ? (
              <EyeOff className="h-4 w-4" />
            ) : (
              <Eye className="h-4 w-4" />
            )}
          </button>
        </div>
        {touched.password && errors.password && (
          <p className="mt-1 text-xs text-destructive">{errors.password}</p>
        )}
      </div>

      {/* Confirmation */}
      <div>
        <label htmlFor="confirmPassword" className="block text-sm font-medium">
          Confirmer le mot de passe
        </label>
        <div className="relative mt-2">
          <input
            id="confirmPassword"
            type={showConfirm ? 'text' : 'password'}
            name="confirmPassword"
            value={values.confirmPassword}
            onChange={handleChange}
            onBlur={handleBlur}
            className={`w-full rounded-lg border px-4 py-2 pr-10 text-sm focus:outline-none focus:ring-2 focus:ring-primary ${
              touched.confirmPassword && errors.confirmPassword
                ? 'border-destructive'
                : 'border-input'
            }`}
            placeholder="••••••••"
          />
          <button
            type="button"
            onClick={() => setShowConfirm(!showConfirm)}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
          >
            {showConfirm ? (
              <EyeOff className="h-4 w-4" />
            ) : (
              <Eye className="h-4 w-4" />
            )}
          </button>
        </div>
        {touched.confirmPassword && errors.confirmPassword && (
          <p className="mt-1 text-xs text-destructive">{errors.confirmPassword}</p>
        )}
      </div>

      {/* Bouton d'enregistrement */}
      <button
        type="submit"
        disabled={isSubmitting}
        className="w-full rounded-lg bg-primary px-4 py-2 font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50 flex items-center justify-center gap-2 transition-colors"
      >
        {isSubmitting && <Loader className="h-4 w-4 animate-spin" />}
        {isSubmitting ? 'Enregistrement...' : 'Créer un compte'}
      </button>

      {/* Lien de connexion */}
      <p className="text-center text-sm text-muted-foreground">
        Vous avez déjà un compte?{' '}
        <Link href="/login" className="font-medium text-primary hover:underline">
          Se connecter
        </Link>
      </p>
    </form>
  );
}
