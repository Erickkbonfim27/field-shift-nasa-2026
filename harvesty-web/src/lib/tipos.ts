// Tipos compartilhados entre o servidor (rotas de API) e a interface.

export type Ponto = [number, number]; // [lon, lat]
export type Poligono = Ponto[];

export type Cultura = "milhoV" | "milho2" | "soja" | "aveia" | "sorgo" | "perene";
export type Prioridade = "comida" | "custo" | "solo" | "renda";
export type SoloDeclarado = "auto" | "raso" | "medio" | "fundo";

export interface Perfil {
  ativ: "leite" | "graos" | "ambos";
  vacas: number;
  cult: Cultura[];
  mesV: number; // mês de plantio do milho de verão (8 a 12)
  data2: number; // dia do ano do plantio do 2º milho (0 = não planta)
  gdd: 1100 | 1250 | 1400; // ciclo do híbrido (graus-dia até o corte)
  solo: SoloDeclarado;
  pri: Prioridade[];
}

export const PERFIL_PADRAO: Perfil = {
  ativ: "leite", vacas: 18, cult: ["milhoV", "milho2", "perene"], mesV: 9, data2: 31, gdd: 1250, solo: "auto", pri: ["comida", "solo"],
};

export type NivelEvidencia = "N2" | "N1" | "MED" | "CONF";

export interface Risco {
  id: string;
  t: string;
  ev: NivelEvidencia;
  num: string;
  dado: string; // pode ter <b>; gerado só no servidor, nunca com texto do usuário
  fazer: string[];
  limite: string;
  rastro: string;
}

export interface LinhaJanela { d: string; em10: number; ic95: [number, number]; n: number }

export interface Analise {
  area: number;
  mun: string;
  celula: { id: string; lat: number; lon: number; elev: number; api: string };
  relevo: { pct: number[]; px: number; morro: number } | null;
  perfil: Perfil;
  limite: string | null;
  limitePorLimiar: Record<string, string | null>;
  limitePorCiclo: Record<string, string | null>;
  riscoLim: { em10: number; ic95: [number, number] } | null;
  ch2: { v: number; ic: [number, number] } | null;
  tarde: { v: number; ic: [number, number] } | null;
  janela: { linhas: LinhaJanela[]; dias: number; periodo: string; seguro: string | null };
  seco: { alertas: number[]; nSafras: number };
  fournier: number[];
  topEros: number[];
  curva2: { k: number[]; n: number[]; sm: number[]; limiteDoy: number | null }; // dias 1..90, no ciclo do perfil
  riscos: Risco[];
  mensagem: string;
  periodo: { ini: number; fim: number };
}

export interface Fazenda {
  id: number;
  nome: string;
  poligono: Poligono;
  perfil: Perfil;
  criadaEm: string;
  atualizadaEm: string;
}

export interface CamadaCelula { id: string; lat: number; lon: number; limite: string | null; chuvaPct: number | null }

export interface DadosAno {
  ano: number;
  tmin: number[]; // 1/jan a 30/set
  chuvaMensal: number[];
  medMes: number[];
  dezfev: number;
  med: number;
  janela2: { inicio: number; dias: number } | null; // em dias desde 1/jan
}
