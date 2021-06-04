# Perftool
### Perftool é uma ferramenta para análise de desempenho de rede. A ferramenta suporta os seguintes parâmetros de entrada:

- execução em modo cliente (-c) ou servidor (-s)
- seleção de uso do protocolo TCP (-t) ou UDP (-u) para comunicação
- definição da porta (-p <porta>) na qual o servidor irá escutar, ou na qual o cliente irá se conectar
- definição do IP (-a <endereço>) do servidor no qual o cliente deve se conectar
- tamanho inicial, final e incremento (-w <inicio,fim.inc>) do pacote em bytes que deverá ser enviado pelo cliente ao servidor
- quantidade de transmissões (-n <número>) do pacote a serem realizadas pelo cliente para cada tamanho
- tamanhos do buffer de envio e recebimento (-b <buffer>) a serem configurados no socket (TCP ou UDP). Se não for especificado o tamanho do buffer ou indicado o tamanho como 0, deverá ser utilizado o valor padrão definido pelo sistema operacional.

A ferramenta deve ser configurada no modo servidor em uma máquina e no modo cliente em outra máquina. O servidor atuará como um servidor de echo, retornando o mesmo conteúdo para o cliente. Ao iniciar o modo cliente, a ferramenta deve iniciar a transmissão dos dados, considerando o tamanho inicial, final e incremento da quantidade de dados. Cada pacote de dados com um determinado tamanho deverá ser enviado N vezes, onde o N é especificado na entrada (com o parâmetro -n). A saída da ferramenta deve apresentar para cada tamanho de transmissão as seguintes informações (separadas por vírgula):
