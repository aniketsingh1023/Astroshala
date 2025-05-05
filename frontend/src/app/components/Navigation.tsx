// src/components/Navigation.tsx
import { Button } from '@/app/components/ui/button';
import Link from 'next/link';

const Navigation = () => {
  return (
    <nav className="fixed w-full bg-white/80 backdrop-blur-sm z-50 top-0 left-0 right-0 h-16 border-b border-slate-300">
      <div className="container mx-auto h-full flex items-center justify-between">
        <Link href="/" className="text-xl font-bold text-purple-600">
          Parasara Jyotish
        </Link>
        
        <div className="space-x-4">
          <Link href="/about">
            <Button variant="ghost">About</Button>
          </Link>
          <Link href="/chat">
            <Button className="bg-purple-600 hover:bg-purple-700 text-white">
              Start Reading
            </Button>
          </Link>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;