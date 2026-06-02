# authenticate-user

Fonction OpenFaaS permettant d'authentifier un utilisateur COFRAP à partir de :

- son nom d'utilisateur ;
- son mot de passe généré automatiquement ;
- son code 2FA/TOTP.

## Entrée attendue

```json
{
  "username": "testuser",
  "password": "mot_de_passe_genere",
  "otp_code": "123456"
}