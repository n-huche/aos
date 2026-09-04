O HTTP (Hypertext Transfer Protocol) transmite hipertexto pela web utilizando um modelo de request-response.

HTTP é um protocolo usado para comunicação na Web.

Quando um navegador acessa um site ele precisa conversar com um servidor. Essa comunicação normalmente acontece usando HTTP (ou HTTPS).

Em termos simples:

Cliente  ─── HTTP Request ───>  Servidor
Cliente  <── HTTP Response ───  Servidor

Originalmente HTTP foi criado para permitir a transferência de documentos de hipertexto, como páginas HTML, mas hoje pode ser usado para transmitir muitos outros tipos de dados.

HTTP define regras para que cliente e servidor saibam como construir, enviar e interpretar requests e responses.

HTTP é um protocolo stateless, no qual cada solicitação é independente.

O protocolo HTTP, por si só, não pressupõe que o servidor "lembre" automaticamente do que aconteceu na request anterior. Isso é relevante em autenticação.

Constitui a base da comunicação na web, sendo frequentemente utilizado com HTTPS para criptografia.

HTTPS não é simplesmente outro protocolo independente do HTTP, HTTPS é HTTP transmitido de forma segura através de TLS. 

TLS é um protocolo de segurança que criptografa os dados trocados pela internet entre um cliente e um servidor.