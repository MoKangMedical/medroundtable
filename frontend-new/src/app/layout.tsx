import type { Metadata } from "next";
import { Inter, Noto_Sans_SC } from "next/font/google";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

const notoSansSc = Noto_Sans_SC({
  variable: "--font-noto-sans-sc",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "MedRoundTable - 医学科研智能圆桌会",
  description: "全球首个基于A2A架构的医学科研协作平台，与AI专家一起探讨临床问题",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN">
      <body
        className={`${inter.variable} ${notoSansSc.variable} antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
