import './globals.css'
import { ReactNode } from 'react'
import { SessionProvider } from "./context/SessionContext";
import Image from "next/image";
import logo from '@/public/logo.png'
import Link from 'next/link';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'MindBlocks',
  description: 'An AI Study Schedule Planner.',
  
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <head>
        <link rel="icon" href="/icon.ico" />

      </head>
      
      <body className='font-story'>
        <header className='flex justify-center p-[1rem]' >
          <Link href='/dashboard'><h1 className='flex text-4xl items-center gap-4'><Image src={logo} width={80} alt="The logo of MindBlocks consisting of a brain in the background and a blue rounded box in the foreground representing a work block on a calendar."/>MindBlocks</h1></Link>
        </header>
        <main style={{ padding: '1rem' }}><SessionProvider>{children}</SessionProvider></main>
        
      </body>
    </html>
  )
}
