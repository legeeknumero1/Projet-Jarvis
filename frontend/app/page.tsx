/**
 * Page d'accueil
 */

import { redirect } from 'next/navigation';

export default function Home() {
  // Rediriger vers le chat
  redirect('/chat');
}
