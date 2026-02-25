import { NextRequest, NextResponse } from 'next/server'
import { prisma } from '@/lib/db'

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams
  const code = searchParams.get('code')
  const error = searchParams.get('error')
  const state = searchParams.get('state')

  const storedState = request.cookies.get('oauth_state')?.value
  const clearStateCookie = { name: 'oauth_state', value: '', maxAge: 0 }

  if (error) {
    console.error('OAuth error:', error)
    const response = NextResponse.redirect(new URL('/?error=' + error, request.url))
    response.cookies.set(clearStateCookie)
    return response
  }

  if (!code) {
    const response = NextResponse.redirect(new URL('/?error=no_code', request.url))
    response.cookies.set(clearStateCookie)
    return response
  }

  if (!state || state !== storedState) {
    const response = NextResponse.redirect(new URL('/?error=invalid_state', request.url))
    response.cookies.set(clearStateCookie)
    return response
  }

  try {
    const tokenParams = new URLSearchParams({
      grant_type: 'authorization_code',
      code: code,
      redirect_uri: process.env.SECONDME_REDIRECT_URI!,
      client_id: process.env.SECONDME_CLIENT_ID!,
      client_secret: process.env.SECONDME_CLIENT_SECRET!,
    })

    const tokenResponse = await fetch('https://app.mindos.com/gate/lab/api/oauth/token/code', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: tokenParams.toString(),
    })

    const tokenResult = await tokenResponse.json()
    
    if (tokenResult.code !== 0 || !tokenResult.data) {
      throw new Error(tokenResult.message || 'Token exchange failed')
    }

    const tokenData = tokenResult.data

    const profileResponse = await fetch('https://app.mindos.com/gate/lab/api/secondme/user/info', {
      headers: { 'Authorization': `Bearer ${tokenData.accessToken}` },
    })

    const profileResult = await profileResponse.json()

    if (profileResult.code !== 0 || !profileResult.data) {
      throw new Error('Failed to fetch profile')
    }

    const profile = profileResult.data
    const secondMeId = profile.email || profile.id

    await prisma.user.upsert({
      where: { secondMeId: secondMeId },
      update: {
        name: profile.name,
        email: profile.email,
        avatar: profile.avatar,
        accessToken: tokenData.accessToken,
        refreshToken: tokenData.refreshToken,
        tokenExpiresAt: new Date(Date.now() + tokenData.expiresIn * 1000),
      },
      create: {
        secondMeId: secondMeId,
        name: profile.name,
        email: profile.email,
        avatar: profile.avatar,
        accessToken: tokenData.accessToken,
        refreshToken: tokenData.refreshToken,
        tokenExpiresAt: new Date(Date.now() + tokenData.expiresIn * 1000),
      },
    })

    const response = NextResponse.redirect(new URL('/role-select', request.url))
    response.cookies.set(clearStateCookie)
    response.cookies.set('session', tokenData.accessToken, {
      httpOnly: true,
      secure: true,
      sameSite: 'lax',
      maxAge: tokenData.expiresIn,
    })

    return response
  } catch (error: any) {
    console.error('OAuth error:', error)
    const response = NextResponse.redirect(new URL('/?error=auth_failed', request.url))
    response.cookies.set(clearStateCookie)
    return response
  }
}
