import os
import pandas as pd
import matplotlib.pyplot as plt

# miniprojeto - analise exploratoria de dados 
# aluno: luiz fernando damasco - turma T8
# cada linha da base e um item de uma compra (mesma compra = mesmo CO_ID)

pd.set_option('display.width', 200)
pd.set_option('display.max_columns', 20)

# arquivos
ARQ_ENTRADA = 'dados/Base_Varejo.csv'     #base original (separador ;)
ARQ_SAIDA = 'varejo_limpo.csv'            #base tratada
PASTA_FIG = 'figuras'

COLS_TEXTO = ['CL_GENERO', 'CL_SEG', 'PR_CAT', 'PR_NOME']
CORRECOES_NOME = {'HAMBUGUER': 'HAMBURGUER'} 
INFANTIS = ['FRALDA', 'PAPINHA INFANTIL', 'CHUPETA', 'MORDEDOR', 'LENCO UMEDECIDO']


#ausentes, textos vazios, espacos, #N/D, minusculas e duplicadas
def diagnostico(df):
    tab = pd.DataFrame(index=df.columns)
    tab['tipo'] = df.dtypes.astype(str)
    tab['ausentes'] = df.isna().sum()
    tab['vazios'] = 0          #texto vazio ou so com espaco
    tab['espaco_borda'] = 0    #espaco no comeco ou no fim
    tab['erro_ND'] = 0         #'#N/D' que vem de procv quebrado no excel
    tab['minusculas'] = 0      #texto com letra minuscula

    cols_txt = df.select_dtypes(exclude=['number', 'datetime']).columns
    for col in cols_txt:
        txt = df[col].dropna().astype(str)
        tab.loc[col, 'vazios'] = (txt.str.strip() == '').sum()
        tab.loc[col, 'espaco_borda'] = (txt != txt.str.strip()).sum()
        tab.loc[col, 'erro_ND'] = (txt.str.strip() == '#N/D').sum()
        tab.loc[col, 'minusculas'] = txt.str.contains('[a-z]').sum()

    n_dup = df.duplicated().sum()
    return tab, n_dup


# padroniza texto: tira espaco das bordas, passa pra maiuscula e remove acento
def padronizar_texto(serie):
    serie = serie.astype(str).str.strip().str.upper()
    return serie.str.normalize('NFKD').str.encode('ascii', 'ignore').str.decode('ascii')


#tratamento da base
def tratar_dados(df, correcoes):
    df = df.copy()

    #colunas 100% vazias
    vazias = df.columns[df.isna().all()]
    df = df.drop(columns=vazias)

    # texto padronizado
    for col in COLS_TEXTO:
        df[col] = padronizar_texto(df[col])

    # #N/D e valor ausente disfarcado -> mantem a linha e deixa explicito
    for col in ['PR_CAT', 'PR_NOME']:
        df[col] = df[col].replace('#N/D', 'NAO IDENTIFICADO')

    # erro de digitacao no nome do produto
    df['PR_NOME'] = df['PR_NOME'].replace(correcoes)

    #data em formato normal 
    df['DATA'] = pd.to_datetime(df['DATA'], format='%d/%m/%Y')

    return df


# resumo por grupo: clientes, compras e itens
def gerar_resumo(df, coluna):
    res = df.groupby(coluna).agg(clientes=('CL_ID', 'nunique'),
                                 compras=('CO_ID', 'nunique'),
                                 itens=('PR_ID', 'size'))
    res['itens_por_compra'] = (res['itens'] / res['compras']).round(1)
    res['pct_itens'] = (100 * res['itens'] / res['itens'].sum()).round(2)
    return res.sort_values('itens', ascending=False)



#leitura e diagnostico

bruto = pd.read_csv(ARQ_ENTRADA, sep=';')

print('primeiras linhas')
print(bruto.head())
print('\nregistros (linhas):', bruto.shape[0])
print('colunas:', bruto.shape[1])
print('nomes das colunas:', list(bruto.columns))
print('\ntipos de dados')
print(bruto.dtypes)

diag_antes, dup_antes = diagnostico(bruto)
print('\ndiagnostico ANTES da limpeza')
print(diag_antes)
print('linhas duplicadas (todas as colunas iguais):', dup_antes)

# verificar o motivo das duplicadas 
rep = bruto.groupby(['CO_ID', 'PR_ID']).size()
print('\nvezes que o mesmo produto aparece na mesma compra:')
print(rep.value_counts().sort_index())

# p = fracao de cada produto na base, n = itens da compra
p = bruto['PR_ID'].value_counts(normalize=True)
n_itens = bruto.groupby('CO_ID').size()
esperado = 0
for n in n_itens:
    esperado += n - (1 - (1 - p)**n).sum()
print('repeticoes esperadas pelo acaso:', round(esperado), '| encontradas:', dup_antes)

# compra inteira repetida com outro CO_ID
assinatura = bruto.sort_values('PR_ID').groupby('CO_ID').agg(
    cliente=('CL_ID', 'first'), data=('DATA', 'first'),
    itens=('PR_ID', lambda s: ','.join(s.astype(str))))
print('compras inteiras repetidas:', assinatura.duplicated().sum())
print('mesmo cliente com mais de uma compra no mesmo dia:',
      assinatura.duplicated(['cliente', 'data']).sum(), '(compras diferentes, nao sao duplicata)')

# atributos do cliente e do produto sao fixos por id?
print('\nconsistencia por id (qtd de ids com mais de um valor):')
print('cliente -> genero, ec, filhos, seg:',
      (bruto.groupby('CL_ID')[['CL_GENERO', 'CL_EC', 'CL_FHL', 'CL_SEG']].nunique() > 1).sum().sum())
print('compra -> data, cliente:', (bruto.groupby('CO_ID')[['DATA', 'CL_ID']].nunique() > 1).sum().sum())
print('produto -> categoria, nome:', (bruto.groupby('PR_ID')[['PR_CAT', 'PR_NOME']].nunique() > 1).sum().sum())

print('\nproduto com #N/D (id):', bruto.loc[bruto['PR_CAT'] == '#N/D', 'PR_ID'].unique().tolist(),
      '-', (bruto['PR_CAT'] == '#N/D').sum(), 'linhas')
print('nomes com minuscula:', bruto.loc[bruto['PR_NOME'].str.contains('[a-z]'), 'PR_NOME'].unique().tolist(),
      '-', bruto['PR_NOME'].str.contains('[a-z]').sum(), 'linhas')
print('nome com erro de digitacao:', bruto.loc[bruto['PR_NOME'].isin(CORRECOES_NOME.keys()), 'PR_NOME'].unique().tolist(),
      '-', bruto['PR_NOME'].isin(CORRECOES_NOME.keys()).sum(), 'linhas')



#sprint 2 e 3 - limpeza  e comparacao
base = tratar_dados(bruto, CORRECOES_NOME)

diag_depois, dup_depois = diagnostico(base)
print('\ndiagnostico DEPOIS da limpeza')
print(diag_depois)
print('linhas duplicadas:', dup_depois, '(mantidas, sao unidades repetidas do mesmo produto)')

print('\nantes x depois')
print('registros:', bruto.shape[0], '->', base.shape[0])
print('colunas:', bruto.shape[1], '->', base.shape[1])
print('celulas ausentes:', bruto.isna().sum().sum(), '->', base.isna().sum().sum())
print('celulas com #N/D:', diag_antes['erro_ND'].sum(), '->', diag_depois['erro_ND'].sum())
print('celulas com minuscula:', diag_antes['minusculas'].sum(), '->', diag_depois['minusculas'].sum())
print('produtos diferentes (nome):', bruto['PR_NOME'].nunique(), '->', base['PR_NOME'].nunique())
print('periodo:', base['DATA'].min().date(), 'a', base['DATA'].max().date())


# sprint 4 - analise
# estatisticas 1: numero de filhos
clientes = base.drop_duplicates('CL_ID')
est_filhos = clientes['CL_FHL'].describe()
print('\nnumero de filhos por cliente')
print('validos:', int(est_filhos['count']), '| media:', round(est_filhos['mean'], 2),
      '| min:', int(est_filhos['min']), '| max:', int(est_filhos['max']))
print('clientes sem filhos:', (clientes['CL_FHL'] == 0).sum())
# se fizer a media direto nas linhas, cliente que compra mais pesa mais
print('media por linha (cliente que compra mais pesa mais):', round(base['CL_FHL'].mean(), 2))

# estatisticas 2: itens por compra
itens_compra = base.groupby('CO_ID').size()
est_itens = itens_compra.describe()
print('\nitens por compra')
print('compras validas:', int(est_itens['count']), '| media:', round(est_itens['mean'], 1),
      '| min:', int(est_itens['min']), '| max:', int(est_itens['max']))
print('se tirasse as linhas repetidas a media cairia para:',
      round(len(base.drop_duplicates()) / base['CO_ID'].nunique(), 1))

# grupo1: por categoria de produto
res_cat = gerar_resumo(base, 'PR_CAT')
res_cat['pct_compras'] = (100 * res_cat['compras'] / base['CO_ID'].nunique()).round(1)
print('\nresumo por categoria (compras = compras com pelo menos 1 item da categoria)')
print(res_cat)

# grupoo 2: por genero do cliente
res_gen = gerar_resumo(base, 'CL_GENERO')
res_gen['compras_por_cliente'] = (res_gen['compras'] / res_gen['clientes']).round(1)
print('\nresumo por genero (a base nao tem preco, entao nao da pra somar faturamento)')
print(res_gen)

# filtro: so itens infantis geram clientes com filhos compram mais?
infantis = base[base['PR_NOME'].isin(INFANTIS)]
print('\nfiltro produtos infantis:', len(infantis), 'itens em', infantis['CO_ID'].nunique(), 'compras')
pct_inf = (100 * infantis.groupby('CL_FHL').size() / base.groupby('CL_FHL').size()).round(2)
res_filhos = pd.DataFrame({'clientes': clientes.groupby('CL_FHL').size(),
                           'itens_total': base.groupby('CL_FHL').size(),
                           'itens_infantis': infantis.groupby('CL_FHL').size(),
                           'pct_infantis': pct_inf})
print('participacao de itens infantis por numero de filhos')
print(res_filhos)

# grafico itens por categoria
os.makedirs(PASTA_FIG, exist_ok=True)
plt.figure(1, figsize=(8, 5))
plt.bar(res_cat.index, res_cat['itens'] / 1000, color='tab:blue')
for i, v in enumerate(res_cat['pct_itens']):
    plt.text(i, res_cat['itens'].iloc[i] / 1000 + 5, f'{v:.1f}%', ha='center')
plt.title('Itens vendidos por categoria (2019-2022)')
plt.xlabel('Categoria')
plt.ylabel('Itens (mil)')
plt.xticks(rotation=20)
plt.grid(axis='y', alpha=0.4)
plt.tight_layout()
plt.savefig(PASTA_FIG + '/itens_por_categoria.png', dpi=150)

# sprint 5 - exportacao
base.to_csv(ARQ_SAIDA, index=False)
conf = pd.read_csv(ARQ_SAIDA)
print('\nbase tratada salva em', ARQ_SAIDA)
print('registros antes:', bruto.shape[0], '| depois:', conf.shape[0])
print('colunas antes:', bruto.shape[1], '| depois:', conf.shape[1])

plt.show()