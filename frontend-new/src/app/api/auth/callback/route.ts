import { NextRequest, NextResponse } from 'next/server';

function redirectWithError(request: NextRequest, error: string, details?: string) {
  const url = new URL('/', request.url);
  url.searchParams.set('error', error);
  if (details) url.searchParams.set('details', details);
  const response = NextResponse.redirect(url);
  response.cookies.set({ name: 'oauth_state', value: '', maxAge: 0, path: '/' });
  return response;
}

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const code = searchParams.get('code');
  const error = searchParams.get('error');
  const state = searchParams.get('state');

  const storedState = request.cookies.get('oauth_state')?.value;

  if (error) {
    return redirectWithError(request, error);
  }

  if (!code) {
    return redirectWithError(request, 'no_code');
  }

  if (!state || state !== storedState) {
    return redirectWithError(request, 'invalid_state');
  }

  try {
    const tokenEndpoint = process.env.SECONDME_TOKEN_ENDPOINT || 'https://app.mindos.com/gate/lab/api/oauth/token/code';
    const profileEndpoint = process.env.SECONDME_PROFILE_ENDPOINT || 'https://api.mindverse.com/gate/lab/api/secondme/user/info';

    const tokenParams = new URLSearchParams({
      grant_type: 'authorization_code',
      code,
      redirect_uri: process.env.SECONDME_REDIRECT_URI || '',
      client_id: process.env.SECONDME_CLIENT_ID || '',
      client_secret: process.env.SECONDME_CLIENT_SECRET || '',
    });

    const tokenResponse = await fetch(tokenEndpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: tokenParams.toString(),
      cache: 'no-store',
    });

    if (!tokenResponse.ok) {
      throw new Error(`token_http_${tokenResponse.status}`);
    }

    const tokenResult = await tokenResponse.json();
    const tokenData = tokenResult?.data || tokenResult;
    const accessToken = tokenData?.accessToken || tokenData?.access_token;
    const refreshToken = tokenData?.refreshToken || tokenData?.refresh_token || '';
    const expiresIn = Number(tokenData?.expiresIn || tokenData?.expires_in || 3600);

    if (!accessToken) {
      throw new Error(tokenResult?.message || 'token_exchange_failed');
    }

    const profileResponse = await fetch(profileEndpoint, {
      headers: { Authorization: `Bearer ${accessToken}` },
      cache: 'no-store',
    });

    if (!profileResponse.ok) {
      throw new Error(`profile_http_${profileResponse.status}`);
    }

    const profileResult = await profileResponse.json();
    const profileData = profileResult?.data || profileResult;

    const profile = {
      id: profileData?.id || profileData?.sub || '',
      name: profileData?.name || profileData?.nickname || 'SecondMe User',
      email: profileData?.email || '',
      avatar: profileData?.avatar || profileData?.avatarUrl || '',
    };

    const response = NextResponse.redirect(new URL('/role-select', request.url));
    response.cookies.set({ name: 'oauth_state', value: '', maxAge: 0, path: '/' });
    response.cookies.set('session', accessToken, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      maxAge: expiresIn,
      path: '/',
    });
    response.cookies.set('secondme_profile', encodeURIComponent(JSON.stringify(profile)), {
      httpOnly: false,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      maxAge: expiresIn,
      path: '/',
    });
    response.cookies.set('secondme_refresh', refreshToken, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      maxAge: expiresIn,
      path: '/',
    });
    return response;
  } catch (err) {
    const message = err instanceof Error ? err.message : 'auth_failed';
    return redirectWithError(request, 'auth_failed', message);
  }
}
