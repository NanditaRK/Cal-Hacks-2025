import { NextRequest, NextResponse } from 'next/server'

export async function POST(req: NextRequest) {
  // Redirect to FastAPI logout
  return NextResponse.redirect('https://mindblocks-backend.onrender.com/auth/logout')
}
