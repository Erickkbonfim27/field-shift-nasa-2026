import type { Poligono } from "@/lib/tipos";

// Mistura no talhão raso: números do motor (mistura_talhao, CAD 39 mm) e da validação V3 (spec v2, estratégia E3).
export const MIS = { s: 7, p10: 46.9, ic: [31.1, 60.8] as [number, number], media: 8.0, mediaIc: [5.4, 11.3] as [number, number] };

// Sítio fictício de exemplo em São Miguel do Oeste (o mesmo do app estático).
export const EXEMPLO: Poligono = [[-53.5648, -26.6862], [-53.5592, -26.6851], [-53.5571, -26.6893], [-53.5603, -26.6931], [-53.5655, -26.6914]];
