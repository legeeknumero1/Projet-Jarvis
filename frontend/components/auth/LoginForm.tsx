/**
 * Formulaire de connexion
 */

'use client';

import React from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useForm } from '@/hooks';
import { useUserStore } from '@/store';
import { authApi } from '@/lib/api';
import { Eye, EyeOff, Loader } from 'lucide-react';

interface LoginFormData {
  email: string;
  password: string;
}

export function LoginForm() {
  const router = useRouter();
  const { setUser, setToken } = useUserStore();
  const [showPassword, setShowPassword] = React.useState(false);
  const [apiError, setApiError] = React.useState<string | null>(null);

  const { values, errors, touched, isSubmitting, handleChange, handleBlur, handleSubmit } = useForm<LoginFormData>({
    initialValues: {
      email: '',
      password: '',
    },
    validate: (values) => {
      const errors: Record<string, string | undefined> = {};

      if (!values.email) {
        errors.email = 'Email requis';
      } else if (!/^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i.test(values.email)) {
        errors.email = 'Email invalide';
      }

      if (!values.password) {
        errors.password = 'Mot de passe requis';
      } else if (values.password.length < 6) {
        errors.password = 'Au moins 6 caractères';
      }

      return errors;
    },
  });

  /**
   * Gérer la connexion
   */
  const onSubmit = handleSubmit(async (values) => {
    try {
      setApiError(null);
      const response = await authApi.login(values.email, values.password);

      // Sauvegarder l'utilisateur et le token
      setUser(response.user);
      setToken(response.token);
      localStorage.setItem('auth_token', response.token);

      // Rediriger
      router.push('/chat');
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Erreur de connexion';
      setApiError(errorMessage);
    }
  });

  return (
    <form onSubmit={onSubmit} className="space-y-6">
      {/* Titre */}
      <div>
        <h1 className="text-2xl font-bold">Connexion</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          Accédez à votre compte Jarvis
        </p>
      </div>

      {/* Erreur globale */}
      {apiError && (
        <div className="rounded-lg bg-destructive/10 p-3 text-sm text-destructive">
          {apiError}
        </div>
      )}

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
            touched.email && errors.email
              ? 'border-destructive'
              : 'border-input'
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
            placeholder="••••••"
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

      {/* Bouton de connexion */}
      <button
        type="submit"
        disabled={isSubmitting}
        className="w-full rounded-lg bg-primary px-4 py-2 font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50 flex items-center justify-center gap-2 transition-colors"
      >
        {isSubmitting && <Loader className="h-4 w-4 animate-spin" />}
        {isSubmitting ? 'Connexion...' : 'Se connecter'}
      </button>

      {/* Lien d'enregistrement */}
      <p className="text-center text-sm text-muted-foreground">
        Pas encore de compte?{' '}
        <Link href="/register" className="font-medium text-primary hover:underline">
          S'enregistrer
        </Link>
      </p>
    </form>
  );
}
