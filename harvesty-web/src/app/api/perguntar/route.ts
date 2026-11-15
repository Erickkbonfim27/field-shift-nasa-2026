import Anthropic from "@anthropic-ai/sdk";
import { NextResponse } from "next/server";
import { analisar, fatos, validarPerfil, validarPoligono } from "@/lib/server/analise";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

// O Claude não calcula nada: recebe os fatos que o motor calculou para a fazenda e só explica.
const SISTEMA = `Você é um extensionista rural do Oeste de Santa Catarina falando com um agricultor familiar com pouca leitura técnica.
Responda em português do Brasil, frases curtas, no máximo 150 palavras.
Regras (spec v2 do projeto Harvesty):
- Use SOMENTE os números dos FATOS. Não invente número nem faça conta nova.
- Comece pela resposta curta à pergunta. Depois: o que ganha e o que arrisca em cada opção; riscos e o que fazer; o que não sabemos.
- Fale sempre de anos ruins: "em cerca de X de cada 10 anos (entre A e B)". Arredonde para inteiro. Sem porcentagem de modelo.
- Item com nivel_evidencia N1 ou "em teste": diga só que está em teste, sem número.
- Não diga: que é validado ou garantido; que o risco de geada é perder a silagem; que a ferramenta prevê o clima da safra; que se não houver aviso o ano é seguro; que o satélite mede o solo; ganho em dinheiro.
- Praga, doença, adubo ou preço: diga que a ferramenta não calcula isso e indique o técnico.
- Texto simples, sem markdown.`;

/** POST { pergunta, poligono, perfil } -> resposta do Claude em texto, transmitida aos poucos. */
export async function POST(req: Request) {
  const corpo = await req.json().catch(() => null);
  const pergunta = String(corpo?.pergunta ?? "").trim().slice(0, 600);
  const poligono = validarPoligono(corpo?.poligono);
  if (!pergunta) return NextResponse.json({ erro: "Escreva ou fale uma pergunta." }, { status: 400 });
  if (!poligono) return NextResponse.json({ erro: "Desenhe a fazenda no mapa antes de perguntar." }, { status: 400 });

  let client: Anthropic;
  try {
    client = new Anthropic(); // ANTHROPIC_API_KEY (ou perfil do `ant auth login`)
  } catch {
    return NextResponse.json({ erro: "A pergunta livre precisa de uma chave da API do Claude no servidor (ANTHROPIC_API_KEY no .env.local)." }, { status: 503 });
  }

  const A = analisar(poligono, validarPerfil(corpo?.perfil));
  const conteudo = `FATOS (JSON):\n${JSON.stringify(fatos(A))}\n\nPERGUNTA DO AGRICULTOR: ${pergunta}`;
  const codificador = new TextEncoder();

  const corpoResposta = new ReadableStream<Uint8Array>({
    async start(controle) {
      const envia = (t: string) => controle.enqueue(codificador.encode(t));
      try {
        const stream = client.beta.messages.stream({
          model: "claude-opus-5-5",
          max_tokens: 16000,
          output_config: { effort: "medium" },
          // se o modelo recusar, o próprio servidor da API tenta de novo num modelo de reserva
          betas: ["server-side-fallback-2026-07-01"],
          fallbacks: "default",
          system: SISTEMA,
          messages: [{ role: "user", content: conteudo }],
        });
        for await (const ev of stream) {
          if (ev.type === "content_block_delta" && ev.delta.type === "text_delta") envia(ev.delta.text);
        }
        const final = await stream.finalMessage();
        if (final.stop_reason === "refusal") envia("\n\nNão consegui responder a esta pergunta. Fale com o técnico da assistência técnica.");
        if (final.stop_reason === "max_tokens") envia("…");
      } catch (e) {
        if (e instanceof Anthropic.AuthenticationError) envia("A pergunta livre não está configurada neste servidor (chave da API do Claude ausente ou inválida).");
        else if (e instanceof Anthropic.RateLimitError) envia("Muitas perguntas seguidas. Espere um pouco e tente de novo.");
        else if (e instanceof Anthropic.APIConnectionError) envia("Não deu para falar com o Claude agora. Tente de novo em instantes.");
        else if (e instanceof Anthropic.APIError) envia(`O Claude não respondeu (erro ${e.status ?? "desconhecido"}).`);
        else if (e instanceof Anthropic.AnthropicError && /authentication method/i.test(e.message))
          envia("A pergunta livre precisa de uma chave da API do Claude no servidor (ANTHROPIC_API_KEY no arquivo .env.local). O resto do app funciona sem ela.");
        else { console.error("perguntar:", e); envia("Não deu para responder agora."); }
      } finally {
        controle.close();
      }
    },
  });
  return new Response(corpoResposta, { headers: { "Content-Type": "text/plain; charset=utf-8", "Cache-Control": "no-store" } });
}
