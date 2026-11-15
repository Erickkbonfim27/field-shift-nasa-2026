# Séries do NASA POWER da validação V1

Esta pasta guarda as séries diárias do NASA POWER (comunidade AG) dos pontos novos usados na extensão fora da amostra da V1. Os arquivos `power_*.json` (cerca de 45 MB) não estão no repositório, porque qualquer pessoa pode baixá-los de novo.

Para baixar:

```bash
bash solucao/validacao/V1/baixa_power.sh
```

O motor (`solucao/motor`) só cita esta pasta no rastro dos números de São Miguel do Oeste; ele não lê estes arquivos para gerar as saídas.
