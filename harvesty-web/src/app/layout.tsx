import type { Metadata, Viewport } from "next";
import { Archivo, Bricolage_Grotesque, IBM_Plex_Mono, Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter", weight: ["400", "500", "600"] });
const bricolage = Bricolage_Grotesque({ subsets: ["latin"], variable: "--font-bricolage", weight: ["500", "700"] });
const plex = IBM_Plex_Mono({ subsets: ["latin"], variable: "--font-plex-mono", weight: ["400", "500"] });
const archivo = Archivo({ subsets: ["latin"], variable: "--font-archivo", weight: ["900"] });

export const metadata: Metadata = {
  title: "Harvesty",
  description: "Riscos do clima para a fazenda familiar do Oeste de Santa Catarina, com dados da NASA (POWER e SRTM).",
  icons: { icon: "/harvesty-icone.svg" },
};

export const viewport: Viewport = { width: "device-width", initialScale: 1, viewportFit: "cover" };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR" className={`${inter.variable} ${bricolage.variable} ${plex.variable} ${archivo.variable}`}>
      <body>{children}</body>
    </html>
  );
}
