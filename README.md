# Miniprojeto - Análise Exploratória da Base Varejo

**Aluno:** Luiz Fernando Damasco
**Turma:** T8

# Objetivo

Fazer uma análise exploratória da base Varejo usando Python e pandas: ler o CSV, verificar a qualidade dos dados, limpar o que estava errado, calcular estatísticas simples e agrupamentos, e salvar uma base tratada (`varejo_limpo.csv`) que possa ser gerada de novo a partir da original.

# Origem da base

- Fonte: Kaggle, base "Base Varejo" (https://www.kaggle.com/datasets/namespaiva/base-varejo/data)
- Arquivo usado: `Base_Varejo.csv`, obtido em outubro de 2026
- Identificação da versão usada: 830.000 linhas de dados + cabeçalho, 14 colunas no cabeçalho, 48,8 MB, separador `;`, MD5 `cc9fe0e90a5863fbc53582a6d78eb261`
- Local no repositório: `dados/Base_Varejo.csv`

# O que cada linha representa

Cada linha é um item de uma compra. Uma compra (`CO_ID`) tem várias linhas, uma para cada produto passado no caixa. Por isso foi preciso separar três contagens diferentes na análise:

- **registros/itens** = linhas da base (830.000)
- **compras** = valores distintos de `CO_ID` (18.471)
- **clientes** = valores distintos de `CL_ID` (1.000)

## Colunas

| Coluna | Significado | Observação |
|---|---|---|
| DATA | data da compra | dia/mês/ano no original, exportada como AAAA-MM-DD |
| CO_ID | código da compra | identificador, não é usado como medida |
| CL_ID | código do cliente | identificador |
| CL_GENERO | gênero do cliente | F ou M |
| CL_EC | estado civil do cliente | código de 1 a 5, a fonte não traz a legenda |
| CL_FHL | número de filhos | 0 a 4, usado nas estatísticas |
| CL_SEG | segmento do cliente | A, B ou C, a fonte não traz a legenda |
| PR_ID | código do produto | identificador |
| PR_CAT | categoria do produto | alimentos, higiene, limpeza, bebidas, pet, acessórios |
| PR_NOME | nome do produto | |

O significado foi deduzido dos prefixos (CL = cliente, CO = compra, PR = produto) e dos valores. Foi conferido que cada cliente tem sempre o mesmo gênero, estado civil, filhos e segmento, que cada compra tem uma só data e um só cliente e que cada produto tem uma só categoria e nome

## Diagnóstico de qualidade

| Verificação | Encontrado |
|---|---|
| Valores ausentes nas 10 colunas com dados | 0 |
| Colunas totalmente vazias (`Unnamed: 10` a `Unnamed: 13`) | 4 colunas, 830.000 ausentes cada |
| Textos vazios ou só com espaços | 0 |
| Espaços no começo ou fim do texto | 0 |
| `#N/D` em PR_CAT e PR_NOME (produto 107) | 3.650 linhas |
| Texto com minúscula (`REFRIGERANTE LIMaO`) | 7.320 linhas |
| Erro de digitação (`HAMBUGUER`) | 7.212 linhas |
| Linhas duplicadas (todas as colunas iguais) | 96.553 |
| Datas inválidas | 0 (período de 04/01/2019 a 08/12/2022) |

## Decisões de limpeza

1. **Colunas vazias removidas.** As 4 colunas sem nome vêm dos `;;;;` que sobram no fim de cada linha do CSV. Estão 100% vazias, então não têm informação nenhuma.
2. **Texto padronizado** em `CL_GENERO`, `CL_SEG`, `PR_CAT` e `PR_NOME`: sem espaço nas bordas, tudo maiúsculo e sem acento, que é o padrão do resto da base. Isso corrigiu `REFRIGERANTE LIMaO` para `REFRIGERANTE LIMAO`.
3. **`HAMBUGUER` corrigido para `HAMBURGUER`.** Foi o único nome com erro de digitação encontrado na lista dos 118 nomes.
4. **`#N/D` trocado por `NAO IDENTIFICADO` (linhas mantidas).** O `#N/D` é erro de PROCV do Excel, ou seja, um valor ausente disfarçado. Ele aparece só no produto 107, nas duas colunas. Não dá para descobrir qual é o produto, então não foi inventada categoria. As linhas foram mantidas porque são itens reais de 3.228 compras; apagar elas diminuiria o tamanho dessas compras.
5. **Duplicatas mantidas.** As 96.553 linhas repetidas são o mesmo produto aparecendo mais de uma vez na mesma compra. Como a base não tem coluna de quantidade, cada linha é uma unidade, e comprar 2 bananas gera 2 linhas iguais. Para confirmar, foi calculado quantas repetições apareceriam se os produtos fossem escolhidos ao acaso: 96.858, quase igual às 96.553 encontradas. Também não existe nenhuma compra inteira repetida com outro código, e os 594 casos de mesmo cliente com duas compras no mesmo dia são compras diferentes (outro `CO_ID`). Assim, nenhuma duplicata foi confirmada como erro e nenhuma linha foi apagada.
6. **DATA convertida para data**, o que também confirmou que não há data inválida.

Resultado: **830.000 registros antes e 830.000 depois**, 14 colunas antes e 10 depois, 0 células ausentes, 0 `#N/D` e 0 textos fora do padrão.

## Conclusões

- A base tem 830.000 itens vendidos em 18.471 compras de 1.000 clientes, entre jan/2019 e dez/2022. Cada compra tem em média **44,9 itens** 
- **Alimentos** são 52,4% dos itens e aparecem em 98,9% das compras. Higiene (18,7%) e limpeza (17,6%) também aparecem em mais de 94% das compras. Acessórios estão em só 49,9% das compras e são 1,8% dos itens.
- Mulheres são 519 dos 1.000 clientes e respondem por 52,1% dos itens. O comportamento por cliente é praticamente igual entre os gêneros: 45,0 x 44,9 itens por compra e 18,5 x 18,4 compras por cliente. A diferença no total vem só de ter mais clientes mulheres.
- Os clientes têm em média **1,14 filho** (0 a 4), e 527 dos 1.000 não têm filhos. A participação de produtos infantis (fralda, papinha, chupeta, mordedor e lenço umedecido) fica entre 4,30% e 4,46% dos itens em todos os grupos, de 0 a 4 filhos. Ou seja, nesta base ter filhos não muda a compra desses produtos.
- **Recomendação:** como alimentos, higiene e limpeza estão em quase toda compra, essas categorias devem ter prioridade de estoque e exposição. Já campanhas de produtos infantis não precisam ser direcionadas só para clientes com filhos, porque os dados não mostram diferença entre os grupos.
- **Limitação:** a base não tem preço nem quantidade, então não foi possível analisar faturamento ou ticket médio, e foi assumido que cada linha é uma unidade. Além disso, os códigos de estado civil e segmento não têm legenda, e o produto 107 não pôde ser identificado.

## Explicação do processo

A leitura acontece no início do script, com `pd.read_csv` lendo `dados/Base_Varejo.csv` com separador `;`. A transformação fica toda dentro da função `tratar_dados()` (Sprints 2 e 3), que recebe a base bruta e devolve uma cópia limpa, e a função `diagnostico()` é chamada antes e depois para comparar. isso fica salvo no final (Sprint 5), com `to_csv('varejo_limpo.csv', index=False)`. A decisão que mais pesou na análise foi manter as linhas repetidas: se elas fossem apagadas como duplicatas, a média de itens por compra cairia de 44,9 para 39,7, uma subestimativa de cerca de 12% causada por apagar unidades que foram realmente compradas.