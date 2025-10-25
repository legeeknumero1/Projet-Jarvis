/**
 * Page d'enregistrement
 */

import { RegisterForm } from '@/components/auth';

export const metadata = {
  title: 'Enregistrement - Jarvis',
};

export default function RegisterPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary/5 to-secondary/5 px-4">
      <div className="w-full max-w-md">
        {/* Conteneur du formulaire */}
        <div className="rounded-2xl border border-border bg-card p-8 shadow-lg">
          <RegisterForm />
        </div>

        {/* Footer */}
        <p className="mt-8 text-center text-sm text-muted-foreground">
          © 2024 Jarvis AI Assistant. Tous droits réservés.
        </p>
      </div>
    </div>
  );
}
