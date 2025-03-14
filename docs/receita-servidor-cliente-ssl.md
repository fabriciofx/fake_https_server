# Passos para Criar um Servidor HTTPS com Certificado Autoassinado e CA Própria

1. **Criar uma Autoridade Certificadora (CA)**

2. **Gerar um Certificado de Servidor e Assiná-lo com a CA**

3. **Criar um Servidor HTTPS em Python 3.13**

4. **Testar a Conexão com o Servidor**

## Passo 1: Criar uma CA Própria

Antes de emitir certificados para o servidor, precisamos criar uma
**CA (Autoridade Certificadora)**.

### 1.1 Criar um arquivo de configuração `openssl.cnf`

```conf
[ ca ]
default_ca = my_ca

[ my_ca ]
dir               = .
certs             = $dir/certs
new_certs_dir     = $dir/newcerts
database          = $dir/index.txt
serial            = $dir/serial
default_md        = sha256
policy            = policy_any
email_in_dn       = no
copy_extensions   = copy

[ policy_any ]
countryName       = optional
stateOrProvinceName = optional
localityName      = optional
organizationName  = optional
organizationalUnitName = optional
commonName        = supplied
emailAddress      = optional

[ req ]
default_bits       = 2048
default_md         = sha256
distinguished_name = req_distinguished_name
x509_extensions    = v3_ca

[ req_distinguished_name ]
countryName         = Country Name (2 letter code)
stateOrProvinceName = State or Province Name (full name)
localityName        = Locality Name (eg, city)
organizationName    = Organization Name (eg, company)
commonName          = Common Name (e.g. server FQDN or YOUR name)

[ v3_ca ]
subjectKeyIdentifier = hash
authorityKeyIdentifier = keyid:always,issuer
basicConstraints = critical, CA:TRUE
keyUsage = critical, keyCertSign, cRLSign
```

### 1.2 Criar a chave privada da CA

```bash
openssl genpkey -algorithm RSA -out ca.key -aes256
```

- Gera um arquivo **`ca.key`** protegido por senha.

### 1.3 Criar um certificado para a CA

```bash
openssl req -new -x509 -key ca.key -sha256 -days 3650 -out ca.crt
    -config openssl.cnf
```

- Esse comando gera um certificado autoassinado para a CA (**`ca.crt`**)
  válido por **10 anos (3650 dias)**.

### 1.3 Verificar se a extensão `keyUsage` está presente

```bash
openssl x509 -in ca.crt -text -noout | grep -A1 "Key Usage"
```

Se estiver correto, a saída incluirá:

```bash
X509v3 Key Usage: critical
Key Cert Sign, CRL Sign
```

---

## Passo 2: Criar um Certificado para o Servidor

Agora, vamos gerar um certificado para o servidor e assiná-lo com a CA.

### 2.1 Criar a chave privada do servidor

```bash
openssl genpkey -algorithm RSA -out server.key
```

### 2.2 Criar um CSR (Certificate Signing Request) para o servidor

```bash
openssl req -new -key server.key -out server.csr
```

- Durante esse processo, o OpenSSL pedirá informações como o
**Common Name (CN)**.
- O **CN** deve ser o nome do host que você usará para acessar o servidor
(exemplo: `localhost`).

### 2.3 Assinar o CSR com a CA

```bash
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial
    -out server.crt -days 3650 -sha256
```

- Isso gera o certificado assinado pela CA: **`server.crt`**.

### 2.4 Verificar se o Certificado do Servidor foi Assinado pelo CA

Verifique a assinatura do certificado do servidor com o seguinte comando:

```bash
openssl verify -CAfile ca.crt server.crt
```

Se o comando não retornar **"OK"**, gere um novo certificado para o servidor e
assine com a CA.

---

## Passo 3: Criar um Servidor HTTPS em Python 3.13

Agora que temos os certificados, podemos criar um **servidor HTTPS**.

### Código do Servidor HTTPS

```python
import http.server
import ssl

# Configuração do servidor, porta 4443
server_address = ('0.0.0.0', 4443)
 # Manipulador padrão para servir arquivos
handler = http.server.SimpleHTTPRequestHandler

# Criar o servidor HTTP
httpd = http.server.HTTPServer(server_address, handler)

# Criar contexto SSL com os certificados gerados
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(certfile="server.crt", keyfile="server.key")
# Opcional, se quiser validar clientes
context.load_verify_locations("ca.crt")

# Associar o contexto SSL ao socket do servidor
httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

print("Servidor HTTPS rodando em https://localhost:4443")
httpd.serve_forever()
```

- Esse código cria um **servidor HTTPS** escutando na porta **`4443`**.
- Ele utiliza os arquivos **`server.key`** (chave privada) e **`server.crt`**
  (certificado assinado pela CA).
- O servidor usa `SimpleHTTPRequestHandler` para servir arquivos do diretório
  atual.

---

## Passo 4: Testar a Conexão

### Testar no Navegador

Abra no navegador:

```bash
https://localhost:4443
```

- **Se o navegador mostrar um aviso de "Conexão não segura"**, isso acontece
porque a CA não é reconhecida. Você pode adicionar o arquivo **`ca.crt`** ao
sistema para resolver isso.

### Testar com `curl`

Para ignorar a verificação SSL:

```bash
curl -k https://localhost:4443
```

Ou, para validar a CA:

```bash
curl --cacert ca.crt https://localhost:4443
```

### Testar com `requests` no Python

Crie um cliente Python para se conectar ao servidor:

```python
import requests

response = requests.get("https://localhost:4443", verify="ca.crt")
print(response.text)
```

Se quiser ignorar a verificação SSL (para testes apenas):

```python
response = requests.get("https://localhost:4443", verify=False)
```

### Testar com `http.client` no Python

Crie um cliente Python para se conectar ao servidor:

```python
import http.client
import ssl

# Criar um contexto SSL confiando na CA personalizada
context = ssl.create_default_context(cafile="ca.crt")

# Criar a conexão HTTPS
conn = http.client.HTTPSConnection("localhost", 4443, context=context)

# Fazer uma requisição
conn.request("GET", "/")
response = conn.getresponse()

# Exibir a resposta
print("Status:", response.status)
print("Resposta:", response.read().decode())

conn.close()
```

## Resumo

1. **Criamos uma CA própria** (`ca.key`, `ca.crt`).

2. **Geramos um certificado de servidor assinado pela CA**
(`server.key`, `server.crt`).

3. **Criamos um servidor HTTPS em Python 3.13**.

4. **Testamos a conexão usando navegador, `curl` e `requests`**.

Agora você tem um **servidor HTTPS seguro com certificado autoassinado e uma
CA própria**!
