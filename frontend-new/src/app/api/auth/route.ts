import { NextResponse } from 'next/server'

export async function GET(request: Request) {
  const clientId = process.env.SECONDME_CLIENT_ID
  const redirectUri = process.env.SECONDME_REDIRECT_URI

  // Generate state with timestamp for security
  const stateData = {
    uuid: crypto.randomUUID(),
    timestamp: Date.now(),
  }
  const state = btoa(JSON.stringify(stateData))

  // Store state in cookie for validation
  const authUrl = new URL('https://go.second.me/oauth/')
  authUrl.searchParams.set('client_id', clientId!)
  authUrl.searchParams.set('redirect_uri', redirectUri!)
  authUrl.searchParams.set('response_type', 'code')
  authUrl.searchParams.set('state', state)

  // Add prompt for better mobile experience
  authUrl.searchParams.set('prompt', 'consent')

  const response = NextResponse.redirect(authUrl.toString())

  // Set state cookie for validation - always secure on Vercel (HTTPS)
  response.cookies.set('oauth_state', state, {
    httpOnly: true,
    secure: true,
    sameSite: 'lax',
    maxAge: 600, // 10 minutes
  })

  return response
}
