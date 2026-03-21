import { NextResponse } from 'next/server';

export async function GET() {
  const clientId = process.env.SECONDME_CLIENT_ID;
  const redirectUri = process.env.SECONDME_REDIRECT_URI;
  const authEndpoint = process.env.SECONDME_AUTHORIZATION_ENDPOINT || 'https://go.second.me/oauth/';

  if (!clientId || !redirectUri) {
    return NextResponse.redirect(new URL('/?error=auth_failed&details=missing_oauth_env', redirectUri || 'http://localhost:3000'));
  }

  const stateData = {
    uuid: crypto.randomUUID(),
    timestamp: Date.now(),
  };
  const state = Buffer.from(JSON.stringify(stateData)).toString('base64url');

  const authUrl = new URL(authEndpoint);
  authUrl.searchParams.set('client_id', clientId);
  authUrl.searchParams.set('redirect_uri', redirectUri);
  authUrl.searchParams.set('response_type', 'code');
  authUrl.searchParams.set('state', state);
  authUrl.searchParams.set('scope', 'user.info user.info.shades user.info.softmemory');
  authUrl.searchParams.set('prompt', 'consent');

  const response = NextResponse.redirect(authUrl.toString());
  response.cookies.set('oauth_state', state, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax',
    maxAge: 600,
    path: '/',
  });
  return response;
}
