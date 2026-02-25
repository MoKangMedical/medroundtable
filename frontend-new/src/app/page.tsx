'use client';

import { useEffect, useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Sparkles, MessageCircle, Users, ArrowRight, Bot, Network, Dna, Microscope, HeartPulse, Stethoscope, Brain, Activity, FileText, FlaskConical, ClipboardCheck, TrendingUp } from 'lucide-react';
import Image from 'next/image';

const ROLES = [
  {
    id: 'director',
    title: 'Senior Clinical Director',
    subtitle: '临床主任',
    description: 'Clinical insight & scientific vision',
    color: 'from-blue-500 to-blue-600',
    bgColor: 'bg-blue-500',
    delay: 0,
  },
  {
    id: 'student',
    title: 'PhD Student',
    subtitle: '博士生',
    description: 'Supervised by Clinical Director',
    color: 'from-emerald-500 to-emerald-600',
    bgColor: 'bg-emerald-500',
    delay: 0.1,
  },
  {
    id: 'epi',
    title: 'Clinical Epidemiologist',
    subtitle: '流行病学家',
    description: 'Study design & protocol development',
    color: 'from-purple-500 to-purple-600',
    bgColor: 'bg-purple-500',
    delay: 0.2,
  },
  {
    id: 'stats',
    title: 'Biostatistician / Data Scientist',
    subtitle: '统计学家',
    description: 'Data modeling, analysis & visualization',
    color: 'from-amber-500 to-amber-600',
    bgColor: 'bg-amber-500',
    delay: 0.3,
  },
  {
    id: 'nurse',
    title: 'Research Nurse / Clinical Research Coordinator',
    subtitle: '研究护士',
    description: 'Data acquisition & quality control',
    color: 'from-cyan-500 to-cyan-600',
    bgColor: 'bg-cyan-500',
    delay: 0.4,
  },
];

const PROCESS_STEPS = [
  { title: 'Clinical Problem Discussion', icon: '💬' },
  { title: 'Research Question & Study Design', icon: '📋' },
  { title: 'Data Collection & Statistical Analysis', icon: '📊' },
  { title: 'Translation & Application', icon: '💡' },
];

export default function Home() {
  const [mounted, setMounted] = useState(false);
  const [activeRole, setActiveRole] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setMounted(true);

    // Check for error in URL
    const params = new URLSearchParams(window.location.search);
    const errorParam = params.get('error');
    const detailsParam = params.get('details');
    if (errorParam) {
      const errorMessages: Record<string, string> = {
        'auth_failed': '登录失败，请重试',
        'no_code': '授权码获取失败',
        'invalid_state': '安全验证失败，请重试',
        'access_denied': '用户取消授权',
      };
      let errorMsg = errorMessages[errorParam] || '登录失败，请重试';
      if (detailsParam) {
        errorMsg += ` (${decodeURIComponent(detailsParam)})`;
      }
      setError(errorMsg);
      window.history.replaceState({}, '', window.location.pathname);
    }

    const interval = setInterval(() => {
      setActiveRole((prev) => (prev + 1) % ROLES.length);
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  const handleLogin = () => {
    setIsLoading(true);
    setError(null);
    window.location.href = '/api/auth/login';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50/30 to-indigo-50/20 flex flex-col lg:flex-row">
      {/* Left Side - Content */}
      <div className="flex-1 relative overflow-hidden flex items-center justify-center p-6 lg:p-10 bg-gradient-to-br from-slate-50 via-blue-50/30 to-indigo-50/20">
        <div className="absolute inset-0 overflow-hidden z-[1]">
          <div className="absolute -top-40 -left-40 w-80 h-80 bg-blue-200/20 rounded-full blur-3xl animate-pulse" />
          <div className="absolute -bottom-40 -right-40 w-80 h-80 bg-purple-200/20 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }} />
        </div>

        <div className="relative z-10 w-full max-w-4xl">
          <div className={`transition-all duration-1000 ${mounted ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
            <div className="flex justify-center mb-4">
              <Badge className="bg-gradient-to-r from-indigo-100/90 to-purple-100/90 backdrop-blur-sm text-indigo-700 border-indigo-200 shadow-lg px-4 py-1.5">
                <Network className="w-3 h-3 mr-1" />
                全球首个 A2A 架构医学科研平台
              </Badge>
            </div>
          </div>

          <div className={`transition-all duration-1000 delay-100 text-center ${mounted ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
            <h1 className="text-3xl lg:text-4xl font-bold text-slate-900 mb-3 leading-tight">
              医学科研
              <span className="bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                智能圆桌会
              </span>
            </h1>
            <p className="text-base text-slate-600 mb-4 max-w-xl mx-auto">
              多人协作医学科研讨论平台，与 AI 专家一起探讨临床问题
            </p>
          </div>

          {/* Login Card - Simplified */}
          <div className={`transition-all duration-1000 delay-200 ${mounted ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
            <Card className="w-full max-w-md mx-auto border-0 shadow-2xl">
              <CardHeader className="text-center">
                <CardTitle className="text-2xl font-bold text-slate-900">MedRoundTable</CardTitle>
                <CardDescription className="text-slate-600">
                  多人协作医学科研圆桌会议平台
                </CardDescription>
              </CardHeader>

              <CardContent className="space-y-4">
                {error && (
                  <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                    <div className="flex items-center gap-2 text-red-700">
                      <span className="text-sm">{error}</span>
                    </div>
                  </div>
                )}

                <div className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-lg p-3 border border-indigo-100">
                  <div className="flex items-center gap-2 mb-2">
                    <Bot className="w-5 h-5 text-indigo-600" />
                    <span className="text-sm font-semibold text-indigo-900">A2A 智能协作</span>
                  </div>
                  <p className="text-xs text-indigo-700">
                    5位 AI 专家自动协作，从临床问题到科研成果全流程自动化。
                  </p>
                </div>

                <Button
                  onClick={handleLogin}
                  disabled={isLoading}
                  className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white"
                  size="lg"
                >
                  {isLoading ? '正在跳转...' : '使用 SecondMe 登录'}
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
