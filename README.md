# VocoderLive2021

# Table of contents

* [Introducción](#Introducción)
* [Enfoque LPC](#Enfoque-LPC)
* [Contacto](#Contacto)
* [Referencias](#Referencias)
 
# Introducción
>[Table of contents](#table-of-contents)

Para el siguiente proyecto se busco implementar unVocoderde aplicación musical.
Un vocoder es un sistema que analiza el sonido de una persona hablando, y mediante
diferentes algoritmos realiza cambios en los pulsos glotales sin alterar el filtro articu-
latorio, y de esta manera logra sintetizar un sonido artificial de la señal de voz de la
persona que este hablando. Junto con esto, y eligiendo frecuencias fundamentales de
los pulsos glotales acordemente, se pueden generar melodías y acordes para utilizar en
ambientes musicales.


# Enfoque LPC
>[Table of contents](#table-of-contents)

Para poder realizar este sistema se decidió utilizar el enfoqueLinear Prediction Coef-
ficients(LPC), que se detallará brevemente a continuación.

## Modelo de producción de voz

Si recordamos del modelo de producción de voz, podemos simplificar el modelo en los
bloques de la Figura 2.1.


Figura 2.1:Diagrama en bloques del modelo de producción de voz

Realizando algunos cálculos [2] [3], se llega a la conclusión que el filtro error de predic-
ción estima la inversa del filtro articulatorio, por lo tanto, simplemente estimando el
filtro error de predicción podemos utilizar el filtro articulatorio obtenido de una porción
de audio para sintetizar unos pulsos glotales artificiales.

## Implementación

Para la implementación de este sistema, se realizó el método de la autocorrelación para
estimar los coeficientes del filtro de error de producción y una ventana dehann para
realizar la sintetización^1. Esto se puede ver en el código a continuación^2

(^1) Recordemos que para sintetizar una señal correctamente debemos cumplir con el requisito de que
la suma de las ventanas en el tiempo debe ser constante, y por lo tanto, con las ventanas de hann, el
overlap debe ser del 50 %.
(^2) Este código fue basado en [1], donde ese código fue implementado para poder sintetizar la voz con
pulsos artificiales, pero intentando modificar lo menos posible la voz de salida respecto de la entrada,

```Python
def vocode(signal , fs , f_custom , block_len , overlap , order , prev_block,p_coverage =0.01 , unvoiced2zeros=True , glotal_type="triang"):

out = zeros(len(signal))
out[:len(prev_block)] = prev_block
prev_delta = 0
T_samples = int((fs / f_custom))

for block , idx in block_process(signal , fs, block_len , overlap):
 gain_correction = (1 - overlap) * 2 # *2 due to hann window
 block *= hann(len(block)) * gain_correction

 rxx = correlate(block , block , mode=’full’)
 rxx = rxx[len(rxx) // 2:]
 period_samples , is_voiced = fundamental_period_estimate(rxx , fs)
 a = -solve_toeplitz(rxx[: order], rxx[1: order + 1])
 a = np.concatenate (([1] , a))
 error_power = rms(lfilter(a, (1,), block))
 if is_voiced:
  vocoded , new_delta = pitch_maker(len(block), T_samples , prev_delta , overlap=overlap)
  prev_delta = new_delta
  impulse_response = glotales[glotal_type ](len(block), p_coverage= p_coverage)
  vocoded = np.convolve(vocoded , impulse_response , mode="same")
 else:
  if unvoiced2zeros:
   vocoded = np.zeros(len(block))
  else:
   vocoded = randn(len(block)) / 2

 vocoded = lfilter (( error_power ,), a, vocoded)
 vocoded *= hann(len(block))
 out[idx:idx + len(block)] += deemphasis(vocoded)
return out
```


En este código se puede ver que, lo primero que se realiza es dividir la señal de en-
trada en bloques deblock_lenmilisegundos, con un overlap deoverlap%^3 , luego, se
trabajará por bloques. Como se puede ver, en cada bloque, lo primero que se hace
es obtener la autocorrelaciónRxx(τ)paraτ ≥ 0 , y se llama a la funciónfundamen-
tal_period_estimate, esta función definida por el creador del código original se utilizaba
por ejemplo para utilizarla en codificación de voz. 3
En este caso, el overlap siempre debería ser del 50 % ya que solo se utiliza ventanas de hann
para obtener el período de los pulsos glotales así como para saber si la señal es sonora
o sorda. Si ahondamos mas profundo en la función y con lo que nos interesa (saber si
la señal es sonora o no), podemos ver que el método que se realiza para determinar si
la señal es o no sonora, simplemente se busca cual es el máximo de la autocorrelación,
y si esta supera un cierto threshold, se determina que es sonora, esto se puede ver
en el Listing 2. Una vez hecho esto, se determinan los coeficientes del filtro error de
producción consolve_toeplitz, y se estima la potencia de error para hacer el control
automático de ganancia (AGC) al final de la síntesis. Finalmente, cuando la señal de
entrada es determinada como sonora, se realizan los pulsos glotales deseados y se los
filtran por el filtroH(z) =AG(z), siendo A(z) el filtro error de predicción yG^2 =e(n).

```Python
1 def fundamental_period_estimate(rxx , fs):
2 """
3 Calculates the fundamental frequency of an auto correlation array.
4 rxx the auto correlation array.
5 fs the sample rate in hertz.
6 """
7 f_low , f_high = 50, 250
8 f_low_idx = round(fs / f_low)
9 f_high_idx = round(fs / f_high)
10 period_idx = argmax(rxx[f_high_idx:f_low_idx ]) + f_high_idx
11 is_voiced = max(rxx) > 0.
12 return (period_idx , is_voiced)
```

## Pulsos glotales



Para la implementación de pulsos glotales sintéticos, se utilizaron 4 formas de pulsos
distintas, ellas son:

Triangular: Cuenta con una amplia personalización donde se es capaz de ajustar
la pendiente de crecimiento, la de decrecimiento, la altura, el ancho, el final de
la primera rampa, y el comienzo de la segunda rampa.
Hamming: Es una ventana de hamming centrada, con ancho ajustable y ampli-
tud ajustable.
Cuadrada: Es un pulso cuadrado con personalización del ancho y la altura del
mismo
Exponencial: Un pulso centrado en 0 donde la parte negativa es una exponencial
creciente y la parte positiva una exponencial decreciente.

[]()

Ejemplos de estos pulsos se pueden ver en la Figura superior. Por otro lado, si sintetizamos
una señal de voz de ejemplo con estos pulsos glotales, con los siguientes parámetros:

* Frecuencia = 500 (Hz)

* Overlap = 50 %

* Bloque = 32 (ms)

Obtenemos los resultados que se pueden observar en la Figura a continuación.

[]()

# Contacto
>[Table of contents](#table-of-contents)

Please do not hesitate to reach out to me if you find any issue with the code or if you have any questions.

* Personal email: [idiaz@itba.edu.ar](mailto:idiaz@itba.edu.ar)

* LinkedIn Profile: [https://www.linkedin.com/in/iancraz/](https://www.linkedin.com/in/iancraz/)

# Referencias
>[Table of contents](#table-of-contents)

[1] Bastian Bechtold.Pocoder.url:https://github.com/bastibe/pocoder.

[2] Thomas F. Quatieri.Discrete Time Speech Signal Proccesing: Principles and prac-
tice. 1.aed. Prentice-Hall, Inc, 2002.isbn: 0-13-242942-X.

[3] Lawrence R. Rabiner y Ronald W. Schafer.Introduction to Digital Speech Proces-
sing. 1.aed. now Publishers Inc., 2007.isbn: 978-1-60198-070-0.

# Licencia
>[Table of contents](#table-of-contents)

```
MIT License

Copyright (c) 2021 Ian Cruz Diaz

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

