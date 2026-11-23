# JBL Infrared

Integração personalizada do Home Assistant para controlar soundbars JBL (SB120, SB140, SB160, SB170 e SB190, que usam o mesmo controle remoto) por meio de um proxy infravermelho, como um dispositivo ESPHome com `ir_rf_proxy`.

Ela segue o modelo da integração oficial **LG Infrared** e usa a plataforma nativa `infrared` do Home Assistant (2026.4 ou mais recente).

## O que ela cria

| Entidade | Quando | O que faz |
|---|---|---|
| `media_player` | com emissor | Liga/desliga, volume +/−, mudo, play/pause, anterior/próxima, fonte (HDMI IN, HDMI ARC, Optical, Bluetooth) e modo de som (Music, Movie, News). Estado presumido. |
| `button` (um por tecla) | com emissor | Envia uma tecla do controle, incluindo Voice, Dolby Atmos e Bass |
| `event` "Comando recebido" | com receptor | Dispara um evento a cada tecla do controle JBL apertada |

## Códigos IR

Capturados de um controle da SB190 (protocolo NEC, endereço `0xBD02`):

| Tecla | Comando | | Tecla | Comando |
|---|---|---|---|---|
| Ligar/desligar | `0x53` | | Optical | `0x4D` |
| Mudo | `0xAD` | | Bluetooth | `0x1B` |
| Volume + | `0x26` | | Music | `0x20` |
| Volume − | `0x28` | | Movie | `0x08` |
| Anterior | `0x25` | | News | `0x6B` |
| Próxima | `0x27` | | Voice | `0x16` |
| Play/pause | `0x0D` | | Dolby Atmos | `0x17` |
| HDMI IN | `0x6C` | | Bass | `0x18` |
| HDMI ARC | `0x6D` | | | |

O ESPHome mostra o comando com 16 bits (por exemplo, `command=0xAC53`); o código da tecla é o byte de baixo (`0x53`), e o de cima é o complemento.

Para capturar teclas novas pelo log do HA (com um receptor configurado):

```yaml
logger:
  logs:
    custom_components.jbl_infrared: debug
```

## Instalação manual

1. Copie `custom_components/jbl_infrared` para a pasta `config/custom_components/` do Home Assistant.
2. Reinicie o Home Assistant.
3. Vá em **Configurações → Dispositivos e serviços → Adicionar integração → JBL Infrared**.

## Limitações

- O controle só tem tecla de ligar/desligar alternada e mudo alternado. Por isso, o estado do `media_player` é presumido e pode ficar fora de sincronia se a soundbar for operada por outro meio.
- As teclas recebidas não atualizam o estado do `media_player`; elas só disparam o evento.
