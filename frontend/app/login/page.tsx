/**
 * Page de connexion
 */

import { LoginForm } from '@/components/auth';

export const metadata = {
  title: 'Connexion - Jarvis',
};

export default function LoginPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary/5 to-secondary/5 px-4">
      <div className="w-full max-w-md">
        {/* Conteneur du formulaire */}
        <div className="rounded-2xl border border-border bg-card p-8 shadow-lg">
          <LoginForm />
        </div>

        {/* Footer */}
        <p className="mt-8 text-center text-sm text-muted-foreground">
          © 2024 Jarvis AI Assistant. Tous droits réservés.
        </p>
      </div>
    </div>
  );
}
